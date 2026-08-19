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

## Próximo passo — Etapa 1: ingestão do CSIC 2010 (sessão 3, quinta 20/08)

Modo: **tentativa curta, depois gabarito** (decidido em 13/08 — o valor da Etapa 1 está no
código funcionando, não na decisão).

Fecha com a **Tabela 1 do artigo** — composição do CSIC 2010 por partição — e o parágrafo
que a analisa, escrito na mesma sessão.

Antes de começar: trocar o Notepad pelo VS Code. (O `git init` já foi feito em 19/08.)

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
