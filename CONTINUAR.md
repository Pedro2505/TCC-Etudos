# CONTINUAR — ponto de retomada

> **Para o Claude:** leia este arquivo, o `ROTEIRO.md` e o `diario.md` antes de responder.
> O material de orientação está em [`docs/aulas/README.md`](docs/aulas/README.md).
>
> Última atualização: **2026-08-19**, fim da sessão 2 (recuperação).

---

## Onde o Pedro está

**ETAPA 0 ENCERRADA em 19/08.** Parte 1 (métricas, 13/08), parte 2 bloco 1 (Random Forest,
13/08) e parte 2 bloco 2 (validação cruzada e vazamento, 19/08). Passou no teste de
fechamento: deu os três exemplos de vazamento de cabeça, sem consultar.

A sessão prevista para **14/08 não aconteceu** e o fim de semana também não teve estudo. A
sessão de 19/08 (quarta, fora do regime) foi de recuperação e o cronograma **não escorregou**.

Aula gravada em `docs/aulas/Etapa 00/etapa-00-fundamentos-parte-2-bloco-2.md`.
Diário do dia registrado.

### O que ele domina agora (verificado por pergunta, sem consulta)

- Matriz de confusão e as cinco métricas; por que acurácia engana
- Random Forest: árvores (não neurônios), duas aleatoriedades, `predict_proba` como placar
  de votação e não probabilidade calibrada
- K-Fold: por que uma divisão só mede sorte; média **± desvio**; previsões **out-of-fold**
- Vazamento nas três formas do projeto, e a régua que resolve as três:
  *se em produção você não teria essa informação, o treino não pode tê-la tido*
- `GroupKFold` e por que `drop_duplicates` não resolve o par GET/POST

### Erros a vigiar (recaídas registradas em 19/08)

1. **A palavra "acurácia".** Duas recaídas na mesma sessão: chamou `predict_proba` de
   acurácia, e disse "pra medir o modelo tem que fazer a acurácia". Gatilho combinado:
   toda vez que a palavra aparecer, o porteiro dorminhoco aparece junto. **Reconferir.**
2. **Escolher o resultado.** Escolheu a semente 42 "porque o F1 deu maior". Reconheceu o
   erro quando reapareceu como forma 3 de vazamento — mas a tentação é reflexo, não
   ignorância. Vai voltar na Etapa 6.
3. O "neurônios" de 13/08 **está curado** (reconferido em 19/08).

### Pergunta de banca ainda sem resposta dada por ele

> Por que forçar cada árvore a ver só uma parte das features **melhora** a floresta, se deixa
> cada árvore individualmente pior?

(Pendente desde 13/08. Cobrar numa retomada.)

## O PLANO MUDOU EM 19/08 — leia isto antes de qualquer coisa

Decisão do Pedro, com a auditoria do projeto antigo na mão: **o que decide a nota é o artigo
e a defesa**, não redigitar 1.750 linhas que já funcionam em `C:\Dev\Tcc`.

- **Todas as etapas passam a ser reaproveitadas e auditadas**, pelo protocolo de 5 passos do
  `CLAUDE.md`. A regra das "5 etapas intocáveis à mão" está **revogada**.
- **O passo 4 do protocolo — nomear a alternativa descartada — não é negociável.** É a
  única coisa que separa este caminho de chegar na banca defendendo o que não entende.
- As ~10 sessões liberadas foram para **artigo (10)** e **simulado de banca (4)**.

### A ameaça número 1 à defesa (descoberta em 19/08)

Medição do projeto antigo (`docs/medicoes/avaliacao_hibrida.md`), recall por família:

| Família | n | Assinaturas | Modelo | Ganho da camada 2 |
| :--- | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 11.332 | 4,0% | 49,6% | **+45,6 pp** |
| SQLi | 1.018 | 100,0% | 99,9% | +0,0 pp |
| XSS | 952 | 100,0% | 100,0% | +0,0 pp |
| **SQLi + XSS (escopo declarado)** | **1.970** | **100,0%** | **99,9%** | **+0,0 pp** |

> **No escopo que o artigo declara, a camada de ML acrescenta zero.** Todo o ganho está em
> *parameter tampering*, que a introdução entregue nem menciona.

Pergunta de banca fatal: *"se o seu WAF de regras já pega 100% de SQLi e XSS, para que serve
o Machine Learning num trabalho sobre SQLi e XSS?"*

Duas saídas, decisão na sessão de **10/09**, com dado na mão:

