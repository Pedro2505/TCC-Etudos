# A analogia do porteiro — precisão, recall e acurácia sem fórmula

> Complemento de [`etapa-00-fundamentos-parte-1.md`](etapa-00-fundamentos-parte-1.md).
> Escrito em 2026-08-13, quando a Tarefa 0 travou nos itens 3 e 4.
>
> Se a matemática confundir, **volte aqui**. Esta é a versão em português da mesma coisa.

--- 
1. Quantos ladrões ele barrou? → 40
2. Quantos clientes ele barrou por engano? → 40
3. Quantos ladrões entraram? → 10
4. Quantos clientes entraram normalmente? → 960
5. Soma → 40 + 960 = 1000
6. Divide por 1.000 → 100%
7. diferentes

## A cena

Você tem uma loja. Na porta tem um **porteiro** — ele é o seu WAF.

Hoje entraram **1.000 pessoas**:

- **950 clientes de verdade**
- **50 ladrões**

O porteiro barrou **80 pessoas**. Dessas, **40 eram ladrões mesmo**.
As outras **40 eram clientes de verdade**, barrados por engano.

---

## O porteiro erra de duas formas diferentes

| Erro | O que aconteceu | Quantos | Consequência |
| :--- | :--- | ---: | :--- |
| **Deixou o ladrão entrar** (FN) | 10 ladrões passaram | 10 | A loja é roubada |
| **Barrou o cliente certo** (FP) | 40 clientes barrados | 40 | Cliente vai embora sem comprar |

São dois erros **completamente diferentes, com consequências diferentes**.
Toda a Etapa 6 do `ROTEIRO.md` existe por causa disso.

---

## Quem na empresa sofre com cada erro?

**O chefe da segurança.** Trabalho dele: *não pode entrar ladrão*. É cobrado quando a loja
é roubada.

**O dono do produto.** Trabalho dele: *o cliente tem que conseguir comprar*. É cobrado pela
venda perdida quando o cliente é barrado na porta e vai embora.

> **As duas perguntas que resolvem o item 3 da Tarefa 0:**
> Quando o porteiro deixa passar um ladrão, **quem apanha**?
> Quando o porteiro barra um cliente, **quem apanha**?

---

## O segredo das métricas está no denominador

Toda métrica é uma divisão. A regra que resolve tudo:

> ### O denominador é o grupo de pessoas sobre quem você está falando.

### Recall = 40 ÷ 50

Denominador = 50 = **todos os ladrões que apareceram**.
Logo, o recall fala sobre **ladrões**.

> "Dos ladrões que apareceram, quantos o porteiro pegou?" → 80%

**Recall ruim significa: ladrão está entrando.**

### Precisão = 40 ÷ 80

Denominador = 80 = **todas as pessoas que o porteiro barrou**.
Logo, a precisão fala sobre **quem foi barrado**.

> "Das pessoas barradas, quantas eram ladrão de verdade?" → 50%

**Precisão ruim significa: cliente está sendo barrado.**

### Juntando

Uma métrica fala de *ladrão que passou*. A outra fala de *cliente barrado por engano*.
Cada uma dessas duas coisas faz o telefone de uma pessoa diferente tocar.

O pareamento do item 3 sai sozinho daí.

---

## O porteiro dorminhoco (item 4)

Um segundo porteiro. Esse não faz **nada** — dorme na cadeira, todo mundo entra.
Mesmo dia, mesmas 1.000 pessoas.

| Pergunta | Resposta |
| :--- | :--- |
| Barrou algum ladrão? | Não. Zero. |
| Barrou algum cliente por engano? | Não. Ele não barra ninguém. |
| Quantos ladrões passaram? | Os 50 |
| Quantos clientes entraram tranquilos? | Os 950 |

### O ponto

**Acurácia = acertos ÷ total.** E "acertar" inclui as duas coisas: barrar quem devia ser
barrado **e deixar entrar quem devia entrar**.

O porteiro dorminhoco deixou entrar 950 clientes que realmente deviam entrar.
Isso conta como **950 acertos**.

> **Faça a divisão: 950 ÷ 1.000 = ?**
> **Escreva esse número ao lado dos seus 95%.**

### O mecanismo

A acurácia dá ponto por "deixar cliente normal entrar". Como ~95% do movimento é cliente
normal, **qualquer porteiro que não atrapalhe muito já tira nota alta — mesmo sem pegar
ladrão nenhum.** A nota é dominada pela parte fácil.

É por isso que a acurácia não entra nos resultados do artigo, a não ser como contraexemplo.

---

## Os dois "40" — 4,2% contra 50%

Os mesmos 40 clientes barrados por engano aparecem em duas contas. **Denominadores
diferentes:**

| Conta | Denominador é | Pergunta que responde | Resultado | Como soa |
| :--- | :--- | :--- | ---: | :--- |
| 40 ÷ 950 | todos os clientes de verdade | "de cada 100 clientes que vieram, quantos barrei?" | **4,2%** | ótimo |
| 40 ÷ 80 | todas as pessoas que barrei | "de cada 100 barrados, quantos eram inocentes?" | **50%** | desastre |

**Os dois estão certos. Falam das mesmas 40 pessoas.**

Dizer em reunião apenas *"nosso WAF só afeta 4,2% do tráfego legítimo"* é verdade — e
esconde que **metade de tudo que ele bloqueia é gente inocente**. Ninguém mentiu; ninguém
contou a história inteira.

> Daí a regra do §0 de [`estrutura-do-artigo.md`](estrutura-do-artigo.md):
> **detecção ganha e falso positivo introduzido são reportados sempre juntos.**

---

## Checklist para fechar a Tarefa 0

- [ ] Ladrão passou → quem apanha? Cliente barrado → quem apanha?
- [ ] Item 3 refeito com o pareamento corrigido
- [ ] Item 3: nomear **as duas métricas que contam histórias opostas** e dar o veredito
- [ ] Item 4: acurácia do porteiro dorminhoco, escrita ao lado dos 95%
- [ ] A pergunta em aberto: 4,2% ou 50% — qual levar para a reunião, e por que sozinho é
      desonesto
