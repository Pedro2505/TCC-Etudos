# Falsos Positivos em Tráfego Benigno Realista

Gerado por `teste_falso_positivo.py` contra `models/demo/`.

- Dataset de treino: Datasets de payload SQLi/XSS (modelo de demonstracao)
- Limiar de decisão: 0.460

Corpus sintético agrupado por categoria de tráfego HTTP real. Ver limitação declarada no cabeçalho do script.

| Categoria | Amostras | Falsos Positivos | Taxa |
| :--- | ---: | ---: | ---: |
| Busca em linguagem natural | 6 | 0 | 0.0% |
| Dados pessoais e cadastro | 6 | 1 | 16.7% |
| Identificadores e numeros | 6 | 1 | 16.7% |
| Texto livre / comentarios | 7 | 2 | 28.6% |
| Mencoes legitimas a SQL (casos-limite) | 8 | 5 | 62.5% |
| Strings curtas e degeneradas | 6 | 2 | 33.3% |
| **TOTAL** | **39** | **11** | **28.2%** |

Taxa medida: **28.2%**.
