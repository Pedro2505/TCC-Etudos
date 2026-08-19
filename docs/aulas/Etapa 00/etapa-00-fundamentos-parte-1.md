# Etapa 0 — Parte 1: como se mede um detector

> Aula de orientação. Material de estudo — não é código do TCC.
> Data: 2026-08-13

Antes de treinar qualquer coisa você precisa saber **ler a régua**. Se treinar primeiro e
aprender a métrica depois, vai passar semanas otimizando o número errado.

Esta parte 1 cobre o que a Tarefa 0 exige. Random Forest, validação cruzada e vazamento de
dados vêm na parte 2, depois da entrega da tarefa.

---

## 1. O que é classificação binária supervisionada

Imagine um fiscal de aduana em treinamento. Você mostra a ele 10 mil malas **já abertas**, e
para cada uma diz: "essa tinha contrabando", "essa não tinha". Ele não decora as malas — ele
aprende a associar *sinais observáveis* (peso, formato, densidade no raio-X, rota de origem)
ao desfecho. Depois você fecha as malas novas e pede o palpite.

Três palavras que vão aparecer o TCC inteiro:

- **Rótulo (label):** a verdade conhecida. Aqui: `0` = requisição legítima, `1` = anômala.
  Vem do dataset, não do modelo.
- **Feature:** um sinal observável, expresso como **número**. "Comprimento da URL = 87".
  "Quantidade de aspas simples = 3".
- **Aprender:** ajustar parâmetros internos para minimizar o erro sobre os exemplos
  rotulados. Nada mais místico que isso.

E o ponto que trava todo mundo: **o modelo não lê texto**. `' OR 1=1--` para o sklearn não é
uma string com significado — é nada. Ele precisa que você transforme isso num vetor de
números. Essa tradução é a **Etapa 4**, e é onde mora quase todo o seu conhecimento de
segurança. O Random Forest é commodity; a representação é sua.

---

## 2. A matriz de confusão

Toda avaliação de detector nasce de cruzar duas perguntas:
**o que era verdade** × **o que eu disse**.

|                  | Modelo disse: ATAQUE      | Modelo disse: NORMAL      |
| :--------------- | :------------------------ | :------------------------ |
| **Era ataque**   | VP — verdadeiro positivo  | **FN** — falso negativo   |
| **Era normal**   | **FP** — falso positivo   | VN — verdadeiro negativo  |

Traduzindo para a aplicação, que é o que importa:

- **VP:** ataque bloqueado. O sistema funcionou.
- **FN:** ataque que passou. O SQLi executou no banco. → **falha de segurança**
- **FP:** cliente legítimo bloqueado. Não consegue comprar, liga para o suporte.
  → **falha de negócio**
- **VN:** tráfego normal que passou. O caso comum, 95% do tempo.

Grave isto: **FN e FP não custam a mesma coisa, e não custam a mesma coisa para as mesmas
pessoas.** O time de segurança teme o FN. O time de produto teme o FP. Na prática, é o FP
que faz alguém desligar o WAF às duas da tarde de uma Black Friday — e um WAF desligado tem
recall zero.

Essa assimetria é a razão de existir a **Etapa 6** inteira.

---

## 3. As três métricas — e a pergunta que cada uma responde

Não decore fórmula. Decore **o denominador**, porque é ele que define a pergunta.

| Métrica | Fórmula | Denominador é... | Pergunta que responde |
| :--- | :--- | :--- | :--- |
| **Precisão** | VP / (VP + FP) | tudo que eu bloqueei | "Quando eu bloqueio, quantas vezes estou certo?" |
| **Recall** | VP / (VP + FN) | todos os ataques que existiam | "Dos ataques que existem, quantos eu peguei?" |
| **Taxa de FP (FPR)** | FP / (FP + VN) | todo o tráfego legítimo | "Do tráfego legítimo, quanto eu atrapalhei?" |

Agora o detalhe que vale a defesa inteira, e que quase ninguém sabe:

> **Recall e FPR olham cada um para uma única coluna da verdade — então não mudam se a
> proporção de ataques mudar. Precisão mistura as duas linhas — então ela muda.**

