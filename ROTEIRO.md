# Roteiro de Reconstrução — refazer o WAF do zero, à mão

**Pedro Henrique Juliani** · agosto de 2026
**Objetivo:** reconstruir o mesmo trabalho (WAF em duas camadas para SQLi/XSS) escrevendo
cada linha, até dominar cada decisão a ponto de defendê-la sem consultar nada.

---

## O contrato entre nós dois

**Meu papel:** explico o conceito, defino a tarefa e o critério de aceite, reviso o que
você escreveu, aponto o erro sem corrigir por você, e te faço a pergunta que a banca faria.

**Não vou escrever o código do seu TCC.** Se você me pedir código pronto no meio do
caminho, eu vou lembrar deste parágrafo e devolver a pergunta.

**Seu papel:** escrever, medir, e — a parte que mais importa — **explicar em voz alta**
cada módulo antes de passar para o próximo.

### As três regras que não se quebram

1. **Todo número que você citar, você sabe qual script gerou.** Se não sabe, não cita —
   diz "não medi isso". Essa regra já está no seu `IMPORTANTE.md` e é o que separa um TCC
   defensável de um TCC decorado.
2. **Nada de copiar e colar do repositório antigo.** Ele vira material de consulta, e só
   *depois* da sua tentativa. Ver a resposta antes de tentar destrói o aprendizado — você
   vai achar que entendeu porque reconheceu, não porque construiu.
3. **Cada etapa só fecha quando você passa no teste de propriedade** (definido abaixo).

### Como preparar o terreno

```
C:\Dev\
  Tcc\            <- o atual. Renomeie mentalmente para "referência". Não edite mais.
  Tcc2\           <- o novo. git init próprio, venv próprio, do zero.
```

Crie também um **caderno de laboratório** (`Tcc2/diario.md`). Uma entrada por sessão:
data, o que tentou, o que quebrou, o que mediu. Esse arquivo é o que vai te salvar quando
a banca perguntar "por que você escolheu X" seis meses depois — e é o insumo bruto do
capítulo de metodologia.

### O teste de propriedade (aplicar ao fim de cada etapa)

Feche o editor. Sem olhar para nada, responda em voz alta, gravando no celular:

- O que este módulo faz, em uma frase?
- Por que ele existe? O que quebraria sem ele?
- Qual foi a decisão de projeto mais discutível que eu tomei aqui, e qual foi a alternativa?
- Que número este módulo produz, e qual comando eu rodo para reproduzi-lo?

Se travar em qualquer uma, a etapa **não fechou**. Volte ao código.

---

## Mapa das etapas

A ordem abaixo é a ordem de *dependência real*, não a ordem em que o projeto original
nasceu. O projeto original nasceu bagunçado (por isso teve reescrita de `model_trainer.py`
no meio do caminho). Você tem a vantagem de já saber onde ele deu errado.

| # | Etapa | Entrega | Peso na defesa |
| :-- | :--- | :--- | :--- |
| 0 | Fundamentos de ML | nenhuma linha de código | — |
| 1 | Ingestão do CSIC 2010 | parser do formato bruto | alto |
| 2 | Normalização | função única de desofuscação | **crítico** |
| 3 | Rotulagem por família | classificador de família | **crítico** |
| 4 | Features | extrator com 3 blocos | alto |
| 5 | Validação honesta | validação cruzada com grupos | **crítico** |
| 6 | Calibração de limiar | escolha do ponto de operação | alto |
| 7 | Ablação e baseline | tabela comparativa | **crítico** |
| 8 | Camada 1 — assinaturas | conjunto de regras nomeadas | alto |
| 9 | Middleware — a cascata | interceptação HTTP | médio |
| 10 | Avaliação híbrida | matriz de concordância | **crítico** |
| 11 | Explicabilidade | laudo por requisição | médio |
| 12 | Monografia e defesa | o texto | **crítico** |

"Crítico" = é aqui que a banca derruba TCC de ML. As três mais perigosas são 5, 7 e 10.

---

# ETAPA 0 — Fundamentos de ML (antes de qualquer código de modelo)

