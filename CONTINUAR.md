# CONTINUAR — ponto de retomada

> **Para o Claude:** leia este arquivo, o `ROTEIRO.md` e o `diario.md` antes de responder.
> O material de orientação está em [`docs/aulas/README.md`](docs/aulas/README.md).
>
> Última atualização: **2026-11-13** (reorganização para o fim de semana sem PC). As seções abaixo
> deste bloco são o estado de **19/08** e ficam como histórico.

---

## ESTADO EM 13/11 — FIM DE SEMANA SEM PC (leia isto primeiro)

O Pedro fica **sem computador de sex 13/11 a seg 16/11** e vai escrever o artigo na lan
house, só com o GitHub no navegador. Para isso, em 13/11:

- Repositório reorganizado e enviado: os `.docx` foram para `docs/artigo/`; criado
  [`docs/artigo/README.md`](docs/artigo/README.md), o mapa de onde está cada material
  (números com script, frases, limitações, tabelas, regras ABNT); `logs/` passou a ser
  versionado (são a prova dos números); README da raiz com a estrutura completa.
- Os scripts **continuam na raiz**, de propósito: eles se importam entre si e gravam em
  caminhos relativos. Mover mexeria no código que gera os números.

**Efeito no plano de 12/11:** a escrita de sex/sáb/dom (cap. 4 e cap. 6) segue. As
**auditorias** previstas para esses dias (`ingestao_csic.py`, `treino_modelo.py`,
`assinaturas.py`, `avaliacao_hibrida.py`) e o **objetivo 5** precisam rodar código, então
passam para **segunda, 16/11** em diante. O texto escrito antes da auditoria fica marcado
como pendente dela.

**Na volta (seg 16/11), começar por:** (1) ler o que ele escreveu e revisar como banca;
(2) gravar no `NECESSARIO.md` o que tiver saído; (3) auditorias atrasadas, uma por vez, com
o passo 4; (4) confirmar as respostas do Paulo (ver "Enviado ao Paulo em 12/11", abaixo).

---

## ESTADO EM 12/11 — PLANO FINAL

**Data informada pelo Pedro em 12/11:** entrega e apresentação entre a **última semana de
novembro e a primeira de dezembro**. Trabalhar com o pior caso: **texto fechado no
domingo, 22/11.** Isso dá 11 dias e acaba o regime de quinta e sexta: é sessão todo dia.

Nada foi registrado entre 06/10 e 12/11. As respostas do Paulo na reunião de 07/10
continuam sem registro.

**CORREÇÃO DE 12/11, depois de reler a `docs/artigo/TCC, 1 entrega.docx`:** a ameaça nº 1 é menor do
que foi registrado em 19/08. O título ("Detecção de Anomalias em Aplicações Web") e o
objetivo geral ("detecção de anomalias em requisições HTTP") **já são o escopo A**. O 1º
parágrafo da introdução cita **"manipulação de parâmetros"**, que é o tampering. A frase "a
introdução nem menciona tampering" estava errada. SQLi/XSS aparecem como **ênfase** (objetivo
específico 1), não como o escopo inteiro. O que continua exposto:
(a) a "ênfase" em SQLi/XSS, onde o ganho do ML é zero;
(b) o resumo promete "payloads ofuscados", o que não foi medido;
(c) zero-day na seção 1.2;
(d) o objetivo 5;
(e) nenhum objetivo prevê a camada de assinaturas.

**Decisões padrão (valem se o Paulo não disser o contrário até 13/11):**
- **Escopo A:** alargar para anomalias HTTP. O resultado já existe e não tem custo de código.
  Mexe no título, no resumo, no problema e nos objetivos do cap. 1.
- **Objetivo 5:** cumprir se ficar pronto em 13/11 (o Pedro troca o estimador, roda e
  compara: regressão logística e árvore de decisão). Se não ficar, reescrever o objetivo.
- **Latência:** o Claude escreve um script de medição de apoio (é infraestrutura, pela exceção
  do CLAUDE.md). Sem ele, a Tab. 6 sai do artigo.

**Auditoria comprimida:** só as 4 peças que geram números do artigo, cada uma com o passo 4
gravado no diário, feitas no mesmo dia do capítulo que as usa.

| Dia | Escrita (Pedro) | Auditoria / apoio |
| :--- | :--- | :--- |
| qui 12/11 | e-mail ao Paulo · decidir o escopo | Claude: script de latência, pacote para o professor |
| sex 13/11 | cap. 4 Metodologia (dataset, Tab. 1, 51.480 → 32.808) | `ingestao_csic.py` |
| sáb 14/11 | cap. 4 (validação, limiar) | `treino_modelo.py` · objetivo 5 |
| dom 15/11 | cap. 6 Resultados (Tab. A–D, por família, complementaridade) | `assinaturas.py`, `avaliacao_hibrida.py` |
| seg 16/11 | cap. 6 (ablação, limiar, latência, FP) · cap. 5 Desenvolvimento | `servidor.py` (normalização duplicada) |
| ter 17/11 | cap. 3: fichar 4 referências | — |
| qua 18/11 | cap. 3: fichar mais 4, escrever | — |
| qui 19/11 | cap. 2 Fundamentação (2.4 já tem 3 frases) | — |
| sex 20/11 | cap. 7 Conclusão e limitações · revisar cap. 1 (escopo, zero-day, acurácia, objetivos) | — |
| sáb 21/11 | referências ABNT, figuras, resumo/abstract | — |
| dom 22/11 | revisão final → **envio ao Paulo** | — |
| 23/11 → | simulados de banca, ensaio da demo | — |

