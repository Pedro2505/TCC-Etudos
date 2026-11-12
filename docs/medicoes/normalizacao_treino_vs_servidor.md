# Normalização: treino × servidor

Gerado por `medir_normalizacao.py` (script de medição de apoio, escrito pelo Claude).
Base: 32808 requisições em escopo do CSIC 2010. Modelo final de `models/`, limiar 0.650. **Probabilidades in-sample**: mede a diferença entre as normalizações, não o desempenho do modelo.

## Quanto o texto muda

| | n | % |
| :--- | ---: | ---: |
| Texto idêntico | 240 | 0.73% |
| Muda só maiúsculas/minúsculas | 32548 | 99.21% |
| Muda além da caixa (decode recursivo ou Base64) | 20 | 0.06% |

## Quanto a decisão muda (camada 1 OU camada 2)

| | Normalização do treino | Normalização do servidor |
| :--- | ---: | ---: |
| Ataques bloqueados (de 14188) | 13151 (92.69%) | 13151 (92.69%) |
| Legítimas bloqueadas (de 18620) | 3 (0.02%) | 3 (0.02%) |
| Assinatura disparou | 3314 | 3308 |

Decisões que trocam de lado: **0** de 32808 (0.00%) — 0 legítimas e 0 ataques.

## Exemplos de texto que muda além da caixa

| Treino vê | Servidor vê |
| :--- | :--- |
| `'?'` | `''` |
| `'?'` | `''` |
| `'\x00'` | `''` |
| `'\x00'` | `''` |
| `'?'` | `''` |
| `'?'` | `''` |
| `'|'` | `''` |
| `'|'` | `''` |
