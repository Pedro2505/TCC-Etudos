# Latência do WAF

Gerado por `medir_latencia.py` (script de medição de apoio, escrito pelo Claude) em 2026-11-12.
Máquina: AMD64 Family 23 Model 96 Stepping 1, AuthenticAMD · Windows 10 · Python 3.11.9.
Amostra: 300 payloads reais do CSIC 2010 em escopo (150 legítimos, 150 ataques), semente 42, 20 de aquecimento descartados. Tempos em **milissegundos**.

## 1. Por etapa (dentro do processo, modelo de `models/`, n_jobs=1)

| Etapa | n | média | p50 | p95 | p99 | máx |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Normalização (servidor) | 300 | 0.02 | 0.02 | 0.02 | 0.04 | 0.04 |
| Camada 1 — assinaturas | 300 | 0.06 | 0.05 | 0.10 | 0.12 | 0.14 |
| Montagem das features | 300 | 4.60 | 4.48 | 5.86 | 8.25 | 9.78 |
| Inferência (Random Forest) | 300 | 6.31 | 6.17 | 7.35 | 9.22 | 10.16 |
| **Total até a decisão da camada 2** | 300 | 10.99 | 10.76 | 13.21 | 16.74 | 18.60 |

O total supõe que a camada 2 sempre roda. Quando a camada 1 bloqueia, o servidor para antes das features e da inferência.

## 2. Ponta a ponta, por HTTP

Servidor: modelo `models`, limiar 0.65. Cliente e servidor na mesma máquina (sem rede física). Inclui o tempo do FastAPI/uvicorn.

**Medido pelo middleware** (`latencia_ms` da resposta: normalização + camadas, sem o transporte HTTP):

| Etapa | n | média | p50 | p95 | p99 | máx |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| decidido por: assinatura | 37 | 0.09 | 0.00 | 0.77 | 1.32 | 1.50 |
| decidido por: modelo | 263 | 11.16 | 11.05 | 13.04 | 15.71 | 21.26 |

**Ida e volta no cliente** (inclui HTTP, FastAPI e a rota):

| Etapa | n | média | p50 | p95 | p99 | máx |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| decidido por: assinatura | 37 | 2.06 | 2.00 | 2.41 | 2.48 | 2.48 |
| decidido por: modelo | 263 | 13.62 | 13.43 | 14.94 | 17.87 | 24.68 |

## Ressalvas

- Uma requisição por vez. Não mede vazão nem comportamento sob carga concorrente.
- Os números dependem da máquina; para comparar, rode na mesma máquina.
- O `latencia_ms` do servidor usa `time.time()`, de resolução grosseira no Windows: abaixo de ~1 ms ele arredonda para 0 (por isso p50 = 0,00 na linha da assinatura). A tabela 1, com `perf_counter`, é a referência para as etapas.
- O servidor sobe com `reload=True` e imprime cada decisão no console; isso pesa na ida e volta, não no `latencia_ms` interno.