Consequência prática: o dataset de teste tem ~43% de ataques. Um site real tem talvez 0,1%.
**O mesmo modelo, com o mesmo FPR e o mesmo recall, teria precisão muito pior em produção** —
porque o volume de tráfego legítimo é mil vezes maior, e mesmo uma fração minúscula dele gera
mais falsos positivos do que existem ataques.

Não precisa medir isso agora. Precisa **saber dizer isso** quando a banca elogiar a precisão.
Elogio de banca costuma ser armadilha.

---

## 4. F1: por que média *harmônica*

```
F1 = 2 · (P · R) / (P + R)
```

É a média harmônica de precisão e recall, e a escolha da harmônica é proposital: ela
**pune o desequilíbrio**.

Um detector que bloqueia tudo tem recall 100% e precisão baixíssima. A média aritmética o
premiaria; a harmônica o afunda, porque é dominada pelo menor dos dois valores. F1 alto exige
que os dois lados sejam decentes ao mesmo tempo.

Mas cuidado — e essa crítica **você** deve fazer no seu texto antes que a banca faça: F1
trata precisão e recall como igualmente importantes. Acabamos de estabelecer que num WAF eles
não são. Então F1 é um resumo conveniente, **não o objetivo**. O objetivo real está na
Etapa 6.

---

## 5. Por que acurácia é inútil aqui

```
Acurácia = (VP + VN) / total
```

Parece a métrica óbvia e é a mais enganosa que existe em dados desbalanceados.

Um detector que **libera absolutamente tudo** — zero linhas de lógica, um `return False` —
num tráfego com 5% de ataques acerta 95% das vezes. Acurácia 95%. Recall 0%. Não detecta
nada e ainda assim ganha no papel da maioria dos modelos mal treinados.

Por isso a acurácia não aparece nos seus resultados a não ser como contraexemplo. E por isso
você precisa saber, **com os números do seu dataset**, qual acurácia teria o classificador
burro. Esse número dá para calcular na Etapa 1, quando o parser rodar.

---

# Tarefa 0 — no papel, sem computador

**Cenário:** 1.000 requisições, das quais 50 são ataques. Seu detector bloqueia 80
requisições, e 40 delas eram ataques de verdade.

## Entregar

1. **A matriz de confusão completa** — as quatro células. Derive-as; os três números do
   enunciado bastam.
   *Comece perguntando:* das 80 bloqueadas, 40 eram ataque — então as outras 40 eram o quê? 
   E dos 50 ataques, 40 foram pegos — então os outros 10 viraram o quê?

2. **Precisão, recall, taxa de FP, F1 e acurácia** — cada um com a conta escrita.

3. **Este detector presta?** Justifique usando **duas métricas que apontem para lados
   opostos**. Diga qual das duas você levaria para o dono do produto e qual levaria para o
   time de segurança. R: o dono do produto eu levaria o recall, e para o time de segurança precisao 

4. **Por que a acurácia desse detector é enganosa** — compare com a acurácia do detector
   burro que libera tudo, no mesmo cenário. R: diz q acertou 95% das 50 q era ataques passaram 10 e bloquearam 40 eu diria q ele é ruim pois ele deixa 10 ataques passarem 

## Critério de aceite

Mandar a resolução escrita (foto do papel ou digitada) e explicar o item 4 com suas
palavras. Se a conta bater mas a explicação do item 4 for vaga, **a etapa não fecha**.

## Armadilha proposital

Existe uma métrica cujo valor, neste cenário, pode ser calculado por dois caminhos diferentes
e que muita gente confunde com outra. Se você notar qual é e por que a confusão é fácil,
me diga — é meio ponto de defesa.

---

## Depois da entrega

Dizer **"terminei a Tarefa 0, revisa"**. Aí vem a **parte 2 da Etapa 0**:

- Random Forest em nível conceitual (árvore → floresta → voto; o que `predict_proba`
  realmente devolve)
- Desbalanceamento de classe e por que ele distorce o limiar padrão de 0,5
- Validação cruzada K-Fold e por que uma única divisão treino/teste tem sorte embutida
- **Vazamento de dados** — o conceito mais importante da etapa; parar só quando conseguir
  dar três exemplos diferentes

## Perguntas de banca guardadas para esta etapa

> "Seu sistema tem 97,88% de precisão. Isso é bom?"

A resposta certa **não é "sim"**. É perguntar de volta qual a taxa de ataques na base — veja
a seção 3.
