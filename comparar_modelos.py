"""
COMPARAÇÃO ENTRE ALGORITMOS — objetivo específico 5 da 1ª entrega; ponto 3 do Paulo
(docs/artigo/paulo.md): "Apresente essa comparação usando as mesmas condições de
avaliação e justifique a escolha final."

Autoria: escrito pelo Claude (assistente de IA) em 25/11/2026, a pedido do Pedro.
Entra na declaração de uso de IA do artigo.

O QUE É IGUAL PARA OS TRÊS (as "mesmas condições"):
    - os mesmos dados: CSIC 2010 em escopo, 32.808 requisições;
    - os mesmos 5 folds: treino_modelo.validar, StratifiedGroupKFold agrupado por
      payload, mesma semente — cada requisição cai no mesmo fold para os três;
    - as mesmas features: heurísticas + contexto HTTP + TF-IDF ajustado DENTRO de cada fold;
    - o mesmo critério de limiar: treino_modelo.escolher_limiar, maior F1 com taxa de
      falso positivo <= 1%, sobre as probabilidades out-of-fold de CADA modelo.

O QUE MUDA: só o algoritmo.
    - Random Forest: o do artigo (100 árvores, semente 42).
    - Regressão logística: modelo linear. Precisa de escala parecida entre as features
      (comprimento ~ centenas, TF-IDF entre 0 e 1), então vai num Pipeline com
      StandardScaler(with_mean=False) — with_mean=False porque a matriz é esparsa.
      O Pipeline é clonado e ajustado dentro de cada fold, então o scaler só vê o
      treino do fold (sem vazamento).
    - Árvore de decisão: uma árvore só, mesma família do RF. Mede o que a "floresta"
      acrescenta sobre uma árvore.

NÃO treina modelo final e NÃO toca em models/. Os números do artigo continuam os mesmos.

Uso:    venv\\Scripts\\python.exe comparar_modelos.py
Saídas: docs/medicoes/comparacao_modelos.md   (tabela)
        logs/comparar_modelos.log             (redirecione a saída do console:
                                               ... comparar_modelos.py > logs/comparar_modelos.log)
Conferência: a linha do Random Forest a 0,5 tem que repetir o F1 do logs/model_trainer.log
(0,7824 ± 0,0088). Se não repetir, a mudança em validar() alterou alguma coisa.
"""
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from treino_modelo import (ALVO_FALSO_POSITIVO, SEMENTE, carregar_dados_csic,
                           escolher_limiar, preparar_colunas_auxiliares, resumir, validar)

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / 'docs' / 'medicoes' / 'comparacao_modelos.md'

MODELOS = {
    'Random Forest (artigo)': None,   # None = o RF padrão de treino_modelo.validar
    'Regressão logística': make_pipeline(StandardScaler(with_mean=False),
                                         LogisticRegression(max_iter=5000)),
    'Árvore de decisão': DecisionTreeClassifier(random_state=SEMENTE),
}


def main() -> None:
    df = preparar_colunas_auxiliares(carregar_dados_csic())
    y = df['Label'].to_numpy()
    tampering = (df['familia_ataque'] == 'Tampering sem assinatura').to_numpy()

    linhas = []
    for nome, modelo in MODELOS.items():
        print(f"\n{'=' * 78}\n{nome}\n{'=' * 78}")
        inicio = time.perf_counter()
        tabela, prob_oof = validar(df, modelo=modelo)
        segundos = time.perf_counter() - inicio
        resumo = resumir(nome, tabela)
        limiar, curva = escolher_limiar(y, prob_oof, ALVO_FALSO_POSITIVO)
        escolhido = curva.loc[(curva['limiar'] - limiar).abs().idxmin()]
        detectou = prob_oof >= limiar
        linhas.append({
            'nome': nome,
            'f1_05': resumo['f1'],
            'auc': resumo['roc_auc'],
            'limiar': limiar,
            'precisao': escolhido['precisao'],
            'recall': escolhido['recall'],
            'f1': escolhido['f1'],
            'taxa_fp': escolhido['taxa_fp'],
            'fp': int(escolhido['fp']),
            'fn': int(escolhido['fn']),
            'recall_tampering': float(detectou[tampering].mean()),
            'fp_minimo': float(curva['taxa_fp'].min()),
            'atinge_alvo': bool((curva['taxa_fp'] <= ALVO_FALSO_POSITIVO).any()),
            'segundos': segundos,
        })

    texto = [
        '# Comparação entre algoritmos (objetivo 5)',
        '',
        'Gerado por `comparar_modelos.py` (escrito pelo Claude a pedido do Pedro, 25/11/2026).',
        'CSIC 2010, 32.808 requisições. Mesmos 5 folds (`StratifiedGroupKFold` agrupado por payload),',
        'mesmas features, TF-IDF por fold, mesmo critério de limiar (maior F1 com FP ≤ 1%,',
        'sobre probabilidades out-of-fold de cada modelo). Só o algoritmo muda.',
        '',
        '## 1. Média ± desvio nos 5 folds, limiar padrão 0,5',
        '',
        '| Algoritmo | F1 (0,5) | ROC-AUC |',
        '| :--- | ---: | ---: |',
    ]
    for r in linhas:
        texto.append(f"| {r['nome']} | {r['f1_05']['media']:.4f} ± {r['f1_05']['desvio']:.4f} | "
                     f"{r['auc']['media']:.4f} ± {r['auc']['desvio']:.4f} |")
    texto += [
        '',
        '## 2. No limiar calibrado (FP ≤ 1%), probabilidades out-of-fold',
        '',
        '| Algoritmo | Limiar | Precisão | Recall | F1 | Taxa de FP | FP | FN | Recall tampering | Tempo da validação |',
        '| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for r in linhas:
        texto.append(f"| {r['nome']} | {r['limiar']:.3f} | {r['precisao']:.2%} | {r['recall']:.2%} | "
                     f"{r['f1']:.4f} | {r['taxa_fp']:.2%} | {r['fp']} | {r['fn']} | "
                     f"{r['recall_tampering']:.1%} | {r['segundos']:.0f} s |")
    for r in linhas:
        if not r['atinge_alvo']:
            texto += ['', f"**Atenção — {r['nome']}: nenhum limiar atinge FP ≤ 1%.** A menor taxa de FP "
                      f"alcançável é {r['fp_minimo']:.2%}; a linha acima usa o limiar de melhor F1 "
                      "sem restrição e **não é comparável** às outras. Na condição do artigo "
                      "(FP ≤ 1%), este algoritmo não opera."]
    texto += [
        '',
        '**Conferência:** a linha do Random Forest no §1 tem que repetir 0,7824 ± 0,0088 '
        '(`logs/model_trainer.log`), e o limiar no §2 tem que dar 0,650.',
        '',
        'O tempo é o da validação inteira (5 treinos + 5 previsões), na máquina das medições; '
        'não é latência por requisição.',
    ]
    SAIDA.write_text('\n'.join(texto) + '\n', encoding='utf-8')
    print('\n' + '\n'.join(texto))


if __name__ == '__main__':
    main()
