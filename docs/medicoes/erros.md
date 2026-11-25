# Matriz de confusão e erros do sistema

Gerado por `medir_erros.py` (medição de apoio, escrita pelo Claude em 25/11/2026).
Mesma metodologia do `avaliacao_hibrida.py`: probabilidades out-of-fold, limiar 0.650.
Figura: [`matriz_confusao.png`](matriz_confusao.png). Requisições em si: `datasets/CSIC2010/erros_exemplos.csv` (fora do Git).

## 1. Matrizes de confusão

| Configuração | VN | FP | FN | VP |
| :--- | ---: | ---: | ---: | ---: |
| A) Assinaturas | 18620 | 0 | 10874 | 3314 |
| B) Modelo (limiar 0.65) | 18436 | 184 | 5756 | 8432 |
| C) União | 18436 | 184 | 5707 | 8481 |

**Conferência:** FP e FN têm que bater com `avaliacao_hibrida.md` §1.

## 2. Falsos positivos da união: 184 requisições legítimas bloqueadas

Por path da aplicação (onde o legítimo foi bloqueado):

| Path | FP |
| :--- | ---: |
| `/tienda1/publico/autenticar.jsp` | 124 |
| `/tienda1/miembros/editar.jsp` | 29 |
| `/tienda1/publico/registro.jsp` | 22 |
| `/tienda1/publico/caracteristicas.jsp` | 3 |
| `/tienda1/publico/entrar.jsp` | 2 |
| `/tienda1/publico/vaciar.jsp` | 2 |
| `/tienda1/publico/pagar.jsp` | 2 |

Probabilidade dos FP: mediana 0.730, mínima 0.650, máxima 1.000.

## 3. Falsos negativos da união: 5707 ataques que passaram (40.2% dos 14188)

| Família | Passaram | Total da família | % da família | % dos que passaram |
| :--- | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 5707 | 11332 | 50.4% | 100.0% |
| CRLF Injection | 0 | 388 | 0.0% | 0.0% |
| Caractere de Controle/Nulo | 0 | 114 | 0.0% | 0.0% |
| Injecao SSI/Comando | 0 | 384 | 0.0% | 0.0% |
| SQLi | 0 | 1018 | 0.0% | 0.0% |
| XSS | 0 | 952 | 0.0% | 0.0% |

Probabilidade dos FN: mediana 0.360 (limiar 0.650). Quanto mais perto do limiar, mais um ajuste o recuperaria — ao custo de FP (ver `curva_limiar.csv`).

**Viés:** a família é atribuída por regex (`ingestao_csic.classificar_familia_ataque`).
