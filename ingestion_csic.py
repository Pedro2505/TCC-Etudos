"""
==============================================================================
PIPELINE DE INGESTAO — HTTP DATASET CSIC 2010
==============================================================================
Por que este modulo substitui o ingestion.py como fonte principal:

Os datasets de SQLi/XSS usados nas Sprints 1-4 tem a classe benigna composta por
CONSULTAS SQL LEGITIMAS (ex: "SELECT COUNT(thumb) FROM elephant"). O WAF, porem,
opera na camada HTTP, onde trafego benigno e "tenis de corrida masculino" ou
"pedro@gmail.com". Essa incompatibilidade de dominio faz a taxa de falso positivo
medida (0,23%) nao descrever a tarefa real: em trafego HTTP realista ela e de
23,1% (ver docs/medicoes/false_positive_test.md).

O CSIC 2010 resolve isso: sao requisicoes HTTP REAIS a uma aplicacao de
e-commerce (a loja "tienda1"), com metodo, path, parametros, headers e corpo.

--- ARQUIVOS ESPERADOS em datasets/CSIC2010/ -------------------------------
    normalTrafficTraining.txt   36.000 requisicoes normais (treino)
    normalTrafficTest.txt       36.000 requisicoes normais (teste)
    anomalousTrafficTest.txt    25.065 requisicoes anomalas (teste)

Fonte original: http://www.isi.csic.es/dataset/  (historicamente instavel)
Mirrors: repositorio msudol/Web-Application-Attack-Datasets no GitHub; Kaggle
("CSIC 2010 Web Application Attacks"). As contagens acima servem como checksum:
se o parser nao encontrar exatamente esses numeros, o arquivo esta truncado.

--- FORMATO BRUTO ---------------------------------------------------------
    GET http://localhost:8080/tienda1/publico/anadir.jsp?id=2&nombre=Jam%F3n HTTP/1.1
    User-Agent: Mozilla/5.0 ...
    Host: localhost:8080
    Content-Length: 146          <- apenas em POST/PUT
                                 <- linha vazia separa headers do corpo
    id=2&nombre=Jam%F3n&precio=85 ...

Requisicoes se separam pela LINHA DE REQUISICAO (metodo + URL + versao), nao por
linha vazia — GET e POST usam linhas vazias internamente, o que quebraria um
split ingenuo por "\n\n".

ATENCAO AO ENCODING: o percent-encoding do CSIC e ISO-8859-1, nao UTF-8.
"Jam%F3n" e "Jamón" em latin-1; decodificar como UTF-8 gera erro ou mojibake.
Os arquivos em si sao ASCII puro (todo byte alto vem percent-encoded).

--- LIMITACOES A DECLARAR NA MONOGRAFIA -----------------------------------
1. Trafego gerado automaticamente, nao capturado de producao.
2. Uma unica aplicacao-alvo (tienda1), tecnologias de 2010.
3. O conjunto anomalo mistura tres categorias (ataques estaticos, ataques
   dinamicos e "requisicoes ilegais nao intencionais"), sem rotulo de tipo.
   A funcao classificar_familia_ataque() supre isso por heuristica.
4. Cada ataque tende a aparecer em variante GET e POST -> deduplicar antes de
   qualquer split, ou havera vazamento treino/teste.
==============================================================================
"""

import re
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple
from urllib.parse import parse_qsl, unquote_plus, urlsplit

import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ_PROJETO = Path(__file__).resolve().parent
PASTA_CSIC = RAIZ_PROJETO / 'datasets' / 'CSIC2010'

ARQUIVOS = {
    'normal_treino': ('normalTrafficTraining.txt', 0, 36000),
    'normal_teste': ('normalTrafficTest.txt', 0, 36000),
    'anomalo_teste': ('anomalousTrafficTest.txt', 1, 25065),
}

# Uma linha de requisicao HTTP: metodo, alvo e versao.
RE_LINHA_REQUISICAO = re.compile(
    r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE|CONNECT)\s+(\S+)\s+(HTTP/\d\.\d)\s*$')

