"""
==============================================================================
CAMADA 1 — DETECCAO POR ASSINATURA
==============================================================================
Este modulo implementa a PRIMEIRA camada do WAF hibrido: um detector por
assinatura, no estilo do OWASP Core Rule Set. Ele existe porque a tese do
trabalho mudou de enquadramento.

--- O QUE MUDOU, E POR QUE -------------------------------------------------
A versao anterior do trabalho comparava ML CONTRA assinaturas, como se fossem
alternativas concorrentes. Esse enquadramento e falso na pratica: ninguem
desliga o ModSecurity para ligar um Random Forest. E ele tambem desperdica o
resultado mais forte que eu tinha medido.

Os perfis de erro dos dois detectores sao COMPLEMENTARES:

    assinaturas -> precisao altissima, recall limitado.
                   quando disparam, quase nunca erram; mas sao cegas para
                   tudo o que ninguem catalogou.
    modelo ML   -> recall alto, precisao menor.
                   generaliza para variantes nao catalogadas; mas ocasionalmente
                   bloqueia linguagem natural que so PARECE ataque.

Somar detectores so vale a pena quando eles erram em coisas DIFERENTES, e e
exatamente esse o caso aqui. Por isso a arquitetura passou a ser em cascata:

    Camada 1 (este modulo)  -> assinatura casou? bloqueia, com a regra nomeada.
    Camada 2 (o modelo)     -> julga o que a camada 1 liberou.

--- HONESTIDADE SOBRE O QUE ESTE MODULO E, E O QUE NAO E -------------------
1. NAO e o OWASP CRS. E um conjunto de ~25 regras INSPIRADO nas familias de
   deteccao do CRS. Um CRS real tem centenas de regras, transformacoes de
   normalizacao e pontuacao de anomalia. Comparar com o CRS de verdade continua
   sendo trabalho futuro declarado.

2. Ele inspeciona a MESMA superficie que o modelo: os valores dos parametros
   ja decodificados. Um ModSecurity real tambem inspecionaria path, headers,
   cookies e corpo. Ou seja, esta camada 1 e mais FRACA que um WAF real -- o
   que torna o ganho medido da camada 2 uma estimativa CONSERVADORA.

3. As regras foram escritas a partir da logica de deteccao do CRS, e NAO
   copiadas de `ingestion_csic.FAMILIAS_PAYLOAD`, que atribui familia de ataque.
   Se eu reusasse aquelas regexes aqui, o recall da camada 1 por familia seria
   100% por construcao, e a medicao nao significaria nada.

   Ainda assim existe SOBREPOSICAO inevitavel entre os dois conjuntos: ambos
   descrevem os mesmos fenomenos (SQLi tem UNION SELECT, XSS tem <script>).
   Consequencia metodologica, declarada em avaliacao_hibrida.py: o recall da
   camada 1 medido POR FAMILIA e otimista, porque a propria definicao de
   familia e feita por regex. Os numeros imunes a esse vies sao os medidos
   contra o rotulo REAL do CSIC (normal/anomalo): recall sobre o conjunto
   anomalo inteiro e taxa de falso positivo sobre o trafego legitimo.

4. NAO incluo regra de impressao digital de scanner (`parosproxy`, `sqlmap`,
   `nikto`). O CSIC 2010 foi gerado com o Paros Proxy, e 748 dos ataques
   carregam a string 'Paros' no payload. Uma regra assim teria recall inflado
   por artefato do dataset, nao por capacidade de deteccao. Deixar de fora e
   uma decisao deliberada.

--- LIMITACAO DE PROJETO ---------------------------------------------------
Assinaturas nao detectam, por definicao, ataque que nao contenha assinatura.
No CSIC isso e 89,9% das anomalias (parameter tampering). Essa nao e uma falha
desta implementacao: e a fronteira da abordagem, e e precisamente o espaco que
a camada 2 ocupa.
==============================================================================
"""

import re
from typing import List, NamedTuple, Optional

import pandas as pd


