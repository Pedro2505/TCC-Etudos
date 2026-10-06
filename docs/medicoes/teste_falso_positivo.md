# Falsos Positivos em Tráfego Benigno Realista

Gerado por `false_positive_test.py` contra `models/demo/`.

- Dataset de treino: Datasets de payload SQLi/XSS (modelo de demonstracao)
- Limiar de decisão: 0.170

Corpus sintético agrupado por categoria de tráfego HTTP real. Ver limitação declarada no cabeçalho do script.

| Categoria | Amostras | Falsos Positivos | Taxa |
| :--- | ---: | ---: | ---: |
| Busca em linguagem natural | 6 | 0 | 0.0% |
| Dados pessoais e cadastro | 6 | 1 | 16.7% |
| Identificadores e numeros | 6 | 2 | 33.3% |
| Texto livre / comentarios | 7 | 4 | 57.1% |
| Mencoes legitimas a SQL (casos-limite) | 8 | 7 | 87.5% |
| Strings curtas e degeneradas | 6 | 3 | 50.0% |
| **TOTAL** | **39** | **17** | **43.6%** |

Taxa medida: **43.6%**.