Todo dia: **15 min de pergunta de banca** sobre o capítulo do dia.

### ENVIADO AO PAULO EM 12/11

O Pedro mandou ao orientador o texto explicando o sistema (`docs/aulas/texto-sistema-respostas.md`,
com as palavras dele, montado por pergunta e resposta). **Na próxima sessão, confirmar:**
(a) se foram também o vídeo e o zip; (b) qual zip, porque o da área de trabalho é **anterior** ao
resumo da aba Resultados; (c) se as perguntas (data, 20 páginas, regra de IA, objetivo 5) foram
junto. **Gravar aqui as respostas do Paulo assim que chegarem.**

### RESPOSTA DO PAULO (registrada em 25/11, texto integral em `docs/artigo/paulo.md`)

Sete pontos: (1) caminho da requisição no código + o que é dele, de terceiros e **de IA**;
(2) dataset, 97.065 → 32.808, features, por que RF, split sem repetição; (3) **comparar
algoritmos** (objetivo 5) — grupos de features não substituem; (4) **modelo da demo ≠ modelo
avaliado no CSIC**: explicar e demonstrar o avaliado; (5) matriz de confusão, regras × modelo ×
híbrido, métricas com os números dele, **discutir os ~40% de anomalias que passaram**;
(6) limitações, FP legítimo, como a latência foi medida; (7) código, dependências e scripts
reprodutíveis. Na banca: abrir o código, explicar trechos, rodar testes escolhidos na hora e
fazer uma alteração ao vivo.

### Feito em 12/11 (pelo Claude, infraestrutura e medição de apoio)

- `medir_latencia.py` → `docs/medicoes/latencia.md`. **A Tab. 6 agora tem script.**
  Total até a decisão da camada 2: 10,99 ms média, 13,21 ms p95.
- `medir_normalizacao.py` → `docs/medicoes/normalizacao_treino_vs_servidor.md`. A
  normalização é diferente, mas **0 de 32.808 decisões mudam**. O item 10 do bloco de 06/10
  deixa de ser gravidade alta e vira limitação declarada.
- `docs/medicoes/amostra_familias_50.txt`: amostra de 25 SQLi + 25 XSS extraída para a
  **anotação manual do Pedro** (Tab. 2). O veredito de cada linha é dele.
- `README.md` reescrito para o professor: como rodar, de onde vem cada número, limitações.
- A Tab. 1 já é explicável pelo log: 97.065 → 51.480 (tira 45.585 sem parâmetro) → 32.808
  (dedup remove 18.672). Quem explica no texto é o Pedro.

### O que falta para cumprir 100% da 1ª entrega (é do Pedro, não do Claude)

| Promessa | Situação | Saída |
| :--- | :--- | :--- |
| Obj. 5, comparar modelos | só RF | Pedro troca o estimador em `treino_modelo.py:279` (LogisticRegression, DecisionTree) e roda. ~1h. Ou reescreve o objetivo. |
| Resumo: "payloads ofuscados" | não medido | suavizar o texto (recomendado) ou medir (escopo B, mais 1 dia) |
| 1.2: "zero-day" | não medido | suavizar, ou declarar em limitações |
| Obj. 7: acurácia | métrica errada para dado desbalanceado | manter como contraexemplo |

---

## ESTADO EM 06/10

**Nomes dos scripts em português desde 06/10** (commit `8affda1`): `api.py` → `servidor.py`,
`model_trainer.py` → `treino_modelo.py`, `extractor.py` → `extrator.py`,
`ingestion_csic.py` → `ingestao_csic.py`, `ingestion.py` → `ingestao.py`,
`explain.py` → `explicacao.py`, `evasion_test.py` → `teste_evasao.py`,
`false_positive_test.py` → `teste_falso_positivo.py`. O texto histórico abaixo usa os nomes antigos.

**Reprodução feita (critério da sessão 3).** Em 06/10, `ingestao_csic.py`,
`treino_modelo.py` e `avaliacao_hibrida.py` rodaram neste repositório. O
`docs/medicoes/avaliacao_hibrida.md` saiu **byte a byte idêntico** ao do projeto antigo.
O treino reproduziu F1 0,7824 ± 0,0088 e o limiar 0,650. A ameaça nº 1 (ganho zero em
SQLi/XSS) está **confirmada aqui**, não é mais só número herdado.

**Tela azul de 06/10 (~03:23).** Zerou `models/*.pkl`, `models/model_metadata.json` e
`docs/medicoes/recall_por_familia.csv`. Foram restaurados do projeto antigo e conferidos
contra o log do treino daqui. O `requirements.txt` registra um segfault intermitente no
treino no mesmo dia. **Suspeita de RAM:** rodar `mdsched.exe` antes do próximo treino pesado.