Você me disse: Python ok, ML fraco. Então essa etapa não é opcional, e ela vem **antes**
de treinar qualquer coisa. Treinar um modelo sem entender a métrica é como medir com uma
régua que você não sabe ler.

### O que estudar (nesta ordem)

1. **Classificação binária supervisionada.** O que é um rótulo, o que é uma feature, o que
   significa "o modelo aprendeu". Pare quando conseguir explicar por que um modelo não
   "entende" texto e precisa de números.
2. **Matriz de confusão.** VP, VN, FP, FN. Essa é a base de tudo o que vem depois.
3. **Precisão, Recall, F1.** Não decore fórmula: entenda *qual pergunta cada uma responde*.
   - Precisão responde: "quando eu bloqueio, quantas vezes eu estou certo?"
   - Recall responde: "dos ataques que existem, quantos eu peguei?"
   - Taxa de FP responde: "do tráfego legítimo, quanto eu atrapalhei?"
4. **Por que acurácia é inútil aqui.** Com 5% de ataques, um modelo que libera tudo tem 95%
   de acurácia. Saiba dizer isso com números do *seu* dataset.
5. **Desbalanceamento de classe** e por que ele distorce o limiar padrão.
6. **Random Forest** em nível conceitual: árvore de decisão → floresta → voto. O que
   `predict_proba` devolve e por que não é "probabilidade" no sentido estatístico estrito.
7. **Validação cruzada K-Fold** e o motivo de existir: uma única divisão treino/teste te dá
   um número com sorte embutida.
8. **Vazamento de dados (data leakage).** Esse é o conceito mais importante da etapa.
   Estude até conseguir dar três exemplos diferentes de vazamento.

### Tarefa 0 (sem computador)

Pegue papel. Invente um cenário: 1.000 requisições, 50 são ataques. Seu detector bloqueia
80 requisições, das quais 40 eram ataques de verdade. Calcule à mão: matriz de confusão
completa, precisão, recall, F1, taxa de FP e acurácia. Depois responda: **este detector
presta?** Justifique usando duas métricas diferentes que apontem para lados opostos.

### Critério de aceite

Você me manda a resolução e explica por que a acurácia desse detector é enganosa.

### Pergunta de banca

> "Seu sistema tem 97,88% de precisão. Isso é bom?"

A resposta certa não é "sim". É perguntar de volta qual a taxa de ataques na base — porque
precisão depende da prevalência, e num tráfego real de produção, com 0,1% de ataques em vez
de 43%, a mesma taxa de FP produziria uma precisão muito pior. Saber isso é o que separa
quem entende de quem decorou.

---

# ETAPA 1 — Ingestão do CSIC 2010

### O conceito

O CSIC 2010 não vem em CSV. Vem como **requisições HTTP cruas em texto**, empilhadas, em
três arquivos: tráfego normal de treino, normal de teste, e anômalo. Antes de escrever uma
linha de parser, **abra o arquivo num editor e leia com os olhos**. Trinta minutos lendo o
formato bruto valem mais do que três horas depurando parser.

Observe: onde começa e termina um bloco? A linha de requisição, os headers, a linha em
branco, o corpo. O que muda entre GET e POST? Onde ficam os parâmetros em cada caso?

### Tarefa 1

Escreva o módulo de ingestão. Ele deve:

- Fatiar o arquivo em blocos, um por requisição.
- Parsear cada bloco em: método, URL, parâmetros (nome e valor), headers, corpo.
- Unificar parâmetros de query string (GET) e de corpo (POST) numa representação só.
- Produzir um DataFrame com uma coluna de texto analisável e uma coluna de rótulo (0/1).

### As armadilhas desta etapa

**(a) Byte nulo.** Alguns payloads do CSIC contêm `\x00`. Ele sobrevive na memória mas
morre quando você serializa para certos formatos. Se ele sumir, você perde exatamente um
tipo de ataque — silenciosamente. Decida o que fazer e **documente a decisão**.

**(b) Duplicatas.** O dataset tem repetição. Se você não deduplicar, a mesma requisição
aparece no treino e no teste, e sua métrica infla. Se você deduplicar demais, perde sinal
de frequência. Decida, meça o impacto nos dois cenários, e documente.