# Heuristicas de familia de ataque, para o experimento leave-one-family-out.
# Aplicadas sobre o payload JA decodificado. A ordem importa: a primeira que
# casar define a familia, entao os padroes mais especificos vem antes.
#
# NOTA: nao usar [^\x20-\x7e] para detectar "formato invalido". O trafego legitimo
# do CSIC e em espanhol e contem acentos (Jamon Iberico, Anadir al carrito), que
# viram bytes altos apos o decode latin-1. Esse padrao classificava trafego normal
# como ataque. Detectar apenas caracteres de CONTROLE e byte nulo.
# CORRECAO (28/07): o template de SQLi mais frequente do CSIC e time-based blind
# ("');waitfor delay '0:0:15';--"), e ele NAO casava com nenhum padrao desta lista:
# 'waitfor delay' nao estava aqui, e o '--\s*$' exige fim de string, enquanto no CSIC
# o comentario vem seguido de outro parametro ("...;-- Pasar por caja"). Resultado:
# 550 injecoes SQL reais eram rotuladas 'Tampering sem assinatura'. Isso contradizia
# o meu proprio roteiro de apresentacao, que descreve o waitfor como "o template mais
# frequente de SQLi no CSIC". Adicionei os padroes de SQLi cego/temporal e soltei a
# ancora do comentario.
FAMILIAS_PAYLOAD: List[Tuple[str, str]] = [
    ('SQLi', r"(?i)(?:\bunion\b.{0,20}\bselect\b|\bdrop\s+table\b|\bselect\b.{0,30}\bfrom\b"
             r"|\binsert\s+into\b|\bdelete\s+from\b|'\s*or\s*'?\d|--\s*$|\bor\s+1\s*=\s*1"
             r"|\bwaitfor\s+delay\b|\bsleep\s*\(|\bbenchmark\s*\(|\bpg_sleep\s*\("
             r"|\bxp_cmdshell\b|['\"]\s*;\s*(?:drop|select|insert|update|delete)\b)"),
    ('XSS', r'(?i)(?:<\s*script|javascript\s*:|onerror\s*=|onload\s*=|<\s*img[^>]*src'
            r'|alert\s*\(|document\.cookie|<\s*iframe|<\s*svg)'),
    # ORDEM CORRIGIDA (28/07): SSI/Comando vem ANTES de Path Traversal.
    #
    # O principio declarado no topo desta lista e "os padroes mais especificos vem
    # antes", e este par o violava. O template de SSI do CSIC e:
    #
    #     <!--#exec cmd="rm -rf /;cat /etc/passwd" -->
    #
    # Com Path Traversal na frente, o '/etc/passwd' casava primeiro e a requisicao era
    # rotulada como travessia de diretorio. Mas '/etc/passwd' aqui e o ALVO do `cat`
    # dentro da diretiva, nao a tecnica: a tecnica e injecao de SSI. Uma diretiva
    # '<!--#exec' e evidencia estrutural muito mais especifica do que a mencao a um
    # nome de arquivo, que qualquer RCE/LFI/SSI pode conter.
    #
    # Impacto medido: as 134 requisicoes da familia 'Path Traversal' eram, todas,
    # injecoes de SSI. Verifiquei que nao ha NENHUMA travessia genuina (sequencia
    # '../' ou '%2e%2e') em valor de parametro no CSIC em escopo -- a familia existia
    # inteiramente por misatribuicao. Apos a correcao: SSI/Comando 250 -> 384 e
    # Path Traversal 134 -> 0.
    #
    # Mantenho o padrao de Path Traversal na lista: ele esta correto para um LFI real
    # do tipo '?file=/etc/passwd', que este dataset simplesmente nao contem. Uma
    # familia com zero membros e informacao, nao codigo morto.
    ('Injecao SSI/Comando', r'(?i)(?:<!--#\s*exec|\|\s*(?:ls|cat|id|whoami)\b|;\s*(?:ls|cat|id)\b|`)'),
    ('Path Traversal', r'(?:\.\./|\.\.\\|%2e%2e|/etc/passwd|\bboot\.ini\b|\bwin\.ini\b)'),
    ('CRLF Injection', r'(?:%0d%0a|%0a%0d|\r\n)'),
    ('Buffer Overflow', r'(?:A{50,}|\d{60,}|.{1000,})'),
    ('Caractere de Controle/Nulo', r'(?:%00|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f])'),
]