**Nada foi registrado entre 19/08 e 06/10.** As sessões de 10/09 (escopo) e 11/09
(objetivo 5) não têm decisão gravada. Nenhuma peça tem auditoria no `diario.md` (0 de 11).
O artigo segue com a introdução entregue e 3 frases da seção 2.4.

### O que falta, em ordem de bloqueio

1. **E-mail ao Paulo, uma mensagem só:** data exata da entrega; se as 20 páginas contam
   referências; escopo A ou B; o objetivo específico da camada de assinaturas; a regra de
   uso de IA. Sem a data não dá para planejar o resto.
2. **Escopo (decisão do Pedro + Paulo).** Recomendação do Claude: **A**, alargar para
   anomalias HTTP. O resultado já existe e está reproduzido, sem custo de código. B custa
   uma sessão e pode não dar resultado.
3. **Objetivo 5:** +2 classificadores na mesma validação, ou reescrever o objetivo.
4. **Auditoria mínima, com passo 4:** `ingestao_csic.py`, `treino_modelo.py`,
   `assinaturas.py` e `avaliacao_hibrida.py`. São as peças que produzem os números do artigo.
   `servidor.py` e `extrator.py` vêm em seguida. As demais podem ficar fora do texto.
5. **Tabelas sem script ainda:**
   - Tab. 1: já tem números no log do `ingestao_csic.py`. Falta explicar 51.480 → 32.808.
   - Tab. 2: rodar `validar_familias.py`. O antigo usou 40 amostras, o ROTEIRO pede 50.
   - **Tab. 4:** a ablação por bloco já sai do `treino_modelo.py`, e a camada 1 isolada
     (`avaliacao_hibrida.py`) serve como o baseline de regex. O `baseline_comparison.py`
     não foi migrado e não faz falta.
   - **Tab. 6 (latência): nenhum script gera os números.** No antigo foi "instrumentação
     direta", sem script salvo. Até existir um script, **não citar** os 31,94 ms.
   - Fig. 1 (diagrama), Fig. 2 (gráfico de `curva_limiar.csv`), Fig. 3 (`explicacao.py`).
6. **Fichamento** de 8–12 referências. Trava os capítulos 2 e 3.
7. **Escrita:** capítulos 2 a 7, ~16 páginas.
8. **Demo — resolvido em 06/10, com uma descoberta.** `models/demo/` foi trazido do `Tcc`.
   O `verificar_roteiro.py` mostra o seguinte:
   - **Modelo do CSIC** (`python servidor.py`): 6 de 26 casos divergem. Ele bloqueia
     **todo o tráfego legítimo em português** ("pedro.almeida", e-mail, comentário) com
     p = 0,88–0,98. O "normal" que ele aprendeu é a loja espanhola de 2010; qualquer outra
     coisa vira anomalia.
   - **Modelo demo** (`WAF_MODELO=demo python servidor.py`): 26 de 26 conforme.
   **A demo da banca usa o modelo demo, e ele NÃO é o modelo medido no artigo.** Isso
   precisa ser dito antes que perguntem. Está registrado no `NECESSARIO.md` §3.
9. `git push`. O repositório remoto está atrás.

10. **NORMALIZAÇÃO DUPLICADA — achado de 06/10, gravidade alta.** O `servidor.py` tem a
    própria `decodificador_ofuscacao` (linha ~84), diferente da `normalizar_payload` do
    `ingestao_csic.py` que o treino usa. É o *training/serving skew* da Etapa 2, e a
    resposta para *"sua normalização é a mesma no treino e em produção?"* hoje é **não**.
    Entra na auditoria do `servidor.py` (a decisão de corrigir é do Pedro). Medir se muda
    algum resultado do roteiro.

### Frontend e aba Artigo (06/10)

O frontend foi refeito: abas **Testar ao vivo** (caminho da requisição etapa por etapa),
**Resultados do modelo** (gráficos) e **Artigo** (mapa por capítulo: checklist, perguntas,
tabelas para copiar no Word, limitações, regras ABNT). Os dados vêm de
`frontend/public/resultados.json`, gerado por `python exportar_painel.py` a partir das
medições. **Rodar o exportador de novo sempre que o treino ou a avaliação híbrida mudarem.**
**Reunião com o orientador: quarta 07/10.** A pauta está na aba **Plano** do site (7
perguntas, com campo para a resposta). As respostas ficam salvas só no navegador em que
foram digitadas: **na próxima sessão, pedir ao Pedro o que o Paulo respondeu** e gravar
aqui as decisões (escopo, objetivos, datas, regra de IA).

Também na aba **Banca**: um manual de estudo com 11 módulos (`frontend/src/lib/manual.js`),
que ensina cada assunto e aponta os cartões que o testam. Desde 06/10 também existe a aba **Banca**: 30 perguntas por tema, com pista, palavras que
não podem faltar e onde conferir, mais autoavaliação e simulado com 3 minutos por pergunta.
Perguntas novas vão em `frontend/src/lib/banca.js`, e fatos do artigo em
`frontend/src/lib/artigo.js`.
O `servidor.py` passou a devolver o payload normalizado e a nota do modelo também quando
libera. Só campos novos na resposta: nenhuma decisão mudou, e o roteiro continua 26/26.