- **A — alargar o escopo declarado** para detecção de anomalias HTTP em geral. O resultado
  central vira os +45,6 pp em tampering. Custo: mexer na introdução entregue e conversar com
  o Paulo.
- **B — provar o ganho dentro do escopo atual**: construir um conjunto de SQLi/XSS
  **ofuscados** que as assinaturas não pegam e medir o recall do modelo neles. O
  `evasion_test.py` do projeto antigo é a semente, mas hoje é demonstração com 5 payloads,
  não medição. Custo: uma sessão, e o resultado pode não ser o desejado.

### Auditoria dos objetivos específicos (19/08)

| # | Objetivo específico | Situação no projeto antigo |
| :--- | :--- | :--- |
| 1 | Estudar SQLi e XSS | texto — a escrever |
| 2 | Analisar WAFs tradicionais | texto — a escrever |
| 3 | Selecionar datasets HTTP | OK — CSIC 2010, 32.808 requisições em escopo |
| 4 | Pré-processamento e features | OK — `extractor.py` |
| 5 | **Treinar e comparar diferentes modelos** | **NÃO CUMPRIDO.** Só Random Forest; B/C/D do `baseline_comparison.md` são ablação de features, todas RF. Resolver em **11/09**. |
| 6 | Middleware integrado | OK — `api.py` |
| 7 | As 6 métricas + tempo de resposta | OK — latência por etapa, p50/p95/p99, 300 execuções |
| — | "Zero-day" (seção 1.2) | **NÃO MEDIDO.** `evasion_test.py` testa ofuscação de ataque conhecido, que não é zero-day. Suavizar ou declarar em limitações. |

## Próximo passo — sessão 3, quinta 20/08

**Migração e reprodução.** Trazer o sistema para este repositório e rodar ponta a ponta.

