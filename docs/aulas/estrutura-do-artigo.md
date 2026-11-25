# Estrutura do artigo — mínimo 20 páginas

> Definido em 2026-08-13. Formato: **artigo científico** (não monografia).
> Entrega: outubro/2026 · Defesa: novembro/2026.
> **Substitui a Etapa 12 do `ROTEIRO.md`**, que descrevia estrutura de monografia.

---

## 0. O enunciado da contribuição (definido em 2026-08-13)

**A camada de ML não substitui o WAF de assinaturas — ela é acrescentada a ele.**

A pergunta de pesquisa, portanto, não é *"meu modelo detecta ataques?"* (já respondida por
muitos trabalhos), e sim:

> **"Dado um WAF de assinaturas já em operação, quanto de detecção adicional uma camada de
> ML acrescenta — e a que custo?"**

### O que isso obriga

| Etapa | Consequência |
| :--- | :--- |
| **7 — baseline** | O regex deixa de ser "adversário burro" e vira **o proxy do WAF que já existe**. A comparação que responde ao trabalho é *só assinaturas* × *assinaturas + ML*. **O resultado é o delta**, não o F1 do modelo. |
| **10 — matriz de concordância** | A célula **"somente o modelo"** é a medida direta da contribuição: os ataques que o WAF atual deixa passar e a nova camada pega. |
| **6 — limiar** | O orçamento de falso positivo é **todo** da camada nova. A camada 1 consome ~zero. |
| **9 — latência** | A camada nova roda em ~99% do tráfego (tudo que a camada 1 liberou). Medir mediana e p95 não é opcional. |

### A regra do delta

> **Detecção ganha e falso positivo introduzido são reportados sempre juntos.**
> Um sem o outro é propaganda, não resultado.

### Pergunta de banca decorrente

> "O WAF de assinaturas praticamente não gera falso positivo. Sua camada só pode piorar
> isso. Quanto de tráfego legítimo você passou a bloquear para ganhar essa detecção a mais?"

Pergunta justa, com resposta — desde que os dois lados do delta tenham sido medidos.

### Se o delta for pequeno

A conclusão honesta é *"a camada agrega pouco neste dataset"*. Um artigo que diz isso com
método correto vale mais que um que esconde. O método é o que está sendo avaliado.

---

## 1. Estrutura e orçamento de páginas

> **Esta é a estrutura que o Pedro já declarou na seção 1.5 da entrega parcial
> (`docs/artigo/TCC, 1 entrega.docx`), e que já está com o orientador. Não inventar outra.**

| Seção | Conteúdo | Alvo | Estado |
| :--- | :--- | ---: | :--- |
| Resumo + Abstract + palavras-chave | formato estruturado (Objetivo/Metodologia/Resultados/Conclusão) | ~0,5 | **feito** |
| **1. Introdução** | contextualização, problema, justificativa, objetivos, organização | 1,5–2 | **feito** |
| **2. Fundamentação teórica** | segurança web, ataques HTTP, WAFs, fundamentos de ML | 2 | a fazer |
| **3. Trabalhos relacionados** | 8–12 referências, com a diferença para o seu trabalho | 1,5–2 | a fazer |
| **4. Metodologia** | dataset, normalização, features, validação, limiar | 4–5 | a fazer |
| **5. Desenvolvimento** | o middleware, o treinamento, a arquitetura em cascata | 2–3 | a fazer |
| **6. Resultados** | as tabelas e figuras da seção 2 deste arquivo, com análise | 4–5 | a fazer |
| **7. Conclusão, limitações e trabalhos futuros** | o que os números provam e o que **não** provam | 2 | a fazer |
| Referências | | 1–1,5 | a fazer |

**Já escrito: ~1.088 palavras (≈3–4 páginas).** Faltam ~16 páginas.

---

## 1b. Pendências herdadas da entrega parcial

Levantadas em 2026-08-13 ao reler o `docs/artigo/TCC, 1 entrega.docx`.