### Como subir o sistema (verificado em 06/10)

```
WAF_MODELO=demo venv\Scripts\python.exe servidor.py    # porta 8000
cd frontend; npm run dev                               # porta 5173
venv\Scripts\python.exe verificar_roteiro.py           # confere os 26 casos
```

Em PowerShell, `WAF_MODELO=demo cmd` não funciona. Use `$env:WAF_MODELO='demo'` antes.

**Decisão de 06/10: continuar no `tccNovo`.** O `Tcc` está parado desde 28/07. O código dele
é o mesmo que está aqui. O que faltava (`models/demo`, `validacao_familias.md`, imagem do
SHAP, medições demo e de falso positivo) foi copiado para cá. O `Tcc` fica só como arquivo
de consulta.

---

## Onde o Pedro está

**ETAPA 0 ENCERRADA em 19/08.** Parte 1 (métricas, 13/08), parte 2 bloco 1 (Random Forest,
13/08) e parte 2 bloco 2 (validação cruzada e vazamento, 19/08). Passou no teste de
fechamento: deu os três exemplos de vazamento de cabeça, sem consultar.

A sessão prevista para **14/08 não aconteceu** e o fim de semana também não teve estudo. A
sessão de 19/08 (quarta, fora do regime) foi de recuperação e o cronograma **não escorregou**.

Aula gravada em `docs/aulas/Etapa 00/etapa-00-fundamentos-parte-2-bloco-2.md`.
Diário do dia registrado.

### O que ele domina agora (verificado por pergunta, sem consulta)

- Matriz de confusão e as cinco métricas; por que acurácia engana
- Random Forest: árvores (não neurônios), duas aleatoriedades, `predict_proba` como placar
  de votação e não probabilidade calibrada
- K-Fold: por que uma divisão só mede sorte; média **± desvio**; previsões **out-of-fold**
- Vazamento nas três formas do projeto, e a régua que resolve as três:
  *se em produção você não teria essa informação, o treino não pode tê-la tido*
- `GroupKFold` e por que `drop_duplicates` não resolve o par GET/POST

### Erros a vigiar (recaídas registradas em 19/08)

1. **A palavra "acurácia".** Duas recaídas na mesma sessão: chamou `predict_proba` de
   acurácia, e disse "pra medir o modelo tem que fazer a acurácia". Gatilho combinado:
   toda vez que a palavra aparecer, o porteiro dorminhoco aparece junto. **Reconferir.**
2. **Escolher o resultado.** Escolheu a semente 42 "porque o F1 deu maior". Reconheceu o
   erro quando reapareceu como forma 3 de vazamento — mas a tentação é reflexo, não
   ignorância. Vai voltar na Etapa 6.
3. **Falso positivo × falso negativo (12/11).** Chamou o 1% de inocentes barrados de "falso
   negativo" duas vezes. Destravou com "o alarme tocou? tinha ladrão?". **Reconferir.**
4. O "neurônios" de 13/08 **está curado** (reconferido em 19/08).

### Pergunta de banca ainda sem resposta dada por ele

> Por que forçar cada árvore a ver só uma parte das features **melhora** a floresta, se deixa
> cada árvore individualmente pior?

(Pendente desde 13/08. Cobrar numa retomada.)

## O PLANO MUDOU EM 19/08 — leia isto antes de qualquer coisa

Decisão do Pedro, com a auditoria do projeto antigo na mão: **o que decide a nota é o artigo
e a defesa**, não redigitar 1.750 linhas que já funcionam em `C:\Dev\Tcc`.

- **Todas as etapas passam a ser reaproveitadas e auditadas**, pelo protocolo de 5 passos do
  `CLAUDE.md`. A regra das "5 etapas intocáveis à mão" está **revogada**.
- **O passo 4 do protocolo — nomear a alternativa descartada — não é negociável.** É a
  única coisa que separa este caminho de chegar na banca defendendo o que não entende.
- As ~10 sessões liberadas foram para **artigo (10)** e **simulado de banca (4)**.

### A ameaça número 1 à defesa (descoberta em 19/08)

Medição do projeto antigo (`docs/medicoes/avaliacao_hibrida.md`), recall por família:

| Família | n | Assinaturas | Modelo | Ganho da camada 2 |
| :--- | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 11.332 | 4,0% | 49,6% | **+45,6 pp** |
| SQLi | 1.018 | 100,0% | 99,9% | +0,0 pp |
| XSS | 952 | 100,0% | 100,0% | +0,0 pp |
| **SQLi + XSS (escopo declarado)** | **1.970** | **100,0%** | **99,9%** | **+0,0 pp** |

> **No escopo que o artigo declara, a camada de ML acrescenta zero.** Todo o ganho está em
> *parameter tampering*, que a introdução entregue nem menciona.

Pergunta de banca fatal: *"se o seu WAF de regras já pega 100% de SQLi e XSS, para que serve
o Machine Learning num trabalho sobre SQLi e XSS?"*

