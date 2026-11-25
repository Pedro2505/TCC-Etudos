# Pedidos do Paulo — mapa para escrever

> Montado em 25/11/2026 a partir de [`paulo.md`](paulo.md). **Não tem texto do artigo.**
> Para cada um dos 7 pontos: onde está o material, de qual script sai cada número, o que
> ainda falta, e as perguntas que o seu parágrafo precisa responder. A resposta é sua.
>
> Índice geral do material: [`README.md`](README.md) desta pasta.
> Números com proveniência: [`NECESSARIO.md`](../../NECESSARIO.md) §2b.

Legenda: ✅ material pronto · ⚠️ existe mas falta algo · ❌ não existe ainda

---

## Ponto 1 — Implementação: o caminho de uma requisição

| O que ele pediu | Onde está | Estado |
| :--- | :--- | :---: |
| Entrada da requisição | `servidor.py:69` (`waf_middleware`) | ✅ |
| Normalização | `servidor.py:84` (`decodificador_ofuscacao`) | ✅ |
| Regras (camada 1) | `servidor.py:151` → `assinaturas.py` (`avaliar`, `REGRAS`) | ✅ |
| Chamada ao modelo (camada 2) | `servidor.py:171`–`236` → `extrator.py` (`classificar`) | ✅ |
| Bloqueio × encaminhamento | `servidor.py:159` (assinatura), `:219` (modelo), `:235` (permitido) | ✅ |
| Bibliotecas e versões | [`requirements.txt`](../../requirements.txt) | ✅ |
| O que é seu, de terceiros e de IA | — | ❌ **só você sabe.** Ver a pergunta (d) |

Perguntas que o texto precisa responder:

- (a) Uma requisição `GET /busca?texto=...` entra. Quais funções ela atravessa, em ordem?
- (b) Por que a assinatura vem **antes** do modelo, se a decisão final é a mesma da união?
  (`NECESSARIO.md` §2, item 9)
- (c) Ele vai pedir para você **fazer uma alteração ao vivo**. Qual linha você mudaria para
  trocar o limiar? E o que esperaria que acontecesse com FP e recall?
- (d) Declaração de autoria: o código veio de `C:\Dev\Tcc`, feito com assistência de IA, e
  foi auditado aqui. Confira a regra da Unimar sobre IA antes de escrever (`NECESSARIO.md` §3).

---

## Ponto 2 — Dados e treinamento

| O que ele pediu | Onde está | Estado |
| :--- | :--- | :---: |
| De onde baixou o dataset | `README.md` da raiz (seção de dados) | ⚠️ falta o **link e a data do download** |
| 97.065 → 51.480 → 32.808 | `logs/ingestion_csic.log`, gerado por `ingestao_csic.py`; sua explicação em `NECESSARIO.md` §2b | ✅ |
| O que foi removido ou transformado | mesmo log + `ingestao_csic.normalizar_payload` | ✅ |
| Features que o modelo analisa | `models/model_metadata.json` (`colunas`): 9 heurísticas + 3 de método + TF-IDF de caracteres | ✅ |
| Por que Random Forest | — | ⚠️ depende do ponto 3 |
| Separação treino/avaliação sem repetição | `treino_modelo.py:237`–`279` (`StratifiedGroupKFold`, `groups=`) | ✅ |
| Ablação por bloco de features | `logs/model_trainer.log` → `NECESSARIO.md` §2b | ✅ |

Perguntas:

- (a) O que é exatamente uma requisição "duplicada" na deduplicação? Por quais campos?
- (b) O que o `groups=` do `StratifiedGroupKFold` impede que a deduplicação não impede?
- (c) Por que o TF-IDF é ajustado **dentro** de cada fold?

---

## Ponto 3 — Comparação entre algoritmos ✅ números prontos (25/11); a justificativa é sua

| O que ele pediu | Onde está | Estado |
| :--- | :--- | :---: |
| ≥ 2 algoritmos além do RF, nas mesmas condições | `comparar_modelos.py` → `docs/medicoes/comparacao_modelos.md` (tabela também na `FICHA-TECNICA.md` §5) | ✅ |
| Justificativa da escolha final | — | ❌ |

Ele escreveu explicitamente: **a ablação por grupo de features não conta.** Isso precisa
rodar antes de escrever. São ~1h: trocar o estimador, rodar a mesma validação e salvar a
saída em `logs/`.

Perguntas: quais dois algoritmos, e por que esses? Se outro algoritmo empatar com o RF, o
que justifica manter o RF?

---

## Ponto 4 — Os dois modelos ⚠️

| | Modelo avaliado (artigo) | Modelo da demo |
| :--- | :--- | :--- |
| Pasta | `models/` | `models/demo/` |
| Como sobe | `python servidor.py` | `WAF_MODELO=demo python servidor.py` (`servidor.py:42`–`44`) |
| Dados de treino | CSIC 2010, 32.808 em escopo (`carregar_dados_csic`, `treino_modelo.py:72`) | datasets SQLi/XSS fora de escopo, 57.465 exemplos (`carregar_dados_demo`, `treino_modelo.py:102`) |
| Limiar | **0,65** (`models/model_metadata.json`) | **0,46** (`models/demo/model_metadata.json`) |
| Números do artigo | sim, todos | **nenhum** |