### RISCO ALTO — nenhum objetivo específico prevê a camada de assinaturas

Os sete objetivos específicos descrevem **uma camada só**: features → modelo → middleware.
O resumo confirma (*"o algoritmo mais adequado será integrado a um middleware"*).

Mas o `ROTEIRO.md` constrói um WAF de **duas** camadas, e o resultado central do trabalho —
a **matriz de concordância** (Etapa 10) — só existe se a camada 1 existir. Sem ela não há
célula "somente o modelo", e sem essa célula não há delta (§0).

O objetivo 2 (*"analisar o funcionamento... dos WAFs tradicionais"*) é **analisar**, não
implementar. Não cobre as Etapas 8 e 10.

**Consequência:** a contribuição real do trabalho não está declarada em nenhum objetivo.

**Correção recomendada — acrescentar um objetivo específico:**

> *"Implementar uma camada de detecção por assinaturas e avaliar a contribuição incremental
> da camada de aprendizado de máquina sobre ela."*

**Conversar com o orientador (Paulo Rogerio) antes da versão final.** Refinar objetivo entre
a entrega parcial e a final é normal; chegar à banca com um resultado que nenhum objetivo
previu, não.

### Sobre reaproveitar o middleware do projeto antigo

Não conflita com o objetivo 6 (*"implementar... um middleware"*). O código é do próprio
Pedro, do mesmo trabalho em versão anterior — é o projeto continuando, não atalho. A
exigência é saber explicá-lo: ver os três pontos de domínio no `CONTINUAR.md`.

### RISCO ALTO — objetivo específico 5

> *"Treinar e comparar diferentes modelos de Machine Learning voltados para classificação"*
> (repetido no resumo: *"modelos preditivos serão treinados e comparados"*)

O plano atual treina **um** modelo (Random Forest). A ablação compara *conjuntos de
features*, não *algoritmos*. A banca abre os objetivos específicos e confere um a um.

**Decisão recomendada: cumprir.** Depois que a Etapa 5 estiver pronta, rodar mais dois
classificadores (ex.: regressão logística e árvore de decisão) sob a **mesma validação** —
é trocar o estimador e rodar de novo. Custo estimado: meia sessão. Gera uma tabela a mais.

*Alternativa:* reescrever o objetivo para "avaliar a contribuição de diferentes conjuntos de
features e comparar com um baseline por assinaturas". Mais barato, menos forte.

### Acurácia na lista de métricas

Aparece no resumo e no objetivo específico 7. Na versão final ela precisa entrar
**declaradamente como contraexemplo** (com a demonstração dos dois detectores de 95%), não
como métrica de avaliação legítima — senão contradiz o que ele vai defender.

### "Zero-day" na seção 1.2

O experimento é sobre CSIC 2010, com ataques conhecidos. Detecção de zero-day **não será
medida**. Suavizar a promessa na introdução **ou** declarar explicitamente no capítulo de
limitações.

### A pergunta de pesquisa está fraca

Atual: *"como desenvolver um middleware capaz de analisar requisições HTTP em tempo real e
classificá-las como legítimas ou anômalas utilizando Machine Learning?"* — é pergunta de
construção; responde-se com "construí".

Refinar para a formulação do §0 deste arquivo: **quanto de detecção adicional a camada de ML
acrescenta a um WAF de assinaturas, e a que custo em falso positivo e latência?**

### RISCO ALTO — nenhuma citação no texto inteiro

As 1.088 palavras não têm **uma única** referência autor-data. Afirmações como *"grande
parte dos WAFs tradicionais fundamenta sua operação em regras estáticas"*, *"o Machine
Learning surge como uma alternativa promissora"* e *"a rigidez dessas regras frequentemente
resulta na geração de falsos positivos"* são plausíveis, mas lidas como opinião.

Em ABNT, introdução sem citação é sinal vermelho imediato.