**(c) A mesma requisição em GET e POST.** O CSIC tem pares: o mesmo payload enviado das duas
formas. São textos *diferentes* (então a deduplicação não pega) mas são o *mesmo ataque*.
Se um cair no treino e o outro no teste, você vazou. Guarde essa observação — ela é a razão
de existir a Etapa 5.

### Critério de aceite

Você imprime as contagens (normal treino / normal teste / anômalo) e **compara com os
números publicados pelo CSIC**. Se divergirem, o parser está errado — investigue antes de
seguir. Um parser que perde 3% das requisições envenena todo o resto do trabalho.

### Pergunta de banca

> "Quantas requisições você descartou na ingestão, e por quê?"

Se você não souber o número exato, a resposta vira "não sei o que entrou no meu modelo".

---

# ETAPA 2 — Normalização (a função mais perigosa do projeto)

### O conceito

Atacante ofusca. `<script>` vira `%3Cscript%3E`, vira `%253Cscript%253E`, vira base64,
vira maiúsculas alternadas. Se você decidir *antes* de normalizar, todo ataque ofuscado
passa. Então existe uma função que recebe o texto cru e devolve o texto canônico.

**Por que ela é a mais perigosa:** ela é chamada em dois lugares — no treino e na
inferência. Se as duas versões divergirem em um detalhe, seu modelo foi treinado sobre uma
distribuição e opera sobre outra. Isso se chama *training/serving skew*, e é invisível: não
dá erro, só degrada a detecção. **Escreva uma função só, num módulo só, importada nos dois
lugares.** Nunca duplique.

### Tarefa 2

Escreva a função de normalização. Ela precisa lidar com:

- URL-decode **em laço**, até o texto parar de mudar (pense: por que uma passada só não
  basta? Teste com `%253C`).
- Base64, quando o parâmetro inteiro for base64 válido. Cuidado: nem toda string que
  *parece* base64 é base64 — decodificar texto legítimo por engano cria falso positivo.
- Caixa (minúsculas).

E precisa **declarar o que ela não faz**. O projeto de referência não decodifica entidade
HTML (`&lt;`), e isso está honestamente declarado na `COLINHA.md` como limitação. Você pode
implementar ou não — mas tem que saber qual escolheu e por quê.

### Critério de aceite

Escreva testes: uma tabela de entrada → saída esperada, cobrindo cada técnica de ofuscação
e, importante, **casos legítimos que não podem ser alterados**. Se sua normalização
corromper um texto normal, você criou falso positivo na fonte.

### Pergunta de banca

> "Sua normalização é a mesma no treino e em produção? Como você garante isso?"

A única resposta boa é: "é a mesma função, importada do mesmo módulo, e tenho teste que
prova". Qualquer outra coisa é fé.

---

# ETAPA 3 — Rotulagem por família de ataque

### O conceito — e por que essa etapa quase derrubou o trabalho original

Seu tema é **SQL Injection e XSS**. Mas no CSIC 2010, SQLi + XSS somam **13,9%** das
anomalias (corrigido em 25/11; o roteiro original dizia 6,6% e 89,9%, números do projeto antigo antes das correções de 28/07). **79,9%** são *parameter tampering* — campos com tipo errado, tamanho
absurdo, caractere inválido. Coisa que não é injeção.

Consequência: **o F1 global do seu modelo mede principalmente detecção de tampering.** Se
você reportar só o número global e afirmar que ele avalia SQLi/XSS, você está apresentando
uma métrica que mede uma tarefa diferente da que você diz avaliar. Uma banca atenta pega
isso, e é fatal.

A solução é rotular cada anomalia por família e reportar **recall por família**. Precisão
não é definível por família (um falso positivo não pertence a família nenhuma) — entenda
por que antes de seguir.

### Tarefa 3

Escreva o classificador de família. Ele olha o payload normalizado e devolve a categoria:
SQLi, XSS, tampering, outros.

### A armadilha (real, aconteceu)

A heurística original **não reconhecia `waitfor delay`** — que é o template de blind SQLi
por tempo, e o mais frequente do CSIC. Resultado: centenas de SQLi rotulados como
tampering, e o recall de SQLi reportado errado.

