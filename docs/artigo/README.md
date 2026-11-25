# docs/artigo — escrever o artigo longe do PC

> Montado em **13/11/2026** para o fim de semana sem computador (sex 13 → seg 16/11).
> Tudo aqui dá pra abrir pelo navegador, no GitHub, em qualquer máquina.
> **Este arquivo não tem texto do artigo.** Ele diz *onde está* cada material. A redação é sua.

---

## Antes de começar, na lan house

- O repositório é **privado**. Entre no GitHub numa **janela anônima** e **saia da conta**
  antes de ir embora. Não marque "lembrar senha".
- **Não salve o rascunho só no PC da lan house.** Escreva no Google Docs (ou no Word online),
  ou mande o arquivo para o seu e-mail ao fim de cada sessão. Você já perdeu texto duas vezes.
- Os `.docx` desta pasta se baixam pelo botão **"Download raw"** na página de cada arquivo.

## Os arquivos desta pasta

| Arquivo | Para quê |
| :--- | :--- |
| `TCC Modelo.docx` | O modelo ABNT da Unimar. **Comece o arquivo do artigo a partir dele**, para herdar a formatação. |
| `TCC, 1 entrega.docx` | A 1ª entrega: resumo + capítulo 1. A estrutura de 7 capítulos da seção 1.5 é a oficial. |

## Onde está cada coisa que você vai precisar

| Preciso de… | Abra |
| :--- | :--- |
| **Todos os fatos num lugar só: dataset, bibliotecas, parâmetros, resultados** | [`FICHA-TECNICA.md`](FICHA-TECNICA.md) |
| **O que o Paulo pediu em 25/11, ponto por ponto, com onde está cada coisa** | [`PEDIDOS-DO-PAULO.md`](PEDIDOS-DO-PAULO.md) |
| **Os números, com o script que gerou cada um** | [`NECESSARIO.md`](../../NECESSARIO.md) §2b |
| As suas frases já prontas (palavras suas) | [`NECESSARIO.md`](../../NECESSARIO.md) §1 |
| Conceitos e decisões a escrever, com o capítulo de destino | [`NECESSARIO.md`](../../NECESSARIO.md) §2 |
| O que vai para limitações | [`NECESSARIO.md`](../../NECESSARIO.md) §3 |
| Correções pendentes no capítulo 1 | [`NECESSARIO.md`](../../NECESSARIO.md) §4 e [`estrutura-do-artigo.md`](../aulas/estrutura-do-artigo.md) §1b |
| Estrutura dos capítulos e orçamento de páginas | [`estrutura-do-artigo.md`](../aulas/estrutura-do-artigo.md) §1 |
| Lista de tabelas e figuras do artigo | [`estrutura-do-artigo.md`](../aulas/estrutura-do-artigo.md) §2 |
| Regras do modelo: Quadro × Tabela, citação, referências | [`estrutura-do-artigo.md`](../aulas/estrutura-do-artigo.md) §3b e §4 |
| As tabelas de resultado, como saíram dos scripts | [`docs/medicoes/`](../medicoes/) (`avaliacao_hibrida.md`, `latencia.md`, `teste_falso_positivo*.md`, `recall_por_familia.csv`) |
| A saída de console de cada rodada (prova dos números) | [`logs/`](../../logs/) |
| A figura do SHAP | [`docs/shap_explain_report.png`](../shap_explain_report.png) |
| O que você já explicou ao Paulo, com as suas palavras | [`texto-sistema-respostas.md`](../aulas/texto-sistema-respostas.md) |
| Como o sistema funciona, passo a passo | [`como-usar-o-sistema.md`](../aulas/como-usar-o-sistema.md) e o [`README.md`](../../README.md) da raiz |
| Conceitos de ML (métricas, Random Forest, validação cruzada, vazamento) | [`docs/aulas/Etapa 00/`](../aulas/Etapa%2000/) |
| Plano dia a dia e decisões já tomadas | [`CONTINUAR.md`](../../CONTINUAR.md), bloco do topo |

## O que dá pra fazer sem PC (e o que não dá)

**Dá** — é escrita, e é o que pesa na nota:

- **Cap. 4 Metodologia:** dataset, Tab. 1 (97.065 → 51.480 → 32.808, a sua explicação está
  no `NECESSARIO.md` §2b), validação agrupada, limiar.
- **Cap. 6 Resultados:** as tabelas já estão em `docs/medicoes/`; o recall por família é o
  resultado central.
- **Cap. 3 Trabalhos relacionados:** fichar referências (Google Acadêmico funciona na lan house).
- **Cap. 2 Fundamentação** e as correções do cap. 1.
- A **anotação manual** da amostra de famílias ([`amostra_familias_50.txt`](../medicoes/amostra_familias_50.txt)):
  dá pra fazer no papel, linha por linha.

**Não dá** — fica para segunda, 16/11:

- **Auditoria das peças** (o passo 1 do protocolo é rodar). Pode escrever o capítulo antes;
  marque no rascunho os trechos que dependem de uma peça ainda não auditada.
- **Objetivo 5** (treinar outros classificadores): precisa rodar.
- Qualquer número que **não** esteja no `NECESSARIO.md` §2b. Se precisar de um, escreva
  `[MEDIR]` no lugar e siga em frente. Não cite de memória.

## As três regras continuam valendo

1. Todo número citado tem um script que o gerou.
2. Nada entra no artigo sem auditoria.
3. Etapa só fecha com a alternativa descartada, dita por você, gravada no diário.

Quando voltar ao PC: cole no chat o que escreveu, e a sessão começa pela revisão.
