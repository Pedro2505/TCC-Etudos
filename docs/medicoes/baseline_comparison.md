# Baseline de Assinaturas vs. Machine Learning

Gerado por `baseline_comparison.py`. Split estratificado 70/30, semente 42, amostra de 10000 registros.
TF-IDF ajustado somente no conjunto de treino.

## Impacto da reescrita heurística de labels

- Labels alterados pela regex: **11102 de 57465 (19.32%)**
- Ataques antes: 22598 → depois: 33700

## Cenário 1 — labels reescritos pela regex

| Detector | Acurácia | Precisão | Recall | F1 | FP | FN | ROC-AUC |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A) Baseline regex (assinaturas) | 83.70% | 100.00% | 72.48% | 84.05% | 0 | 489 | — |
| B) RF completo (manuais+TFIDF) | 99.43% | 99.61% | 99.44% | 99.52% | 7 | 10 | 0.9979 |
| C) RF sem keywords (estrutural) | 93.70% | 94.96% | 94.37% | 94.67% | 89 | 100 | 0.9769 |
| D) RF apenas TF-IDF (n-grams) | 99.47% | 99.77% | 99.32% | 99.55% | 4 | 12 | 0.9966 |

Concordância A vs B: **83.80%**

## Cenário 2 — labels originais dos CSVs

| Detector | Acurácia | Precisão | Recall | F1 | FP | FN | ROC-AUC |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A) Baseline regex (assinaturas) | 65.23% | 55.71% | 60.99% | 58.23% | 578 | 465 | — |
| B) RF completo (manuais+TFIDF) | 99.37% | 99.58% | 98.83% | 99.20% | 5 | 14 | 0.9978 |
| C) RF sem keywords (estrutural) | 92.50% | 91.93% | 88.93% | 90.41% | 93 | 132 | 0.9706 |
| D) RF apenas TF-IDF (n-grams) | 99.10% | 99.49% | 98.24% | 98.86% | 6 | 21 | 0.9955 |

Concordância A vs B: **65.60%**

## Leitura

- Ganho do ML sobre assinaturas (F1), cenário 1: **+15.48%**
- Ganho do ML sobre assinaturas (F1), cenário 2: **+40.97%**