# Familias detectadas no PATH, nao no valor dos parametros. Avaliadas primeiro,
# porque um GET para /tienda1/asf-logo-wide.gif~ nao tem parametro nenhum.
FAMILIAS_PATH: List[Tuple[str, str]] = [
    ('Arquivo Sensivel (path)', r'(?i)(?:\.(?:bak|old|inc|log|ini|conf|passwd|htaccess|DS_Store)$'
                                r'|~$|/WEB-INF|/META-INF|\.jsp\.)'),
    ('Path Traversal', r'(?:\.\./|\.\.\\|%2e%2e)'),
    ('Recurso Inexistente/Enumeracao (path)', r'(?:/\d{8,}|\.gif/$|\.jsp/$)'),
]


# ==============================================================================
# PARSING
# ==============================================================================

def _fatiar_blocos(linhas: Iterator[str]) -> Iterator[List[str]]:
    """
    Agrupa as linhas do arquivo em blocos, um por requisicao.

    Streaming (generator) de proposito: os tres arquivos somam ~56 MB de texto e
    nao ha razao para materializar tudo na RAM antes de transformar.
    """
    bloco: List[str] = []
    for linha in linhas:
        linha = linha.rstrip('\r\n')
        if RE_LINHA_REQUISICAO.match(linha):
            if bloco:
                yield bloco
            bloco = [linha]
        elif bloco:
            bloco.append(linha)
        # Linhas antes da primeira requisicao (lixo de cabecalho) sao descartadas.
    if bloco:
        yield bloco


def _parsear_bloco(bloco: List[str]) -> Optional[Dict]:
    """Converte um bloco de linhas em um dicionario estruturado da requisicao."""
    m = RE_LINHA_REQUISICAO.match(bloco[0])
    if not m:
        return None
    metodo, alvo, versao = m.groups()

    # Headers vao até a primeira linha vazia; o restante é corpo.
    headers: Dict[str, str] = {}
    i = 1
    while i < len(bloco) and bloco[i].strip():
        if ':' in bloco[i]:
            chave, _, valor = bloco[i].partition(':')
            headers[chave.strip().lower()] = valor.strip()
        i += 1
    corpo = '\n'.join(bloco[i + 1:]).strip() if i + 1 <= len(bloco) else ''

    partes = urlsplit(alvo)
    return {
        'metodo': metodo,
        'versao': versao,
        'path': partes.path,
        'query': partes.query,
        'corpo': corpo,
        'headers': headers,
    }


def _decodificar(texto: str) -> str:
    """
    Decodifica percent-encoding usando ISO-8859-1, o encoding do CSIC 2010.
    unquote_plus tambem converte '+' em espaco, correto para query strings e
    para corpos application/x-www-form-urlencoded.
    """
    if not texto:
        return ''
    return unquote_plus(texto, encoding='latin-1', errors='replace')


def _extrair_parametros(req: Dict) -> List[Tuple[str, str]]:
    """
    Devolve os pares (nome, valor) da query string e do corpo urlencoded.

    keep_blank_values=True de proposito: parametro presente mas vazio e um sinal
    relevante (varias anomalias do CSIC sao justamente campos esvaziados).
    """
    pares = parse_qsl(req['query'], keep_blank_values=True, encoding='latin-1')
    tipo = req['headers'].get('content-type', '')
    if req['corpo'] and 'urlencoded' in tipo:
        pares += parse_qsl(req['corpo'], keep_blank_values=True, encoding='latin-1')
    elif req['corpo']:
        pares += [('__corpo__', req['corpo'])]
    return pares


def parsear_arquivo(caminho: Path, label: int) -> pd.DataFrame:
    """
    Le um arquivo bruto do CSIC e devolve um DataFrame estruturado.

    A coluna 'Sentence' concentra o que o middleware de fato inspeciona: os
    VALORES dos parametros, decodificados e concatenados. Isso mantem
    compatibilidade com extrair_features_manuais() e com o pipeline existente.
    As colunas estruturais (metodo, path, n_parametros...) ficam disponiveis
    para as features de contexto HTTP que o modelo atual ainda nao usa.
    """
    registros = []
    with open(caminho, 'r', encoding='utf-8', errors='replace') as f:
        for bloco in _fatiar_blocos(f):
            req = _parsear_bloco(bloco)
            if req is None:
                continue
            pares = _extrair_parametros(req)
            valores = [_decodificar(v) for _, v in pares]

            registros.append({
                'Sentence': ' '.join(valores),
                'Label': label,
                'metodo': req['metodo'],
                'path': req['path'],
                'query_decodificada': _decodificar(req['query']),
                'corpo_decodificado': _decodificar(req['corpo']),
                'nomes_parametros': '|'.join(n for n, _ in pares),
                'n_parametros': len(pares),
                'tem_corpo': int(bool(req['corpo'])),
                'content_length': int(req['headers'].get('content-length') or 0),
                'n_headers': len(req['headers']),
                'origem': caminho.name,
            })
    return pd.DataFrame(registros)


