// ============================================================================
// MAPA DO ARTIGO
//
// Matéria-prima por capítulo: o que entra, as perguntas que o texto precisa
// responder, os elementos (tabela/figura/quadro) e os cuidados. Não tem texto
// pronto de propósito: a redação é do Pedro, e é ela que a banca vai testar.
//
// Fontes: docs/aulas/estrutura-do-artigo.md (estrutura e inventário de
// elementos) e NECESSARIO.md (frases dele, limitações).
// ============================================================================

export const DECISOES_ABERTAS = [
  {
    titulo: 'Escopo: SQLi/XSS ou anomalias HTTP?',
    porque: 'No CSIC 2010 as regras já pegam 100% de SQLi e XSS. O ganho do modelo (+45,6 pontos) está em parameter tampering, que a introdução não menciona.',
    caminhos: [
      'A — alargar o tema para anomalias em requisições HTTP (sem código novo; muda a introdução)',
      'B — medir SQLi/XSS disfarçados que as regras não pegam (uma sessão; resultado incerto)',
    ],
    com: 'Paulo',
  },
  {
    titulo: 'Objetivo específico da camada de regras',
    porque: 'Nenhum dos 7 objetivos prevê a camada de assinaturas, mas o resultado central (quem pegou cada ataque) depende dela.',
    caminhos: ['acrescentar um objetivo sobre implementar as regras e medir o quanto o ML soma a elas'],
    com: 'Paulo',
  },
  {
    titulo: 'Objetivo 5: comparar diferentes modelos',
    porque: 'Só existe Random Forest. A ablação compara grupos de features, não algoritmos.',
    caminhos: [
      'cumprir: treinar mais 2 classificadores com a mesma validação',
      'reescrever o objetivo',
    ],
    com: 'você',
  },
  {
    titulo: 'Data exata da entrega e se as 20 páginas contam referências',
    porque: 'Define quanto tempo sobra para escrever e quanto texto falta.',
    caminhos: [],
    com: 'Paulo',
  },
];

// Ordem em que vale escrever: primeiro o que já tem dado, por último o que
// resume o resto.
export const ORDEM_DE_ESCRITA = ['metodologia', 'resultados', 'desenvolvimento',
  'conclusao', 'fundamentacao', 'trabalhos', 'introducao', 'resumo'];