Duas saídas, decisão na sessão de **10/09**, com dado na mão:

- **A — alargar o escopo declarado** para detecção de anomalias HTTP em geral. O resultado
  central vira os +45,6 pp em tampering. Custo: mexer na introdução entregue e conversar com
  o Paulo.
- **B — provar o ganho dentro do escopo atual**: construir um conjunto de SQLi/XSS
  **ofuscados** que as assinaturas não pegam e medir o recall do modelo neles. O
  `evasion_test.py` do projeto antigo é a semente, mas hoje é demonstração com 5 payloads,
  não medição. Custo: uma sessão, e o resultado pode não ser o desejado.

### Auditoria dos objetivos específicos (19/08)

| # | Objetivo específico | Situação no projeto antigo |
| :--- | :--- | :--- |
| 1 | Estudar SQLi e XSS | texto — a escrever |
| 2 | Analisar WAFs tradicionais | texto — a escrever |
| 3 | Selecionar datasets HTTP | OK — CSIC 2010, 32.808 requisições em escopo |
| 4 | Pré-processamento e features | OK — `extractor.py` |
| 5 | **Treinar e comparar diferentes modelos** | **NÃO CUMPRIDO.** Só Random Forest; B/C/D do `baseline_comparison.md` são ablação de features, todas RF. Resolver em **11/09**. |
| 6 | Middleware integrado | OK — `api.py` |
| 7 | As 6 métricas + tempo de resposta | OK — latência por etapa, p50/p95/p99, 300 execuções |
| — | "Zero-day" (seção 1.2) | **NÃO MEDIDO.** `evasion_test.py` testa ofuscação de ataque conhecido, que não é zero-day. Suavizar ou declarar em limitações. |

## Próximo passo — sessão 3, quinta 20/08

**Migração e reprodução.** Trazer o sistema para este repositório e rodar ponta a ponta.