# ==============================================================================
# CLASSIFICACAO HEURISTICA DE FAMILIA (para leave-one-family-out)
# ==============================================================================

def classificar_familia_ataque(df: pd.DataFrame) -> pd.Series:
    """
    Atribui uma familia de ataque por heuristica de regex.

    O CSIC 2010 nao rotula o TIPO de ataque, apenas normal/anomalo. Sem tipo nao
    da para fazer o experimento leave-one-family-out, que e o unico que sustenta
    a alegacao de deteccao de ataque nao visto.

    Avalia o PATH antes do payload: 22,3% das anomalias do CSIC nao tem parametro
    algum, o ataque esta no recurso requisitado.

    A categoria final, 'Tampering sem assinatura', corresponde a terceira classe
    do CSIC ("unintentional illegal requests"): requisicoes que violam o
    comportamento esperado da aplicacao sem conter nenhuma assinatura de ataque
    (ex: senha com caracteres improvaveis, campo obrigatorio ausente). E a
    categoria mais relevante para a tese: por definicao, nenhum WAF de assinatura
    a detecta.

    ATENCAO: e uma aproximacao, nao ground-truth. Declarar como tal na
    monografia e validar manualmente uma amostra por familia.

    --- CORRECAO DE 28/07: SOBRE QUAL TEXTO A FAMILIA E ATRIBUIDA ---------
    Esta funcao casava os padroes contra `query_decodificada + corpo_decodificado`,
    que passam por UMA decodificacao (`_decodificar` sobre a query crua). Mas a
    coluna `Sentence` -- a unica que o modelo e o middleware de fato inspecionam --
    passa por DUAS: `parse_qsl` ja decodifica cada valor, e `_decodificar` decodifica
    de novo.

    Consequencia: em payloads duplamente codificados no arquivo bruto, a atribuicao
    de familia lia `%3CSCRIPT%3E` enquanto o modelo lia `<SCRIPT>`. As regexes nao
    casavam e o ataque caia em 'Tampering sem assinatura'. Medi 868 requisicoes
    nessa situacao: 480 XSS e 388 CRLF Injection rotuladas como tampering.

    Isso inflava a estatistica central do trabalho: 'SQLi e XSS sao 6,6% das
    anomalias' e '89,9% e tampering'. Os dois numeros estavam errados.

    Correcao: casar sobre `Sentence`, que e por definicao a superficie inspecionada.
    A familia passa a descrever o que o detector realmente ve, e nao um estagio
    intermediario do parser.
    """
    payload = df['Sentence'].fillna('').astype(str)
    path = df['path'].fillna('')

    familia = pd.Series('Tampering sem assinatura', index=df.index, dtype=object)
    familia[df['Label'] == 0] = 'Normal'
    pendentes = df['Label'] == 1

    for nome, padrao in FAMILIAS_PATH:
        if not pendentes.any():
            break
        casou = pendentes & path.str.contains(padrao, regex=True, na=False)
        familia[casou] = nome
        pendentes &= ~casou

    for nome, padrao in FAMILIAS_PAYLOAD:
        if not pendentes.any():
            break
        casou = pendentes & payload.str.contains(padrao, regex=True, na=False)
        familia[casou] = nome
        pendentes &= ~casou

    return familia


# ==============================================================================
# CARREGADORES
# ==============================================================================