**Correção mais barata do projeto:** as 8–12 referências dos *Trabalhos relacionados*
resolvem isso de uma vez — cada uma dessas frases vira `(AUTOR, ano)`.

### Contradição entre a seção 1.2 e os resultados esperados

A seção 1.2 apresenta **dois** problemas dos WAFs de assinatura:

1. falham contra ataque novo ou ofuscado → **falso negativo**
2. a rigidez gera falsos positivos → **falso positivo**

E propõe ML como resposta aos dois. **Mas a camada de ML só resolve o (1); ela piora o (2)** —
acrescentar FP a um sistema que quase não tinha é exatamente o custo do delta (§0).

Se a banca cruzar o parágrafo 1.2 com a tabela de resultados, a contradição aparece.

**Correção:** reformular o problema (2) como **restrição de projeto** — o FP dos WAFs
tradicionais é o que *limita o orçamento* disponível para a nova camada — e não como algo
que o trabalho promete resolver.

### Falta a delimitação de escopo

Não há nenhum parágrafo dizendo **o que o trabalho não faz**: outros tipos de ataque, tráfego
de produção, tráfego cifrado, zero-day.

O `ROTEIRO.md` (Etapa 12) insiste nisso na primeira página. Limite declarado com precisão
desarma a pergunta; limite descoberto pela banca vira falha.

### Tempo verbal

Tudo em futuro (*"serão treinados"*, *"será baseada"*) — correto para entrega parcial. A
versão final tem que virar **passado, com números no lugar das promessas**. Conferir que não
sobrou frase órfã no futuro: isso denuncia texto remendado.

### Especificidade — a introdução ainda serve para qualquer TCC do tema

Não aparecem: CSIC 2010, Random Forest, a arquitetura em duas camadas, o fato de SQLi+XSS
serem 13,9% das anomalias do dataset (corrigido em 25/11; o 6,6% antigo estava errado), o delta. A contribuição real do trabalho ainda não está
escrita em lugar nenhum. Normal numa entrega parcial; **é o que separa nota boa de nota
máxima na versão final.**

### Correções de texto

