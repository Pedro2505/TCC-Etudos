# Avaliação da arquitetura híbrida — assinaturas + Machine Learning

Gerado por `avaliacao_hibrida.py`. **Não editar à mão.**

HTTP DATASET CSIC 2010 em escopo: 32808 requisições (18620 legítimas / 14188 anômalas). Validação `StratifiedGroupKFold(5)` agrupada por payload, TF-IDF ajustado dentro de cada fold, probabilidades *out-of-fold*.

Camada 1: 24 assinaturas (`assinaturas.py`), inspecionando a mesma superfície do modelo.


## 1. As quatro configurações

| Configuração | Precisão | Recall | F1 | Taxa de FP | FP | FN |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| A) Camada 1 isolada (assinaturas) | 100.00% | 23.36% | 0.3787 | 0.00% | 0 | 10874 |
| B) Camada 2 isolada (modelo, limiar 0.650) | 97.86% | 59.43% | 0.7395 | 0.99% | 184 | 5756 |
| C) Uniao (limiar 0.650) | 97.88% | 59.78% | 0.7422 | 0.99% | 184 | 5707 |
| D) Cascata recalibrada (limiar 0.650) | 97.88% | 59.78% | 0.7422 | 0.99% | 184 | 5707 |

> **Cascata e união são equivalentes em decisão.** Bloquear na camada 1 e consultar a camada 2 só para o que passou produz o mesmo conjunto bloqueado que "camada 1 OU camada 2". A cascata não existe para ganhar recall: ela existe pela proveniência do bloqueio, pelo custo evitado e pelo orçamento de falso positivo — que é o que a configuração D explora.


## 2. Complementaridade dos detectores

Sobre os **14188 ataques** do conjunto:

| Detectado por | n | % dos ataques |
| :--- | ---: | ---: |
| Ambas as camadas | 3265 | 23.0% |
| **Somente a assinatura** | 49 | 0.3% |
| **Somente o modelo** | 5167 | 36.4% |
| Nenhuma das duas | 5707 | 40.2% |

Somar duas camadas só compensa quando elas erram em requisições diferentes. As células "somente" quantificam exatamente isso: **5167 ataques (36.4%) seriam perdidos por um WAF de assinaturas operando sozinho**, e 49 (0.3%) seriam perdidos pelo modelo operando sozinho.


## 3. Recall por família — onde cada camada contribui

| Família | n | Camada 1 (assinaturas) | Camada 2 (modelo) | Combinado | Ganho da camada 2 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 11332 | 4.0% | 49.6% | 49.6% | +45.6 pp |
| SQLi | 1018 | 100.0% | 99.9% | 100.0% | +0.0 pp |
| XSS | 952 | 100.0% | 100.0% | 100.0% | +0.0 pp |
| CRLF Injection | 388 | 100.0% | 98.5% | 100.0% | +0.0 pp |
| Injecao SSI/Comando | 384 | 100.0% | 100.0% | 100.0% | +0.0 pp |
| Caractere de Controle/Nulo | 114 | 100.0% | 63.2% | 100.0% | +0.0 pp |
| **SQLi + XSS (escopo do TCC)** | **1970** | **100.0%** | **99.9%** | **100.0%** | **+0.0 pp** |

### Viés declarado nesta tabela

O CSIC 2010 rotula apenas normal/anômalo. A **família é atribuída por regex** (`ingestion_csic.classificar_familia_ataque`). As regras da camada 1 foram escritas de forma independente, mas descrevem os mesmos fenômenos, então há sobreposição inevitável.

**Consequência:** o recall da camada 1 por família é **otimista por construção** — uma família definida como "casa com regex de SQLi" tende a ser detectada por um detector de assinaturas de SQLi. Os números imunes a esse viés são os da Seção 1 e da Seção 2, medidos contra o rótulo real do dataset.

A linha de *tampering sem assinatura* é o caso extremo: a camada 1 tem recall zero nela **por tautologia**, já que a família é definida como "não casou com nenhuma assinatura". Mas a tautologia é o próprio argumento — "ataque sem assinatura" e "assinaturas não detectam" são a mesma afirmação, e ela vale para qualquer WAF de regras. O que não é tautológico é quanto desses ataques a camada 2 detecta.


## 4. Orçamento de falso positivo

| | |
| :--- | ---: |
| Alvo declarado de falso positivo | ≤ 1.0% |
| FP consumido pela camada 1 | 0 (0.00%) |
| Limiar da camada 2 na monografia | 0.650 |
| Limiar da camada 2 recalibrado na cascata | 0.650 |

A camada 2 não precisa mais cobrir sozinha todo o recall: parte dele vem da camada 1, a um custo de falso positivo que esta tabela mede. O limiar recalibrado é a consequência direta disso — é o mesmo critério de calibração do `model_trainer.py` (maior F1 dentro do orçamento), aplicado ao sistema completo em vez de ao modelo isolado. Curva completa em `curva_limiar_cascata.csv`.


## 5. Regras que mais dispararam

| Regra | Nome | Disparos |
| :--- | :--- | ---: |
| `SQLI-005` | Funcao SQL de exfiltracao ou atraso | 744 |
| `XSS-001` | Tag <script> | 698 |
| `RCE-001` | Diretiva Server-Side Include | 520 |
| `PROTO-001` | Injecao de CRLF | 388 |
| `SQLI-001` | Tautologia SQL (OR 1=1) | 322 |
| `XSS-003` | Pseudo-protocolo executavel | 254 |
| `SQLI-003` | Consulta empilhada apos terminador | 168 |
| `PROTO-002` | Byte nulo | 114 |
| `SQLI-004` | DDL/DML em valor de parametro | 106 |

## 6. Limitações desta medição

1. **A camada 1 não é o OWASP CRS.** São ~25 regras inspiradas nas famílias de detecção do CRS. Um CRS real tem centenas de regras e pontuação de anomalia. A comparação com o CRS de verdade continua sendo trabalho futuro declarado.
2. **A camada 1 inspeciona a mesma superfície que o modelo** (valores de parâmetro decodificados). Um ModSecurity real também veria path, headers, cookies e corpo. Logo esta camada 1 é *mais fraca* que um WAF real, e o ganho medido para a camada 2 é uma estimativa **conservadora**.
3. **Sem regra de impressão digital de scanner.** O CSIC foi gerado com o Paros Proxy e 748 ataques carregam a string `Paros` no payload. Uma regra assim teria recall inflado por artefato do dataset; foi deliberadamente excluída.
4. **A atribuição de família é heurística**, validada manualmente em 40 amostras (ver `validacao_familias.md`), não *ground truth*.
