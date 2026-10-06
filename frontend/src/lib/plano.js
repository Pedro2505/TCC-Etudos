// ============================================================================
// PLANO: reunião com o orientador e semanas até a defesa.
// As datas de outubro assumem entrega em 31/10 — confirmar na reunião de quarta.
// ============================================================================

export const REUNIAO = {
  titulo: 'Reunião com o Paulo — quarta, 07/10',
  preparar: [
    'Treinar em voz alta, em 1 minuto: o que o sistema faz, o resultado principal (ganho e custo) e o problema do escopo',
    'Abrir o site no notebook antes de sair (servidor + frontend) e conferir a demo (aba Testar ao vivo → Conferir antes de apresentar)',
    'Deixar aberta a aba Artigo → 6. Resultados → Tabela 8 (recall por tipo de ataque): é ela que mostra o problema do escopo',
    'Levar a entrega parcial (TCC, 1 entrega.docx)',
  ],
  perguntas: [
    { id: 'datas', texto: 'Qual a data exata da entrega do artigo e da defesa?' },
    { id: 'paginas', texto: 'As 20 páginas contam referências e a parte pré-textual (resumo, abstract)?' },
    { id: 'escopo', texto: 'Escopo: as regras já pegam 100% de SQLi/XSS no CSIC e o ganho do ML está em tampering. Alargo o tema para anomalias HTTP (A), ou meço SQLi/XSS disfarçados (B)?' },
    { id: 'objetivo-regras', texto: 'Posso acrescentar um objetivo específico sobre a camada de regras? O resultado central depende dela.' },
    { id: 'objetivo5', texto: 'Objetivo 5 ("comparar diferentes modelos"): treino mais 2 classificadores, ou posso reescrever o objetivo?' },
    { id: 'ia', texto: 'Qual a regra da Unimar sobre uso de IA no TCC, e o que preciso declarar?' },
    { id: 'zeroday', texto: 'A introdução promete zero-day, que não foi medido. Tiro a promessa ou declaro como limitação?' },
  ],
  depois: 'Depois da reunião: contar ao Claude o que foi decidido, para atualizar o CONTINUAR.md e o plano.',
};

export const SEMANAS = [
  {
    id: 's1', periodo: '06 a 11/10',
    foco: 'Decidir e começar pela Metodologia',
    tarefas: [
      'Reunião com o Paulo (quarta) e anotar as respostas aqui',
      'Manual: módulos 1 a 4, e os cartões de cada um',
      'Escrever a parte de dados da Metodologia (Tabela 1, deduplicação)',
      'Fichamento: os 2 primeiros artigos com CSIC 2010',
      'Auditoria do treino_modelo.py (passos 2 a 5 do protocolo)',
    ],
  },
  {
    id: 's2', periodo: '12 a 18/10',
    foco: 'Aplicar as decisões e escrever os Resultados',
    tarefas: [
      'Aplicar a decisão de escopo (mexer na introdução, ou medir os disfarçados)',
      'Objetivo 5: treinar os 2 classificadores, ou reescrever o objetivo',
      'Normalização: corrigir o servidor, ou medir o impacto e declarar',
      'Terminar a Metodologia e escrever os Resultados (capítulo 6)',
      'Manual: módulos 5 a 8, e os cartões',
      'Fichamento: mais 4 artigos',
    ],
  },
  {
    id: 's3', periodo: '19 a 25/10',
    foco: 'Os outros capítulos',
    tarefas: [
      'Desenvolvimento (5) e Conclusão com limitações (7)',
      'Fundamentação (2) e Trabalhos relacionados (3), com o fichamento completo',
      'Manual: módulos 9 a 11',
      'Primeiro simulado de banca com o Claude (20 minutos, com interrupção)',
      'Auditoria do avaliacao_hibrida.py e do assinaturas.py',
    ],
  },
  {
    id: 's4', periodo: '26 a 31/10',
    foco: 'Fechar e entregar',
    tarefas: [
      'Reescrever a Introdução com os resultados reais',
      'Resumo e abstract (por último)',
      'Formatação ABNT, quadros e tabelas, referências no MORE',
      'Revisão final lendo em voz alta',
      'Entregar',
    ],
  },
  {
    id: 's5', periodo: 'Novembro, até a defesa',
    foco: 'Apresentação e banca',
    tarefas: [
      'Slides (10 a 12), com a Tabela 7 e a Tabela 8 no centro',
      'Ensaio cronometrado da apresentação, gravando no celular',
      'Rodar a conferência da demo no dia anterior',
      'Segundo e terceiro simulados de banca com o Claude',
      'Todos os cartões em "sei explicar"',
    ],
  },
];

export const HABITO = [
  '20 minutos por dia de cartões em voz alta (aba Banca)',
  'Commitar ao fim de cada sessão',
  'Número novo só entra no artigo com o script que o gerou',
];