Critério de aceite: **os números reproduzem**. Se o recall por família sair diferente do que
está em `C:\Dev\Tcc\docs\medicoes\`, descobrir por quê antes de seguir.

Fecha com a **Tabela 1 do artigo** (composição do CSIC 2010 por partição) gerada por script
**deste** repositório — e o parágrafo que a analisa. Isso também resolve a divergência dos
6,6% x 13,9% (ver `CLAUDE.md`).

### Estado da escrita (fim de 19/08)

**Seção 2.4 do artigo — 3 de 6 frases do parágrafo de vazamento**, escritas por ele. Texto e
registro do processo em `NECESSARIO.md` §1. Retomar por aí: faltam os **três exemplos
concretos** (TF-IDF fora do fold, par GET/POST, limiar), que é a parte fácil — ele deu os
três de cabeça em 19/08. Depois os parágrafos de classificação, Random Forest e validação.

**As subseções 2.1, 2.2 e 2.3 estão travadas por referências**, não por escrita. Sem
fichamento não adianta sentar para escrever — vira `[CITAR]` a cada linha.

> **O gargalo real do trabalho hoje é o fichamento de 8–12 referências.** Ele trava o
> capítulo 2 (três quartos) e o capítulo 3 inteiro. Não cabe nas sessões de quinta e sexta;
> é leitura de terça à noite, duas por noite. **Cobrar isso dele toda sessão.**

**Método de escrita que funcionou** (usar de novo): ele responde **falando**, depois
transforma em frase. Uma ideia por frase, ponto final em vez de "que" encadeado. Checklist
dos erros de forma dele em `NECESSARIO.md` §1.

Antes de começar: trocar o Notepad pelo VS Code.

## Calendário revisado (22 sessões, 20/08 a 30/10)

| Sessões | Datas | O quê |
| :--- | :--- | :--- |
| 3–4 | 20, 21/08 | Migração e reprodução ponta a ponta · **Tabela 1** |
| 5–8 | 27, 28/08 · 03, 04/09 | **Auditoria** das 11 peças, protocolo de 5 passos, ~3 por sessão |
| 9 | 10/09 | **Resolver o escopo** — medir SQLi/XSS ofuscados, decidir A ou B |
| 10 | 11/09 | **Cumprir o objetivo 5** — +2 classificadores sob a mesma validação |
| 11–16 | 17, 18, 24, 25/09 · 01, 02/10 | **Artigo** — capítulos 2 a 7, um por sessão |
| 17–18 | 08, 09/10 | Consolidação: tabelas, figuras, referências ABNT |
| 19–20 | 15, 16/10 | Revisão final. **Texto fechado em 16/10.** |
| 21–24 | 22, 23, 29, 30/10 | **Simulados de banca e ensaio da defesa** |

**Fora das sessões:** fichamento de 8–12 referências para *Trabalhos relacionados*.
Continua sendo o único item que não cabe nas quintas e sextas — e agora é o gargalo do
capítulo 3.

## Como treinar a defesa (definido em 19/08)

Em ordem de eficácia. Os dois primeiros são diários, os dois últimos são de sessão:

1. **Explicar em voz alta, sem olhar, com cronômetro.** 3 minutos por peça. Mental não vale
   — mental engana.
2. **A pergunta "por que não Y?"** para cada decisão. É o passo 4 do protocolo e é o que
   separa quem fez de quem viu ser feito.
3. **Simulado de banca com interrupção.** 20 minutos ao fim de cada etapa auditada, sem
   consulta. Ele precisa **pedir** — até 19/08 nunca pediu nenhum.
4. **Gravar o áudio explicando e ouvir depois.** Desconfortável e eficaz: as hesitações
   aparecem.

## Decisões travadas (não reabrir)

| Decisão | Detalhe |
| :--- | :--- |
| **Formato** | **Artigo** ABNT NBR 6022, mínimo 20 páginas — não é monografia. Isso substitui a Etapa 12 do `ROTEIRO.md`. Ver `docs/aulas/estrutura-do-artigo.md`. |
| **Prazos** | Entrega **outubro/2026** · defesa **novembro/2026**. Texto fechado em **16/10**. |
| **Regime** | Quintas e sextas. 24 sessões até 31/10. Ver `docs/aulas/arquivo/cronograma-ate-outubro.md` (arquivado). |
| **Enquadramento** | A camada de ML é **acrescentada** ao WAF de assinaturas, **não o substitui**. O resultado do trabalho é o **delta** (detecção ganha × FP introduzido), não o F1 do modelo. Ver `estrutura-do-artigo.md` §0. |
| **Cortes** | Etapa 11 (SHAP) em versão mínima; `datasets/SQL Injection/` e `datasets/XSS/` fora de escopo. |
| **Reaproveitamento do projeto antigo** (13/08) | **Frontend:** reaproveitado inteiro — não está nas 13 etapas, não é o trabalho. **Middleware (Etapa 9):** esqueleto reaproveitado, mas três pontos são dele (ver abaixo). Todo o resto continua sendo feito à mão. |
| **Intocáveis** | Etapas 2, 3, 5, 7 e 10 — feitas à mão, sem consultar o projeto antigo antes da própria tentativa. |

### Modo de execução por etapa (fechado em 13/08)

**Critério:** onde o valor está na *decisão* → à mão. Onde o valor está no *código
funcionando* → pega pronto do projeto antigo.

| Etapa | Modo | Sessões | Linhas (referência do antigo) |
| :--- | :--- | :--: | ---: |
| 1 — Ingestão | tentativa curta, depois **gabarito** | 1 | 715 |
| **2 — Normalização** | **à mão** | 1 | ~80 |
| **3 — Rotulagem** | **à mão** + amostra de 50 anotada | 1 | ~160 |
| **4 — Features** | **à mão** | 2 | 203 |
| **5 — Validação honesta** | **à mão** | **3** | ~300 |
| **6 — Limiar** | **à mão** | 1 | ~80 |
| **7 — Ablação e baseline** | **à mão** | 2 | 235 |
| 8 — Assinaturas | regras dele, gabarito depois | 1 | 282 |
| 9 — Middleware | **reaproveita** + 3 pontos abaixo | ~2h | 296 |
| **10 — Avaliação híbrida** | **à mão** | **3** | 404 |
| 11 — Explicabilidade | **reaproveita**, versão mínima | 1 | 70 |
| Frontend | **reaproveita inteiro** | 0 | — |
| Artigo | escrita concentrada | 4 | — |

**Total à mão: ~1.750 linhas em 14 sessões (~125 linhas/sessão).** O tempo vai em pensar,
não em digitar. O que foi economizado nas etapas 1, 9 e 11 foi realocado para **5 e 10**,
que ganharam uma sessão cada — são as que decidem a nota.

**Método para as peças reaproveitadas** (1 hora por peça, não uma sessão):
roda e vê funcionando → lê uma vez → **fecha e explica em voz alta** → identifica os pontos
de defesa. Se travar no passo 3, volta ao 2.

### Os três pontos do middleware que o Pedro precisa dominar

Mesmo com o código reaproveitado, estes têm peso de defesa e são responsabilidade dele:

1. **A chamada da normalização** — saber apontar a linha onde a função da Etapa 2 é
   importada. É a resposta para *"sua normalização é a mesma no treino e em produção?"*
   (training/serving skew).
2. **A reindexação das colunas** pelo metadata, e a decisão de **falhar alto** se faltar
   coluna em vez de prever errado.
3. **A latência** — mediana e p95 medidas por ele, com script dele. Vira a **Tabela 7** do
   artigo e é o "custo" do delta.

Custo estimado: ~2 horas, não as 2 sessões previstas. Libera 24 e 25/09.

### A demo é instrumento de defesa

A banca não lê código, mas **vê o sistema rodando**. Roteiro de demo (30 s), que é a prova
visual da tese: requisição com `' OR 1=1--` → bloqueio com o nome da regra (`SQLI-001`) →
payload ofuscado que a assinatura não pega e o modelo pega. É a célula "somente o modelo"
da matriz de concordância acontecendo ao vivo.

## Regras de sessão

1. **Toda sessão fecha com uma tabela ou figura do artigo produzida** — e o parágrafo que a
   analisa, escrito na mesma sessão. (A Etapa 0 é a única exceção: não produz elemento.)