def _verificar_arquivos() -> None:
    faltando = [nome for nome, _, _ in ARQUIVOS.values()
                if not (PASTA_CSIC / nome).exists()]
    if faltando:
        raise FileNotFoundError(
            f"Arquivos do CSIC 2010 nao encontrados em {PASTA_CSIC}:\n"
            + '\n'.join(f'  - {n}' for n in faltando)
            + "\n\nBaixe de http://www.isi.csic.es/dataset/ ou de um mirror "
              "(GitHub: msudol/Web-Application-Attack-Datasets, ou Kaggle) "
              "e coloque os .txt nessa pasta. Ver o docstring deste modulo."
        )


def carregar_bruto(verificar_contagem: bool = True) -> Dict[str, pd.DataFrame]:
    """Parseia os tres arquivos e devolve um dict de DataFrames, sem juntar."""
    _verificar_arquivos()
    resultado = {}
    for chave, (nome, label, esperado) in ARQUIVOS.items():
        df = parsear_arquivo(PASTA_CSIC / nome, label)
        print(f"[*] {nome}: {len(df)} requisicoes parseadas (esperado: {esperado})")
        if verificar_contagem and len(df) != esperado:
            raise ValueError(
                f"{nome}: parseadas {len(df)} requisicoes, esperadas {esperado}. "
                "Arquivo truncado ou formato divergente — nao prossiga com dados parciais."
            )
        resultado[chave] = df
    return resultado


# Chave de deduplicacao. Inclui 'metodo' DE PROPOSITO: o CSIC replica cada
# requisicao em variante GET (parametros na query) e POST (mesmos parametros no
# corpo). Sem 'metodo' na chave, todos os 25.580 POSTs sao descartados como
# duplicata dos GETs, e o dataset perde a diversidade de metodo — que e
# justamente um dos sinais de contexto HTTP que o modelo deveria aprender.
CHAVE_DEDUP = ['Sentence', 'path', 'metodo', 'Label']

RE_DIGITOS = re.compile(r'\d+')
RE_ESPACOS = re.compile(r'\s+')

# --- PRESERVACAO DO BYTE NULO NO ARTEFATO SERIALIZADO -----------------------
# Bug medido em 28/07: o CSV nao sobrevive a um \x00. O pandas escreve o byte, e
# na releitura a string e TRUNCADA nele:
#
#     'registro ... @b-sign.cg \x00 <resto do payload>'   (em memoria)
#     'registro ... @b-sign.cg '                          (depois do round-trip)
#
# As 114 anomalias da familia 'Caractere de Controle/Nulo' sao exatamente ataques
# de byte nulo, entao o artefato versionado entregava ao treino um payload com a
# evidencia do ataque amputada. E o mesmo tipo de desalinhamento treino/inferencia
# que eu ja havia documentado para `qtd_url_encode`: o middleware, em producao,
# recebe o \x00 de verdade apos o URL-decode.
#
# Solucao sem dependencia nova (nao ha engine de parquet no ambiente): trocar o
# \x00 por um ponto de codigo da Area de Uso Privado do Unicode na escrita e
# desfazer na leitura. U+E000 e seguro por construcao -- o parser decodifica em
# latin-1, que so produz U+0000 a U+00FF, entao esse caractere nao pode ocorrer
# em trafego real do dataset.
MARCADOR_NULO = '\ue000'
COLUNAS_TEXTO = ['Sentence', 'query_decodificada', 'corpo_decodificado', 'grupo_payload']


def proteger_nulo(df: pd.DataFrame) -> pd.DataFrame:
    """Aplicar ANTES de serializar em CSV."""
    df = df.copy()
    for col in COLUNAS_TEXTO:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('\x00', MARCADOR_NULO, regex=False)
    return df


def restaurar_nulo(df: pd.DataFrame) -> pd.DataFrame:
    """Aplicar DEPOIS de ler o CSV, para devolver o payload fiel ao original."""
    for col in COLUNAS_TEXTO:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(MARCADOR_NULO, '\x00', regex=False)
    return df


