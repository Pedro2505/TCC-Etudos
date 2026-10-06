"""
==============================================================================
VALIDACAO DA ATRIBUICAO HEURISTICA DE FAMILIA DE ATAQUE
==============================================================================
Por que eu escrevi este script:

O recall por familia se tornou o resultado principal do meu trabalho (SQLi 99,1%,
XSS 100,0%). Mas o CSIC 2010 rotula apenas normal/anomalo, sem tipo de ataque --
a atribuicao de familia e minha, por heuristica de regex em
classificar_familia_ataque(). Se essa heuristica estiver errada, o meu resultado
principal desmorona.

Entao eu validei manualmente. Este script extrai a MESMA amostra que eu inspecionei
(semente fixa), para que qualquer pessoa da banca possa reproduzir a extracao e
conferir os meus vereditos, registrados em docs/validacao_familias.md.

Rodar:  python validar_familias.py
        python validar_familias.py --n 40         (amostra maior)
        python validar_familias.py --templates    (so a analise de templates)

RESULTADO DA MINHA VALIDACAO: 40/40 corretas (20 SQLi + 20 XSS).

O QUE A VALIDACAO REVELOU DE INESPERADO
Os 468 payloads de SQLi derivam de apenas 8 templates distintos, e os 472 de XSS
de apenas 4. Ou seja, o recall de 99,6% mede a deteccao de ~12 templates injetados
em 7 combinacoes de parametros ao longo de 8 rotas -- nao de 940 ataques
estruturalmente diferentes. Essa e uma limitacao do dataset que eu preciso declarar,
e ela torna o experimento de leave-one-template-out viavel e necessario.
==============================================================================
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).resolve().parent
CSIC = RAIZ / 'datasets' / 'CSIC2010' / 'csic2010_processado.csv.gz'
SEMENTE_AMOSTRA = 7   # a mesma que eu usei na validacao manual documentada

# Regex de identificacao de TEMPLATE (nao de familia). Servem para medir quantos
# payloads estruturalmente distintos existem por tras da contagem de amostras.
TEMPLATES = {
    'SQLi': re.compile(
        r"(?i)('\s*;?\s*drop\s+table\s+\w+.*?like\s*'%"
        r"|'\s*delete\s+from\s+\w+"
        r"|[',)0]*\)?;?\s*waitfor\s+delay\s*'[^']*'\s*;?--)"),
    'XSS': re.compile(
        r'(?i)(<\s*script.*?</\s*script\s*>'
        r'|bob@<scr[^>]*>alert\([^)]*\)</scr[^>]*>[^&]*'
        r"|paros%22%20style=%22background:url\(javascript:alert\([^)]*\)\))"),
}


def carregar() -> pd.DataFrame:
    if not CSIC.exists():
        raise FileNotFoundError(
            f"{CSIC} nao encontrado. Rode `python ingestao_csic.py` primeiro.")
    return pd.read_csv(CSIC, keep_default_na=False)


def texto_alvo(linha) -> str:
    """O que o classificador de familia le: query + corpo, ja decodificados."""
    return f"{linha['query_decodificada']} {linha['corpo_decodificado']}".strip()


def amostrar(df: pd.DataFrame, familia: str, n: int) -> pd.DataFrame:
    sub = df[(df['Label'] == 1) & (df['familia_ataque'] == familia)]
    return sub.sample(min(n, len(sub)), random_state=SEMENTE_AMOSTRA)


def listar_amostra(df: pd.DataFrame, familia: str, n: int) -> None:
    """
    Imprime a amostra COMPLETA, sem truncar.

    Truncar foi um erro que eu cometi na primeira tentativa: cortei em 190
    caracteres e sete amostras nao mostravam o ataque, porque o payload estava
    injetado no ULTIMO parametro da requisicao. Julgar por texto truncado teria me
    levado a marcar amostras corretas como erradas.
    """
    amostra = amostrar(df, familia, n)
    total = int(((df['Label'] == 1) & (df['familia_ataque'] == familia)).sum())
    print(f"\n{'=' * 100}")
    print(f"{familia}: {len(amostra)} amostras de {total} (random_state={SEMENTE_AMOSTRA})")
    print('=' * 100)

    rx = TEMPLATES.get(familia)
    for i, (_, r) in enumerate(amostra.iterrows(), start=1):
        alvo = texto_alvo(r)
        print(f"\n#{i:2} [{r['metodo']}] {r['path']}  (len={len(alvo)})")
        print(f"    {alvo}")
        if rx:
            m = rx.search(alvo)
            print(f"    -> template: {m.group(0).strip()[:100]!r}" if m
                  else "    -> TEMPLATE NAO IDENTIFICADO (inspecionar manualmente)")


def analisar_templates(df: pd.DataFrame) -> None:
    """
    Conta quantos payloads estruturalmente distintos existem por familia.

    Esta e a analise que mais me surpreendeu. A contagem de amostras (468 SQLi,
    472 XSS) sugere diversidade que nao existe: sao poucos templates repetidos em
    campos diferentes.
    """
    print(f"\n{'=' * 100}")
    print("DIVERSIDADE DE TEMPLATES DE ATAQUE")
    print('=' * 100)
    print("A contagem de amostras nao equivale a diversidade de ataques: o CSIC injeta")
    print("um punhado de payloads em muitos campos diferentes.\n")

    for familia, rx in TEMPLATES.items():
        sub = df[(df['Label'] == 1) & (df['familia_ataque'] == familia)]
        contagem, sem_template = {}, 0
        for _, r in sub.iterrows():
            m = rx.search(texto_alvo(r))
            if m:
                chave = re.sub(r'\s+', ' ', m.group(0).strip().lower())[:88]
                contagem[chave] = contagem.get(chave, 0) + 1
            else:
                sem_template += 1

        print(f"{familia}: {len(sub)} amostras -> {len(contagem)} templates distintos"
              f" ({sem_template} nao identificados)")
        for chave, n in sorted(contagem.items(), key=lambda x: -x[1]):
            print(f"    {n:5}x  {chave}")
        print(f"    injetados em {sub['nomes_parametros'].nunique()} combinacoes de "
              f"parametros, ao longo de {sub['path'].nunique()} rotas\n")

    print("CONSEQUENCIA QUE EU DECLARO: o recall de 99,6% em SQLi+XSS mede a deteccao")
    print("de ~12 templates, nao de 940 ataques estruturalmente distintos. Com tao")
    print("poucos templates, o experimento de leave-one-template-out (treinar sem um")
    print("template e testar so nele) e viavel e passa a ser indispensavel para eu")
    print("afirmar qualquer coisa sobre generalizacao.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--n', type=int, default=20, help='amostras por familia (padrao: 20)')
    ap.add_argument('--templates', action='store_true', help='apenas a analise de templates')
    args = ap.parse_args()

    print(__doc__)
    df = carregar()

    if not args.templates:
        for familia in ['SQLi', 'XSS']:
            listar_amostra(df, familia, args.n)

    analisar_templates(df)
    print(f"\nMeus vereditos manuais estao em docs/validacao_familias.md")


if __name__ == '__main__':
    main()
