# Etapa 0 — Parte 2, bloco 2: validação cruzada e vazamento de dados

> Aula de 2026-08-19 (sessão de recuperação — a sessão de 14/08 não aconteceu).
> Fecha a Etapa 0. Continuação de
> [`etapa-00-fundamentos-parte-2.md`](etapa-00-fundamentos-parte-2.md).
>
> Quase tudo aqui foi **derivado pelo Pedro em perguntas de uma palavra**, não exposto.
> O texto abaixo é o registro do raciocínio, não uma aula lida.

---

## A. Por que uma divisão treino/teste não serve

61.000 requisições do CSIC. Separa 80/20, treina, mede: **F1 = 0,94**.
Embaralha com outra semente, separa outros 80/20, mede de novo: **F1 = 0,89**.

O número mudou porque **outras requisições caíram no teste**, e umas são mais difíceis que
outras.

### A armadilha, e ela foi cometida ao vivo

Perguntado qual dos dois números vai no artigo, a resposta foi **0,94**. Motivo declarado:
*"porque o F1 deu maior"*.

Isso é escolher o resultado. Se o critério de escolha da divisão é o número que ela produz,
o 0,94 mede **sorte no embaralhamento**, não o modelo.

> Esta é a mesma estrutura da **forma 3 de vazamento** (seção C). Reconhecer que os dois são
> o mesmo erro foi o que destravou aquela parte.

### A saída: várias divisões

Cinco rodadas → cinco números → média. Mas a média sozinha joga fora o essencial:

| | Rodadas | Média |
| :--- | :--- | ---: |
| **A** | 0,94 · 0,89 · 0,92 · 0,90 · 0,93 | 0,916 |
| **B** | 0,99 · 0,71 · 0,98 · 0,75 · 0,95 | 0,916 |

Média idêntica, confiança oposta. O que separa os dois é o **desvio padrão** — o quanto os
valores se espalham. No artigo escreve-se `0,916 ± 0,02`, nunca `0,916` sozinho.

O que o cenário B diz, na frase dele: *"o modelo pegou dados diferentes e caiu de 0,99 pra
0,71"* — ou seja, **o desempenho depende de qual pedaço do dataset ele recebeu**. Não dá pra
prometer 0,92 a ninguém.

> **Escorregão a vigiar:** ao explicar por que 0,94 mede sorte, ele disse *"pra medir o
> modelo tem que fazer a acurácia"* — desfazendo a parte 1 inteira. Corrigido na hora
> voltando ao detector que libera tudo (95% de acurácia, zero detecção).
> **Gatilho combinado: toda vez que a palavra "acurácia" aparecer, o porteiro dorminhoco
> aparece junto.**

### Do sorteio repetido ao K-Fold

Com 5 sorteios aleatórios de 80/20, uma requisição específica pode ser testada 3 vezes ou
nenhuma. Cobertura torta e desperdício.

Pergunta feita: *"como você organiza as 5 divisões pra garantir que toda requisição seja
testada exatamente uma vez?"*
Resposta dele: **"separo os que já foram e tiro do sorteio."** Isso **é** o K-Fold.

| Rodada | Teste | Treino |
| :--- | :--- | :--- |
| 1 | bloco 1 | 2, 3, 4, 5 |
| 2 | bloco 2 | 1, 3, 4, 5 |
| 3 | bloco 3 | 1, 2, 4, 5 |
| 4 | bloco 4 | 1, 2, 3, 5 |
| 5 | bloco 5 | 1, 2, 3, 4 |

Cada linha é testada **exatamente uma vez**, sempre por um modelo que não a viu no treino.

**Subproduto:** no fim, existe uma nota de suspeita para **toda** linha do dataset, cada uma
produzida por um modelo que não a conhecia. São as **previsões out-of-fold (OOF)**. Elas
resolvem a forma 3 de vazamento.

---

## B. Vazamento de dados

**Definição:** qualquer informação sobre o conjunto de teste que chega ao treino. O número
medido fica alto e **não se sustenta em produção**.

**Analogia que grudou:** estudar a matéria e tirar 85 × receber o gabarito na véspera e
tirar 98. A 98 mede acesso ao gabarito, não conhecimento — e não se repete numa prova nova.

### A régua que resolve as três formas

> **Se em produção você não teria essa informação, o treino não pode tê-la tido.**

Teste prático: chega agora uma requisição que ninguém nunca viu. Quando você treinou, semana
passada, você tinha alguma informação sobre ela? Não. Então o treino não pode ter tido
nenhuma.

---

## C. As três formas que atacam este projeto

### Forma 1 — a estatística calculada cedo demais

