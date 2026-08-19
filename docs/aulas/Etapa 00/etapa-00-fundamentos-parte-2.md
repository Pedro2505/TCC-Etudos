# Etapa 0 — Parte 2, bloco 1: Random Forest e o limiar

> Aula de 2026-08-13. Complemento de
> [`etapa-00-fundamentos-parte-1.md`](etapa-00-fundamentos-parte-1.md).
>
> O **bloco 2** (validação cruzada K-Fold e vazamento de dados) fica para a sessão de 14/08.

---

## 1. Árvore de decisão: um jogo de vinte perguntas

Uma árvore de decisão é um fluxograma de perguntas sim/não:

```
o texto tem mais de 3 aspas simples?
├─ sim → tem a sequência "--"?
│         ├─ sim → ATAQUE
│         └─ não → tem "select"?
│                   ├─ sim → ATAQUE
│                   └─ não → NORMAL
└─ não → o comprimento passa de 200?
          ├─ sim → ATAQUE
          └─ não → NORMAL
```

Você não escreve essas perguntas. **O algoritmo as descobre** — testa cada feature em cada
ponto de corte e escolhe a que melhor separa ataque de normal no treino. Depois repete
dentro de cada ramo.

### O problema de uma árvore só

Ela não sabe quando parar. Se deixar, cria perguntas cada vez mais específicas até separar
perfeitamente os dados de treino — **inclusive as coincidências**. Uma requisição normal que
por acaso tinha 4 aspas vira regra.

Isso é **overfitting**: decorou o gabarito em vez de aprender o assunto. Acerta quase 100%
no treino e vai mal em dado novo. É o equivalente a decorar respostas para a banca.

---

## 2. Floresta: um comitê em vez de um especialista

Random Forest treina **centenas** de árvores, e cada uma vê uma versão diferente do
problema. Duas fontes de aleatoriedade — daí o "Random":

1. **Cada árvore vê um sorteio das linhas** (amostra com repetição, não o dataset inteiro).
2. **Em cada pergunta, a árvore só pode escolher entre um sorteio das features.**

A segunda parece burrice deliberada — e é, de propósito. Se todas pudessem ver tudo,
descobririam a mesma pergunta "melhor" no topo e você teria 300 cópias da mesma árvore.
**Um comitê de clones não vale mais que uma pessoa.**

Forçar informação parcial é o que gera desacordo, e é o desacordo que faz o voto valer.
Cada árvore erra de um jeito diferente; erros diferentes se cancelam no voto, e o sinal
verdadeiro — que todas veem — se acumula.

> ⚠ **Random Forest = árvores. Rede neural = neurônios.** Não se misturam. RF não tem
> neurônios, nem pesos, nem camadas.

---

## 3. `predict_proba` — a pergunta de banca escondida

Você chama `predict_proba` e recebe **0,87**.

**É a fração de árvores que votou "ataque".** 261 de 300 → 0,87. Um **placar de votação**.

**Não é** "87% de chance de ser ataque".

### Como provar isso em dez segundos

Se fosse mesmo probabilidade, teria que valer: *de 100 requisições que receberam 0,87, umas
87 seriam ataque de verdade*. Isso tem nome — **calibração** — e quase nunca bate. O número
**ordena bem** (0,9 é mais suspeito que 0,6) mas a **escala não corresponde** à frequência
real.

### Por que não corresponde — a analogia do júri

Doze jurados que estudaram no mesmo lugar, leram as mesmas provas e têm o mesmo viés podem
votar 12 a 0 e estarem todos errados. **O placar mede o quanto os jurados concordam entre
si, não o quanto a acusação é verdadeira.**

Com as árvores é idêntico: todas foram treinadas no mesmo dataset. A concordância delas é
propriedade **da floresta**, não do mundo.

### A resposta pronta para a banca

> "Não. 0,87 é a fração de árvores que votou 'ataque' — placar de votação, não probabilidade
> calibrada. Serve para ordenar requisições por suspeita, e é por isso que eu calibro um
> limiar em vez de usar o 0,5 padrão. Para afirmar 'chance de 87%' eu precisaria ter medido
> a calibração, e eu não medi."

A última linha é a **regra nº 1 do projeto** aplicada: não se diz o que não se mediu.

---

## 4. Por que 0,5 é um default e não uma escolha

Se `predict_proba` é fração de votos, usar limiar 0,5 significa exatamente:
**"bloqueio quando a maioria das árvores concorda"**. Por que a maioria seria o ponto certo?
Não há razão. É só o número que estava lá.

### O desbalanceamento piora isso

O veredito de uma árvore numa folha é simplesmente **qual classe é maioria naquela folha**.

Com 95% de tráfego normal no treino, quase toda folha tem maioria normal — não por culpa das
perguntas, mas porque há 19 vezes mais tráfego normal para distribuir. Para uma folha virar
"ataque", precisa concentrar ataques de forma muito forte. **Na dúvida, a folha é normal.**

E "na dúvida, chuta normal" é ótima estratégia para a árvore: acerta 95% das vezes.

> É **exatamente o argumento do porteiro dorminhoco** da parte 1. A mesma pressão estatística
> que fazia a acurácia premiar quem não faz nada faz cada árvore preferir dizer "normal".

**Analogia:** um médico numa cidade onde 95% das tosses são resfriado comum classifica toda
tosse ambígua como resfriado. Acerta quase sempre — e perde o caso grave atípico.

### O efeito no placar

| Ataque | Onde cai | Placar |
| :--- | :--- | :--- |
| Óbvio (`' OR 1=1--` cru) | folhas fortemente dominadas por ataque | ~0,95 |
| Sutil ou ofuscado | regiões ambíguas, muitas folhas com maioria normal | ~0,40 |

O segundo é um ataque real. Com limiar 0,5 ele **passa** — não por ser inofensivo, mas
porque a composição do treino puxou a votação para baixo.

**Por isso a Etapa 6 existe.** Você vai varrer a curva inteira e provavelmente escolher um
limiar **abaixo** de 0,5, compensando esse viés — e vai pagar em falso positivo, dentro de um
orçamento que você define.

E é por isso que a pergunta de banca é *"de onde veio esse 0,650?"*. A resposta boa não é
"testei e deu bom". É: *"da varredura sobre as probabilidades out-of-fold, escolhendo o
melhor F1 dentro do orçamento de falso positivo que a operação tolera."*

---

## Nota de proveniência

O **0,87**, as **300 árvores** e as **261** são exemplo didático **inventado** — não são
medidas deste projeto.

Já o **0,650** de limiar e os **97,88%** de precisão estão no `ROTEIRO.md` (perguntas de
banca das Etapas 6 e 0) e vieram do projeto antigo. Quando o modelo novo rodar, os números
serão outros — e cada um terá script.

---

## Perguntas de banca deste bloco

1. Por que forçar cada árvore a ver só uma parte das features **melhora** a floresta, se
   deixa cada árvore individualmente pior?
2. O modelo devolve 0,87. "Então é 87% de chance de ser ataque?" — o que você responde?
3. Por que um dataset com 95% de tráfego normal empurra os placares de ataque para baixo?

*(A 1 continua sem resposta dada por ele — retomar na próxima sessão.)*
