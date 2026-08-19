# Diário de laboratório

Uma entrada por sessão de trabalho. Este arquivo é o insumo bruto do capítulo de
metodologia da monografia — e é o que vai responder, daqui a seis meses, "por que eu
escolhi isso?".

Escreva mesmo quando a sessão foi ruim. Principalmente quando foi ruim: o que quebrou e
por quê é mais valioso que o que funcionou.

## Modelo de entrada

```
## AAAA-MM-DD — Etapa N

**O que eu tentei:**

**O que quebrou:**

**Decisão que eu tomei (e a alternativa que eu descartei):**

**O que eu medi:** (número + comando que o gerou)

**Dúvida em aberto:**
```

---

## 2026-08-12 — Etapa 0 (montagem)

**O que eu tentei:** montei o repositório e li o ROTEIRO inteiro.

**Próximo passo:** fundamentos de ML — classificação binária, matriz de confusão,
precisão/recall/F1, vazamento de dados. Depois, a Tarefa 0 no papel.

---

## 2026-08-13 — Etapa 0 (parte 1: métricas)

**O que eu tentei:**
Fiz matriz de confusão e metricas no papel.

**O que quebrou:**
Foram dois lugares que travei: o pareamento das métricas com os stakeholders, e a confusão
entre os dois cenários no item 4. n estava percebendo que acuracia era ruim, q mesmo em um
cenario q passa tudo e um cenario q tem 95% de acuracia os 2 tem os mesmos 95% de acuracia.

**Decisão que eu tomei (e a alternativa que eu descartei):**

1. **Formato:** artigo ABNT, mínimo 20 páginas. Entrega em outubro, defesa em novembro.

2. **Enquadramento:** a camada de ML é **acrescentada** ao WAF de assinaturas, não o
   substitui. Isso muda a pergunta de pesquisa e muda o que as Etapas 7 e 10 vão medir.
   - *Alternativa descartada:* **substituir** o WAF de assinaturas por um detector baseado
     só em ML — caminho comum na literatura sobre CSIC 2010, que treina um classificador e
     reporta o F1 dele como se fosse o WAF inteiro.
   - *Por que descartei:* não faz sentido trocar algo que já funciona por algo novo; é
     melhor somar. Substituir significaria abrir mão de um detector com precisão altíssima
     e proveniência auditável (a regra que disparou tem nome) em troca de um que erra mais
     em tráfego legítimo e responde "probabilidade 0,87" quando o analista pergunta por que
     bloqueou.

3. **Cortes de escopo:** Etapa 11 em versão mínima; datasets de SQLi/XSS fora do escopo
   neste prazo.

**O que eu medi:**

Cenário fictício da Tarefa 0 — 1.000 requisições, 50 ataques, 80 bloqueios, 40 deles
corretos. Matriz: VP=40, FP=40, FN=10, VN=910.

| Métrica | Conta | Valor |
| :--- | :--- | ---: |
| Acurácia | (40+910)/1000 | 95% |
| Precisão | 40/80 | 50% |
| Recall | 40/50 | 80% |
| F1 | 2·(0,5·0,8)/(0,5+0,8) | 61,5% |
| Taxa de FP | 40/950 | 4,2% |

Origem: calculado à mão, no papel. Foto em `docs/aulas/tarefa-00-itens-1-2.jpeg`.

Comparação que fechou a tarefa: um detector que **libera tudo** obtém VP=0, FP=0, FN=50,
VN=950 — acurácia **95%**, a mesma do detector avaliado.

**Dúvida em aberto:**
Nenhuma.

---

## 2026-08-19 — Etapa 0 (parte 2, bloco 2: validação cruzada e vazamento)

Sessão de recuperação. A sessão prevista para 14/08 não aconteceu e o fim de semana também
não teve estudo — seis dias sem contato com o material.

**O que eu tentei:**
Fechar a Etapa 0. Primeiro uma reconferência do bloco 1 (Random Forest), depois validação
cruzada K-Fold e as três formas de vazamento de dados. Tudo por pergunta e resposta, sem
código. Aula gravada em
`docs/aulas/Etapa 00/etapa-00-fundamentos-parte-2-bloco-2.md`.

**O que quebrou:**

1. **`predict_proba` virou "acurácia do modelo".** Seis dias depois de ter derivado sozinho
   que 0,87 = 261/300 árvores, respondi que 0,87 era acurácia. Só reconstruí depois de
   perceber que acurácia precisa de um conjunto com gabarito e o `predict_proba` recebe
   **uma** requisição.
2. **Recaída na acurácia.** Ao explicar por que um F1 de uma divisão só mede sorte, eu disse
   "pra medir o modelo tem que fazer a acurácia" — exatamente o oposto do que eu mesmo
   escrevi no `NECESSARIO.md` na semana passada. Gatilho combinado para não repetir: toda
   vez que a palavra "acurácia" sair, lembrar do porteiro dorminhoco.
3. **Escolhi a semente 42 porque o F1 deu maior.** Cometi ao vivo o erro que a Etapa 5
   existe para impedir. Serviu: quando chegou a forma 3 de vazamento (escolher o limiar
   olhando o teste), reconheci que era o mesmo erro.
4. **Achei que `drop_duplicates` resolvia o par GET/POST.** Não resolve — as duas linhas não
   são idênticas. E depois errei de novo dizendo que "tanto faz" em qual bloco cada uma cai,
   cinco mensagens depois de ter dito que o modelo "reconhece o payload que já viu".

**O que eu acertei sem ajuda:**
Projetei o K-Fold antes de saber o nome ("separo os que já foram e tiro do sorteio").
Reconstruí sozinho o argumento de por que o placar das árvores não é probabilidade: todas
treinaram no mesmo dataset, erram do mesmo jeito, e o placar mede a concordância delas entre
si. Corrigi a ordem do TF-IDF (divide primeiro, ajusta só no treino) e deduzi que são 5
tabelas de raridade, uma por fold.

**Decisão que eu tomei (e a alternativa que eu descartei):**
Recuperar a Etapa 0 hoje (quarta, fora do regime de quinta/sexta) em vez de emendar com a
Etapa 1 amanhã. *Alternativa descartada:* começar a ingestão com o vazamento ainda por
aprender — o que plantaria o erro nas Etapas 1 a 4 e transformaria a Etapa 5 em retrabalho.

**O que eu medi:**
Nada. A Etapa 0 é a única que não produz tabela nem figura, por definição — todos os números
usados na aula (0,94 / 0,89 / 300 árvores / 0,65) são exemplos didáticos inventados, não
medidas deste projeto.

**Teste de fechamento (critério de 13/08 — três exemplos de vazamento, de cabeça):**

1. TF-IDF no dataset inteiro antes de dividir
2. GET e POST do mesmo payload em blocos diferentes
3. Escolher o limiar olhando o teste

Passou. **Etapa 0 encerrada.**

**Dúvida em aberto:**
Nenhuma registrada. Próximo passo: Etapa 1 — ingestão do CSIC 2010 (20/08).
