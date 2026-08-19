# Cronograma — TCC até 31/10/2026

> Definido em 2026-08-13. Regime: **quintas e sextas**, dia cheio (~6h efetivas).
> Total disponível: **24 sessões** (12 quintas + 12 sextas) em 11,3 semanas.

## A conta

| | |
| :--- | :--- |
| Sessões até 31/10 | 24 |
| Horas disponíveis (a 6h/sessão) | ~144h |
| Cronograma original do `ROTEIRO.md` | 14 semanas (~168h) |
| Sessões realistas (descontando imprevistos) | ~20 |

**Veredito: é viável, mas sem folga.** Só funciona com as três condições abaixo.

---

## Condição 1 — escrever em paralelo, desde a primeira sessão

O `ROTEIRO.md` reserva 3 semanas de texto no fim. **Essas 3 semanas não existem neste
prazo.**

> **Regra: toda sessão termina com 40 minutos escrevendo a seção correspondente do artigo.**
>
> Formulação concreta (ver `estrutura-do-artigo.md`): **toda sessão fecha respondendo
> "qual tabela ou figura do artigo eu produzi hoje?"** — e o parágrafo que analisa essa
> tabela é escrito na mesma sessão. Se a resposta for "nenhuma", a sessão não fechou.

Terminou a Etapa 5? Escreve a seção de metodologia sobre validação enquanto a decisão está
fresca. Não é rascunho — é o texto.

Não é sacrifício, é atalho: escrever sobre o que acabou de fazer é muito mais rápido que
reconstruir em novembro o que se pensou em setembro. E é o teste de propriedade em forma
escrita.

---

## Condição 2 — cortar o que tem peso "médio"

O `ROTEIRO.md` marca o peso de cada etapa na defesa. Cortes decididos:

| Etapa | Peso | Decisão |
| :--- | :--- | :--- |
| **11 — Explicabilidade (SHAP)** | médio | Versão mínima: importância de features + **um** laudo comentado. Se apertar, vira "trabalhos futuros" declarado. |
| **9 — Middleware** | médio | Funcional e medido (mediana/p95). Sem experimentação de otimização de latência. |
| `datasets/SQL Injection/`, `datasets/XSS/` | — | **Fora de escopo neste prazo.** Se sobrar tempo, viram validação externa. |
| **2, 3, 5, 7, 10** | crítico | **Intocáveis.** Cortar aqui é cortar o TCC. |

> Corte declarado no capítulo de limitações **soma** ponto.
> Corte escondido é o que a banca encontra.

---

## Condição 3 — o calendário

> **Revisado em 13/08** após a decisão de reaproveitar parte do projeto antigo.
> Modo de execução de cada etapa (à mão × gabarito × reaproveita): ver `CONTINUAR.md`.

| Sessões | Data | Etapa |
| :--- | :--- | :--- |
| 1–2 | 13, 14/08 | **0** — fundamentos de ML + montagem do ambiente |
| 3 | 20/08 | **1** — ingestão (tentativa curta, depois gabarito) |
| 4 | 21/08 | **2** — normalização · *à mão* |
| 5 | 27/08 | **3** — rotulagem + amostra de 50 · *à mão* |
| 6–7 | 28/08, 03/09 | **4** — features · *à mão* |
| 8–10 | 04, 10, 11/09 | **5** — validação honesta · *à mão* ← **não economize** |
| 11 | 17/09 | **6** — calibração do limiar · *à mão* |
| 12–13 | 18, 24/09 | **7** — ablação e baseline · *à mão* |
| 14 | 25/09 | **8** assinaturas · **9** middleware (~2h, reaproveitado) |
| 15–17 | 01, 02, 08/10 | **10** — avaliação híbrida · *à mão* ← **resultado central** |
| 18 | 09/10 | **11** mínima (reaproveitada) · consolidação do texto |
| 19–20 | 15, 16/10 | Artigo — resultados, discussão, limitações, conclusão |

**Fora das sessões (terças/noites):** leitura e fichamento de 8–12 referências para a seção
de *Trabalhos relacionados*. Ver `estrutura-do-artigo.md`. Não cabe nas quintas e sextas.
| 21–24 | 22, 23, 29, 30/10 | **Folga + revisão + ensaio da defesa** |

As quatro últimas sessões são **intencionalmente vazias**. São o que faz o plano sobreviver
ao contato com a realidade. O ensaio de defesa não é opcional quando o objetivo é nota
máxima.

---

## O que realmente decide a nota

A banca não vai rodar o código. Vai ler o capítulo de metodologia e fazer quatro perguntas.

Nota máxima vem de **explicar por que cada escolha foi feita** — e isso está inteiro nas
etapas 5, 7 e 10, e no `diario.md`. Não está em ter SHAP.

## A vantagem que não pode virar armadilha

A versão antiga em `C:\Dev\Tcc` funciona, e o `ROTEIRO.md` já lista onde ela deu errado.
Este não é um caminho no escuro — é um caminho mapeado. É por isso que 24 sessões podem
bastar.

**Mas:** abrir o projeto antigo *antes* da própria tentativa transforma a vantagem em
armadilha. Você reconhece a resposta sem ter construído o raciocínio, e descobre isso na
frente da banca.

---

## Prazos confirmados (2026-08-13)

- **Entrega da monografia: outubro/2026**
- **Defesa: novembro/2026**

O calendário acima está **válido como está**. Consequências:

1. O texto tem que estar **fechado na sessão 20 (16/10)**. As sessões 21–24 são revisão e
   folga — não são tempo de escrita.
2. **Novembro é só defesa.** Nada de código em novembro. O mês inteiro é ensaio, slides e
   as perguntas de banca do `ROTEIRO.md`.
3. Depois da entrega, o trabalho muda de natureza: não se melhora mais o sistema, treina-se
   a explicação dele. **O que estiver no texto em 16/10 é o que vai ser defendido.**

### Ainda falta confirmar

**A data exata da entrega em outubro.** O plano assume final do mês (~31/10). Se a entrega
for antes do dia 20, as 4 sessões de folga desaparecem e os cortes da Condição 2 passam de
recomendados a obrigatórios — a Etapa 11 sai inteira, para "trabalhos futuros".

### Novembro — o mês da defesa

| O quê | Insumo |
| :--- | :--- |
| Slides | resultado central = matriz de concordância (Etapa 10) |
| Ensaio cronometrado, em voz alta | teste de propriedade de cada módulo |
| Simulação de banca | as perguntas de banca de cada etapa do `ROTEIRO.md` |
| Defesa dos números | `diario.md` — cada número com o script que o gerou |
