# Demonstração com o modelo avaliado (ponto 4 do Paulo)

Gerado por `demo_csic.py` contra `python servidor.py` (modelo de `models/`). 6 requisições GET reais do CSIC por categoria, semente 42.

| Categoria | Enviadas | Bloqueadas pela assinatura | Bloqueadas pelo modelo | Passaram |
| :--- | ---: | ---: | ---: | ---: |
| Legítima | 6 | 0 | 0 | 6 |
| SQLi | 6 | 6 | 0 | 0 |
| XSS | 6 | 6 | 0 | 0 |
| Tampering | 6 | 0 | 5 | 1 |

**Não é medida de desempenho.** O modelo de `models/` foi treinado com todas as 32.808 requisições, inclusive estas. A demonstração mostra o mecanismo; o desempenho é o das probabilidades out-of-fold (`avaliacao_hibrida.md`).