Critério de aceite: **os números reproduzem**. Se o recall por família sair diferente do que
está em `C:\Dev\Tcc\docs\medicoes\`, descobrir por quê antes de seguir.

Fecha com a **Tabela 1 do artigo** (composição do CSIC 2010 por partição) gerada por script
**deste** repositório — e o parágrafo que a analisa. Isso também resolve a divergência dos
6,6% x 13,9% (ver `CLAUDE.md`).

### Estado da escrita (fim de 19/08)

**Seção 2.4 do artigo — 3 de 6 frases do parágrafo de vazamento**, escritas por ele. Texto e
registro do processo em `NECESSARIO.md` §1. Retomar por aí: faltam os **três exemplos
concretos** (TF-IDF fora do fold, par GET/POST, limiar), que é a parte fácil — ele deu os
três de cabeça em 19/08. Depois os parágrafos de classificação, Random Forest e validação.

**As subseções 2.1, 2.2 e 2.3 estão travadas por referências**, não por escrita. Sem
fichamento não adianta sentar para escrever — vira `[CITAR]` a cada linha.

> **O gargalo real do trabalho hoje é o fichamento de 8–12 referências.** Ele trava o
> capítulo 2 (três quartos) e o capítulo 3 inteiro. Não cabe nas sessões de quinta e sexta;
> é leitura de terça à noite, duas por noite. **Cobrar isso dele toda sessão.**

**Método de escrita que funcionou** (usar de novo): ele responde **falando**, depois
transforma em frase. Uma ideia por frase, ponto final em vez de "que" encadeado. Checklist
dos erros de forma dele em `NECESSARIO.md` §1.

Antes de começar: trocar o Notepad pelo VS Code.

## Calendário revisado (22 sessões, 20/08 a 30/10)

| Sessões | Datas | O quê |
| :--- | :--- | :--- |
| 3–4 | 20, 21/08 | Migração e reprodução ponta a ponta · **Tabela 1** |
| 5–8 | 27, 28/08 · 03, 04/09 | **Auditoria** das 11 peças, protocolo de 5 passos, ~3 por sessão |
| 9 | 10/09 | **Resolver o escopo** — medir SQLi/XSS ofuscados, decidir A ou B |
| 10 | 11/09 | **Cumprir o objetivo 5** — +2 classificadores sob a mesma validação |
| 11–16 | 17, 18, 24, 25/09 · 01, 02/10 | **Artigo** — capítulos 2 a 7, um por sessão |
| 17–18 | 08, 09/10 | Consolidação: tabelas, figuras, referências ABNT |
| 19–20 | 15, 16/10 | Revisão final. **Texto fechado em 16/10.** |
| 21–24 | 22, 23, 29, 30/10 | **Simulados de banca e ensaio da defesa** |

**Fora das sessões:** fichamento de 8–12 referências para *Trabalhos relacionados*.
Continua sendo o único item que não cabe nas quintas e sextas — e agora é o gargalo do
capítulo 3.

## Como treinar a defesa (definido em 19/08)

Em ordem de eficácia. Os dois primeiros são diários, os dois últimos são de sessão:

1. **Explicar em voz alta, sem olhar, com cronômetro.** 3 minutos por peça. Mental não vale
   — mental engana.
2. **A pergunta "por que não Y?"** para cada decisão. É o passo 4 do protocolo e é o que
   separa quem fez de quem viu ser feito.
3. **Simulado de banca com interrupção.** 20 minutos ao fim de cada etapa auditada, sem
   consulta. Ele precisa **pedir** — até 19/08 nunca pediu nenhum.
4. **Gravar o áudio explicando e ouvir depois.** Desconfortável e eficaz: as hesitações
   aparecem.

## Decisões travadas (não reabrir)

| Decisão | Detalhe |
| :--- | :--- |
| **Formato** | **Artigo** ABNT NBR 6022, mínimo 20 páginas — não é monografia. Isso substitui a Etapa 12 do `ROTEIRO.md`. Ver `docs/aulas/estrutura-do-artigo.md`. |
| **Prazos** | Entrega **outubro/2026** · defesa **novembro/2026**. Texto fechado em **16/10**. |
| **Regime** | Quintas e sextas. 24 sessões até 31/10. Ver `docs/aulas/cronograma-ate-outubro.md`. |
| **Enquadramento** | A camada de ML é **acrescentada** ao WAF de assinaturas, **não o substitui**. O resultado do trabalho é o **delta** (detecção ganha × FP introduzido), não o F1 do modelo. Ver `estrutura-do-artigo.md` §0. |
| **Cortes** | Etapa 11 (SHAP) em versão mínima; `datasets/SQL Injection/` e `datasets/XSS/` fora de escopo. |
| **Reaproveitamento do projeto antigo** (13/08) | **Frontend:** reaproveitado inteiro — não está nas 13 etapas, não é o trabalho. **Middleware (Etapa 9):** esqueleto reaproveitado, mas três pontos são dele (ver abaixo). Todo o resto continua sendo feito à mão. |
| **Intocáveis** | Etapas 2, 3, 5, 7 e 10 — feitas à mão, sem consultar o projeto antigo antes da própria tentativa. |

### Modo de execução por etapa (fechado em 13/08)

**Critério:** onde o valor está na *decisão* → à mão. Onde o valor está no *código
funcionando* → pega pronto do projeto antigo.

| Etapa | Modo | Sessões | Linhas (referência do antigo) |
| :--- | :--- | :--: | ---: |
| 1 — Ingestão | tentativa curta, depois **gabarito** | 1 | 715 |
| **2 — Normalização** | **à mão** | 1 | ~80 |
| **3 — Rotulagem** | **à mão** + amostra de 50 anotada | 1 | ~160 |
| **4 — Features** | **à mão** | 2 | 203 |
| **5 — Validação honesta** | **à mão** | **3** | ~300 |
| **6 — Limiar** | **à mão** | 1 | ~80 |
| **7 — Ablação e baseline** | **à mão** | 2 | 235 |
| 8 — Assinaturas | regras dele, gabarito depois | 1 | 282 |
| 9 — Middleware | **reaproveita** + 3 pontos abaixo | ~2h | 296 |
| **10 — Avaliação híbrida** | **à mão** | **3** | 404 |
| 11 — Explicabilidade | **reaproveita**, versão mínima | 1 | 70 |
| Frontend | **reaproveita inteiro** | 0 | — |
| Artigo | escrita concentrada | 4 | — |

**Total à mão: ~1.750 linhas em 14 sessões (~125 linhas/sessão).** O tempo vai em pensar,
não em digitar. O que foi economizado nas etapas 1, 9 e 11 foi realocado para **5 e 10**,
que ganharam uma sessão cada — são as que decidem a nota.

**Método para as peças reaproveitadas** (1 hora por peça, não uma sessão):
roda e vê funcionando → lê uma vez → **fecha e explica em voz alta** → identifica os pontos
de defesa. Se travar no passo 3, volta ao 2.

### Os três pontos do middleware que o Pedro precisa dominar

Mesmo com o código reaproveitado, estes têm peso de defesa e são responsabilidade dele:

1. **A chamada da normalização** — saber apontar a linha onde a função da Etapa 2 é
   importada. É a resposta para *"sua normalização é a mesma no treino e em produção?"*
   (training/serving skew).
2. **A reindexação das colunas** pelo metadata, e a decisão de **falhar alto** se faltar
   coluna em vez de prever errado.
3. **A latência** — mediana e p95 medidas por ele, com script dele. Vira a **Tabela 7** do
   artigo e é o "custo" do delta.

Custo estimado: ~2 horas, não as 2 sessões previstas. Libera 24 e 25/09.

### A demo é instrumento de defesa

A banca não lê código, mas **vê o sistema rodando**. Roteiro de demo (30 s), que é a prova
visual da tese: requisição com `' OR 1=1--` → bloqueio com o nome da regra (`SQLI-001`) →
payload ofuscado que a assinatura não pega e o modelo pega. É a célula "somente o modelo"
da matriz de concordância acontecendo ao vivo.