export const CAPITULOS = [
  {
    id: 'introducao',
    numero: '1',
    titulo: 'Introdução',
    paginas: '1,5–2',
    estado: 'entregue, precisa revisar',
    itens: [
      'Passar do futuro ("serão treinados") para o passado, com números no lugar das promessas',
      'Reescrever a pergunta de pesquisa (hoje ela é de construção: "como desenvolver…")',
      'Colocar citações (autor, ano) nas afirmações sobre WAFs tradicionais',
      'Acrescentar o parágrafo de delimitação: o que o trabalho não faz',
      'Ajustar o problema 2 da seção 1.2 (falso positivo) — o ML não resolve, ele aumenta',
      'Suavizar ou tirar a promessa de detectar zero-day',
      'Acrescentar o objetivo da camada de regras (depois de falar com o Paulo)',
      'Corrigir: algoritimo → algoritmo · traffics analysis → traffic analysis · system`s → system\'s',
    ],
    perguntas: [
      'Qual é a pergunta que o trabalho responde, em uma frase, que só pode ser respondida com um número?',
      'Por que somar uma camada de ML a um WAF de regras, em vez de trocar um pelo outro?',
      'O que o leitor deve saber, já na primeira página, que o trabalho não cobre?',
    ],
    elementos: [],
    cuidados: [
      'A introdução promete o que os resultados entregam. Reescreva por último, depois do capítulo 6.',
    ],
  },
  {
    id: 'fundamentacao',
    numero: '2',
    titulo: 'Fundamentação teórica',
    paginas: '2',
    estado: '3 frases escritas (seção 2.4)',
    itens: [
      '2.1 Segurança web: o que é SQL injection, XSS e parameter tampering',
      '2.2 WAF: como funciona a detecção por assinaturas, e por que ela não pega o que não conhece',
      '2.3 Machine Learning: classificação, Random Forest, precisão / recall / F1 / falso positivo',
      '2.3 Por que acurácia engana com classes desbalanceadas (usar como contraexemplo)',
      '2.4 Vazamento de dados: terminar o parágrafo com os três exemplos',
    ],
    perguntas: [
      'O que um WAF de assinaturas faz bem e onde ele falha? (com citação)',
      'O que o Random Forest devolve quando dá "0,87"? É uma probabilidade de verdade?',
      'Qual pergunta cada métrica responde? (precisão: quando barra, acerta? recall: dos ataques, quantos pega?)',
      'Quais são as três formas de vazamento neste projeto?',
    ],
    frases: [
      {
        onde: 'acurácia (13/08)',
        texto: 'A acurácia não distingue um detector que funciona de um que não faz nada. No cenário testado, um classificador que libera todo o tráfego obtém os mesmos 95% do detector avaliado.',
      },
      {
        onde: 'seção 2.4, vazamento (19/08) — 3 de 6 frases',
        texto: 'O vazamento de dados (data leakage) ocorre quando os dados de teste vazam e vão para os dados de treino. O recall fica alto no experimento, mas em produção não repete esse valor. Se em produção o modelo não teria a informação, no treino não pode ter essa informação.',
      },
    ],
    elementos: [],
    cuidados: [
      'As seções 2.1 a 2.3 dependem das referências do capítulo 3. Sem fichamento, vira [CITAR] em toda linha.',
      'Fundamentação é curta (2 páginas). Não encher para chegar nas 20.',
    ],
  },
  {
    id: 'trabalhos',
    numero: '3',
    titulo: 'Trabalhos relacionados',
    paginas: '1,5–2',
    estado: 'não começou — é o gargalo',
    itens: [
      'Achar 8 a 12 artigos, começando pelos que usam o CSIC 2010',
      'Fichar cada um numa linha (modelo de tabela abaixo)',
      'Gerar a referência ABNT na hora, no MORE (more.ufsc.br)',
      'Procurar a lacuna: artigos que dão um F1 global sem separar o tipo de ataque',
    ],
    perguntas: [
      'O que cada trabalho fez, com que dados, e que número tirou?',
      'Em que o seu trabalho é diferente de cada um? (essa coluna vira o capítulo)',
    ],
    elementos: ['fichamento'],
    cuidados: [
      'Só entra na lista de referências o que for citado no texto.',
    ],
  },
  {
    id: 'metodologia',
    numero: '4',
    titulo: 'Metodologia',
    paginas: '4–5',
    estado: 'a escrever — comece por aqui',
    itens: [
      'O dataset: CSIC 2010, quantas requisições, quantas entraram e por quê (Tabela 1)',
      'Os tipos de ataque e como cada um foi rotulado (Tabela 2)',
      'Normalização: o que ela desfaz e o que não desfaz (entidade HTML)',
      'As features em três blocos (Quadro 1)',
      'A validação: 5 partes, agrupadas por payload, TF-IDF ajustado em cada parte',
      'O limiar: teto de 1% de falso positivo, escolhido nas previsões de teste',
    ],
    perguntas: [
      'De 51.480 requisições com payload, por que só 32.808 entraram? O que aconteceu com as outras?',
      'Como você sabe que o que chamou de SQLi é SQLi? (amostra conferida à mão)',
      'Por que n-gramas de caracteres e não de palavras?',
      'Por que agrupar por payload? O que acontece com o par GET/POST se não agrupar?',
      'Por que o limiar não é 0,5? Por que o critério é o F1 dentro do teto, e não o recall máximo?',
    ],
    frases: [
      {
        onde: 'deduplicação (06/10) — rascunho, falta revisar',
        texto: 'foram removidas 18.672 requisições duplicadas para o modelo não decorar',
      },
    ],
    fatos: [
      ['97.065 requisições lidas dos três arquivos (36.000 + 36.000 + 25.065), igual ao publicado pelo CSIC', 'ingestao_csic.py (log)'],
      ['45.585 (47,0%) não têm nenhum parâmetro; 5.585 delas são ataques: 22,3% dos 25.065 ataques ficam fora do alcance do WAF, que só olha valores de parâmetro', 'ingestao_csic.py (log)'],
      ['51.480 com parâmetro → 18.672 cópias idênticas removidas (36,3%) → 32.808 usadas', 'ingestao_csic.py (log)'],
      ['Cópia idêntica = mesmo texto, mesmo path, mesmo método e mesmo rótulo', 'ingestao_csic.py (CHAVE_DEDUP)'],
      ['32.808 = 18.620 normais + 14.188 anômalas (43,2% de ataques)', 'avaliacao_hibrida.py'],
      ['16.034 grupos de payload (path + texto), 2,0 requisições por grupo em média, no máximo 5', 'ingestao_csic.py (log)'],
      ['266 grupos (1,66%) têm o mesmo payload rotulado como normal e como ataque', 'ingestao_csic.py (log)'],
      ['114 requisições com byte nulo, protegidas para não serem cortadas ao salvar em CSV', 'ingestao_csic.py (log)'],
      ['Tampering 11.332 (79,9%) · SQLi 1.018 (7,2%) · XSS 952 (6,7%) · CRLF 388 · SSI/comando 384 · controle/nulo 114', 'ingestao_csic.py (log)'],
      ['Validação: StratifiedGroupKFold com 5 folds, semente 42; cada fold com 43,2% de ataques', 'treino_modelo.py (log)'],
      ['Limiar 0,650: maior F1 entre os limiares com falso positivo ≤ 1%, nas previsões out-of-fold', 'treino_modelo.py (log)'],
    ],
    elementos: ['tab1', 'tab2', 'quadro1'],
    cuidados: [
      'A família de cada ataque foi dada por expressões regulares — diga isso aqui, não esconda no fim.',
      'Rotulagem conferida em 40 amostras, não nas 50 que o roteiro pedia.',
      'O servidor usa uma normalização própria, diferente da usada no treino. Resolver antes de afirmar que treino e produção veem a mesma coisa.',
    ],
  },
  {
    id: 'desenvolvimento',
    numero: '5',
    titulo: 'Desenvolvimento',
    paginas: '2–3',
    estado: 'a escrever',
    itens: [
      'A arquitetura: requisição → normalização → regras → modelo → aplicação (Figura 1)',
      'O middleware: roda antes da rota, por isso a rota vulnerável nunca executa o ataque barrado',
      'As 24 regras: o que procuram (estrutura, não palavra solta)',
      'Por que a ordem das camadas não muda a decisão, e por que ela existe mesmo assim',
      'Os dois modelos: o do CSIC (artigo) e o de demonstração (apresentação)',
    ],
    perguntas: [
      'Se a cascata decide igual a "regra OU modelo", para que serve a ordem?',
      'Por que existe um segundo modelo só para a demonstração?',
      'O que o middleware NÃO inspeciona? (path, headers, corpo)',
    ],
    fatos: [
      ['24 regras de assinatura; nenhum falso positivo nas 18.620 requisições normais', 'avaliacao_hibrida.py'],
      ['Modelo final: Random Forest, 100 árvores, 62 features, treinado nas 32.808 requisições', 'treino_modelo.py → model_metadata.json'],
      ['Modelo de demonstração: limiar 0,46, treinado em 20.000 exemplos de outros datasets', 'models/demo/model_metadata.json (copiado do projeto antigo)'],
      ['Com o modelo do CSIC, as 4 frases normais em português foram barradas (p de 0,88 a 0,98); com o demo, 26 de 26 exemplos deram o previsto', 'verificar_roteiro.py (06/10)'],
    ],
    elementos: ['fig1', 'tab6'],
    cuidados: [
      'Latência: nenhum script deste repositório mediu. Não cite 31,94 ms nem 3,6× até existir o script.',
    ],
  },
  {
    id: 'resultados',
    numero: '6',
    titulo: 'Resultados',
    paginas: '4–5 (a seção mais longa)',
    estado: 'dados prontos, texto a escrever',
    itens: [
      'Validação cruzada do modelo, fold a fold (Tabela 3)',
      'A curva do limiar e o ponto escolhido (Figura 2)',
      'Cada bloco de features ajuda? (Tabela 4)',
      'As configurações: só regras, só modelo, juntas (Tabela 5)',
      'Quem pegou cada ataque — o resultado central (Tabela 7)',
      'Recall por tipo de ataque (Tabela 8)',
      'Um bloqueio explicado pelo SHAP (Figura 3)',
    ],
    perguntas: [
      'Por que o F1 do modelo é 0,782 na Tabela 3 e 0,740 na Tabela 5, se é o mesmo modelo?',
      'Quantos ataques só o modelo pegou? E quanto tráfego normal ele barrou para isso? (sempre os dois juntos)',
      'Em que tipo de ataque está o ganho do modelo? O que isso diz sobre o tema do trabalho?',
      'O que a célula "nenhuma pegou" (40%) significa para quem opera o WAF?',
    ],
    fatos: [
      ['Validação cruzada, limiar 0,5: F1 0,782 ± 0,009 · precisão 92,9% · recall 67,6% · FP 3,9% · ROC-AUC 0,888', 'treino_modelo.py'],
      ['Ablação (F1): só contexto 0,431 · só TF-IDF 0,669 · heurísticas + TF-IDF 0,718 · os três blocos 0,782', 'treino_modelo.py (log)'],
      ['No limiar 0,650: recall 59,4% · precisão 97,9% · FP 0,99% (184 requisições normais) · F1 0,740', 'treino_modelo.py / avaliacao_hibrida.py'],
      ['Só as regras: precisão 100% · recall 23,4% · FP 0%', 'avaliacao_hibrida.py'],
      ['Regras + modelo: recall 59,8% · FP 0,99% — todo o falso positivo vem do modelo', 'avaliacao_hibrida.py'],
      ['Dos 14.188 ataques: as duas pegaram 23,0% · só as regras 0,3% (49) · só o modelo 36,4% (5.167) · nenhuma 40,2% (5.707)', 'avaliacao_hibrida.py'],
      ['Ganho do modelo: tampering +45,6 pp (4,0% → 49,6%) · SQLi e XSS +0,0 pp (as regras já pegam 100%)', 'avaliacao_hibrida.py'],
      ['Com limiar 0,5 em vez de 0,65, o recall em tampering sobe de 49,6% para 59,6%, com FP de 3,9%', 'treino_modelo.py (log)'],
    ],
    elementos: ['tab3', 'fig2', 'tab4', 'tab5', 'tab7', 'tab8', 'fig3'],
    cuidados: [
      'Detecção ganha e falso positivo introduzido aparecem sempre juntos. Um sem o outro é propaganda.',
      'Não use "acurácia" como resultado.',
      'Todo número da tabela tem a fonte (script). Se não souber o script, não cite.',
    ],
  },
  {
    id: 'conclusao',
    numero: '7',
    titulo: 'Conclusão, limitações e trabalhos futuros',
    paginas: '2',
    estado: 'a escrever',
    itens: [
      'Responder a pergunta de pesquisa com o número',
      'Limitações, uma por parágrafo curto (lista abaixo)',
      'Trabalhos futuros que saem das limitações',
    ],
    perguntas: [
      'O que os números provam? E o que eles NÃO provam?',
      'Se fosse refazer, o que mudaria primeiro?',
    ],
    elementos: ['limitacoes'],
    cuidados: [
      'Declarar o limite antes da banca desarma a pergunta. Limite descoberto pela banca vira falha.',
    ],
  },
  {
    id: 'resumo',
    numero: '—',
    titulo: 'Resumo e abstract',
    paginas: '0,5',
    estado: 'escrever por último',
    itens: [
      'Reescrever com os resultados de verdade (até 200 palavras)',
      'Traduzir para o abstract',
      'Conferir as 3 a 5 palavras-chave',
    ],
    perguntas: ['Objetivo, método, resultado (com número) e conclusão — uma ou duas frases cada.'],
    elementos: [],
    cuidados: ['Resumo escrito antes do resultado promete o que o trabalho não entrega.'],
  },
];