Lição: sua heurística de rotulagem é **código de medição**, e código de medição errado
produz um TCC inteiro construído sobre um número falso. Trate-a com mais rigor que o
próprio detector.

### Critério de aceite

Sorteie **50 anomalias ao acaso**, classifique **à mão**, e compare com a saída da sua
heurística. Reporte a taxa de concordância. Se der abaixo de ~90%, sua rotulagem não serve
para medir nada. Guarde essa amostra anotada — ela é evidência metodológica que você pode
mostrar na defesa.

### Pergunta de banca

> "Como você sabe que o que você chamou de SQLi é realmente SQLi?"

Sem a amostra anotada à mão, não tem resposta.

---

# ETAPA 4 — Engenharia de features

### O conceito

O modelo não lê texto, lê números. Você vai construir três blocos:

**Bloco 1 — heurísticas de AppSec (poucas, interpretáveis).** Contagens que traduzem
conhecimento de segurança: comprimento, densidade de caracteres especiais, palavras-chave
de SQL, palavras-chave de XSS, marcas de encoding. São as features que você consegue
*explicar* para a banca uma a uma.

**Bloco 2 — contexto HTTP.** Método, número de parâmetros, presença de corpo, tamanho do
corpo, número de headers. Atenção ao método: ele é categórico. Se você codificar
GET=0, POST=1, PUT=2, o modelo vai supor que PUT é "maior" que GET, o que não significa
nada. Estude *one-hot encoding* e aplique.

**Bloco 3 — TF-IDF de n-grams de caractere.** Esse é o bloco que você tem que entender de
verdade, porque a banca vai perguntar. Estude o que é TF-IDF antes de usar. Depois responda
para si mesmo: **por que n-grams de caractere e não de palavra, em segurança?** (Dica:
pense em `<script>` versus `<ScRiPt>` como tokens de palavra, e depois como conjuntos de
trigramas de caractere. E pense em fragmentos que atravessam fronteira de palavra: `';`,
`--`, `%27`.)

Decida também o limite de features do TF-IDF, e saiba justificar: cada coluna custa tempo
de inferência em **toda** requisição em produção. É um trade-off explícito entre poder de
representação e latência — e você está no caminho crítico.

### Tarefa 4

Escreva o extrator. **Uma função de montagem, um caminho único.** No projeto de referência
essa montagem estava duplicada em quatro arquivos, e quando um ficou dessincronizado o erro
só apareceu quando o sklearn reclamou da contagem de colunas — depois de rodar predições
erradas. Salve a lista ordenada de colunas num arquivo de metadata e reindexe explicitamente
na inferência. Se faltar coluna, **falhe alto** em vez de prever errado.

### Critério de aceite

Para cinco payloads escolhidos por você (dois legítimos, um SQLi, um XSS, um ofuscado),
imprima o vetor de features e **explique cada valor não-zero**. Se tiver um número que você
não sabe explicar, você não entende sua própria representação.

### Pergunta de banca

> "Por que essas features e não outras? Você testou sem elas?"

A resposta vive na Etapa 7. Guarde a pergunta.

---

# ETAPA 5 — Validação honesta (a etapa que derruba TCC de ML)

### O conceito

Existem três formas de vazamento nesse projeto, e você precisa saber as três:

**(a) Vazamento pelo TF-IDF.** Se você ajusta o vetorizador sobre o dataset inteiro e
*depois* divide em treino e teste, as estatísticas de IDF do conjunto de teste entraram no
treino. O modelo viu, indiretamente, o que deveria prever. Regra: `fit_transform` **só no
treino do fold**, `transform` no teste. E isso significa que o TF-IDF é ajustado **dentro
de cada fold**, não antes da validação.

**(b) Vazamento por near-duplicate.** Lembra do par GET/POST da Etapa 1? Deduplicação
exata não pega, porque os textos diferem. Se um cai no treino e o gêmeo no teste, o modelo
não generalizou — ele memorizou. A solução é **agrupar**: definir uma chave de grupo (o
payload normalizado, por exemplo) e garantir que todo o grupo caia no mesmo lado da divisão.