2. **O Claude escreve o `diario.md`.** Combinado em 13/08 — o Pedro perdeu texto duas vezes
   por não salvar no Notepad. Ele responde no chat *o que travou* e *a alternativa
   descartada*; o Claude formata e grava. O resto do conteúdo continua sendo dele.

---

## A entrega parcial já feita

`docs/artigo/TCC, 1 entrega.docx` — **1.088 palavras (~3–4 páginas ABNT)**, já entregue ao
orientador (Paulo Rogerio de Mello Cardoso). Contém resumo/abstract estruturados e o
capítulo 1 completo (contextualização, problema, justificativa, objetivos, organização).

**A estrutura de 7 capítulos declarada na seção 1.5 é a estrutura oficial do artigo.**
Não inventar outra. Está transcrita em `docs/aulas/estrutura-do-artigo.md` §1.

Pendências herdadas dela (detalhadas em `estrutura-do-artigo.md` §1b):

- **RISCO ALTO** — **nenhum objetivo específico prevê a camada de assinaturas.** Os sete
  descrevem uma camada só (features → modelo → middleware). A matriz de concordância
  (Etapa 10, resultado central) só existe com a camada 1. Acrescentar um objetivo do tipo
  *"implementar uma camada de detecção por assinaturas e avaliar a contribuição incremental
  da camada de ML sobre ela"* — **falar com o orientador antes da versão final**.
- **RISCO ALTO** — o objetivo específico 5 promete *"treinar e comparar diferentes modelos"*.
  O plano treina só Random Forest. Recomendação: **cumprir** (rodar +2 classificadores sob a
  mesma validação, ~meia sessão) em vez de reescrever o objetivo.
- Acurácia está na lista de métricas — na versão final tem que entrar como **contraexemplo**.
- "Zero-day" é prometido na seção 1.2 e **não será medido** — suavizar ou declarar em
  limitações.
- A pergunta de pesquisa é de construção ("como desenvolver..."); refinar para a formulação
  do delta.
- Correções: "algoritimo" → algoritmo; "traffics analysis" → traffic analysis; "system\`s".

## Pendências abertas

- [ ] **Data exata da entrega em outubro** (o plano assume ~31/10). Se for antes do dia 20,
      as 4 sessões de folga somem e a Etapa 11 sai inteira.
- [ ] **As 20 páginas incluem referências e pré-textuais?**
- [ ] **Trabalhos relacionados:** 8–12 referências fichadas, fora do horário de sessão.
      Ainda não começou.
- [ ] Trocar o Notepad por VS Code antes da Etapa 1. **Vence hoje** — a Etapa 1 é amanhã.
- [x] **Git resolvido em 19/08.** Repositório **privado** em
      `https://github.com/Pedro2505/TCC-Etudos.git`, branch `main`, primeiro commit enviado.
      Fora do versionamento: CSIC bruto (54 MB) e os datasets SQLi/XSS fora de escopo.
      **Novo hábito: commitar ao fim de cada sessão.**

## Frases já prontas para o artigo

Saíram desta sessão e vão quase inteiras para o texto:

> "A acurácia não distingue um detector que funciona de um que não faz nada. No cenário
> testado, um classificador que libera todo o tráfego obtém os mesmos 95% do detector
> avaliado."

> "Não faz sentido trocar algo que já funciona por algo novo. Substituir significaria abrir
> mão de um detector com precisão altíssima e proveniência auditável em troca de um que erra
> mais em tráfego legítimo e responde 'probabilidade 0,87' quando o analista pergunta por
> que bloqueou."

### Limpeza de 12/11 (pedido do Pedro: "só o que está sendo usado")

Removidos, recuperáveis pelo Git (commit anterior a esta limpeza):
`teste_evasao.py` (nada o chamava, era uma demonstração com 5 payloads, não medição; se o
escopo B voltar, ele está no histórico) · `docs/medicoes/baseline_comparison.md` (veio do
projeto antigo, o script dele não existe aqui, então não pode ser citado) · a cópia
duplicada de `docs/medicoes/shap_explain_report.png` (o `explicacao.py` grava em `docs/`) ·
`static/index.html` (painel antigo, substituído por `frontend/`) · `__pycache__/`.
Mantidos de propósito: `logs/` (é a prova dos números de 06/10), `ingestao.py` e os datasets
de SQLi/XSS (treinam o modelo demo), `docs/artigo/TCC Modelo.docx` (o template do artigo).

### Limpeza do repositório (25/11)

Removidos: `logs/model_trainer_rerun2.log` (rodada interrompida pelo segfault), os prints
`image*.png` da raiz, a pasta vazia `static/` (agora no `.gitignore`), e as abas ocultas
Artigo, Banca e Plano do painel (componentes e `lib/`). Arquivado: `docs/aulas/arquivo/cronograma-ate-outubro.md`.
Mantido de propósito: `logs/model_trainer_rerun1.log`, idêntico ao `model_trainer.log`, que é a
prova de reprodutibilidade. O build do frontend passou depois da remoção.

### Paulo sobre a apresentação (recebido em 25/11)