class Regra(NamedTuple):
    """Uma assinatura. `id` aparece no log de auditoria e na resposta HTTP."""
    id: str
    nome: str
    familia: str
    padrao: str


# =============================================================================
# O CONJUNTO DE REGRAS
# =============================================================================
# Ordem = prioridade: a primeira que casar define o veredito e o motivo. Coloco
# os padroes mais especificos antes dos mais genericos, para que a regra
# reportada seja a mais informativa possivel.
#
# Todas usam (?i) porque o payload chega em minusculas do middleware, mas os
# scripts de medicao podem passar o texto original -- assim o resultado e o
# mesmo nos dois caminhos.
# =============================================================================

REGRAS: List[Regra] = [
    # --- SQL Injection ------------------------------------------------------
    Regra('SQLI-001', 'Tautologia SQL (OR 1=1)', 'SQLi',
          r"(?i)['\"\s(]\s*(?:or|and)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+"),
    Regra('SQLI-002', 'UNION SELECT', 'SQLi',
          r"(?i)\bunion\b[\s\S]{0,40}\bselect\b"),
    Regra('SQLI-003', 'Consulta empilhada apos terminador', 'SQLi',
          r"(?i)['\"]?\s*;\s*(?:drop|select|insert|update|delete|exec|shutdown|truncate)\b"),
    Regra('SQLI-004', 'DDL/DML em valor de parametro', 'SQLi',
          r"(?i)(?:\bdrop\s+(?:table|database)\b|\binsert\s+into\b|\bdelete\s+from\b"
          r"|\bselect\b[\s\S]{0,60}\bfrom\b|\bupdate\b[\s\S]{0,40}\bset\b)"),
    Regra('SQLI-005', 'Funcao SQL de exfiltracao ou atraso', 'SQLi',
          r"(?i)(?:\bwaitfor\s+delay\b|\bsleep\s*\(|\bbenchmark\s*\(|\bpg_sleep\s*\("
          r"|\bload_file\s*\(|\binto\s+(?:out|dump)file\b|\bxp_cmdshell\b)"),
    # O (?!>) impede que o fechamento de um comentario HTML/SSI ('-->') seja
    # reportado como comentario SQL. Sem ele, '<!--#EXEC cmd="ls /"-->' era
    # bloqueado pela regra certa do ponto de vista da decisao e pelo motivo
    # errado do ponto de vista do log -- e o motivo e justamente o que esta
    # camada existe para fornecer.
    Regra('SQLI-006', 'Comentario SQL terminando a expressao', 'SQLi',
          r"""(?:['")\s;]--(?!>)|^--(?!>)|/\*!)"""),
    Regra('SQLI-007', 'Aspa seguida de operador logico', 'SQLi',
          r"(?i)'\s*(?:or|and)\s+"),

    # --- Cross-Site Scripting ----------------------------------------------
    Regra('XSS-001', 'Tag <script>', 'XSS',
          r"(?i)<\s*/?\s*script\b"),
    Regra('XSS-002', 'Atributo manipulador de evento', 'XSS',
          r"(?i)\bon(?:error|load|click|mouseover|mouseout|focus|blur|submit|change"
          r"|keydown|keyup|abort|toggle|animationstart)\s*="),
    Regra('XSS-003', 'Pseudo-protocolo executavel', 'XSS',
          r"(?i)(?:javascript|vbscript)\s*:"),
    Regra('XSS-004', 'Tag HTML perigosa', 'XSS',
          r"(?i)<\s*(?:iframe|svg|object|embed|applet|meta|base|form|frameset|style)\b"),
    Regra('XSS-005', 'Tag com atributo src', 'XSS',
          r"(?i)<\s*(?:img|video|audio|source|input|track|iframe)[^>]{0,120}\bsrc\s*="),
    Regra('XSS-006', 'Sink de JavaScript', 'XSS',
          r"(?i)(?:document\s*\.\s*(?:cookie|location|write|domain)"
          r"|window\s*\.\s*location|\beval\s*\(|string\.fromcharcode|\batob\s*\()"),
    Regra('XSS-007', 'Chamada a dialogo do navegador', 'XSS',
          r"(?i)\b(?:alert|prompt|confirm)\s*\("),
    Regra('XSS-008', 'CSS executavel', 'XSS',
          r"(?i)(?:expression\s*\(|behaviou?r\s*:|-moz-binding|@import\b)"),

    # --- Execucao de comando / Server-Side Includes ------------------------
    # ORDEM: o bloco RCE vem ANTES do bloco LFI, e nao por acaso.
    #
    # O template de SSI do CSIC e '<!--#exec cmd="rm -rf /;cat /etc/passwd" -->'.
    # Com o LFI na frente, a regra de "arquivo sensivel" casava primeiro e o bloqueio
    # era reportado como Path Traversal. Mas '/etc/passwd' ali e o ALVO do `cat` dentro
    # da diretiva, nao a tecnica empregada. Uma diretiva '<!--#exec' e evidencia
    # estrutural muito mais especifica do que a mencao a um nome de arquivo -- que
    # qualquer RCE, LFI ou SSI pode conter.
    #
    # Como a camada 1 existe justamente para dar o MOTIVO do bloqueio, reportar a regra
    # errada anula boa parte do seu valor. A decisao (bloquear) era a mesma; o laudo,
    # nao. O mesmo ajuste foi aplicado em ingestion_csic.FAMILIAS_PAYLOAD, para que a
    # taxonomia das duas camadas concorde.
    Regra('RCE-001', 'Diretiva Server-Side Include', 'Injecao SSI/Comando',
          r"(?i)<!--\s*#\s*(?:exec|include|echo|config|printenv)\b"),
    Regra('RCE-002', 'Metacaractere de shell seguido de comando', 'Injecao SSI/Comando',
          r"(?i)[;|&`]\s*(?:ls|cat|id|whoami|uname|dir|type|rm|wget|curl|nc|netcat"
          r"|bash|sh|cmd|powershell|ping)\b"),
    Regra('RCE-003', 'Substituicao de comando', 'Injecao SSI/Comando',
          r"(?:\$\([^)]{1,60}\)|\$\{[^}]{1,60}\})"),

    # --- Path Traversal / Local File Inclusion -----------------------------
    Regra('LFI-001', 'Travessia de diretorio', 'Path Traversal',
          r"(?:\.\./|\.\.\\|%2e%2e|\.\.%2f|%252e%252e)"),
    Regra('LFI-002', 'Acesso a arquivo sensivel do sistema', 'Path Traversal',
          r"(?i)(?:/etc/(?:passwd|shadow|hosts|group)\b|\bboot\.ini\b|\bwin\.ini\b"
          r"|/proc/self/environ|\bweb\.config\b|\bhtaccess\b)"),
    Regra('LFI-003', 'Wrapper de protocolo', 'Path Traversal',
          r"(?i)\b(?:php|file|expect|zip|glob|data)://"),

    # --- Ataques de protocolo ----------------------------------------------
    Regra('PROTO-001', 'Injecao de CRLF', 'CRLF Injection',
          r"(?:%0d%0a|%0a%0d|\r\n|\n\r)"),
    Regra('PROTO-002', 'Byte nulo', 'Caractere de Controle/Nulo',
          r"(?:%00|\x00)"),
    Regra('PROTO-003', 'Caractere de controle em valor de parametro',
          'Caractere de Controle/Nulo',
          r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]"),
]