**(c) Vazamento pela calibração.** Se você escolhe o limiar olhando o mesmo dado em que
mediu o desempenho, o limiar está superajustado. Resolve-se com predições *out-of-fold* —
veja abaixo.

### Tarefa 5

Implemente a validação cruzada com três propriedades simultâneas:

- **K-Fold**: cada requisição é testada exatamente uma vez; você tem K medidas, não uma.
- **Estratificada**: cada fold preserva a proporção de ataques do dataset completo.
- **Agrupada**: nenhum grupo se divide entre treino e teste.

Ao final, colete as **probabilidades out-of-fold (OOF)**: a probabilidade de cada requisição
prevista pelo modelo do fold em que ela era *teste* — nunca por um modelo que a viu no
treino. Esse vetor é o insumo da Etapa 6.

Estude `StratifiedGroupKFold` antes de usar. E saiba que satisfazer estratificação e
agrupamento ao mesmo tempo nem sempre é possível: grupos grandes forçam desbalanceamento.
**Por isso seu script tem que imprimir a proporção de ataques em cada fold**, para você
conferir que nenhum ficou degenerado.

### Critério de aceite

Rode a validação **duas vezes com sementes diferentes** e compare. Se o F1 variar muito
entre sementes, seu resultado não é estável e você precisa reportar desvio-padrão, não um
número só. Reporte média ± desvio entre folds — sempre.

### Perguntas de banca (as duas mais perigosas do trabalho)

> "Você fez o `fit` do TF-IDF antes ou depois do split?"
>
> "Você tem certeza de que não há requisição parecida no treino e no teste?"

---

# ETAPA 6 — Calibração do limiar de decisão

### O conceito

`.predict()` do sklearn usa 0,5 implicitamente. **0,5 não é uma escolha, é um default** — e
num problema desbalanceado com custos assimétricos ele é quase sempre o valor errado.

Em WAF, os dois erros custam coisas diferentes: um falso negativo é um ataque que passou;
um falso positivo é um cliente legítimo bloqueado. Em produção, o falso positivo é o que
faz desligarem o WAF. Então a formulação correta não é "maximize o F1" e sim: **dado um
orçamento de falso positivo que a operação tolera, qual o melhor ponto de operação?**

Note a sutileza: *dentro* do orçamento, escolher por recall máximo empurra sempre para o
limite do orçamento, mesmo quando o ganho é irrelevante. Escolher por F1 dentro da restrição
evita esse desperdício, porque o F1 penaliza a perda de precisão. Entenda esse argumento —
ele é uma decisão de projeto sua, e a banca pode contestá-la.

### Tarefa 6

Usando as probabilidades **OOF** da Etapa 5 (nunca as de treino), varra os limiares
possíveis e monte a curva: limiar → taxa de FP, recall, precisão, F1. Escolha o limiar
segundo o critério que você definiu e **grave-o no metadata do modelo**, junto com a lista
de colunas. A inferência tem que ler esse limiar, não usar 0,5.

### Critério de aceite

Uma tabela mostrando o trade-off em vários limiares, com o escolhido marcado. Você tem que
saber dizer, olhando a tabela, **o que aconteceria se você tivesse escolhido outro**.

### Pergunta de banca

> "De onde veio esse 0,650?"

---

# ETAPA 7 — Ablação e baseline

### O conceito

Até aqui você tem um número. Um número sozinho não prova nada: **prova em relação a quê?**

Duas comparações obrigatórias:

**Ablação** — treine com blocos de features diferentes (só heurísticas / só TF-IDF /
heurísticas + contexto / tudo). Isso responde "cada bloco de feature contribui, ou eu
inflei o vetor à toa?".

**Baseline** — um detector burro e barato: um punhado de regex. Se seu Random Forest com 62
features não superar significativamente um regex de vinte linhas, **o ML não se justifica**,
e o TCC honesto tem que dizer isso. Essa comparação é o que transforma "eu treinei um
modelo" em "eu demonstrei que vale a pena treinar um modelo".

### Tarefa 7

Rode a ablação e o baseline sob **exatamente a mesma validação** da Etapa 5. Mesma divisão,
mesmos grupos, mesma semente. Comparação com metodologia diferente não é comparação.