def normalizar_payload(texto: str) -> str:
    """
    Forma canonica de um payload: minusculas, digitos -> 'N', espacos colapsados.

    CUIDADO: NAO use isto como chave de agrupamento no CSIC 2010.

    Eu comecei usando esta normalizacao para agrupar variantes quase-identicas, na
    suposicao de que "id=2&precio=85" e "id=7&precio=99" fossem a mesma requisicao
    com valores diferentes. No CSIC isso e falso e destrutivo:

        '3 Vino Rioja 100 55 Anadir al carrito'  -> NORMAL
        '1 Vino Rioja 85 63 Anadir al carrito'   -> ATAQUE

    Boa parte das anomalias do CSIC e *parameter tampering*: a requisicao e
    estruturalmente identica a uma legitima e a anomalia esta no VALOR estar fora do
    dominio valido (um preco que nao corresponde ao produto, uma quantidade fora de
    faixa). Normalizar digitos apaga justamente o sinal que separa as classes, e
    ainda cria grupos gigantes (medi um com 2.385 requisicoes misturando as duas
    classes), o que arruina o balanceamento dos folds.

    Mantenho a funcao porque ela e util para MEDIR quantos ataques sao
    estruturalmente indistinguiveis de trafego normal (medi 12,8%), o que e um
    resultado relevante: essa fracao e, por construcao, invisivel para qualquer
    classificador que leia apenas o texto do payload.
    """
    if not isinstance(texto, str):
        return ''
    return RE_ESPACOS.sub(' ', RE_DIGITOS.sub('N', texto.lower())).strip()


def carregar_supervisionado(deduplicar: bool = True,
                            somente_com_payload: bool = True) -> pd.DataFrame:
    """
    Monta o dataset para o classificador supervisionado (Random Forest).

    deduplicar: remove requisicoes identicas em (Sentence, path, metodo, Label).
        Necessario porque variantes repetidas cairiam nos dois lados do split,
        inflando as metricas.

    somente_com_payload: mantem apenas requisicoes que tem ao menos um valor de
        parametro para inspecionar.

        ISSO E UMA DECISAO DE ESCOPO, NAO UMA LIMPEZA. 40.000 das 72.000
        requisicoes normais e 5.585 das 25.065 anomalas (22,3%) NAO TEM
        PARAMETRO NENHUM — sao GETs a recursos, tipo
        /tienda1/asf-logo-wide.gif~ ou /tienda1/6909030637832563290.jsp.

        Consequencia arquitetural: o middleware atual (api.py) inspeciona apenas
        os VALORES dos query params, portanto e estruturalmente incapaz de
        detectar 22,3% dos ataques deste dataset, por mais bem treinado que o
        modelo esteja. Detectar esses casos exige features do PATH, o que e uma
        extensao do middleware, nao um ajuste do modelo.

        Com somente_com_payload=True, o dataset descreve honestamente o escopo do
        detector atual. Com False, inclui os casos fora de escopo — util para
        quantificar o teto de deteccao da arquitetura atual.
    """
    partes = carregar_bruto()
    df = pd.concat(partes.values(), ignore_index=True)
    df['familia_ataque'] = classificar_familia_ataque(df)
    df['tem_payload'] = (df['Sentence'].str.strip() != '').astype(int)

    total = len(df)
    print(f"\n[*] Requisicoes brutas: {total}")
    print(f"[*] Sem payload inspecionavel (ataque no path ou GET simples): "
          f"{(df['tem_payload'] == 0).sum()} "
          f"({(df['tem_payload'] == 0).mean():.1%}) — dessas, "
          f"{((df['tem_payload'] == 0) & (df['Label'] == 1)).sum()} sao ataques")

    if somente_com_payload:
        df = df[df['tem_payload'] == 1]
        print(f"[*] Escopo restrito a requisicoes com payload: {len(df)} restantes")

    if deduplicar:
        antes = len(df)
        df = df.drop_duplicates(subset=CHAVE_DEDUP, keep='first')
        print(f"[*] Deduplicacao por {CHAVE_DEDUP}: {antes - len(df)} removidas "
              f"({(antes - len(df)) / antes:.1%}), {len(df)} restantes")

    # --- CHAVE DE AGRUPAMENTO PARA O SPLIT ---
    # Problema que ela resolve: a variante GET e a variante POST do MESMO payload
    # sobrevivem a deduplicacao (o metodo difere) e, num split aleatorio, caem em
    # lados opostos. Como o modelo le o payload, isso e vazamento.
    #
    # A chave usa o payload LITERAL, sem normalizar digitos -- ver o aviso em
    # normalizar_payload(). Assim as variantes GET/POST do mesmo payload ficam
    # juntas (e o que queremos), mas variantes de tampering que diferem apenas nos
    # valores permanecem em grupos separados, porque sao amostras genuinamente
    # distintas e nao vazamento.
    #
    # Use com StratifiedGroupKFold ou GroupShuffleSplit: groups=df['grupo_payload'].
    df['grupo_payload'] = df['path'].fillna('') + '::' + df['Sentence'].fillna('')

    n_grupos = df['grupo_payload'].nunique()
    tam_max = df['grupo_payload'].value_counts().max()
    mistos = (df.groupby('grupo_payload')['Label'].nunique() > 1).sum()
    print(f"[*] Grupos de payload distintos: {n_grupos} para {len(df)} requisicoes "
          f"({len(df) / n_grupos:.1f} por grupo em media, maior com {tam_max})")
    print(f"[*] Grupos contendo as duas classes: {mistos} "
          f"({mistos / n_grupos:.2%}) — quanto menor, melhor a estratificacao dos folds")
    print("    -> use groups=df['grupo_payload'] em StratifiedGroupKFold; um split "
          "aleatorio comum vaza payload entre treino e teste")

    return df.reset_index(drop=True)