# Compiladas uma vez na importacao. No middleware isso roda por requisicao;
# recompilar 25 regexes a cada chamada seria custo puro.
_COMPILADAS: List[tuple] = [(r, re.compile(r.padrao)) for r in REGRAS]

FAMILIAS_COBERTAS = sorted({r.familia for r in REGRAS})


# =============================================================================
# AVALIACAO
# =============================================================================

def avaliar(payload: str) -> Optional[Regra]:
    """
    Devolve a PRIMEIRA regra que casar com o payload, ou None.

    Primeira em vez de todas, de proposito: a camada 1 e uma decisao binaria de
    bloqueio, e o operador precisa de um motivo unico e citavel no log. Quem
    quiser o conjunto completo usa avaliar_todas().

    O payload esperado e o texto JA decodificado -- o mesmo que vai para o
    modelo. Manter as duas camadas sobre a mesma entrada elimina uma variavel
    da comparacao: qualquer diferenca de resultado e diferenca de detector, nao
    de pre-processamento.
    """
    if not payload:
        return None
    for regra, compilada in _COMPILADAS:
        if compilada.search(payload):
            return regra
    return None


def avaliar_todas(payload: str) -> List[Regra]:
    """Todas as regras que casam. Util para depurar e para o laudo de bloqueio."""
    if not payload:
        return []
    return [regra for regra, compilada in _COMPILADAS if compilada.search(payload)]