### Critério de aceite

Uma tabela final com todas as configurações, e um parágrafo seu dizendo o que ela prova
**e o que ela não prova**.

### Pergunta de banca

> "Um regex simples não resolveria?"

Essa é a pergunta que mata TCC de ML aplicado. Você precisa da tabela.

---

# ETAPA 8 — Camada 1: assinaturas

### O conceito

Agora inverte o ângulo. WAF de assinatura (tipo OWASP CRS) tem **precisão altíssima e
recall limitado**: quando dispara quase nunca erra, mas só reconhece o que alguém já
catalogou.

A tese do seu trabalho é que **os perfis de erro são complementares**: assinatura erra por
falso negativo, modelo erra por falso positivo — e por isso somar vale mais do que escolher.
Mas isso é uma **hipótese até você medir**. A Etapa 10 é onde ela se confirma ou cai.

### Tarefa 8

Escreva o conjunto de regras. Requisitos:

- Cada regra tem **nome próprio** (`SQLI-001`, `XSS-003`...). Isso não é enfeite: é
  *proveniência*. Um bloqueio que sai com o nome da regra é auditável; um que sai com
  "probabilidade 0,87" exige explicação. Essa diferença é um dos argumentos da sua defesa.
- As regras procuram **estrutura de injeção**, não palavra solta. Uma regra que bloqueia a
  palavra "select" vai barrar texto em linguagem natural. Uma que exige a estrutura
  `select ... from` não.
- Cobertura pensada por técnica: união, comentário, tautologia, blind por tempo, empilhamento
  de comandos; tag script, handler de evento, `javascript:` em atributo, entidade/encoding.

Escreva as regras **você**, uma a uma, entendendo cada uma. Não importe o CRS.

### Critério de aceite

Meça a camada 1 **isolada** sobre o mesmo conjunto: precisão, recall, taxa de FP. A precisão
deve ser altíssima e a taxa de FP deve ser praticamente zero — se não for, sua regra está
procurando palavra em vez de estrutura, e você tem que consertar.

### Pergunta de banca

> "Suas 24 regras são arbitrárias. Por que essas?"

---

# ETAPA 9 — O middleware: a cascata

### O conceito

O WAF precisa rodar **antes do roteamento** da aplicação — se rodar depois, a rota
vulnerável já executou. Estude o que é um middleware ASGI e onde ele se encaixa no ciclo.

O fluxo: requisição → normalização (a função da Etapa 2!) → camada 1 → se casou, bloqueia
com o nome da regra → se não casou, camada 2 → se passou do limiar, bloqueia com a
probabilidade → senão, segue para a rota.

### Tarefa 9

Implemente o middleware e uma aplicação-alvo deliberadamente vulnerável (as rotas concatenam
SQL sem sanitizar — é o ponto: você está demonstrando que a proteção está no WAF, não na
aplicação).

### As armadilhas

- **Ordem das colunas.** A matriz da inferência tem que estar na mesma ordem do treino. Leia
  do metadata e reindexe explicitamente.
- **Latência.** Meça. Paralelizar a floresta para prever *uma* linha custa mais do que
  percorrer as árvores em série — distribuir entre threads tem overhead que não se paga com
  uma amostra só. Meça as duas configurações e reporte o número.
- **O que é decisão e o que é proveniência.** Seja honesto: em termos de *decisão*, a
  cascata é equivalente a "assinatura OU modelo" — ordenar as camadas não aumenta o recall.
  O que a ordem entrega é outra coisa: proveniência, custo (o que a camada 1 resolve não
  paga a inferência) e orçamento de FP (a camada 1 consome zero, então toda a margem fica
  disponível para a camada 2). **Declare isso antes que perguntem.**

### Critério de aceite

Latência medida (mediana e p95) das duas camadas, separadamente.

---

# ETAPA 10 — Avaliação híbrida: a matriz de concordância

### O conceito — este é o resultado central do seu TCC

Não basta dizer que as camadas se complementam. **Meça.** Para cada ataque, registre se foi
detectado pela camada 1, pela camada 2, por ambas, ou por nenhuma. Isso é uma tabela 2×2:

| Detectado por | n | % |
| :--- | ---: | ---: |
| Ambas | | |
| Somente a assinatura | | |
| **Somente o modelo** | | |
| Nenhuma | | |

A célula **"somente o modelo"** é a contribuição do seu trabalho — são os ataques que um WAF
de assinaturas operando sozinho deixaria passar, porque não há assinatura para casar. Se
essa célula for pequena, sua tese é fraca e você precisa dizer isso. Se for grande, você tem
o resultado.

A célula **"nenhuma das duas"** é a sua limitação, e ela também vai para o texto.

### Tarefa 10

Monte a avaliação híbrida. Um detalhe metodológico que você precisa pensar: a camada 2 só vê
o que a camada 1 liberou. Então o limiar dela, calibrado sobre o tráfego *inteiro*, é o
limiar certo para operar sobre o tráfego *filtrado*? Pense se cabe recalibrar
condicionalmente — e justifique a decisão nos dois sentidos.

Produza também o recall **por família** (Etapa 3) para cada configuração. É esse recorte que
responde a pergunta do seu trabalho, não o F1 global.

### Critério de aceite

A matriz preenchida, e um parágrafo seu explicando o que cada célula significa
operacionalmente para quem administra o WAF.

### Pergunta de banca

> "Você provou que somar é melhor, ou só que as duas camadas juntas detectam mais?"

Pense nessa. Ela é mais afiada do que parece.

---

# ETAPA 11 — Explicabilidade

### O conceito

Um bloqueio com "probabilidade 0,87" é inútil para o analista de plantão às 3h da manhã. Ele
precisa saber **o que** na requisição pesou. Estude SHAP em nível conceitual: contribuição
marginal de cada feature para aquela predição específica.

### Tarefa 11

Gere um laudo por requisição bloqueada: as features que mais pesaram, com o sinal da
contribuição.

### Critério de aceite

Pegue um bloqueio e explique o laudo para alguém que não é da área. E pegue um **falso
positivo** e explique por que o modelo errou — essa é a mais valiosa das duas.

---

# ETAPA 12 — A monografia

Escreva **depois**, e escreva a partir do `diario.md`. Estrutura que funciona para trabalho
experimental:

1. Objetivo e **delimitação de escopo** (o que você não fez, dito na primeira página)
2. Fundamentação (WAF, assinatura vs. anomalia, o problema do FP)
3. Arquitetura
4. Metodologia experimental (dataset, validação, como você evitou vazamento) — **é aqui que
   você ganha ou perde a banca**
5. Resultados (com ablação e baseline, não só o número final)
6. Discussão: o que os números provam e o que não provam
7. **Limitações declaradas** — capítulo próprio, não um parágrafo escondido
8. Trabalhos futuros

O capítulo de limitações é contraintuitivo mas é o que mais te protege: declarar o limite
com precisão desarma a pergunta. Tentar defender o indefensável na frente da banca é pior do
que reconhecer o limite.

---

## Cronograma sugerido

Ajuste ao seu prazo, mas mantenha as proporções — o erro clássico é gastar tudo em código e
chegar sem texto.

| Bloco | Etapas | Tempo |
| :--- | :--- | :--- |
| Fundamento | 0 | 1 semana |
| Dados | 1, 2, 3 | 2 semanas |
| Modelo | 4, 5, 6 | 3 semanas |
| Evidência | 7 | 1 semana |
| Sistema | 8, 9 | 2 semanas |
| Resultado | 10, 11 | 2 semanas |
| Texto | 12 | 3 semanas |

## Como me acionar

- **"Etapa N, me explica o conceito"** → eu ensino, sem código.
- **"Terminei a etapa N, revisa"** → eu leio, aponto erros e faço as perguntas de banca.
  Não corrijo por você.
- **"Travei em X"** → eu te dou a próxima pergunta a se fazer, não a resposta.
- **"Me faz perguntas de banca sobre a etapa N"** → eu ataco, sem dó.

Uma coisa que eu vou fazer sempre: se você me trouxer um número, eu vou perguntar qual
script gerou. Acostume-se.
