# Vídeos em português — apoio ao estudo

> Levantado em 2026-08-13, ampliado em 2026-08-19. Busca real, não de memória.
> **Nenhum deles foi assistido/verificado por mim** — são pontos de partida, não currículo.

---

## Três regras antes de assistir

**1. Vídeo é passivo, e passivo dá a sensação de aprender sem aprender.**
Regra: **assiste → fecha → explica em voz alta.** Não conseguiu explicar? Assiste de novo.
É o mesmo teste de propriedade do `ROTEIRO.md`.

**2. Assista desconfiado.** Vários vão dizer que `predict_proba` é "a probabilidade" e vão
tratar acurácia como métrica de avaliação normal. Você já sabe por que os dois são
imprecisos — se pegar o vídeo errando, é sinal de que entendeu.

**3. Vocabulário.** "Revocação", "cobertura" e "recall" são **a mesma coisa**. A literatura
em português usa os três e isso confunde. **No artigo, escolher um e usar sempre o mesmo.**

---

## Métricas — Etapa 0

- [Descomplicando a Matriz de Confusão](https://www.youtube.com/watch?v=vNpD7ctJlvA) Entendi como funciona 
- [Acurácia, precisão e revocação | Matriz de confusão](https://www.youtube.com/watch?v=Edzs9FQL5k0) Nao esta disponivel
- [Definição das métricas de classificação](https://www.youtube.com/watch?v=O8hwAaMU7SM) Acuracia para testar o modelo, Precisao     denominador para VP e FP, Recall denominador para VP e FN usando quando FN é alto, F1 combina precisao e recall
- [Precisão, Revocação, Média F, Acurácia — Parte 1](https://www.youtube.com/watch?v=p33F1ovVy08) meio ruim esse video n falou nada 

## Random Forest — Etapa 0, parte 2

**Comece pelo de árvore de decisão.** Floresta sem árvore não faz sentido.

- [Árvore de decisão — Como funciona](https://www.youtube.com/watch?v=W7MfsE5av0c)
- [Como Funcionam as Árvores de Decisão e o Random Forest — Explicação Simples](https://www.youtube.com/watch?v=ZXIgblas1EI)
- [Qual a diferença entre árvore de decisão e random forest?](https://www.youtube.com/watch?v=IruwYlxdWXE)
- [Modelo Random Forest — Teoria](https://www.youtube.com/watch?v=eQep5PbvEXg)
- [Entenda o Algoritmo de Machine Learning Random Forest](https://www.youtube.com/watch?v=jBGxiu8K11o)

## Validação cruzada — Etapa 5 (a mais crítica)

- [Avaliação de Modelos Preditivos: Validação cruzada K-fold](https://www.youtube.com/watch?v=E1VAYcKnLxg)
- [Holdout × Validação Cruzada (K-Fold)](https://www.youtube.com/watch?v=8qTkdC_ccdY)
- [Validação Cruzada (Cross Validation) | Machine Learning: Fundamentos](https://www.youtube.com/watch?v=CWxaXyXZ-1A)
- [Princípios de separação de dados em treino, validação e teste](https://www.youtube.com/watch?v=R5c8S61balo)

## Ingestão do CSIC com pandas — Etapa 1 (20/08)

Você já tem Python confortável; isto é só para relembrar a API do pandas antes de amanhã.
Não precisa dos três — escolhe um.

- [Lendo e Salvando Datasets com Pandas (CSV, EXCEL e HTML)](https://www.youtube.com/watch?v=TL4NuLp3RUU)
- [Estruturas Básicas: DataFrames, Series e Manipulação de CSV — Aula 1](https://www.youtube.com/watch?v=2U9aVEuu4wM)
- [Como Ler Arquivos CSV, Excel e TXT com Python (jun/2025, o mais recente)](https://www.youtube.com/watch?v=iyRxQmHHkKE)

> Cuidado: o CSIC 2010 **não vem em CSV limpo** — vem em arquivos de requisição HTTP crua.
> Nenhum destes vídeos cobre isso. Eles servem para montar o DataFrame **depois** que você
> parseou, não para o parsing.

## TF-IDF — Etapa 4 (03/09)

- [TF-IDF (Term Frequency — Inverse Document Frequency)](https://www.youtube.com/watch?v=RVx_QYZPGaU) — os cálculos, do zero
- [Detecção de Fake News com TF-IDF](https://www.youtube.com/watch?v=AYlzNE35yXk) — **o mais parecido com o seu caso**: classificar texto em duas classes usando TF-IDF
- [Bag of Words e TF-IDF lendo os papers originais](https://www.youtube.com/watch?v=3xMbGnuQf_A)

> Assista com a pergunta da Etapa 0 na cabeça: **em que momento o autor ajusta o TF-IDF?**
> A maioria ajusta no dataset inteiro antes de dividir. Se você pegar o vídeo fazendo isso,
> você entendeu vazamento — e já tem material para a discussão do artigo.

---

## O buraco — e é no lugar mais importante

Busca dedicada a **vazamento de dados (data leakage)** em português **não retornou material
específico**. Só conteúdo sobre separar treino e teste, que é o caso mais básico.

**O conceito que mais derruba TCC de ML é o que tem menos material em português.**

As três formas que interessam a este trabalho **não estão em vídeo nenhum**:

1. TF-IDF ajustado fora do fold
2. par GET/POST do mesmo payload caindo em lados opostos do split
3. limiar calibrado sobre o mesmo dado em que se mediu

Estão no `ROTEIRO.md`, Etapa 5. Vídeo não substitui — a parte 2 da Etapa 0 continua valendo.

**O lado bom:** se material rigoroso sobre isso é raro em português, um artigo que trata
vazamento com rigor **se destaca**. É onde se ganha da média.

### Por que a busca falha (descoberto em 19/08)

Em português, **"vazamento de dados" significa incidente de segurança / LGPD**. A busca
devolve dicas de proteção de dados pessoais, não *data leakage* de Machine Learning. São
conceitos diferentes com o mesmo nome.

> **No artigo:** na primeira ocorrência, escrever **"vazamento de dados (*data leakage*)"**
> e definir na hora. Senão a banca lê LGPD.

### O único material específico encontrado — em inglês

- [Preventing Data Leakage](https://www.youtube.com/watch?v=lxcGfnyCaaU) (jun/2025) — cobre o
  conceito e por que ele destrói a integridade do modelo em silêncio
- [Using Scikit-Learn Pipelines for Data Preprocessing](https://www.youtube.com/watch?v=2_7vRKawvEU)
  — `Pipeline` é o **antídoto prático da forma 1**: ele obriga o TF-IDF a ser ajustado
  dentro de cada fold, em vez de depender de você lembrar

Nenhum dos dois cobre as formas 2 e 3 do seu projeto. Essas continuam sendo só da aula.
