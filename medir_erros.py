"""
Script de MEDIÇÃO DE APOIO — escrito pelo Claude (assistente de IA) em 25/11/2026,
pela exceção do CLAUDE.md ("script de medição de apoio"). Não é peça do TCC: não
treina modelo salvo, não decide, não altera models/. Só mede.

Perguntas que ele responde (pontos 5 e 6 do Paulo, docs/artigo/paulo.md):
    1. Qual é a matriz de confusão das configurações A (assinaturas), B (modelo) e
       C (união)?
    2. Quais requisições legítimas foram bloqueadas (os falsos positivos)?
    3. De que família são os ataques que passaram pelas duas camadas (os falsos
       negativos, "os ~40%")?

Metodologia: a MESMA do avaliacao_hibrida.py. Mesmas probabilidades out-of-fold
(treino_modelo.validar, StratifiedGroupKFold agrupado por payload, TF-IDF por fold)
e o mesmo limiar de models/model_metadata.json. Os totais de FP e FN têm que bater
com docs/medicoes/avaliacao_hibrida.md; se não baterem, este script está errado.

Uso:  venv\\Scripts\\python.exe medir_erros.py
Saídas:
    docs/medicoes/matriz_confusao.png      figura (A, B, C)
    docs/medicoes/erros.md                 contagens: FP por path, FN por família
    datasets/CSIC2010/erros_exemplos.csv   as requisições em si (FORA do Git:
                                           é tráfego bruto do CSIC, redistribuição restrita)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

import assinaturas
from treino_modelo import carregar_dados_csic, preparar_colunas_auxiliares, validar

RAIZ = Path(__file__).resolve().parent
PASTA_MEDICOES = RAIZ / 'docs' / 'medicoes'
FIGURA = PASTA_MEDICOES / 'matriz_confusao.png'
RELATORIO = PASTA_MEDICOES / 'erros.md'
EXEMPLOS = RAIZ / 'datasets' / 'CSIC2010' / 'erros_exemplos.csv'


def main() -> None:
    df = preparar_colunas_auxiliares(carregar_dados_csic())
    y = df['Label'].to_numpy()

    print('[1/3] Camada 1 (assinaturas)...')
    disparou = assinaturas.avaliar_serie(df['Sentence'])['disparou'].to_numpy()

    print('[2/3] Camada 2 (validação cruzada, igual ao avaliacao_hibrida.py)...')
    _, prob_oof = validar(df, usar_heuristicas=True, usar_tfidf=True,
                          usar_contexto=True, verboso=False)
    with open(RAIZ / 'models' / 'model_metadata.json', encoding='utf-8') as f:
        limiar = json.load(f)['limiar_decisao']
    detectou_ml = prob_oof >= limiar

    configs = {
        'A) Assinaturas': disparou.astype(int),
        f'B) Modelo (limiar {limiar:.2f})': detectou_ml.astype(int),
        'C) União': (disparou | detectou_ml).astype(int),
    }

    print('[3/3] Matrizes, falsos positivos e falsos negativos...')
    matrizes = {nome: confusion_matrix(y, pred, labels=[0, 1]) for nome, pred in configs.items()}

    # --- Figura -------------------------------------------------------------
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.2))
    for eixo, (nome, m) in zip(eixos, matrizes.items()):
        eixo.imshow(m, cmap='Blues')
        for i in range(2):
            for j in range(2):
                eixo.text(j, i, f'{m[i, j]:,}'.replace(',', '.'), ha='center', va='center',
                          fontsize=13, color='white' if m[i, j] > m.max() / 2 else 'black')
        eixo.set_xticks([0, 1], ['Legítima', 'Anômala'])
        eixo.set_yticks([0, 1], ['Legítima', 'Anômala'])
        eixo.set_xlabel('Previsto')
        eixo.set_ylabel('Real')
        eixo.set_title(nome)
    fig.suptitle('Matriz de confusão — CSIC 2010, 32.808 requisições, probabilidades out-of-fold')
    fig.tight_layout()
    fig.savefig(FIGURA, dpi=200)

    # --- Erros da configuração C --------------------------------------------
    pred_c = configs['C) União']
    fp = df[(y == 0) & (pred_c == 1)].copy()
    fn = df[(y == 1) & (pred_c == 0)].copy()
    fp['prob'] = prob_oof[(y == 0) & (pred_c == 1)]
    fn['prob'] = prob_oof[(y == 1) & (pred_c == 0)]

    fp_por_path = fp['path'].value_counts()
    ataques = df[y == 1]
    fn_por_familia = (pd.DataFrame({'passaram': fn['familia_ataque'].value_counts(),
                                    'total': ataques['familia_ataque'].value_counts()})
                      .fillna(0).astype(int).sort_values('passaram', ascending=False))
    fn_por_familia['pct_da_familia'] = fn_por_familia['passaram'] / fn_por_familia['total']
    fn_por_familia['pct_dos_que_passaram'] = fn_por_familia['passaram'] / len(fn)

    EXEMPLOS.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([fp.assign(erro='falso_positivo'), fn.assign(erro='falso_negativo')])[
        ['erro', 'metodo', 'path', 'Sentence', 'familia_ataque', 'prob']
    ].to_csv(EXEMPLOS, index=False, encoding='utf-8')

    # --- Relatório ----------------------------------------------------------
    linhas = [
        '# Matriz de confusão e erros do sistema',
        '',
        'Gerado por `medir_erros.py` (medição de apoio, escrita pelo Claude em 25/11/2026).',
        f'Mesma metodologia do `avaliacao_hibrida.py`: probabilidades out-of-fold, limiar {limiar:.3f}.',
        f'Figura: [`matriz_confusao.png`](matriz_confusao.png). Requisições em si: '
        '`datasets/CSIC2010/erros_exemplos.csv` (fora do Git).',
        '',
        '## 1. Matrizes de confusão',
        '',
        '| Configuração | VN | FP | FN | VP |',
        '| :--- | ---: | ---: | ---: | ---: |',
    ]
    for nome, m in matrizes.items():
        tn, fpn, fnn, tp = m.ravel()
        linhas.append(f'| {nome} | {tn} | {fpn} | {fnn} | {tp} |')
    linhas += [
        '',
        '**Conferência:** FP e FN têm que bater com `avaliacao_hibrida.md` §1.',
        '',
        f'## 2. Falsos positivos da união: {len(fp)} requisições legítimas bloqueadas',
        '',
        'Por path da aplicação (onde o legítimo foi bloqueado):',
        '',
        '| Path | FP |',
        '| :--- | ---: |',
    ]
    linhas += [f'| `{p}` | {n} |' for p, n in fp_por_path.items()]
    linhas += [
        '',
        f'Probabilidade dos FP: mediana {fp["prob"].median():.3f}, '
        f'mínima {fp["prob"].min():.3f}, máxima {fp["prob"].max():.3f}.',
        '',
        f'## 3. Falsos negativos da união: {len(fn)} ataques que passaram '
        f'({len(fn) / len(ataques):.1%} dos {len(ataques)})',
        '',
        '| Família | Passaram | Total da família | % da família | % dos que passaram |',
        '| :--- | ---: | ---: | ---: | ---: |',
    ]
    for familia, r in fn_por_familia.iterrows():
        linhas.append(f'| {familia} | {int(r.passaram)} | {int(r.total)} | '
                      f'{r.pct_da_familia:.1%} | {r.pct_dos_que_passaram:.1%} |')
    linhas += [
        '',
        f'Probabilidade dos FN: mediana {fn["prob"].median():.3f} '
        f'(limiar {limiar:.3f}). Quanto mais perto do limiar, mais um ajuste o recuperaria '
        '— ao custo de FP (ver `curva_limiar.csv`).',
        '',
        '**Viés:** a família é atribuída por regex (`ingestao_csic.classificar_familia_ataque`).',
    ]
    RELATORIO.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print('\n'.join(linhas))


if __name__ == '__main__':
    main()
