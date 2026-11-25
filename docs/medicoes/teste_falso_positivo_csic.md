# Falsos Positivos em Tráfego Benigno Realista

Gerado por `teste_falso_positivo.py` contra `models/`.

- Dataset de treino: HTTP DATASET CSIC 2010
- Limiar de decisão: 0.650

> **Atenção.** Corpus em português contra modelo treinado em espanhol (CSIC/tienda1). O número abaixo mede falha de transferência entre domínios, **não** falso positivo. A taxa de falso positivo do modelo no seu próprio domínio é de 3,92% (limiar padrão 0,5) ou 0,99% (limiar calibrado 0,65; logs/model_trainer.log).

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
