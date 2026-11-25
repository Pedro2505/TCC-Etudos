# NECESSARIO — material bruto do artigo

> Coletor. Tudo que sai de uma sessão e tem destino no artigo cai aqui primeiro.
> **Não é o artigo.** É a matéria-prima dele, para não depender da memória em outubro.
>
> Inventário das 12 tabelas e figuras: [`docs/aulas/estrutura-do-artigo.md`](docs/aulas/estrutura-do-artigo.md) §2.
> Estrutura dos 7 capítulos: mesmo arquivo, §1. Não duplicar aqui.

## Regra deste arquivo

Nada entra sem **origem**. Frase minha ou decisão tomada em sessão, com a data.
Número só entra com o script que o gerou. Se não sei qual script, escrevo "não medi".

---

## 1. Frases já prontas (minhas, saíram das sessões)

**Sobre acurácia** — 13/08, Tarefa 0:

> A acurácia não distingue um detector que funciona de um que não faz nada. No cenário
> testado, um classificador que libera todo o tráfego obtém os mesmos 95% do detector
> avaliado.

**Sobre o enquadramento (por que somar e não substituir)** — 13/08:

> Não faz sentido trocar algo que já funciona por algo novo. Substituir significaria abrir
> mão de um detector com precisão altíssima e proveniência auditável em troca de um que
> erra mais em tráfego legítimo e responde "probabilidade 0,87" quando o analista pergunta
> por que bloqueou.

**Seção 2.4 — parágrafo do vazamento, escrito por ele em 19/08.** Estado: **3 de 6 frases.**

> O vazamento de dados (*data leakage*) ocorre quando os dados de teste vazam e vão para os
> dados de treino. O recall fica alto no experimento, mas em produção não repete esse valor.
> Se em produção o modelo não teria a informação, no treino não pode ter essa informação.

*Pendência de digitação:* corrigir `infomração` → informação na terceira frase.

*Falta escrever — os três exemplos concretos:* TF-IDF ajustado antes de dividir · par
GET/POST do mesmo payload no CSIC (e por que `drop_duplicates` não resolve) · limiar
escolhido no mesmo dado em que se mede.

**Capítulo 4 (Metodologia) — deduplicação, primeira frase dele, 06/10.** Estado: rascunho.

> foram removidas 18.672 requisições duplicadas para o modelo não decorar

*Origem do número:* `logs/ingestion_csic.log` linha 62, gerado por `ingestao_csic.py`
(51.480 com payload → 32.808 depois da deduplicação por texto, path, método e rótulo).
*Pendências apontadas na revisão:* dizer o que "duplicada" significa; dizer de quanto para
quanto; trocar "para o modelo não decorar" (o problema é a cópia no teste, não decorar o
treino); falta a frase do recall inflado.

*Como chegou nela (06/10):* não sabia de onde vinham as 18.672; achou no log. Errou duas
vezes no caminho: disse que o recall serve para detectar se o modelo decorou, e depois que
o F1 serve. Corrigiu com a analogia dos dois alunos com nota 98. **Ponto a reconferir:**
nenhuma métrica medida sobre o teste vazado denuncia o vazamento.

### Como estas três frases nasceram (registro do processo)

Vale para o diário e para a próxima sessão de escrita — os erros dele são previsíveis e
todos foram corrigidos por ele mesmo, com pergunta:

1. Definiu vazamento como causa de **overfitting**. Corrigiu com a pergunta dos dois alunos
   que receberam o gabarito: o que estudou também tirou 98, logo o defeito está na
   **medição**, não no modelo.
2. Escreveu que o vazamento "deixa o recall ruim". Corrigiu para **alto** ao lembrar que a
   nota do gabarito foi 98 — o vazamento não parece erro, parece sucesso.
3. Escreveu a régua proibindo "os dados de teste". Corrigiu para **essa informação** ao
   responder que na forma 1 nenhuma linha do teste foi copiada e mesmo assim houve vazamento.