export const LIMITACOES = [
  'O ganho do modelo em SQLi e XSS no CSIC 2010 é zero: as regras já pegam 100%. O ganho está em tampering.',
  'Os SQLi/XSS do CSIC se concentram em poucos modelos de ataque, repetidos em várias rotas (validar_familias.py). A contagem exata de modelos ainda precisa ser conferida: o texto do script cita um total antigo.',
  'O tipo de cada ataque foi atribuído por expressões regulares, parecidas com as regras: o recall das regras por tipo é otimista.',
  'O modelo do CSIC barra texto comum em português: ele aprendeu o tráfego de uma loja. Outro site exigiria retreinar.',
  'A demonstração usa outro modelo, treinado em dados fora do escopo do artigo.',
  'Zero-day não foi medido; os ataques disfarçados testados são de tipos conhecidos.',
  'As 24 regras não são o OWASP CRS: um WAF real teria centenas.',
  'O WAF inspeciona só os valores dos parâmetros — não o path, headers nem corpo. 5.585 dos 25.065 ataques (22,3%) não têm parâmetro nenhum (ingestao_csic.py, log).',
  'Com o modelo demo, 11 de 39 frases normais difíceis foram barradas (teste_falso_positivo.py).',
  'Latência não medida por script neste repositório.',
];