- Resumo: "algoritimo" → **algoritmo**
- Abstract: "traffics analysis" → **traffic analysis**
- Abstract: "The system\`s" → apóstrofo correto (**system's**)

### O que já está certo e não se mexe

A entrega parcial **já declara** que o ML não substitui o WAF tradicional (seção 1.1) e fala
em "camada complementar" (resumo). O enquadramento do §0 não é mudança de rumo — é a
formalização do que já estava escrito, e já está registrado com o orientador.

### A regra de proporção

> **Resultados tem que ser a seção mais longa.** Fundamentação inflada com resultados
> curtos é o que denuncia trabalho sem experimento.

Nunca encher linguiça na fundamentação para chegar às 20 páginas. O volume vem dos
elementos gráficos da seção 5 e da análise em volta deles.

---

## 2. Inventário de elementos gráficos

**12 elementos.** Cada um nasce de uma etapa do `ROTEIRO.md`. Com a análise em volta de
cada um, as 20 páginas se preenchem honestamente.

> **Revisado em 2026-08-19** aplicando a distinção Quadro × Tabela do `TCC Modelo.docx`
> (§3b). "Features por bloco" é conteúdo textual → virou **Quadro 1**, e as tabelas
> seguintes foram renumeradas. As duas séries são independentes.

| # | Elemento | Tipo | Etapa |
| :--- | :--- | :--- | :--- |
| Tab. 1 | Composição do CSIC 2010 por partição | numérico | 1 |
| Tab. 2 | Distribuição das famílias de anomalia + concordância da amostra de 50 | numérico | 3 |
| **Quadro 1** | **Features por bloco** | **textual** | 4 |
| Tab. 3 | Validação cruzada — média ± desvio entre folds | numérico | 5 |
| Fig. 2 | Curva limiar × FPR / recall / precisão | gráfico | 6 |
| Tab. 4 | **Ablação e baseline regex** | numérico | 7 |
| Tab. 5 | Camada 1 (assinaturas) isolada | numérico | 8 |
| Fig. 1 | Arquitetura da cascata | diagrama | 9 |
| Tab. 6 | Latência — mediana e p95 por camada | numérico | 9 |
| **Tab. 7** | **Matriz de concordância** ← *resultado central* | numérico | 10 |
| Tab. 8 | Recall **por família**, por configuração | numérico | 10 |
| Fig. 3 | Laudo de explicabilidade | imagem | 11 |

**Candidato a Quadro 2, ainda não decidido** (levantado em 19/08): as **24 regras de
assinatura** da camada 1 — nome da regra, o que casa, exemplo. É conteúdo textual puro, e
responde à pergunta de banca *"quais são as suas assinaturas?"* sem gastar página de
resultado. Decidir na Etapa 8.

### Regra de sessão (a partir de 2026-08-13)

> **Toda sessão fecha respondendo: "qual tabela ou figura do artigo eu produzi hoje?"**
> Se a resposta for "nenhuma", a sessão não fechou.

Isso substitui a regra dos 40 minutos de escrita por algo mais concreto: a escrita passa a
ter alvo. Produziu a tabela → escreve o parágrafo que a analisa, na hora.

---

## 3. Trabalhos relacionados — fora do horário de sessão

A seção 2 é **trabalho novo**, que não existe no `ROTEIRO.md`, e não cabe nas quintas e
sextas sem roubar tempo de experimento.

**Solução: ler artigo não é trabalho de sessão.** É o que se faz numa terça à noite.

### Meta

**8 a 12 referências**, fichadas em uma linha cada:

| Referência | O que fizeram | Dataset | Resultado | **Em que meu trabalho difere** |
| :--- | :--- | :--- | :--- | :--- |

A última coluna é a seção 2 inteira já escrita.

### Por onde começar

Pelos artigos que usam **CSIC 2010** — com eles a comparação é número contra número.

### A lacuna a procurar (e provavelmente encontrar)

Muito artigo sobre CSIC 2010 reporta **F1 global sem separar família de ataque**. Como
SQLi + XSS são apenas 13,9% das anomalias do dataset (79,9% é *parameter tampering*; `avaliacao_hibrida.py`), esses
trabalhos reportam uma métrica que mede majoritariamente tampering.

Se você encontrar isso — **é a sua lacuna**, e vira o argumento de contribuição da
introdução. É um dos parágrafos mais fortes que o artigo pode ter.

---

## 3b. Regras do `TCC Modelo.docx` (lidas em 2026-08-19)

O modelo da Unimar está na raiz do repositório. **Ele manda mais que qualquer combinado
deste arquivo.** O que ele exige, e que não estava sendo seguido:

### Numeração de seções

`2 SEÇÃO 2` · `2.1 Subseção 2.1` — número, espaço, título. Seção em maiúsculas e negrito,
subseção em negrito com inicial maiúscula.

### Quadro × Tabela — são coisas diferentes, com numerações independentes

| | **Quadro** | **Tabela** |
| :--- | :--- | :--- |
| Conteúdo | explicações e conteúdo **textual** | resumo de conteúdo **numérico** |
| Bordas | **fechadas** — grade completa | **laterais abertas** — só três linhas horizontais: topo, sob o cabeçalho, base |
| Chamada no texto | "Quadro 1", "Quadro 2"… | "Tabela 1", "Tabela 2"… |

Sempre com inicial maiúscula seguida da numeração, e **sempre referidos no texto**.
As duas séries são numeradas **separadamente**.

### Título, fonte e alinhamento (vale para Quadro, Tabela e Figura)

- **Título acima**, centralizado: `**Quadro 1** – Exemplo de quadro`. Só o rótulo em negrito;
  travessão e título em texto normal.
- **Fonte abaixo**, centralizada: `**Fonte:** Elaboração própria`. Só "Fonte:" em negrito.
  Quando não for sua: `Fonte: Universidade de Marília (2026)`.
- O elemento inteiro **centralizado no texto**.

### Citações — as formas que o modelo exemplifica

Indiretas:

| Autores | Forma |
| :--- | :--- |
| um | `(Sobrenome, 2026)` |
| dois ou três | `(Sobrenome 1; Sobrenome 2; Sobrenome 3, 2026)` |
| mais de três | `(Sobrenome et al., 2026)` |
| autor no corpo do texto | `De acordo com Autor (2026, p. 11)` |

Diretas:

- **até 3 linhas** — entre aspas, no corpo do parágrafo, com `(Sobrenome, 2026, p. 10)`.
- **4 linhas ou mais** — pula uma linha, **recuo de 4 cm no parágrafo inteiro, fonte
  tamanho 11, sem aspas**, com a citação antes ou depois.

### Referências

- **Somente as citadas no texto.** Referência não citada é erro, não é bônus.
- Padrão das diretrizes da revista **RDBCI**. O modelo traz os seis formatos: livro, evento,
  periódico, periódico online, monografia/dissertação/tese, publicação online.
- Ferramenta indicada pelo próprio modelo: **MORE UFSC** — https://more.ufsc.br/
  **Usar durante o fichamento**, gerando a entrada na hora, em vez de deixar as 12 para o fim.

### Resumo e palavras-chave — conferidos em 19/08

| Exigência do modelo | Estado na entrega parcial |
| :--- | :--- |
| Resumo estruturado, até 200 palavras | **158 palavras** — OK |
| Abstract | 155 palavras — OK |
| 3 a 5 palavras-chave separadas por `;` | 5, separadas por `;` — OK |

---

## 4. Formato: ABNT (confirmado em 2026-08-13)

Artigo científico em **ABNT NBR 6022**, uma coluna.

### Configuração de página

| Item | Valor |
| :--- | :--- |
| Fonte | Times New Roman ou Arial, **12** |
| Entrelinhas do corpo | **1,5** |
| Margens | 3 cm superior e esquerda · 2 cm inferior e direita |
| Recuo de parágrafo | 1,25 cm |
| Citação longa (+3 linhas) | recuo 4 cm, fonte 10, espaço simples |
| Legenda de tabela/figura | **acima** do elemento; fonte **abaixo** — sempre |
| Citação no texto | autor-data, NBR 10520 |
| Referências | NBR 6023, ordem alfabética |

### A conta de páginas

Uma página ABNT (12pt, 1,5) comporta ~300–350 palavras.

| | |
| :--- | ---: |
| 20 páginas, se fossem só texto | ~6.500 palavras |
| Espaço ocupado pelos 12 elementos gráficos + legendas | ~4–5 páginas |
| **Texto corrido efetivo a escrever** | **~15 páginas ≈ 5.000 palavras** |

**Isso é factível.** ABNT é uma coluna — 20 páginas aqui é bem menos texto do que 20
páginas em template de duas colunas (SBC/IEEE). Distribuído pelas 20 sessões do
cronograma, dá **~250 palavras por sessão**. Um parágrafo bom por sessão resolve.

> Não escrever tudo no fim. 5.000 palavras de uma vez é o que faz artigo virar
> encheção de linguiça — e encheção de linguiça em ABNT é visível, porque a fundamentação
> incha e os resultados não.

### Elementos pré-textuais exigidos

Título · autoria · **Resumo** (150–250 palavras) · palavras-chave · **Abstract** ·
*keywords*. O resumo se escreve **por último**, quando os resultados existirem — resumo
escrito antes do experimento sempre promete o que o trabalho não entrega.

### Pendência

- [ ] **As 20 páginas incluem referências e elementos pré-textuais?** Se incluírem, o texto
      efetivo cai para ~13 páginas e a meta por sessão diminui. Confirmar com o orientador
      ou no edital do curso.