**Padrão dos erros de forma dele:** sujeito omitido, repetição da mesma palavra na mesma
frase, "a gente" no lugar da forma impessoal, e frases longas com três "que" encadeados.
A solução que funcionou para a última foi **ponto final**: uma ideia por frase.

---

### Cap. 4 Metodologia — respostas do Pedro, com as palavras dele (25/11)

Método: uma pergunta por vez no chat; a resposta entra aqui sem reescrever.

1. *De onde vieram os dados?* — "do kaggle, dataset csic 2010 de uma loja espanhola"
2. *O que tirou de 97.065 → 32.808, e por quê?* — "tirei as repetidas e as do teste para n dar overfitig o modelo decorar"
   *Revisão:* o 2º corte é "sem parâmetro" (45.585), não "do teste"; e o motivo da dedup é a cópia no teste inflar a medição (vazamento), não overfitting — o mesmo erro de 06/10.
   *Corrigido por ele, mesma sessão:* o problema da repetida no treino e no teste é "a nota que a gente mede, fica inflada".
3. *Par GET/POST do mesmo ataque em lados opostos do split?* — "a nota ficaria inflada de novo, o modelo ja viu"
4. *O que o StratifiedGroupKFold faz?* (explicado no chat antes, com a analogia dos gêmeos) — "ele divide em 5 partes os dados, eiqueta e cada parte ficar com a mesma proporcao de ataques q o total"
   *Falta:* que etiquetas iguais ficam do mesmo lado, e o porquê (o par GET/POST).

---

## 2. Conteúdo levantado, ainda por escrever (eu escrevo)

Cada item abaixo é um parágrafo que ainda não existe. A ideia está fechada; o texto não.

| # | Conteúdo | Vai para | Levantado em |
| :--- | :--- | :--- | :--- |
| 1 | `predict_proba` é fração de árvores que votou "ataque", não probabilidade calibrada — logo o limiar precisa ser escolhido, não herdado do 0,5 | Metodologia (limiar) | 13/08, revisto 19/08 |
| 2 | Uma divisão treino/teste só mede sorte; reportar média ± desvio entre folds | Metodologia (validação) | 19/08 |
| 3 | TF-IDF ajustado por fold, nunca sobre o dataset inteiro — 5 vocabulários, não 1 | Metodologia (validação) | 19/08 |
| 4 | Agrupamento por payload no split: GET e POST do mesmo ataque não podem cair em lados opostos. Dedup exata não resolve | Metodologia (validação) | 19/08 |
| 5 | Comparação `KFold` × `GroupKFold` como evidência de validação honesta — o recall cai, e a queda é o resultado | Resultados | 19/08 |
| 6 | Rodar `KFold` comum contra `StratifiedGroupKFold` agrupado por payload e mostrar o recall inflar sem o agrupamento | Resultados + Metodologia | 19/08 |
| 7 | Complementaridade das camadas: quantos ataques só a assinatura pega, quantos só o modelo pega, quantos nenhuma | Resultados (**resultado central**) | 19/08 |
| 8 | Latência por etapa do pipeline e o efeito do `n_jobs` na inferência unitária — o custo do delta | Resultados | 19/08 |
| 9 | Por que cascata e união são equivalentes em decisão, e por que a cascata existe mesmo assim (proveniência do bloqueio e custo evitado) | Desenvolvimento | 19/08 |
| 10 | **Escopo alargado** para anomalias HTTP (decisão do Pedro, falta o aval do Paulo): SQLi/XSS viram famílias; o ganho do ML (+45,6 pp) está no tampering. Definir *parameter tampering*. Exemplo dele, 25/11: "trocar o preço ou a quantidade pra valor negativo" | Cap. 1 (objetivos, introdução) + Fundamentação | 25/11 |
| 11 | **Pergunta aberta (dica de 25/11):** por que uma assinatura não pega `precio=-85`? Como o modelo percebe que é anômalo, e o que ele precisou ver no treino? **A mesma resposta explica o ponto 4 do Paulo** (o modelo do CSIC bloqueia português legítimo). Resposta: do Pedro, ainda não dada | Resultados (tampering) + Limitações + ponto 4 | 25/11 |