> "Vc vai entregar o artigo para a banca ler, e vai fazer uma apresentação falando do artigo e
> mostrando os resultados, como vc alcançou, e explicando a teoria, a metodologia e os
> resultados finais."

Formato da defesa: **artigo lido pela banca antes** + **apresentação** em 4 blocos (teoria,
metodologia, como alcançou os resultados, resultados finais). Somado ao `paulo.md`: abrir o
código, explicar trechos, testes escolhidos na hora, alteração ao vivo.
**Tempo da apresentação: ~15 min** (Pedro, 25/11). **Ainda sem resposta:** data de entrega, data da banca, escopo, demo.

### DECISÃO DE ESCOPO (25/11) — falta o aval do Paulo

O Pedro escolheu **alargar o escopo**: o tema passa a ser detecção de anomalias em requisições
HTTP com ML, e SQLi/XSS viram famílias dentro dele. Razão dele: "o tema é detecção de anomalias
HTTP usando ML". Consequências: a tabela por família vira o resultado central, o tampering
precisa ser definido na fundamentação, e o cap. 1 (título, objetivos, introdução) precisa ser
revisado. **Falta:** a alternativa descartada dita por ele, e o aval do Paulo.

### Objetivo 5 — preparação (25/11)

`treino_modelo.validar` ganhou o parâmetro `modelo=None` (padrão: o mesmo Random Forest de
sempre; outro estimador entra via `sklearn.base.clone`, um modelo limpo por fold). O Pedro
escreveu o parâmetro e o import; **o `if`/`else` das linhas 279–286 foi escrito pelo Claude a
pedido dele**: entra na declaração de uso de IA (ponto 1 do Paulo). Import do módulo testado: ok.
Nada foi retreinado; `models/` intacto. **Falta:** o script `comparar_modelos.py` e conferir
que o RF dá de novo F1 0,7824 ± 0,0088.
**Atualização, mesmo dia:** `comparar_modelos.py` escrito pelo Claude a pedido do Pedro e rodado.
RF repete 0,7824 ± 0,0088 e o limiar 0,650 (a mudança na `validar` não alterou nada). RL bem pior;
árvore não opera em FP ≤ 1%. Resultado em `docs/medicoes/comparacao_modelos.md`. **Ponto 3 do
Paulo: números prontos; a justificativa da escolha é do Pedro.**

### Ponto 4 — demonstração com o modelo avaliado (25/11)

`demo_csic.py` (escrito pelo Claude a pedido do Pedro) reenvia requisições GET reais do CSIC a
`python servidor.py` (modelo de `models/`). Rodado: legítimas 6/6 passaram, SQLi 6/6 e XSS 6/6
pela assinatura, tampering 5/6 pelo modelo. In-sample (o modelo final viu tudo) — mostra o
mecanismo, não o desempenho. README corrigido (a demo não é "treinada em português"; XSS sintético).
**Dos pedidos do Paulo que precisam de PC, não falta nenhum.** Daqui em diante é escrita.

### Revisão geral (25/11)

Pedido do Pedro: revisar tudo e corrigir o que estiver errado. O artigo ainda não existe, ficou fora.
- **Comentários do código com números errados, corrigidos:** 36,6% → 36,4% e 6,7 → 6,4 pontos
  (`servidor.py`); 6,6%/89,9% → 13,9%/79,9% (`treino_modelo.py`, `assinaturas.py`); 28,54/7,95 ms
  (sem script) → 6,31 ms de `medir_latencia.py` (`servidor.py`, `extrator.py`, `treino_modelo.py`);
  23,1% → 28,2% e 12,8% marcado sem script (`ingestao_csic.py`); 3,89%/0,97% → 3,92%/0,99%
  (`teste_falso_positivo.py`). Todos compilam.
- **Teste de falso positivo rerodado** para os dois modelos: CSIC 97,4% (transferência), demo 28,2%.
- **Documentos:** 6,6%/89,9% corrigidos no `ROTEIRO.md`, `estrutura-do-artigo.md` e `CLAUDE.md`;
  latência antiga riscada no `NECESSARIO.md`.
- **Conferido sem erro:** `texto-sistema-respostas.md` (o que foi ao Paulo) e o `resultados.json` do painel.
- **Continua pendente (não se corrige por código):** a validação manual de famílias
  (`validacao_familias.md`) é anterior às correções de 28/07 — refazer com a amostra de 50 (é do Pedro).

### Onde parou (25/11, fim da sessão)

Começou o Cap. 4 pelo método "pergunta por vez, resposta dele no NECESSARIO". Respostas 1–4 gravadas
no `NECESSARIO.md` ("Cap. 4 Metodologia — respostas do Pedro"). Parou cansado na pergunta do "Group":
**retomar por aí** (etiquetas iguais ficam do mesmo lado, para o par GET/POST não vazar). Próximas
perguntas do Cap. 4: TF-IDF por fold, limiar 0,65, por que 1% de FP. Guia visual:
https://claude.ai/artifact/PHJ6tQT4K9PUpfq2SCyRCF. Ainda falta mandar a mensagem ao Paulo.
