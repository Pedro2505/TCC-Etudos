# Comparação entre algoritmos (objetivo 5)

Gerado por `comparar_modelos.py` (escrito pelo Claude a pedido do Pedro, 25/11/2026).
CSIC 2010, 32.808 requisições. Mesmos 5 folds (`StratifiedGroupKFold` agrupado por payload),
mesmas features, TF-IDF por fold, mesmo critério de limiar (maior F1 com FP ≤ 1%,
sobre probabilidades out-of-fold de cada modelo). Só o algoritmo muda.

## 1. Média ± desvio nos 5 folds, limiar padrão 0,5

| Algoritmo | F1 (0,5) | ROC-AUC |
| :--- | ---: | ---: |
| Random Forest (artigo) | 0.7824 ± 0.0088 | 0.8880 ± 0.0027 |
| Regressão logística | 0.5359 ± 0.0119 | 0.7193 ± 0.0106 |
| Árvore de decisão | 0.7410 ± 0.0090 | 0.7785 ± 0.0082 |

## 2. No limiar calibrado (FP ≤ 1%), probabilidades out-of-fold

| Algoritmo | Limiar | Precisão | Recall | F1 | Taxa de FP | FP | FN | Recall tampering | Tempo da validação |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Random Forest (artigo) | 0.650 | 97.86% | 59.43% | 0.7395 | 0.99% | 184 | 5756 | 49.6% | 47 s |
| Regressão logística | 0.644 | 96.31% | 34.17% | 0.5044 | 1.00% | 186 | 9340 | 18.6% | 24 s |
| Árvore de decisão | 0.427 | 74.84% | 73.54% | 0.7419 | 18.83% | 3507 | 3754 | 67.4% | 33 s |

**Atenção — Árvore de decisão: nenhum limiar atinge FP ≤ 1%.** A menor taxa de FP alcançável é 18.17%; a linha acima usa o limiar de melhor F1 sem restrição e **não é comparável** às outras. Na condição do artigo (FP ≤ 1%), este algoritmo não opera.

**Conferência:** a linha do Random Forest no §1 tem que repetir 0,7824 ± 0,0088 (`logs/model_trainer.log`), e o limiar no §2 tem que dar 0,650.

O tempo é o da validação inteira (5 treinos + 5 previsões), na máquina das medições; não é latência por requisição.
