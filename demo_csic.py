"""
DEMONSTRAÇÃO COM O MODELO AVALIADO — ponto 4 do Paulo (docs/artigo/paulo.md):
"Você também deverá demonstrar o funcionamento do modelo efetivamente avaliado no trabalho."

Autoria: escrito pelo Claude (assistente de IA) em 25/11/2026, a pedido do Pedro.
Script de apoio à demonstração: não treina, não decide, não altera models/.

O QUE FAZ: reenvia requisições REAIS do CSIC 2010 ao servidor rodando com o modelo do
artigo (`python servidor.py`, SEM a variável WAF_MODELO) e mostra o que cada camada
decidiu. As requisições vão para o path original da loja (/tienda1/...). O servidor não
tem essas rotas, então:
    403 -> o WAF bloqueou (camada 1 ou 2, diz a resposta)
    404 -> o WAF deixou passar e a requisição chegou à aplicação (que não tem a página)

Amostra (semente fixa, só GET, porque o middleware inspeciona só a query string):
    legítimas · SQLi · XSS · tampering (onde está o ganho do ML e também os erros)

ATENÇÃO — LEIA ANTES DE APRESENTAR:
    O modelo de models/ foi treinado com TODAS as 32.808 requisições (treinar_final).
    Então estas requisições já foram vistas no treino: a demonstração mostra o
    MECANISMO (o caminho da requisição e qual camada decide), não o DESEMPENHO.
    O desempenho é o das probabilidades out-of-fold (avaliacao_hibrida.md), onde
    nenhuma requisição é julgada por um modelo que a viu.

Uso (dois terminais):
    venv\\Scripts\\python.exe servidor.py              (modelo do CSIC)
    venv\\Scripts\\python.exe demo_csic.py             (6 por categoria)
    venv\\Scripts\\python.exe demo_csic.py 20          (20 por categoria)

Saída: no console (as requisições são tráfego do CSIC, que não vai para o Git) e um
resumo só com contagens em docs/medicoes/demo_csic.md.
"""
import sys
from pathlib import Path
from urllib.parse import parse_qsl

import pandas as pd
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / 'datasets' / 'CSIC2010' / 'csic2010_processado.csv.gz'
SAIDA = RAIZ / 'docs' / 'medicoes' / 'demo_csic.md'
BASE = 'http://127.0.0.1:8000'
SEMENTE = 42

CATEGORIAS = {
    'Legítima': lambda d: d['Label'] == 0,
    'SQLi': lambda d: (d['Label'] == 1) & (d['familia_ataque'] == 'SQLi'),
    'XSS': lambda d: (d['Label'] == 1) & (d['familia_ataque'] == 'XSS'),
    'Tampering': lambda d: (d['Label'] == 1) & (d['familia_ataque'] == 'Tampering sem assinatura'),
}


def conferir_servidor() -> None:
    try:
        info = requests.get(f'{BASE}/api/waf/info', timeout=5).json()
    except requests.RequestException:
        sys.exit('Servidor fora do ar. Suba antes: venv\\Scripts\\python.exe servidor.py')
    if info.get('modelo') != 'models':
        sys.exit(f"O servidor está com o modelo '{info.get('modelo')}'. Para esta demonstração "
                 "ele precisa estar com o modelo do artigo: suba SEM a variável WAF_MODELO.")
    print(f"Servidor no ar com o modelo do artigo (models/), limiar {info.get('limiar_decisao')}.\n")


def enviar(linha) -> dict:
    parametros = parse_qsl(linha['query_decodificada'], keep_blank_values=True)
    r = requests.get(BASE + linha['path'], params=parametros, timeout=10)
    corpo = r.json() if r.headers.get('content-type', '').startswith('application/json') else {}
    if r.status_code == 403:
        camada = corpo.get('camada', '?')
        detalhe = (corpo.get('regra_id', '') + ' ' + corpo.get('regra_familia', '')
                   if camada == 'assinatura' else f"p={corpo.get('probabilidade_ataque', 0):.3f}")
        return {'veredito': 'BLOQUEADO', 'camada': camada, 'detalhe': detalhe.strip()}
    return {'veredito': 'PASSOU', 'camada': '—', 'detalhe': f'HTTP {r.status_code}'}


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    conferir_servidor()
    df = pd.read_csv(DADOS, keep_default_na=False)
    df = df[(df['metodo'] == 'GET') & (df['query_decodificada'] != '')]

    resumo = []
    for categoria, filtro in CATEGORIAS.items():
        amostra = df[filtro(df)].sample(n=n, random_state=SEMENTE)
        print(f"{'=' * 100}\n{categoria}  ({n} requisições reais do CSIC)\n{'=' * 100}")
        bloqueadas = {'assinatura': 0, 'modelo': 0}
        for _, linha in amostra.iterrows():
            res = enviar(linha)
            if res['veredito'] == 'BLOQUEADO':
                bloqueadas[res['camada']] = bloqueadas.get(res['camada'], 0) + 1
            certo = (res['veredito'] == 'PASSOU') == (categoria == 'Legítima')
            print(f"  {'ok ' if certo else 'ERRO'} {res['veredito']:9} {res['camada']:10} "
                  f"{res['detalhe']:22} {linha['path']}  {linha['Sentence'][:60]!r}")
        resumo.append((categoria, n, bloqueadas['assinatura'], bloqueadas['modelo'],
                       n - bloqueadas['assinatura'] - bloqueadas['modelo']))
        print()

    texto = [
        '# Demonstração com o modelo avaliado (ponto 4 do Paulo)',
        '',
        f'Gerado por `demo_csic.py` contra `python servidor.py` (modelo de `models/`). '
        f'{n} requisições GET reais do CSIC por categoria, semente {SEMENTE}.',
        '',
        '| Categoria | Enviadas | Bloqueadas pela assinatura | Bloqueadas pelo modelo | Passaram |',
        '| :--- | ---: | ---: | ---: | ---: |',
    ]
    texto += [f'| {c} | {t} | {a} | {m} | {p} |' for c, t, a, m, p in resumo]
    texto += [
        '',
        '**Não é medida de desempenho.** O modelo de `models/` foi treinado com todas as '
        '32.808 requisições, inclusive estas. A demonstração mostra o mecanismo; o desempenho '
        'é o das probabilidades out-of-fold (`avaliacao_hibrida.md`).',
    ]
    SAIDA.write_text('\n'.join(texto) + '\n', encoding='utf-8')
    print('\n'.join(texto))


if __name__ == '__main__':
    main()