def carregar_para_anomalia() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Devolve (treino_normal, teste_normal, teste_anomalo) na divisao ORIGINAL do
    CSIC, sem embaralhar.

    Esta e a razao de o dataset trazer um arquivo de treino separado e composto
    apenas de trafego normal: ele foi desenhado para deteccao de anomalia
    (IsolationForest / One-Class SVM), onde o modelo aprende so o comportamento
    legitimo e sinaliza desvios. Nao use train_test_split aqui — isso descartaria
    o desenho experimental do dataset.
    """
    partes = carregar_bruto()
    return partes['normal_treino'], partes['normal_teste'], partes['anomalo_teste']


# ==============================================================================
def main() -> None:
    print(__doc__)
    df = carregar_supervisionado()

    print(f"\n{'=' * 78}\nRESUMO DO DATASET CSIC 2010\n{'=' * 78}")
    print(f"Total de requisicoes: {len(df)}")
    print(f"\nDistribuicao de classes:\n{df['Label'].value_counts().to_string()}")
    print(f"\nMetodos HTTP:\n{df['metodo'].value_counts().to_string()}")
    print(f"\nFamilias de ataque (heuristica) — base para o leave-one-family-out:\n"
          f"{df[df['Label'] == 1]['familia_ataque'].value_counts().to_string()}")
    print(f"\nPaths mais frequentes:\n{df['path'].value_counts().head(8).to_string()}")

    print(f"\n--- Exemplos de trafego NORMAL (o que o modelo antigo nunca viu) ---")
    for s in df[df['Label'] == 0]['Sentence'].head(6):
        print(f"  {s[:95]!r}")
    print(f"\n--- Exemplos de trafego ANOMALO ---")
    for _, r in df[df['Label'] == 1].head(6).iterrows():
        print(f"  [{r['familia_ataque']}] {r['Sentence'][:80]!r}")

    # Comprimido: o CSV cru tem ~15 MB, o .gz fica em ~2 MB e o pandas le direto
    # com pd.read_csv(...). Assim o artefato processado cabe no repositorio e o
    # projeto fica reproduzivel sem exigir o download dos 53 MB de .txt brutos.
    destino = PASTA_CSIC / 'csic2010_processado.csv.gz'
    n_nulos = int(df['Sentence'].astype(str).str.contains('\x00', regex=False).sum())
    proteger_nulo(df).to_csv(destino, index=False, encoding='utf-8', compression='gzip')
    print(f"\n[OK] Dataset processado salvo em {destino}")
    print(f"     Colunas: {list(df.columns)}")
    print(f"     Byte nulo protegido como U+E000 em {n_nulos} requisicoes — sem isso o "
          "round-trip pelo CSV TRUNCA o payload no \\x00 e apaga a evidencia do ataque.")
    print("\n     Para carregar:  use model_trainer.carregar_dados_csic(), que ja aplica "
          "restaurar_nulo().")
    print("     Direto pelo pandas:  pd.read_csv(..., keep_default_na=False) seguido de "
          "ingestion_csic.restaurar_nulo(df).")
    print("     keep_default_na=False e necessario: sem isso o pandas converte "
          "payloads vazios e strings como 'null'/'NA' em NaN.")


if __name__ == '__main__':
    main()