def avaliar_serie(textos: pd.Series) -> pd.DataFrame:
    """
    Versao vetorizada, para avaliar o dataset inteiro de uma vez.

    Aplicar avaliar() linha a linha sobre 32.808 requisicoes com 25 regexes
    seria lento; str.contains delega o laco ao nivel do pandas. A semantica e a
    mesma da avaliar(): vence a primeira regra na ordem de REGRAS.

    Devolve um DataFrame alinhado ao indice de entrada, com:
        disparou (bool) | regra_id | regra_nome | regra_familia
    """
    textos = textos.astype(str).fillna('')
    resultado = pd.DataFrame({
        'disparou': False,
        'regra_id': '',
        'regra_nome': '',
        'regra_familia': '',
    }, index=textos.index)

    pendentes = pd.Series(True, index=textos.index)
    for regra, _ in _COMPILADAS:
        if not pendentes.any():
            break
        casou = pendentes & textos.str.contains(regra.padrao, regex=True, na=False)
        resultado.loc[casou, 'disparou'] = True
        resultado.loc[casou, 'regra_id'] = regra.id
        resultado.loc[casou, 'regra_nome'] = regra.nome
        resultado.loc[casou, 'regra_familia'] = regra.familia
        pendentes &= ~casou

    return resultado


# =============================================================================
def main() -> None:
    """Inspecao rapida do conjunto de regras. `python assinaturas.py`"""
    print(__doc__)
    print(f"{'=' * 78}\n{len(REGRAS)} REGRAS EM {len(FAMILIAS_COBERTAS)} FAMILIAS\n{'=' * 78}")
    print(f"{'ID':<12}{'Familia':<30}{'Nome'}")
    print('-' * 78)
    for r in REGRAS:
        print(f"{r.id:<12}{r.familia:<30}{r.nome}")

    exemplos = [
        ("' or 1=1--", 'SQLi classico'),
        ("1','0','0','0');waitfor delay '0:0:15';--", 'SQLi time-based (template do CSIC)'),
        ('<SCRipt>alert(1)</scrIPT>', 'XSS com caixa alternada'),
        ('" style="background:url(javascript:alert(1))', 'XSS de atributo, sem a tag script'),
        ('<!--#EXEC cmd="ls /"-->', 'SSI (template do CSIC)'),
        ('../../etc/passwd', 'path traversal'),
        ('3 Vino Rioja 100 55 Anadir al carrito', 'LEGITIMO (CSIC)'),
        ('tenis de corrida masculino', 'LEGITIMO (portugues)'),
        ('aprenda SELECT e JOIN em SQL', 'LIMITE: texto didatico sobre SQL'),
        ('2/ Jamon Iberico 85 49 Anadir al carrito', 'tampering: ataque SEM assinatura'),
    ]
    print(f"\n{'=' * 78}\nCOMPORTAMENTO EM PAYLOADS CONHECIDOS\n{'=' * 78}")
    for payload, descricao in exemplos:
        regra = avaliar(payload.lower())
        veredito = f"BLOQUEIA [{regra.id}] {regra.nome}" if regra else 'libera (segue para a camada 2)'
        print(f"  {payload[:46]:<48} {veredito}")
        print(f"  {'':<48} {descricao}")


if __name__ == '__main__':
    main()