Já medido (`NECESSARIO.md` §3, 06/10, `verificar_roteiro.py`): com o modelo do CSIC, os 4
casos legítimos em português foram **bloqueados** (p = 0,88–0,98). Com o demo, os 26 passam.

O que falta:

- ✅ O comentário do `servidor.py` (~linha 38) foi conferido em 25/11: está correto.
- ✅ **Modelo avaliado funcionando:** `demo_csic.py` (25/11) reenvia requisições reais do CSIC a
  `python servidor.py` e mostra qual camada decide. Resultado em `docs/medicoes/demo_csic.md`.
  Mostra o mecanismo, **não** o desempenho (o modelo final viu essas requisições no treino).
- ✅ README corrigido: dizia que o modelo demo foi "treinado com tráfego em português".
- ❌ De onde vêm os dois limiares? Os dois foram escolhidos pelo mesmo critério?
  (`treino_modelo.py:344`, `escolher_limiar`, alvo de FP)

**Dica (25/11):** a resposta deste ponto é a mesma da pergunta "como o modelo percebe que
`precio=-85` é anômalo, se não tem palavra suspeita?". Responda aquela, e esta sai junto.
Ver `NECESSARIO.md` §2, item 11.

Perguntas: as 3 da sessão de 25/11 — dados de cada um, por que a demo não usa o do CSIC, e
se o limiar é o mesmo. E mais: isso é defeito do trabalho ou é um resultado? (o modelo
aprende o "normal" de **uma** aplicação)

---

## Ponto 5 — Resultados e interpretação

| O que ele pediu | Onde está | Estado |
| :--- | :--- | :---: |
| Regras × modelo × combinação | `docs/medicoes/avaliacao_hibrida.md` §1 (`avaliacao_hibrida.py`) | ✅ |
| Matriz de confusão | os 4 números saem da mesma tabela (FP, FN, e os totais 18.620 / 14.188) | ✅ `docs/medicoes/matriz_confusao.png` (`medir_erros.py`) |
| Precisão, recall, F1 e FP com os seus números | mesma tabela | ✅ (a explicação é sua) |
| **Os ~40% que passaram** | complementaridade: "nenhuma camada" = 40,2%; recall por família | ✅ números: **100% tampering** (`docs/medicoes/erros.md`) · discussão ❌ |

Perguntas:

- (a) Monte a matriz de confusão da configuração C à mão, a partir de FP = 184 e FN = 5.707.
  Quanto dá VP e VN? (Se você consegue montar, consegue explicar na banca.)
- (b) Os 40,2% que passaram são de qual família? (tabela por família: o tampering tem
  11.332 casos e 49,6% de recall)
- (c) Por que 0,99% de FP com limiar 0,65, e o que acontece com os 40% se o limiar baixar?
  (`docs/medicoes/curva_limiar.csv`)

---

## Ponto 6 — Limitações e latência

| O que ele pediu | Onde está | Estado |
| :--- | :--- | :---: |
| Onde o sistema erra | `NECESSARIO.md` §3 (zero-day, escopo, só query string 22,3%, viés da família por regex) | ✅ |
| Por que bloqueia legítimo | os 184 FP + o caso do português no modelo do CSIC | ✅ `docs/medicoes/erros.md`: 124 em `autenticar.jsp`. Falta você olhar os exemplos |
| Usar em outra aplicação | ponto 4: precisa retreinar com o "normal" dela | ✅ |
| Como mediu a latência e em que condições | `docs/medicoes/latencia.md` (`medir_latencia.py`): 300 payloads, `n_jobs=1`, uma requisição por vez, AMD/Windows/Python 3.11 | ✅ |

Atenção: **os 31,94 ms do projeto antigo não valem.** Só os de 12/11 (10,99 ms média).

---

## Ponto 7 — Documentação e reprodução

| O que ele pediu | Onde está | Estado |
| :--- | :--- | :---: |
| Código organizado | raiz do repositório | ✅ |
| Dependências | `requirements.txt` | ✅ |
| Instruções de execução | `README.md` da raiz | ✅ |
| Script de cada resultado | `README.md` da raiz, tabela "de onde vem cada número" | ⚠️ falta a comparação de algoritmos (ponto 3) |
| Fundamentação com referências | cap. 2 e 3 | ❌ escrita sua |

---

## Ordem sugerida

1. **Ponto 3** (rodar) e **ponto 4** (roteiro da demo com o modelo avaliado): são os únicos
   que precisam de PC e de código. O resto é escrita.
2. Ponto 5: montar a matriz à mão e discutir os 40%.
3. Pontos 2 e 6: material pronto, falta a redação.
4. Pontos 1 e 7: redação curta e a declaração de autoria.