export const FICHAMENTO_COLUNAS = ['Referência', 'O que fizeram', 'Dataset', 'Resultado',
  'Em que meu trabalho difere'];

export const QUADRO1 = [
  ['Heurísticas de segurança', '5', 'comprimento, caracteres especiais, palavras-chave SQL, palavras-chave XSS, sinais de URL-encode'],
  ['Contexto HTTP', '7', 'nº de parâmetros, tem corpo, content-length, nº de headers, método (GET, POST, PUT em one-hot)'],
  ['TF-IDF', '50', 'pedaços de 2 a 3 caracteres mais frequentes no treino (char_wb, ajustado em cada fold)'],
];

export const ABNT = [
  'Times New Roman ou Arial 12 · entrelinhas 1,5 · recuo de parágrafo 1,25 cm',
  'Margens: 3 cm em cima e à esquerda, 2 cm embaixo e à direita',
  'Seções: "2 SEÇÃO" em maiúsculas e negrito · subseções: "2.1 Subseção" em negrito',
  'Tabela (números): só 3 linhas horizontais, laterais abertas. Quadro (texto): grade fechada',
  'Título acima ("Tabela 1 – …", só o rótulo em negrito) · fonte abaixo ("Fonte: Elaboração própria")',
  'Tabelas e quadros numerados separadamente, e sempre citados no texto',
  'Citação: (Sobrenome, 2026) · dois ou três autores: (A; B; C, 2026) · mais de três: (A et al., 2026)',
  'Citação direta de 4 linhas ou mais: recuo de 4 cm, fonte 11, sem aspas',
  'Referências: só as citadas, padrão RDBCI (gerar no MORE UFSC)',
];
