"""
Script de MEDIÇÃO DE APOIO — escrito pelo Claude (assistente de IA) em 12/11/2026,
pela exceção do CLAUDE.md ("script de medição de apoio"). Não é peça do TCC: não
treina, não decide, não altera nada. Só mede.

Pergunta que ele responde (objetivo específico 7, "tempo de resposta"):
    "Quanto tempo o WAF acrescenta a cada requisição, e em que etapa esse tempo é gasto?"

Duas medições:

1. POR ETAPA, dentro do processo (time.perf_counter): normalização do servidor,
   camada 1 (assinaturas), montagem das features, inferência do Random Forest.
   Usa as mesmas funções que o servidor.py chama, com o modelo de `models/` (o do
   artigo) e n_jobs=1, como o servidor carrega.

2. PONTA A PONTA, por HTTP, contra o servidor rodando de verdade
   (`python servidor.py` na porta 8000). Mede o tempo de ida e volta no cliente e
   lê o `latencia_ms` que o próprio middleware devolve. Se o servidor não estiver
   no ar, esta parte é pulada e o relatório diz isso.

Amostra: N payloads reais do CSIC 2010 em escopo, metade legítimos e metade ataques,
sorteados com semente fixa. Cada payload passa uma vez por cada etapa.

Uso:  venv\\Scripts\\python.exe medir_latencia.py            (N = 300)
      venv\\Scripts\\python.exe medir_latencia.py 1000
Saída: docs/medicoes/latencia.md
"""
import platform
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np

import assinaturas
from extrator import carregar_artefatos, preparar_para_inferencia
from ingestao_csic import carregar_supervisionado
from medir_normalizacao import carregar_funcao_do_servidor

RAIZ = Path(__file__).parent
SAIDA = RAIZ / 'docs' / 'medicoes' / 'latencia.md'
URL = 'http://127.0.0.1:8000/api/comentarios'
SEMENTE = 42
AQUECIMENTO = 20


def resumo(ms):
    a = np.asarray(ms, dtype=float)
    return {'n': len(a), 'media': a.mean(), 'p50': np.percentile(a, 50),
            'p95': np.percentile(a, 95), 'p99': np.percentile(a, 99), 'max': a.max()}


def linha(nome, r):
    return (f"| {nome} | {r['n']} | {r['media']:.2f} | {r['p50']:.2f} | "
            f"{r['p95']:.2f} | {r['p99']:.2f} | {r['max']:.2f} |")


def medir_etapas(amostra, contextos):
    decod = carregar_funcao_do_servidor()
    modelo, vetorizador, meta = carregar_artefatos(RAIZ / 'models')
    t = {'normalizacao': [], 'assinaturas': [], 'features': [], 'inferencia': [],
         'total_camada2': []}

    for i, (texto, ctx) in enumerate(zip(amostra, contextos)):
        a0 = time.perf_counter()
        norm = decod(texto)
        a1 = time.perf_counter()
        assinaturas.avaliar(norm)
        a2 = time.perf_counter()
        X = preparar_para_inferencia(norm, vetorizador, meta['colunas'], ctx).to_numpy()
        a3 = time.perf_counter()
        modelo.predict_proba(X)
        a4 = time.perf_counter()
        if i < AQUECIMENTO:
            continue
        t['normalizacao'].append((a1 - a0) * 1000)
        t['assinaturas'].append((a2 - a1) * 1000)
        t['features'].append((a3 - a2) * 1000)
        t['inferencia'].append((a4 - a3) * 1000)
        t['total_camada2'].append((a4 - a0) * 1000)
    return {k: resumo(v) for k, v in t.items()}


