// ============================================================================
// PERGUNTAS DE BANCA
//
// Cada pergunta tem:
//   pista  -> a próxima pergunta a se fazer, se travar (não é a resposta)
//   chaves -> palavras/números que a resposta não pode deixar de ter
//   onde   -> onde conferir no projeto
//
// Treino: responder EM VOZ ALTA, com cronômetro, antes de abrir a ajuda.
// Fontes: ROTEIRO.md (perguntas por etapa), CONTINUAR.md, NECESSARIO.md e o
// que apareceu na sessão de 06/10.
// ============================================================================

export const TEMAS = {
  dados: 'Dados',
  vazamento: 'Validação e vazamento',
  metricas: 'Métricas e limiar',
  modelo: 'Modelo e features',
  arquitetura: 'Arquitetura',
  resultados: 'Resultados e escopo',
};

export const PERGUNTAS = [
  // ---------------------------------------------------------------- dados
  {
    id: 'descartes', tema: 'dados', perigo: 2,
    pergunta: 'Quantas requisições você descartou, e por quê?',
    pista: 'São dois cortes, um depois do outro. Qual é o primeiro? Qual é o segundo?',
    chaves: ['97.065 lidas', 'sem parâmetro: 45.585', 'cópias idênticas: 18.672', '32.808 usadas'],
    onde: 'logs/ingestion_csic.log · aba Artigo → Tabela 1',
  },
  {
    id: 'duplicata', tema: 'dados', perigo: 2,
    pergunta: 'O par GET/POST do mesmo ataque é uma duplicata? O drop_duplicates resolve?',
    pista: 'As duas linhas têm o mesmo texto. O que é diferente entre elas?',
    chaves: ['método diferente', 'não é cópia idêntica', 'agrupar', 'grupo = path + texto'],
    onde: 'ingestao_csic.py (CHAVE_DEDUP e grupo_payload)',
  },
  {
    id: 'proporcao', tema: 'dados', perigo: 3,
    pergunta: 'Seu trabalho é sobre SQLi e XSS. Quanto do CSIC 2010 é SQLi e XSS?',
    pista: 'Some SQLi e XSS e divida pelo total de ataques usados.',
    chaves: ['1.970 de 14.188', '~13,9%', 'tampering 79,9%'],
    onde: 'aba Artigo → Tabela 2',
  },
  {
    id: 'rotulo-familia', tema: 'dados', perigo: 3,
    pergunta: 'Como você sabe que o que chamou de SQLi é SQLi de verdade?',
    pista: 'Quem deu o tipo de cada ataque: o CSIC ou você? Como você conferiu?',
    chaves: ['o CSIC só diz normal/anômalo', 'expressões regulares', 'conferência manual (40 amostras)', 'viés a favor das regras'],
    onde: 'validar_familias.py · docs/medicoes/validacao_familias.md',
  },
  {
    id: 'path', tema: 'dados', perigo: 2,
    pergunta: 'Por que 22,3% dos ataques do CSIC ficaram fora do experimento?',
    pista: 'Se a requisição não tem parâmetro nenhum, onde está o ataque?',
    chaves: ['5.585 de 25.065', 'ataque no path', 'o WAF só olha valores de parâmetro', 'limite da arquitetura'],
    onde: 'logs/ingestion_csic.log · ingestao_csic.py (docstring de somente_com_payload)',
  },
  {
    id: 'ambiguos', tema: 'dados', perigo: 1,
    pergunta: '266 grupos têm o mesmo payload como normal e como ataque. Como isso é possível?',
    pista: 'O grupo junta mesmo path e mesmo texto. O que sobra de diferente entre as duas requisições?',
    chaves: ['ainda não investigado', 'algo fora do payload decide o rótulo', 'o modelo não tem como separar esses'],
    onde: 'logs/ingestion_csic.log ("Grupos contendo as duas classes")',
  },

  // ---------------------------------------------------------------- vazamento
  {
    id: 'tfidf-fit', tema: 'vazamento', perigo: 3,
    pergunta: 'Você fez o fit do TF-IDF antes ou depois de dividir treino e teste?',
    pista: 'Na validação, existe um vocabulário ou cinco?',
    chaves: ['dentro de cada fold', 'fit só no treino', 'transform no teste', '5 vocabulários'],
    onde: 'treino_modelo.py, função montar_matriz',
  },
  {
    id: 'parecidas', tema: 'vazamento', perigo: 3,
    pergunta: 'Você tem certeza de que não há requisição parecida no treino e no teste?',
    pista: 'Qual é a chave de grupo, e o que ela obriga a cair do mesmo lado?',
    chaves: ['StratifiedGroupKFold', 'grupo = path + payload', 'GET e POST juntos', '16.034 grupos'],
    onde: 'treino_modelo.py (validar) · ingestao_csic.py (grupo_payload)',
  },
  {
    id: 'recall-decorou', tema: 'vazamento', perigo: 3,
    pergunta: 'Seu recall alto prova que o modelo não decorou?',
    pista: 'Os dois alunos tiraram 98. Pela nota, dá para saber quem colou?',
    chaves: ['nenhuma métrica denuncia vazamento', 'impedir antes de medir', 'deduplicação + grupo + TF-IDF por fold'],
    onde: 'NECESSARIO.md §1 (sessão de 06/10)',
  },
  {
    id: 'kfold', tema: 'vazamento', perigo: 2,
    pergunta: 'Por que 5 folds e não uma divisão treino/teste só?',
    pista: 'Se uma divisão desse 0,72, como você saberia se foi o modelo ou a sorte?',
    chaves: ['cada requisição testada uma vez', 'média ± desvio', '0,782 ± 0,009'],
    onde: 'aba Artigo → Tabela 3',
  },
  {
    id: 'semente', tema: 'vazamento', perigo: 2,
    pergunta: 'Por que a semente 42?',
    pista: 'Se você testasse 10 sementes e ficasse com a melhor, que forma de vazamento seria?',
    chaves: ['fixada antes', 'não escolhida pelo resultado', 'desvio entre folds pequeno'],
    onde: 'treino_modelo.py (SEMENTE) · diario.md 19/08',
  },

  // ---------------------------------------------------------------- métricas
  {
    id: 'precisao-boa', tema: 'metricas', perigo: 3,
    pergunta: 'Seu sistema tem 97,9% de precisão. Isso é bom?',
    pista: 'Quantos % do seu dataset são ataques? E num site real?',
    chaves: ['43,2% de ataques no dataset', 'em produção, bem menos', 'a mesma taxa de FP derruba a precisão'],
    onde: 'ROTEIRO.md, Etapa 0',
  },
  {
    id: 'acuracia', tema: 'metricas', perigo: 2,
    pergunta: 'Por que você não usa acurácia?',
    pista: 'O porteiro que dorme e deixa todo mundo entrar: qual é a acurácia dele?',
    chaves: ['libera tudo = 95%', 'classes desbalanceadas', 'não separa detector bom de inútil'],
    onde: 'NECESSARIO.md §1 (frase de 13/08)',
  },
  {
    id: 'limiar', tema: 'metricas', perigo: 3,
    pergunta: 'De onde veio o 0,650?',
    pista: 'Qual foi o teto de falso positivo? E em quais previsões você varreu os limiares?',
    chaves: ['FP ≤ 1%', 'previsões out-of-fold', 'maior F1 dentro do teto'],
    onde: 'treino_modelo.py (escolher_limiar) · aba Resultados → curvas',
  },
  {
    id: 'f1-teto', tema: 'metricas', perigo: 2,
    pergunta: 'Por que escolher pelo F1 dentro do teto, e não pelo maior recall?',
    pista: 'O maior recall dentro do teto sempre empurra o limiar para onde?',
    chaves: ['para o limite do teto', 'gasta FP para ganhar pouco recall', 'F1 pune a perda de precisão'],
    onde: 'treino_modelo.py (docstring de escolher_limiar)',
  },
  {
    id: 'f1-diferente', tema: 'metricas', perigo: 2,
    pergunta: 'Por que o F1 do modelo é 0,782 numa tabela e 0,740 em outra?',
    pista: 'Qual limiar cada tabela usa?',
    chaves: ['0,5 × 0,65', 'média por fold × previsões juntas', 'mais FP aceito → mais recall'],
    onde: 'aba Artigo → Tabelas 3 e 5',
  },
  {
    id: 'proba', tema: 'metricas', perigo: 2,
    pergunta: 'O modelo deu 0,87. Isso é 87% de chance de ser ataque?',
    pista: 'O que as 100 árvores fazem para chegar no 0,87?',
    chaves: ['fração de árvores que votou ataque', 'não é probabilidade calibrada', 'por isso o limiar é escolhido'],
    onde: 'NECESSARIO.md §2, item 1',
  },

  // ---------------------------------------------------------------- modelo
  {
    id: 'rf-features', tema: 'modelo', perigo: 2,
    pergunta: 'Por que forçar cada árvore a ver só uma parte das features melhora a floresta?',
    pista: 'Se todas as árvores olhassem as mesmas features fortes, elas errariam igual ou diferente?',
    chaves: ['árvores diferentes', 'erros diferentes', 'o voto cancela os erros'],
    onde: 'pendente desde 13/08 (CONTINUAR.md)',
  },
  {
    id: 'ngramas', tema: 'modelo', perigo: 2,
    pergunta: 'Por que n-gramas de caractere e não de palavra?',
    pista: "<script> e <ScRiPt>; e os pedaços '; e -- . Isso são palavras?",
    chaves: ['ofuscação', 'fragmentos que não são palavras', 'atravessa fronteira de palavra'],
    onde: 'ROTEIRO.md, Etapa 4',
  },
  {
    id: 'ablacao', tema: 'modelo', perigo: 2,
    pergunta: 'Cada bloco de features ajuda? Prove.',
    pista: 'O que acontece com o F1 quando se tira cada bloco?',
    chaves: ['só TF-IDF 0,669', 'heurísticas + TF-IDF 0,718', 'os três 0,782', 'só contexto 0,431'],
    onde: 'aba Artigo → Tabela 4',
  },
  {
    id: 'so-rf', tema: 'modelo', perigo: 3,
    pergunta: 'Seu objetivo diz "comparar diferentes modelos". Onde está a comparação?',
    pista: 'Isso foi feito? Se não, o que você decidiu?',
    chaves: ['objetivo 5', 'só Random Forest', 'cumprir ou reescrever (decisão em aberto)'],
    onde: 'aba Artigo → decisões em aberto',
  },

  // ---------------------------------------------------------------- arquitetura
  {
    id: 'skew', tema: 'arquitetura', perigo: 3,
    pergunta: 'A sua normalização é a mesma no treino e em produção?',
    pista: 'Abra servidor.py (decodificador_ofuscacao) e ingestao_csic.py (normalizar_payload). É a mesma função?',
    chaves: ['hoje não', 'training/serving skew', 'corrigir ou declarar com a medida do impacto'],
    onde: 'servidor.py linha ~84 · CONTINUAR.md item 10',
  },
  {
    id: 'cascata', tema: 'arquitetura', perigo: 2,
    pergunta: 'Se a cascata decide igual a "regra OU modelo", para que serve a ordem?',
    pista: 'O que um bloqueio da camada 1 tem que a nota 0,87 não tem?',
    chaves: ['nome da regra (proveniência)', 'custo da inferência evitado', 'orçamento de FP fica para o modelo'],
    onde: 'servidor.py (comentário da camada 1) · NECESSARIO.md §2, item 9',
  },
  {
    id: 'demo', tema: 'arquitetura', perigo: 3,
    pergunta: 'O modelo que você está mostrando é o mesmo dos números do artigo?',
    pista: 'Qual modelo barra "pedro.almeida"?',
    chaves: ['não', 'modelo demo, outros dados', 'o do CSIC barra português', 'dizer antes de perguntarem'],
    onde: 'aba Testar ao vivo (cabeçalho) · verificar_roteiro.py',
  },
  {
    id: 'latencia', tema: 'arquitetura', perigo: 2,
    pergunta: 'Quanto tempo o WAF acrescenta em cada requisição?',
    pista: 'Qual script deste repositório mediu isso?',
    chaves: ['ainda não medido por script', 'não citar 31,94 ms', 'o tempo por requisição aparece na tela, mas não é medição'],
    onde: 'NECESSARIO.md §2b',
  },

  // ---------------------------------------------------------------- resultados
  {
    id: 'pra-que-ml', tema: 'resultados', perigo: 3,
    pergunta: 'Se as regras já pegam 100% de SQLi e XSS, para que serve o ML num trabalho sobre SQLi e XSS?',
    pista: 'Em que tipo de ataque está o ganho do modelo?',
    chaves: ['+0,0 pp em SQLi/XSS', '+45,6 pp em tampering', 'decisão de escopo (A ou B)'],
    onde: 'aba Artigo → Tabela 8',
  },
  {
    id: 'so-modelo', tema: 'resultados', perigo: 3,
    pergunta: 'Quantos ataques só o modelo pegou, e a que custo?',
    pista: 'Detecção ganha e falso positivo introduzido: sempre juntos.',
    chaves: ['5.167 (36,4%)', '184 normais barradas (0,99%)', 'todo o FP vem do modelo'],
    onde: 'aba Artigo → Tabelas 5 e 7',
  },
  {
    id: 'somar', tema: 'resultados', perigo: 2,
    pergunta: 'Você provou que somar é melhor, ou só que as duas juntas detectam mais?',
    pista: 'Juntas, o falso positivo subiu ou ficou igual? De quem ele é?',
    chaves: ['ganho com custo', 'compara regras × regras + modelo', 'FP de 0% para 0,99%'],
    onde: 'aba Artigo → Tabela 5',
  },
  {
    id: 'nenhuma', tema: 'resultados', perigo: 2,
    pergunta: '40% dos ataques nenhuma camada pegou. O seu WAF funciona?',
    pista: 'Que tipo de ataque são esses? O que você declara sobre eles?',
    chaves: ['5.707 ataques', 'quase todos tampering', 'limite declarado, não escondido'],
    onde: 'aba Resultados → as duas camadas juntas',
  },
  {
    id: 'zeroday', tema: 'resultados', perigo: 2,
    pergunta: 'Seu sistema detecta zero-day?',
    pista: 'Disfarçar um ataque conhecido é a mesma coisa que um ataque nunca visto?',
    chaves: ['não foi medido', 'ofuscação ≠ zero-day', 'vai para limitações'],
    onde: 'NECESSARIO.md §3',
  },
];