---

## 2b. Números da auditoria de 19/08 — reproduzidos em 06/10, **exceto a latência**

Vieram de `C:\Dev\Tcc\docs\medicoes\`, geradas pelo projeto antigo. **Regra nº 1: só entram
no artigo depois de rerodados por script deste repositório.**

**Atualização 06/10 (checkup):** rerodados aqui, com resultado idêntico:

- configurações A–D, complementaridade e recall por família:
  `python avaliacao_hibrida.py` → `docs/medicoes/avaliacao_hibrida.md`
- validação cruzada, ablação por bloco, limiar 0,650 e recall por família do modelo:
  `python treino_modelo.py` → `models/model_metadata.json`, `docs/medicoes/curva_limiar.csv`

A regra 1 está cumprida para esses números. **A regra 2 ainda não:** nenhum dos dois scripts
foi auditado. **A latência continua sem script.** No antigo foi "instrumentação direta" sem
arquivo salvo (`C:\Dev\Tcc\docs\testes_realizados.md` §2). Não citar.

**Atualização 12/11 — latência agora TEM script** (`medir_latencia.py`, medição de apoio
escrita pelo Claude → `docs/medicoes/latencia.md`). 300 payloads reais do CSIC (150/150),
modelo de `models/`, n_jobs=1, em ms:
normalização 0,02 · assinaturas 0,06 (p95 0,10) · features 4,60 (p95 5,86) ·
inferência 6,31 (p95 7,35) · **total até a decisão da camada 2: 10,99 média / 13,21 p95**.
Por HTTP, medido pelo middleware: decidido pela camada 1 0,09 ms · pela camada 2 11,16
(p95 13,04). Ida e volta no cliente: 2,06 / 13,62 ms.
**Os 31,94 ms do projeto antigo não valem mais**: eram com n_jobs=-1 e sem script. Citar
só os de 12/11, dizendo a máquina (AMD, Windows, Python 3.11) e "uma requisição por vez".

**Atualização 12/11 — normalização treino × servidor medida** (`medir_normalizacao.py` →
`docs/medicoes/normalizacao_treino_vs_servidor.md`): 99,21% dos textos mudam só na caixa,
0,06% (20) mudam além disso, **0 de 32.808 decisões trocam de lado** (in-sample).

**Atualização 25/11 — comparação entre algoritmos (objetivo 5)** (`comparar_modelos.py`, escrito
pelo Claude a pedido do Pedro → `docs/medicoes/comparacao_modelos.md`, `logs/comparar_modelos.log`).
F1 a 0,5 (5 folds): RF 0,7824 ± 0,0088 · regressão logística 0,5359 ± 0,0119 · árvore 0,7410 ± 0,0090.
ROC-AUC: 0,8880 · 0,7193 · 0,7785. No FP ≤ 1%: RF recall 59,43% / F1 0,7395; RL recall 34,17% /
F1 0,5044; **árvore não atinge FP ≤ 1% (mínimo 18,17%)**. Recall em tampering: RF 49,6% · RL 18,6%.

**Atualização 25/11 — erros da união** (`medir_erros.py`, medição de apoio → `docs/medicoes/erros.md`,
figura `docs/medicoes/matriz_confusao.png`). Matriz C: VN 18.436 · FP 184 · FN 5.707 · VP 8.481
(bate com `avaliacao_hibrida.md`). **Os 5.707 que passaram são 100% tampering** (50,4% da família);
prob. mediana 0,360. Os 184 FP: autenticar.jsp 124 · editar.jsp 29 · registro.jsp 22 · outros 9;
prob. mediana 0,730. Assinaturas: 24 regras em 6 famílias (`python assinaturas.py`).

Números novos do log do `treino_modelo.py` (06/10), ablação por bloco de features
(F1 médio ± desvio, 5 folds):
heurísticas + TF-IDF 0,7182 ± 0,0126 · só TF-IDF 0,6686 ± 0,0085 · só contexto HTTP
0,4312 ± 0,0077 · **completo 0,7824 ± 0,0088**.

Tabela 1, do log do `ingestao_csic.py` (06/10): 36.000 normais de treino · 36.000 normais
de teste · 25.065 anômalas, todas parseadas (bate com o publicado). 51.480 com payload →
**32.808 em escopo**. A queda de 51.480 para 32.808 ainda precisa ser explicada. **Explicada pelo Pedro em 12/11, de cabeça:** 97.065 → tira "as que não têm parâmetro" (45.585) → 51.480 → tira os "repetidos" (18.672) → 32.808. Números do log do `ingestao_csic.py`.

Base: CSIC 2010, 32.808 requisições em escopo (18.620 legítimas / 14.188 anômalas).
Validação `StratifiedGroupKFold(5)` agrupada por payload, TF-IDF por fold, probabilidades
out-of-fold, limiar 0,650.

| Configuração | Precisão | Recall | F1 | Taxa de FP |
| :--- | ---: | ---: | ---: | ---: |
| Camada 1 isolada (24 assinaturas) | 100,00% | 23,36% | 0,3787 | 0,00% |
| Camada 2 isolada (modelo) | 97,86% | 59,43% | 0,7395 | 0,99% |
| União / cascata | 97,88% | 59,78% | 0,7422 | 0,99% |

Complementaridade sobre os 14.188 ataques: ambas 23,0% · **só assinatura 0,3%** ·
**só modelo 36,4%** · nenhuma 40,2%.

Recall por família — **a tabela que decide a defesa**:

| Família | n | Assinaturas | Modelo | Ganho da camada 2 |
| :--- | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 11.332 | 4,0% | 49,6% | **+45,6 pp** |
| SQLi | 1.018 | 100,0% | 99,9% | +0,0 pp |
| XSS | 952 | 100,0% | 100,0% | +0,0 pp |
| CRLF Injection | 388 | 100,0% | 98,5% | +0,0 pp |
| Injeção SSI/Comando | 384 | 100,0% | 100,0% | +0,0 pp |
| Caractere de Controle/Nulo | 114 | 100,0% | 63,2% | +0,0 pp |

~~Latência do projeto antigo (300 execuções por etapa): extração de features 2,28 ms média / 2,71 ms p95 ·
inferência 28,54 ms / 30,50 ms · pipeline completo 31,94 ms / 34,33 ms. Com `n_jobs=1` a
inferência cai para 7,95 ms — 3,6×.~~ **SEM SCRIPT, NÃO CITAR.** Os números válidos são os de 12/11 (`medir_latencia.py`), acima.

**Viés a declarar junto da tabela por família:** a família é atribuída por regex, e as
assinaturas descrevem os mesmos fenômenos — o recall da camada 1 por família é otimista por
construção. Os números imunes a esse viés são os das duas primeiras tabelas, medidos contra
o rótulo real do dataset.

---

## 3. Pendências que viram parágrafo de limitações

- **Zero-day.** Palavra ausente do vocabulário do treino é ignorada pelo TF-IDF. Isso limita
  o que o modelo pode prometer sobre ataque nunca visto. A seção 1.2 da entrega parcial
  promete zero-day; ou suaviza, ou declara aqui. *(19/08)*
- **Acurácia** entra na versão final como **contraexemplo**, não como métrica de resultado.
- **Cortes de escopo declarados:** Etapa 11 em versão mínima; `datasets/SQL Injection/` e
  `datasets/XSS/` fora de escopo.

- **Ganho zero no escopo declarado.** Assinaturas pegam 100% de SQLi e XSS; a camada de ML
  acrescenta +0,0 pp nessas duas famílias. Ou o escopo alarga, ou se mede ganho sobre
  SQLi/XSS ofuscados. Decisão marcada para **10/09**. *(19/08)*
- **Objetivo específico 5 não cumprido pelo projeto antigo:** só Random Forest, sem
  comparação entre modelos diferentes. Resolver em **11/09** rodando +2 classificadores sob
  a mesma validação. *(19/08)*
- **Nenhum objetivo específico prevê a camada de assinaturas**, mas ela produz o resultado
  central. Falar com o Paulo antes da versão final.
- **O modelo do CSIC não generaliza para outro domínio, e a demo usa outro modelo.** Medido
  em 06/10 com `verificar_roteiro.py` contra `python servidor.py` (modelo do CSIC): os 4
  casos legítimos em português ("pedro.almeida", "joao.silva@email.com", um comentário,
  uma busca) foram bloqueados pela camada 2 com p = 0,88–0,98. Com o modelo demo
  (`models/demo/`, treinado nos datasets de SQLi/XSS fora de escopo) os 26 casos passam.
  Consequências: (a) o "normal" do modelo é o tráfego de **uma** aplicação; em outra, ele
  precisaria ser retreinado. (b) A demonstração ao vivo não roda o modelo cujos números
  estão no artigo. Pergunta de banca garantida. *(06/10)*
- **O modelo demo NÃO é "treinado em português".** Conferido em 12/11 com `ingestao.unificar_datasets()`:
  57.465 exemplos, 23.765 legítimos, de texto variado (e-mails, nomes, números, frases em inglês,
  endereços em espanhol). Só ~5% têm cara de português, por uma heurística grosseira. Ele não barra
  português porque viu texto legítimo **variado**, não porque viu português. O painel dizia
  "treinado em português" e foi corrigido. O README dizia o mesmo, corrigido em 25/11. O comentário do `servidor.py` (linha ~38):
  conferido em 25/11: o texto atual não diz "treinado em português" e está correto. *(12/11)*
- **O dataset de XSS da demo é sintético** (achado em 25/11). `datasets/XSS/xss_dataset.csv`
  foi gerado por `C:\Dev\Tcc\generate_xss.py`: 12 payloads XSS + 12 frases normais em
  português, sorteadas 1.000 vezes cada. A origem dos CSVs de SQLi da demo é desconhecida.
  Nenhum número da demo deve ir para o artigo. O CSIC veio do Kaggle (`ispangler`). *(25/11)*
- **Normalização diferente no treino e no servidor** (achado em 06/10). O treino usa
  `ingestao_csic.normalizar_payload`, e o `servidor.py` usa a sua própria
  `decodificador_ofuscacao`. Ou se corrige antes da defesa, ou entra aqui como limitação,
  com a medida do impacto. *(06/10)* **Medido em 12/11: 0 decisões mudam no CSIC.** Continua
  sendo limitação de engenharia (o Base64 heurístico pode alterar texto legítimo fora do CSIC). *(12/11)*
- **Comentários do código citam números sem script:** 36,6% (`servidor.py`; o medido é
  36,4%), "6,7 pontos de F1" (o log dá 6,4) e 28,54 ms. Nenhum desses vai para o artigo
  sem rerodar. *(06/10)* **Corrigidos no código em 25/11** (36,4%, 6,4 pontos, latência com script). **Correção, mesmo dia:** o 22,3% tem origem sim. O log do
  `ingestao_csic.py` mostra 5.585 ataques sem parâmetro, de 25.065 = 22,3%.
- **Uso de IA no trabalho:** descobrir a regra da Unimar e declarar o que for exigido.
  Pergunta para o Paulo. *(19/08)*

Detalhamento das pendências herdadas da entrega parcial: `estrutura-do-artigo.md` §1b.

---

## 4. Correções de texto pendentes na entrega parcial

`algoritimo` → algoritmo · `traffics analysis` → traffic analysis · ``system`s`` → system's