## Regras de sessão

1. **Toda sessão fecha com uma tabela ou figura do artigo produzida** — e o parágrafo que a
   analisa, escrito na mesma sessão. (A Etapa 0 é a única exceção: não produz elemento.)
2. **O Claude escreve o `diario.md`.** Combinado em 13/08 — o Pedro perdeu texto duas vezes
   por não salvar no Notepad. Ele responde no chat *o que travou* e *a alternativa
   descartada*; o Claude formata e grava. O resto do conteúdo continua sendo dele.

---

## A entrega parcial já feita

`TCC, 1 entrega.docx` na raiz — **1.088 palavras (~3–4 páginas ABNT)**, já entregue ao
orientador (Paulo Rogerio de Mello Cardoso). Contém resumo/abstract estruturados e o
capítulo 1 completo (contextualização, problema, justificativa, objetivos, organização).

**A estrutura de 7 capítulos declarada na seção 1.5 é a estrutura oficial do artigo.**
Não inventar outra. Está transcrita em `docs/aulas/estrutura-do-artigo.md` §1.

Pendências herdadas dela (detalhadas em `estrutura-do-artigo.md` §1b):

- **RISCO ALTO** — **nenhum objetivo específico prevê a camada de assinaturas.** Os sete
  descrevem uma camada só (features → modelo → middleware). A matriz de concordância
  (Etapa 10, resultado central) só existe com a camada 1. Acrescentar um objetivo do tipo
  *"implementar uma camada de detecção por assinaturas e avaliar a contribuição incremental
  da camada de ML sobre ela"* — **falar com o orientador antes da versão final**.
- **RISCO ALTO** — o objetivo específico 5 promete *"treinar e comparar diferentes modelos"*.
  O plano treina só Random Forest. Recomendação: **cumprir** (rodar +2 classificadores sob a
  mesma validação, ~meia sessão) em vez de reescrever o objetivo.
- Acurácia está na lista de métricas — na versão final tem que entrar como **contraexemplo**.
- "Zero-day" é prometido na seção 1.2 e **não será medido** — suavizar ou declarar em
  limitações.
- A pergunta de pesquisa é de construção ("como desenvolver..."); refinar para a formulação
  do delta.
- Correções: "algoritimo" → algoritmo; "traffics analysis" → traffic analysis; "system\`s".

## Pendências abertas

- [ ] **Data exata da entrega em outubro** (o plano assume ~31/10). Se for antes do dia 20,
      as 4 sessões de folga somem e a Etapa 11 sai inteira.
- [ ] **As 20 páginas incluem referências e pré-textuais?**
- [ ] **Trabalhos relacionados:** 8–12 referências fichadas, fora do horário de sessão.
      Ainda não começou.
- [ ] Trocar o Notepad por VS Code antes da Etapa 1. **Vence hoje** — a Etapa 1 é amanhã.
- [x] **Git resolvido em 19/08.** Repositório **privado** em
      `https://github.com/Pedro2505/TCC-Etudos.git`, branch `main`, primeiro commit enviado.
      Fora do versionamento: CSIC bruto (54 MB) e os datasets SQLi/XSS fora de escopo.
      **Novo hábito: commitar ao fim de cada sessão.**

## Frases já prontas para o artigo

Saíram desta sessão e vão quase inteiras para o texto:

> "A acurácia não distingue um detector que funciona de um que não faz nada. No cenário
> testado, um classificador que libera todo o tráfego obtém os mesmos 95% do detector
> avaliado."

> "Não faz sentido trocar algo que já funciona por algo novo. Substituir significaria abrir
> mão de um detector com precisão altíssima e proveniência auditável em troca de um que erra
> mais em tráfego legítimo e responde 'probabilidade 0,87' quando o analista pergunta por
> que bloqueou."
