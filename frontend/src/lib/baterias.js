// ============================================================================
// ROTEIRO DE DEMONSTRAÇÃO — WAF EM DUAS CAMADAS
//
// Cada caso declara duas coisas: o status HTTP que eu espero e qual camada
// deveria resolver. A segunda é a que interessa. Se eu só checasse "bloqueou",
// a Bateria 5 não provaria nada, porque bloquear é o que as duas camadas fazem.
//
// Testei todos os payloads contra o modelo de demonstração antes de colocar
// aqui. Nenhum é chute.
// ============================================================================

export const BATERIAS = [
  {
    id: 'legitimo',
    titulo: 'Bateria 1 — Tráfego legítimo',
    cor: 'verde',
    resumo: 'Primeiro: o WAF não pode atrapalhar quem está comprando.',
    objetivo:
      'Começo por aqui porque um WAF que bloqueia cliente não serve, por melhor que ' +
      'seja o recall. Nenhuma das duas camadas deve reagir a nada nesta bateria.',
    casos: [
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: 'tênis de corrida masculino azul',
        esperado: 200,
        camadaEsperada: null,
        porque:
          'Busca normal de loja. Nenhum caractere que quebre sintaxe, nenhuma ' +
          'palavra-chave.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: 'pedro.almeida',
        esperado: 200,
        camadaEsperada: null,
        porque: 'Login comum. Ponto no meio não é sinal de nada.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: 'joao.silva@email.com',
        esperado: 200,
        camadaEsperada: null,
        porque:
          'O @ e o ponto não entram na minha contagem de caracteres especiais. Não ' +
          'servem para quebrar SQL nem HTML.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: 'O design do TCC ficou incrível, parabéns!',
        esperado: 200,
        camadaEsperada: null,
        porque: 'Texto livre com acento. Vírgula e exclamação não pesam.',
      },
    ],
  },

  {
    id: 'sqli',
    titulo: 'Bateria 2 — SQL Injection',
    cor: 'vermelho',
    resumo: 'Ataque catalogado. A camada 1 resolve e diz qual regra pegou.',
    objetivo:
      'São ataques com sintaxe conhecida. A camada 1 resolve todos sem nem chamar o ' +
      'modelo, e o log mostra a regra que disparou. É o que um WAF de assinaturas bem ' +
      'feito já faz, e é por isso que eu mantive ele no sistema.',
    casos: [
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "' OR 1=1--",
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'O bypass de login mais manjado que existe. A aspa fecha o literal, o OR 1=1 ' +
          'deixa a condição sempre verdadeira e o -- comenta o resto. Regra SQLI-001.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "admin' UNION SELECT username, password FROM users--",
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'UNION para roubar dados: cola uma segunda consulta no resultado da primeira. ' +
          'Regra SQLI-002.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: '1; DROP TABLE usuarios;',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'O ponto e vírgula encerra a query e começa outra. Regra SQLI-003.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "';waitfor delay '0:0:15';--",
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Blind SQLi por tempo: o atacante não recebe dado nenhum, ele cronometra a ' +
          'resposta. Esse é o template de SQLi que mais aparece no CSIC 2010, e é o ' +
          'mesmo que a minha heurística de família não reconhecia até eu achar o bug. ' +
          'Regra SQLI-005.',
      },
    ],
  },

  {
    id: 'xss',
    titulo: 'Bateria 3 — Cross-Site Scripting',
    cor: 'vermelho',
    resumo: 'Mesma história do SQLi: sintaxe conhecida, camada 1 resolve.',
    objetivo:
      'XSS com estrutura reconhecível. Vale reparar que os quatro casos disparam regras ' +
      'diferentes. Não é uma assinatura só cobrindo tudo.',
    casos: [
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '<script>alert(document.cookie)</script>',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque: 'Tag script pegando o cookie de sessão. Regra XSS-001.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '<img src=x onerror=alert(1)>',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Não tem tag script nenhuma aqui. A imagem falha de propósito e o onerror ' +
          'roda. Quem pega é a regra de handler de evento, a XSS-002.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: 'paros" style="background:url(javascript:alert(\'XSS\'))',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Esse é o meu preferido: não tem tag nenhuma. A aspa fecha o atributo do HTML ' +
          'e injeta um style com javascript: dentro. Filtro que só procura <script> ' +
          'passa reto. Regra XSS-003.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '"><input autofocus onfocus=alert(1)>',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Escapa do atributo com "> e injeta um campo que dispara sozinho quando ganha ' +
          'foco. A vítima não precisa clicar em nada. Regra XSS-002.',
      },
    ],
  },

  {
    id: 'evasao',
    titulo: 'Bateria 4 — Evasão e ofuscação',
    cor: 'roxo',
    resumo: 'A normalização roda antes das duas camadas, então protege as duas.',
    objetivo:
      'São os mesmos ataques da Bateria 3, disfarçados. O ponto aqui não é modelo contra ' +
      'assinatura: é que eu normalizo o payload antes de qualquer decisão, então as duas ' +
      'camadas se beneficiam. Sem isso, nenhuma das duas veria o ataque.',
    casos: [
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '<ScRiPt>aLeRt(1)</sCrIpT>',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Caixa alternada, resolvida jogando tudo para minúscula. Curiosidade: o TF-IDF ' +
          'já aguentaria isso sozinho, porque <script> e <ScRiPt> compartilham quase ' +
          'todos os n-grams de 2 e 3 caracteres.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '%3Cscript%3Ealert(1)%3C%2Fscript%3E',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque: 'URL-encode simples. O middleware decodifica antes de classificar.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '%253Cscript%253Ealert(1)%253C%252Fscript%253E',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Encode duplo: %253C vira %3C e só depois vira <. Por isso eu decodifico em ' +
          'laço, até parar de mudar. Se eu chamasse unquote uma vez só, esse aqui ' +
          'passava, e passava calado.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '&#60;script&#62;alert(1)&#60;/script&#62;',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Entidade HTML. Eu preciso ser honesto nesse: eu NÃO decodifico entidade HTML. ' +
          'O que pegou foi a regra XSS-007, que casa a chamada alert(. Ou seja, deu certo ' +
          'meio por acaso. Um payload em entidade sem alert() ia passar. Está na minha ' +
          'lista de coisas a arrumar.',
      },
    ],
  },

  {
    id: 'so-modelo',
    titulo: 'Bateria 5 — O que só o modelo pega',
    cor: 'ciano',
    destaque: true,
    resumo: 'É aqui que o trabalho se justifica.',
    objetivo:
      'Essa é a bateria que importa. São ataques montados para não bater com assinatura ' +
      'nenhuma: sem a palavra OR, sem tag script, sem terminador reconhecível. A camada 1 ' +
      'deixa passar e o modelo segura. É o mesmo efeito que eu medi no CSIC, onde 36,4% ' +
      'dos ataques só o modelo pegou.',
    casos: [
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "admin'||'1'='1",
        esperado: 403,
        camadaEsperada: 'modelo',
        porque:
          'Mesma tautologia de sempre, mas com concatenação (||) no lugar do OR. Minha ' +
          'regra procura as palavras or/and seguidas de número igual a número, então não ' +
          'casa. O modelo bloqueia com p≈0,64 porque a forma da coisa continua sendo a de ' +
          'uma injeção, mesmo sem a palavra.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "admin'/**/oR/**/1",
        esperado: 403,
        camadaEsperada: 'modelo',
        porque:
          'O OR picado por comentário de bloco. O banco ignora o /**/ e executa o OR ' +
          'normalmente. A minha regex usa \\bor\\b e não enxerga palavra nenhuma ali. ' +
          'Esse é o caso que eu uso para explicar onde exatamente a assinatura quebra.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "1' ORDER BY 9--",
        esperado: 403,
        camadaEsperada: 'modelo',
        porque:
          'Contagem de colunas, que é o passo antes de montar um UNION SELECT. Não tem ' +
          'nenhuma palavra da minha lista, e o -- vem colado num número, o que escapa da ' +
          'regra de comentário. O modelo dá p≈0,97.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: '1 AND (SELECT 1)=1',
        esperado: 403,
        camadaEsperada: 'modelo',
        porque:
          'Tem SELECT, mas não tem FROM, e a minha regra exige o par. Depois do AND vem ' +
          'parêntese em vez de número, então a regra de tautologia também não pega. ' +
          'Modelo: p≈0,81.',
      },
      {
        rota: '/api/login_alvo',
        parametro: 'usuario',
        payload: "' oorr 1=1",
        esperado: 403,
        camadaEsperada: 'modelo',
        porque:
          'Truque contra WAF que apaga a palavra "or": se ele apagar, sobra "or". A minha ' +
          'camada 1 não apaga nada, então ela simplesmente não reconhece e libera. O ' +
          'modelo pega com p≈0,74.',
      },
    ],
  },

  {
    id: 'limites',
    titulo: 'Bateria 6 — Onde ele erra',
    cor: 'amarelo',
    resumo: 'Prefiro mostrar antes de me perguntarem.',
    objetivo:
      'Aqui estão as falhas que eu conheço. Repara que todo falso positivo vem da camada ' +
      '2. A camada 1 não errou nenhuma vez, nem aqui nem nas 18.620 requisições legítimas ' +
      'do CSIC.',
    casos: [
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: 'aprenda SELECT e JOIN em SQL',
        esperado: 403,
        camadaEsperada: 'modelo',
        esperadoEhFalha: true,
        porque:
          'Falso positivo (p≈0,97). É um texto didático falando de SQL, não atacando. ' +
          'Repara que a camada 1 acerta em não reagir, porque não tem estrutura de ' +
          'injeção. Quem erra é o modelo, que conta palavra-chave sem saber se é menção ' +
          'ou uso. Para resolver eu teria que olhar o nome do parâmetro junto.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: 'math: (2+3)*4 = 20',
        esperado: 403,
        camadaEsperada: 'modelo',
        esperadoEhFalha: true,
        porque:
          'Falso positivo (p≈0,85). Parêntese, igual e asterisco dão a mesma contagem de ' +
          'caracteres especiais de uma injeção. É o limite de feature que só conta coisa ' +
          'e não olha contexto.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '0x3c7363726970743e',
        esperado: 200,
        esperadoEhFalha: true,
        porque:
          'Falso negativo. Isso é <script> escrito em hexadecimal, e nenhuma das duas ' +
          'camadas pega: eu não decodifico hex, e para o modelo é só uma string ' +
          'alfanumérica qualquer. Ponto cego assumido, minha normalização cobre ' +
          'URL-encode e Base64, hex não.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '2/ Jamon Iberico 85 49 Anadir al carrito',
        esperado: 200,
        esperadoEhFalha: true,
        porque:
          'Falso negativo estrutural, e esse eu não tenho como resolver com a ' +
          'representação atual. No CSIC isso é ataque (o valor está fora da faixa ' +
          'válida), e existe uma requisição legítima quase igual só com outro número. ' +
          'Nenhum classificador que leia só o texto separa os dois. São 12,8% das ' +
          'anomalias, e é por isso que o recall em tampering trava em 49,6%.',
      },
      {
        rota: '/api/comentarios',
        parametro: 'texto',
        payload: '/static<script>alert(1)</script>',
        esperado: 403,
        camadaEsperada: 'assinatura',
        porque:
          'Isso aqui desligava o WAF inteiro até eu achar. A exceção para arquivo ' +
          'estático testava se "/static" aparecia no payload da query, e não no path. ' +
          'Bastava escrever a string no meio do ataque. Arrumei testando o path, e deixo ' +
          'o caso no roteiro para mostrar que a correção funcionou.',
      },
    ],
  },
];

/** Todos os casos numa lista plana, para o botão "executar tudo". */
export const TODOS_OS_CASOS = BATERIAS.flatMap((b) =>
  b.casos.map((c) => ({ ...c, bateria: b.id, tituloBateria: b.titulo })),
);
