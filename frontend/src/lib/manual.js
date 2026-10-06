// ============================================================================
// MANUAL DE ESTUDO PARA A BANCA
//
// Um módulo por assunto. Cada um ensina a ideia com analogia, liga ao número
// do projeto, mostra a armadilha (quase sempre um erro que o Pedro já cometeu)
// e aponta os cartões da banca que testam o módulo.
//
// É material para ENTENDER. Não é texto para o artigo.
// ============================================================================

export const MODULOS = [
  {
    id: 'tese',
    titulo: 'O problema e a ideia do trabalho',
    frase: 'Um WAF de regras é preciso mas só pega o que conhece; o trabalho mede quanto uma camada de ML acrescenta a ele, e a que custo.',
    blocos: [
      'Pense na segurança de um aeroporto. O detector de metal (as regras) procura coisas que alguém já catalogou: faca, arma, \' OR 1=1--, <script>. Quando apita, quase nunca erra. Mas uma faca de cerâmica passa, porque não está na lista.',
      'O cão farejador (o modelo de ML) não tem lista. Ele aprendeu, vendo muitos passageiros, como é o "normal", e desconfia do que foge disso. Pega coisas que o detector não pega — e às vezes late para um inocente.',
      'O seu trabalho não troca o detector pelo cão. Ele coloca o cão DEPOIS do detector e mede duas coisas juntas: quantos ataques a mais foram pegos (ganho) e quantas pessoas normais passaram a ser barradas (custo). Uma sem a outra é propaganda.',
    ],
    noProjeto: [
      'Só as regras: 23,4% dos ataques, 0% de falso positivo.',
      'Regras + modelo: 59,8% dos ataques, 0,99% de falso positivo.',
      'Ganho: 5.167 ataques que só o modelo pegou (36,4%). Custo: 184 requisições normais barradas.',
    ],
    armadilha: 'Dizer "o modelo tem F1 0,78" como se fosse o resultado. O resultado é o ganho sobre as regras, com o custo do lado.',
    cartoes: ['so-modelo', 'somar', 'pra-que-ml'],
  },
  {
    id: 'dados',
    titulo: 'Os dados: o CSIC 2010',
    frase: 'Tráfego HTTP de uma loja espanhola, gerado por programa, com cada requisição marcada como normal ou anômala.',
    blocos: [
      'O CSIC 2010 vem em três arquivos de texto com requisições HTTP cruas: 36.000 normais de treino, 36.000 normais de teste e 25.065 anômalas. O seu leitor leu as 97.065, exatamente o número publicado. Isso é o primeiro sinal de que a ingestão está certa.',
      'Dois cortes reduziram o conjunto. Primeiro: 45.585 requisições não têm parâmetro nenhum (pedir uma imagem, por exemplo). O seu WAF só olha os valores dos parâmetros, então elas saem. Segundo: das 51.480 que sobraram, 18.672 eram cópias idênticas (mesmo texto, página, método e rótulo). Ficaram 32.808.',
      'Atenção à composição: dos 14.188 ataques usados, quase 80% são "parameter tampering" — valores estranhos, tipo errado, tamanho absurdo — e não SQLi nem XSS. SQLi e XSS juntos são 1.970 (13,9%). Isso importa muito para a pergunta de escopo.',
      'O CSIC só diz "normal" ou "anômalo". O tipo de cada ataque (SQLi, XSS, tampering…) foi você que atribuiu, com expressões regulares, e conferiu à mão numa amostra de 40.',
    ],
    noProjeto: [
      '97.065 lidas → 51.480 com parâmetro → 32.808 usadas',
      '5.585 ataques (22,3%) estão no path, sem parâmetro: o WAF não os vê',
      'Tampering 11.332 · SQLi 1.018 · XSS 952 · outros 886',
    ],
    armadilha: 'Achar que o drop_duplicates resolve o par GET/POST. Não resolve: o método é diferente, então as linhas não são idênticas. Isso é resolvido pelo agrupamento (módulo 6).',
    cartoes: ['descartes', 'duplicata', 'proporcao', 'rotulo-familia', 'path'],
  },
  {
    id: 'metricas',
    titulo: 'As métricas: como se mede um detector',
    frase: 'Cada métrica responde uma pergunta diferente; escolher a métrica é escolher a pergunta.',
    blocos: [
      'Tudo começa na matriz de confusão: verdadeiro positivo (ataque barrado), falso positivo (normal barrado), falso negativo (ataque que passou), verdadeiro negativo (normal que passou).',
      'Precisão responde: "quando eu barro, quantas vezes era ataque?". Recall responde: "dos ataques que existem, quantos eu peguei?". Taxa de falso positivo responde: "do tráfego normal, quanto eu atrapalhei?". F1 junta precisão e recall num número só.',
      'Acurácia engana. O porteiro que dorme e deixa todo mundo entrar tem 95% de acurácia se só 5% são ladrões. Ele não faz nada e parece ótimo.',
      'A precisão depende de quantos ataques existem. No seu dataset, 43% é ataque. Num site real, talvez 0,1%. Com a mesma taxa de falso positivo, a precisão num site real seria muito menor. Por isso "97,9% de precisão" não é "bom" sozinho.',
    ],
    noProjeto: [
      'Limiar 0,65: precisão 97,9% · recall 59,4% · falso positivo 0,99% · F1 0,740',
      'Dataset: 43,2% de ataques — muito acima de um site real',
    ],
    armadilha: 'Usar a palavra "acurácia" para qualquer número (você já fez isso duas vezes). Lembre do porteiro dorminhoco.',
    cartoes: ['precisao-boa', 'acuracia', 'proba'],
  },
  {
    id: 'rf',
    titulo: 'Random Forest',
    frase: 'Muitas árvores de decisão diferentes votam; a nota é a fração de árvores que votou "ataque".',
    blocos: [
      'Uma árvore de decisão é uma sequência de perguntas: "tem aspas? tem mais de 3 palavras SQL? o texto é longo?". Cada caminho termina em "ataque" ou "normal". Uma árvore sozinha decora o treino e erra fora dele.',
      'A floresta treina 100 árvores, cada uma com dois sorteios: um sorteio das requisições que ela vê, e um sorteio das features que ela pode usar em cada pergunta. Por isso as árvores ficam diferentes entre si.',
      'Por que árvores diferentes são melhores, se cada uma fica pior? Porque erram em lugares diferentes. Numa votação, os erros de uma são cancelados pelos acertos das outras. Se todas fossem iguais, errariam juntas.',
      'A nota 0,87 quer dizer: 87 das 100 árvores votaram "ataque". Não é "87% de chance" no sentido estatístico — as árvores aprenderam do mesmo dado e erram parecido. Por isso o corte (limiar) precisa ser escolhido, e não herdado do 0,5.',
    ],
    noProjeto: ['100 árvores · 62 features · treinado nas 32.808 requisições'],
    armadilha: 'Falar de "neurônios" (é árvore, não rede neural) ou chamar a nota de "acurácia".',
    cartoes: ['rf-features', 'proba', 'so-rf'],
  },
  {
    id: 'features',
    titulo: 'As features: o que o modelo enxerga',
    frase: 'O modelo não lê texto; ele recebe 62 números sobre cada requisição, em três blocos.',
    blocos: [
      'Heurísticas (5): contagens que você escolheu por conhecimento de segurança — tamanho, caracteres especiais, palavras de SQL, palavras de XSS, sinais de URL-encode. São as que você consegue explicar uma a uma.',
      'Contexto HTTP (7): dados da requisição que não estão no texto — método (GET/POST/PUT, cada um como uma coluna 0/1, para o modelo não achar que PUT é "maior" que GET), número de parâmetros, tamanho do corpo, número de headers.',
      'TF-IDF (50): o texto é fatiado em pedaços de 2 a 3 caracteres, e cada pedaço vira uma coluna com um peso. Pedaço comum em todo lugar pesa pouco; pedaço raro pesa mais. São pedaços de caractere, e não palavras, porque ataque não respeita palavra: \'; e -- não são palavras, e <ScRiPt> e <script> viram os mesmos pedaços depois das minúsculas.',
      'Ablação é tirar um bloco e ver o quanto o resultado cai. É a prova de que cada bloco paga o próprio custo.',
    ],
    noProjeto: ['F1 por bloco: só contexto 0,431 · só TF-IDF 0,669 · heurísticas + TF-IDF 0,718 · os três 0,782'],
    armadilha: 'Dizer que testou outros tamanhos de TF-IDF. Não testou (50 foi fixado). Se perguntarem, diga que é trade-off de tempo por requisição e que não mediu outras opções.',
    cartoes: ['ngramas', 'ablacao'],
  },
  {
    id: 'vazamento',
    titulo: 'Validação honesta e vazamento',
    frase: 'Vazamento é o teste "saber" algo do treino; a régua: se em produção o modelo não teria a informação, no treino não pode ter tido.',
    blocos: [
      'Dois alunos tiram 98. Um estudou, o outro recebeu o gabarito antes. Pela nota, não dá para saber quem colou. É isso o vazamento: ele não parece erro, parece sucesso. Recall, precisão e F1 sobem todos juntos — nenhuma métrica denuncia. A única defesa é impedir antes de medir.',
      'Forma 1 — TF-IDF ajustado antes de dividir. Ele aprende "quais pedaços são raros" olhando o teste também. Solução: ajustar dentro de cada fold, só no treino. São 5 vocabulários, um por fold.',
      'Forma 2 — o par GET/POST. O CSIC manda o mesmo ataque como GET e como POST. Se um cai no treino e o outro no teste, o modelo reconhece o que já viu. Solução: agrupar por path + texto (16.034 grupos) e usar StratifiedGroupKFold, que nunca separa um grupo.',
      'Forma 3 — escolher o limiar olhando o teste. Solução: usar as previsões out-of-fold, em que cada requisição foi julgada pelo modelo que NÃO a viu no treino.',
      'Por que 5 folds e não uma divisão só: uma divisão dá um número com sorte dentro. Com 5, cada requisição é testada uma vez e você tem média ± desvio (0,782 ± 0,009). Desvio pequeno quer dizer resultado estável.',
    ],
    noProjeto: ['StratifiedGroupKFold(5), semente 42 · 16.034 grupos · TF-IDF por fold · limiar nas previsões out-of-fold'],
    armadilha: 'Três que você já cometeu: escolher a semente 42 "porque o F1 deu maior" (é a forma 3); achar que drop_duplicates resolve o par GET/POST; e dizer que o recall serve para saber se o modelo decorou.',
    cartoes: ['tfidf-fit', 'parecidas', 'recall-decorou', 'kfold', 'semente'],
  },
  {
    id: 'limiar',
    titulo: 'O limiar de decisão',
    frase: 'O modelo dá uma nota; o limiar é o corte a partir do qual ele barra, e foi escolhido com um teto de 1% de falso positivo.',
    blocos: [
      'O sklearn barra a partir de 0,5 por padrão. Isso não é uma escolha, é um default. Num WAF, barrar um cliente custa caro (é o que faz desligarem o WAF), então o critério foi: entre os cortes que barram no máximo 1% do tráfego normal, ficar com o de maior F1.',
      'Por que F1 e não o maior recall? O maior recall dentro do teto sempre empurra o corte até encostar no 1%, mesmo quando o ganho é mínimo. O F1 pune quando a precisão cai, e evita gastar falso positivo à toa.',
      'Na curva: corte baixo pega mais ataques e incomoda mais gente normal; corte alto o contrário. Em 0,5 o FP é 3,9%; em 0,65, 0,99%; em 0,8, 0,28%.',
      'É isso que explica o F1 0,782 (corte 0,5) e o 0,740 (corte 0,65): o mesmo modelo, com cortes diferentes. Com o corte mais alto, ele aceita menos falso positivo e pega menos ataques.',
    ],
    noProjeto: ['Limiar 0,650 · FP 0,99% · recall 59,4% · escolhido nas previsões out-of-fold'],
    armadilha: 'Dizer que o limiar foi "ajustado para dar o melhor resultado". Foi escolhido por um critério declarado ANTES (teto de 1%), nas previsões de teste de cada fold.',
    cartoes: ['limiar', 'f1-teto', 'f1-diferente'],
  },
  {
    id: 'arquitetura',
    titulo: 'A arquitetura: o middleware e as duas camadas',
    frase: 'Um middleware intercepta cada requisição antes da rota: normaliza, testa as regras e, se nenhuma casar, consulta o modelo.',
    blocos: [
      'O WAF roda antes do roteamento. Se rodasse depois, a rota vulnerável já teria executado o SQL. A aplicação é vulnerável de propósito: a proteção inteira está no middleware.',
      'A normalização desfaz disfarces: decodifica %XX em laço (%253C vira %3C e depois <), tenta Base64 e põe em minúsculas. Ela precisa ser a MESMA no treino e no servidor, senão o modelo opera sobre um texto diferente do que aprendeu (training/serving skew). Hoje o servidor tem uma função própria: isso precisa ser resolvido ou declarado.',
      'Em decisão, a cascata é igual a "regra OU modelo": a ordem não aumenta o recall. A ordem existe por três motivos: o bloqueio da regra sai com nome (SQLI-001), o que é auditável; o que a regra resolve não paga o custo do modelo; e todo o orçamento de falso positivo fica para o modelo.',
      'Existem dois modelos. O do CSIC, de onde saem os números do artigo, barra texto comum em português porque aprendeu o "normal" de uma loja espanhola. A demonstração usa outro modelo, treinado com tráfego em português. Diga isso antes que perguntem.',
    ],
    noProjeto: ['24 regras, zero falso positivo · demo: 26 de 26 exemplos certos · o do CSIC barra "pedro.almeida" com nota 0,92'],
    armadilha: 'Dizer que a ordem das camadas melhora a detecção. Não melhora: melhora proveniência e custo.',
    cartoes: ['skew', 'cascata', 'demo', 'latencia'],
  },
  {
    id: 'resultados',
    titulo: 'Os resultados: como ler as tabelas',
    frase: 'A tabela central é "quem pegou cada ataque"; a pergunta mais perigosa é em que tipo de ataque está o ganho.',
    blocos: [
      'Dos 14.188 ataques: as duas camadas pegaram 23,0%; só as regras 0,3%; só o modelo 36,4%; nenhuma 40,2%. A célula "só o modelo" é a contribuição; a "nenhuma" é a limitação.',
      'Agora separe por tipo. Em SQLi e XSS, as regras já pegam 100%: o modelo acrescenta zero. O ganho inteiro (+45,6 pontos) está em tampering. Se o tema é "SQLi e XSS", o ML não ajudou no tema. Isso é a ameaça número 1 e precisa da decisão de escopo.',
      'O recall das regras por tipo é otimista: o tipo foi dado por expressões regulares parecidas com as próprias regras. Os números imunes a isso são os gerais (Tabelas 5 e 7), medidos contra o rótulo do CSIC.',
      'Os 40% que ninguém pegou são quase todos tampering que, na representação usada, se parece com tráfego normal. Isso vai para as limitações, com o número.',
    ],
    noProjeto: ['Só o modelo: 5.167 (36,4%) · nenhuma: 5.707 (40,2%) · tampering 4,0% → 49,6%'],
    armadilha: 'Falar do ganho sem falar do custo, ou falar "o sistema detecta 100% de SQLi" como mérito do ML.',
    cartoes: ['so-modelo', 'somar', 'nenhuma', 'pra-que-ml'],
  },
  {
    id: 'limites',
    titulo: 'Limitações: como falar delas',
    frase: 'Limite declarado por você desarma a pergunta; limite descoberto pela banca vira falha.',
    blocos: [
      'Diga a limitação antes, com número, e diga o que faria para resolver. Exemplo de estrutura: "isto não foi medido / isto vale só para este dataset — por causa de X — o próximo passo seria Y".',
      'As principais: ganho zero em SQLi/XSS no CSIC; poucos modelos de ataque repetidos; tipo atribuído por regex; o modelo do CSIC não generaliza para português; a demo usa outro modelo; zero-day não foi medido; 24 regras não são o OWASP CRS; o WAF não olha path, headers nem corpo (22,3% dos ataques); latência sem script.',
      'Zero-day: disfarçar um ataque conhecido não é zero-day. Zero-day é um tipo de ataque nunca visto. O trabalho não mediu isso.',
    ],
    noProjeto: ['Lista completa na aba Artigo → capítulo 7'],
    armadilha: 'Defender o indefensável. "Não medi isso" é uma resposta respeitável; inventar não é.',
    cartoes: ['zeroday', 'nenhuma', 'ambiguos'],
  },
  {
    id: 'postura',
    titulo: 'Como se comportar na banca',
    frase: 'Resposta curta, com número e de onde ele veio; se não souber, diga que não mediu.',
    blocos: [
      'Responda em até 3 frases. A banca interrompe resposta longa, e a interrupção quase sempre vem com uma pergunta mais difícil.',
      'Todo número que você falar, saiba o script que o gerou. Se não souber: "não medi isso". É a sua regra número 1.',
      'Para cada decisão, tenha a alternativa descartada: "fiz X; a opção óbvia era Y; não usei Y porque…". É isso que separa quem fez de quem viu ser feito.',
      'Se não entender a pergunta, peça para repetir. Se a pergunta tiver uma premissa errada, corrija a premissa com calma antes de responder.',
      'Treine falando: em voz alta, com cronômetro, gravando no celular. Pensar a resposta na cabeça engana.',
    ],
    noProjeto: ['Use o Simulado desta aba e peça ao Claude um "simulado de banca" com interrupção'],
    armadilha: 'Ler os cartões até "reconhecer" a resposta. Reconhecer não é saber explicar.',
    cartoes: [],
  },
];
