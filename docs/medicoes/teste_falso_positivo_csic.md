# Falsos Positivos em Tráfego Benigno Realista

Gerado por `false_positive_test.py` contra `models/`.

- Dataset de treino: HTTP DATASET CSIC 2010
- Limiar de decisão: 0.651

> **Atenção.** Corpus em português contra modelo treinado em espanhol (CSIC/tienda1). O número abaixo mede falha de transferência entre domínios, **não** falso positivo. A taxa de falso positivo do modelo no seu próprio domínio é de 3,89% (limiar padrão) ou 0,97% (limiar calibrado).

Corpus sintético agrupado por categoria de tráfego HTTP real. Ver limitação declarada no cabeçalho do script.

| Categoria | Amostras | Falsos Positivos | Taxa |
| :--- | ---: | ---: | ---: |
| Busca em linguagem natural | 6 | 6 | 100.0% |
| Dados pessoais e cadastro | 6 | 6 | 100.0% |
| Identificadores e numeros | 6 | 6 | 100.0% |
| Texto livre / comentarios | 7 | 7 | 100.0% |
| Mencoes legitimas a SQL (casos-limite) | 8 | 8 | 100.0% |
| Strings curtas e degeneradas | 6 | 5 | 83.3% |
| **TOTAL** | **39** | **38** | **97.4%** |

Taxa medida: **97.4%**.