def medir_http(amostra):
    try:
        import requests
        requests.get('http://127.0.0.1:8000/api/waf/info', timeout=2).raise_for_status()
    except Exception as e:
        return None, f'servidor fora do ar ({type(e).__name__}) — parte HTTP pulada'

    info = requests.get('http://127.0.0.1:8000/api/waf/info', timeout=2).json()
    ida_volta, interno = {'assinatura': [], 'modelo': []}, {'assinatura': [], 'modelo': []}
    sessao = requests.Session()
    for i, texto in enumerate(amostra):
        t0 = time.perf_counter()
        r = sessao.get(URL, params={'texto': texto}, timeout=10)
        dt = (time.perf_counter() - t0) * 1000
        if i < AQUECIMENTO:
            continue
        corpo = r.json()
        if r.status_code == 403 and corpo.get('camada') == 'assinatura':
            via, lat = 'assinatura', corpo.get('latencia_ms')
        elif r.status_code == 403:
            via, lat = 'modelo', corpo.get('latencia_ms')
        else:
            via, lat = 'modelo', (corpo.get('waf') or {}).get('latencia_ms')
        ida_volta[via].append(dt)
        if lat is not None:
            interno[via].append(lat)
    return {'info': info,
            'ida_volta': {k: resumo(v) for k, v in ida_volta.items() if v},
            'interno': {k: resumo(v) for k, v in interno.items() if v}}, None


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    df = carregar_supervisionado()
    rng = np.random.default_rng(SEMENTE)
    idx = np.concatenate([
        rng.choice(np.flatnonzero(df['Label'] == 0), n // 2, replace=False),
        rng.choice(np.flatnonzero(df['Label'] == 1), n - n // 2, replace=False)])
    rng.shuffle(idx)
    # aquecimento: os primeiros AQUECIMENTO payloads rodam mas não entram na conta
    idx = np.concatenate([idx[:AQUECIMENTO], idx])
    sub = df.iloc[idx]
    amostra = sub['Sentence'].fillna('').astype(str).tolist()
    contextos = sub[['metodo', 'n_parametros', 'tem_corpo', 'content_length',
                     'n_headers']].to_dict('records')

    print(f'[*] Medindo etapas em processo ({n} payloads)...')
    etapas = medir_etapas(amostra, contextos)
    print('[*] Medindo ponta a ponta por HTTP...')
    http, aviso = medir_http(amostra)

    cab = ['| Etapa | n | média | p50 | p95 | p99 | máx |',
           '| :--- | ---: | ---: | ---: | ---: | ---: | ---: |']
    L = ['# Latência do WAF', '',
         'Gerado por `medir_latencia.py` (script de medição de apoio, escrito pelo Claude) '
         f'em {date.today().isoformat()}.',
         f'Máquina: {platform.processor() or platform.machine()} · {platform.system()} '
         f'{platform.release()} · Python {platform.python_version()}.',
         f'Amostra: {n} payloads reais do CSIC 2010 em escopo ({n // 2} legítimos, '
         f'{n - n // 2} ataques), semente {SEMENTE}, {AQUECIMENTO} de aquecimento descartados. '
         'Tempos em **milissegundos**.', '',
         '## 1. Por etapa (dentro do processo, modelo de `models/`, n_jobs=1)', '', *cab,
         linha('Normalização (servidor)', etapas['normalizacao']),
         linha('Camada 1 — assinaturas', etapas['assinaturas']),
         linha('Montagem das features', etapas['features']),
         linha('Inferência (Random Forest)', etapas['inferencia']),
         linha('**Total até a decisão da camada 2**', etapas['total_camada2']), '',
         'O total supõe que a camada 2 sempre roda. Quando a camada 1 bloqueia, '
         'o servidor para antes das features e da inferência.', '',
         '## 2. Ponta a ponta, por HTTP', '']
    if http is None:
        L.append(f'*{aviso}.* Suba `python servidor.py` e rode de novo.')
    else:
        L += [f"Servidor: modelo `{http['info'].get('modelo')}`, "
              f"limiar {http['info'].get('limiar_decisao')}. Cliente e servidor na mesma "
              'máquina (sem rede física). Inclui o tempo do FastAPI/uvicorn.', '',
              '**Medido pelo middleware** (`latencia_ms` da resposta: normalização + '
              'camadas, sem o transporte HTTP):', '', *cab]
        for k, r in http['interno'].items():
            L.append(linha(f'decidido por: {k}', r))
        L += ['', '**Ida e volta no cliente** (inclui HTTP, FastAPI e a rota):', '', *cab]
        for k, r in http['ida_volta'].items():
            L.append(linha(f'decidido por: {k}', r))
    L += ['', '## Ressalvas', '',
          '- Uma requisição por vez. Não mede vazão nem comportamento sob carga concorrente.',
          '- Os números dependem da máquina; para comparar, rode na mesma máquina.',
          '- O servidor sobe com `reload=True` e imprime cada decisão no console; '
          'isso pesa na ida e volta, não no `latencia_ms` interno.']
    SAIDA.write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))
    print(f'\n[OK] {SAIDA}')


if __name__ == '__main__':
    main()