O TF-IDF precisa saber **quão rara é cada palavra**, e monta essa tabela varrendo um conjunto
de requisições.

Ordem errada: carregar as 61.000 → rodar TF-IDF nas 61.000 → **depois** dividir.
A tabela de raridade foi calculada com as linhas de teste dentro.

Ordem certa (dele): **divide primeiro, TF-IDF só no treino.**

Consequência que quase todo mundo esquece: cada rodada tem um treino diferente, logo o
K-Fold de 5 folds produz **5 tabelas de raridade**, não uma. Construir uma só e reusar traz
o vazamento de volta pela porta dos fundos.

**Pergunta de banca — palavra nunca vista.** Se `xp_cmdshell` aparece no teste mas não está
no vocabulário do treino, o TF-IDF a **ignora**. Ele não pode acrescentá-la — acrescentar
significaria mudar a tabela por causa do dado de teste, que é exatamente o vazamento que
acabou de ser eliminado.

Isso **não é defeito do experimento**: é o que vai acontecer em produção quando chegar um
payload com vocabulário novo. O experimento está sendo honesto ao reproduzir a limitação.

> **Consequência para o artigo:** limita o que se pode prometer sobre zero-day. A seção 1.2
> da entrega parcial promete zero-day. Ou suaviza, ou declara em limitações.

### Forma 2 — o par GET/POST do mesmo payload

O CSIC 2010 foi gerado automaticamente: cada payload de ataque aparece em **duas** versões.

```
GET  /tienda1/publico/anadir.jsp?id=2%27+OR+%271%27%3D%271
POST /tienda1/publico/anadir.jsp     (corpo: id=2' OR '1'='1)
```

Mesmo payload, linhas **não idênticas**. Embaralhando, uma cai no treino e a outra no teste.
Quando o modelo acerta a do teste, nas palavras dele: *"reconheceu, já tinha visto o payload
no treino"*. Não generalizou.

Estrago: o recall reportado fica inflado por **memória de payload** — e é justamente ataque
novo que o WAF precisa pegar.

**Por que `drop_duplicates` não resolve:** as duas linhas não são idênticas. Deduplicação
exata não as vê como par.

**O que resolve:** agrupar. O que as duas compartilham é o **payload**; linhas do mesmo
payload têm que cair no **mesmo bloco**. Ferramenta: **`GroupKFold`**, recebendo uma coluna
de grupo.

Duas obrigações que nascem daí:

1. **A coluna de grupo não existe no CSIC.** Extrair e normalizar o payload para usar como
   chave é trabalho das Etapas 2 e 3 — é *por isso* que elas existem.
2. **O número vai cair.** Recall com `GroupKFold` < recall com `KFold` comum. Não é
   regressão: é o número deixando de mentir.

> **Vira elemento do artigo:** rodar as duas versões e mostrar a diferença. A maioria dos
> trabalhos sobre CSIC 2010 não faz isso.

### Forma 3 — escolher e medir no mesmo dado

Varredura de limiares:

| Limiar | F1 |
| :--- | ---: |
| 0,30 | 0,88 |
| 0,50 | 0,91 |
| **0,65** | **0,94** |
| 0,80 | 0,90 |

Escolher 0,65 olhando o teste e depois reportar 0,94 **medido no mesmo teste** é o mesmo erro
da semente 42: usar o resultado para decidir e reportar esse resultado como desempenho
esperado. O 0,94 é o **melhor de quatro tentativas**.

**O que resolve:** varrer os limiares sobre as **probabilidades out-of-fold**. Na frase dele:
*"o limiar é escolhido em dado que o modelo não viu"*.

---

## Teste de fechamento

Critério definido em 13/08: o bloco só fecha com **três exemplos diferentes de vazamento**,
de cabeça. Dados em 19/08, sem consulta:

1. TF-IDF no dataset inteiro antes de dividir
2. GET e POST do mesmo payload em blocos diferentes
3. Escolher o limiar olhando o teste

**Etapa 0 encerrada.**

---

## Perguntas de banca deste bloco

1. Por que você reporta `± desvio` e não só a média entre os folds?
2. Seu recall caiu de 0,94 para 0,88 quando você trocou `KFold` por `GroupKFold`. Por que
   isso é um resultado melhor e não pior?
3. `drop_duplicates` não resolveu o problema dos pares GET/POST. Por quê?
4. De onde veio o seu limiar? (A resposta ruim é "testei e deu bom".)
5. Um payload com uma palavra que não existia no treino chega em produção. O que o TF-IDF
   faz com ela, e o que isso significa para a sua afirmação sobre zero-day?
