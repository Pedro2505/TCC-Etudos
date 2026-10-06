import { numero } from '../lib/resultado';

/**
 * A última requisição atravessando o WAF, etapa por etapa.
 *
 * Cada etapa aparece com um pequeno atraso em relação à anterior, para dar para
 * acompanhar com os olhos onde a requisição parou.
 */
export default function Pipeline({ r }) {
  if (r && r.status === 0) {
    return (
      <div className="pipeline-erro">
        Não consegui falar com o servidor. Ele está rodando na porta 8000?
      </div>
    );
  }

  const regraBarrou = r?.camada === 'assinatura';
  const modeloBarrou = r?.camada === 'modelo';
  const barrado = r?.status === 403 || r?.status === 503;

  const etapas = [
    {
      titulo: 'Entrada',
      faz: 'o valor como chegou',
      estado: r ? 'passou' : 'vazia',
      corpo: r && (
        <>
          <code className="texto-payload">{r.payloadEnviado}</code>
          <span className="fraco pequeno">enviado para {r.rota}</span>
        </>
      ),
    },
    {
      titulo: 'Normalização',
      faz: 'desfaz %XX, Base64 e maiúsculas',
      estado: r ? 'passou' : 'vazia',
      corpo: r && <Normalizacao r={r} />,
    },
    {
      titulo: 'Regras',
      faz: '24 padrões de ataque conhecidos',
      estado: !r ? 'vazia' : regraBarrou ? 'barrou' : 'passou',
      corpo: r && (regraBarrou ? (
        <>
          <span className="destaque-barrado">casou com {r.regraId}</span>
          <span className="pequeno">{r.regraNome}</span>
        </>
      ) : (
        <span>nenhuma das 24 regras casou</span>
      )),
    },
    {
      titulo: 'Modelo',
      faz: 'Random Forest dá uma nota de 0 a 1',
      estado: !r ? 'vazia' : regraBarrou ? 'pulada' : modeloBarrou ? 'barrou' : 'passou',
      corpo: r && (regraBarrou ? (
        <span className="fraco">não precisou ser consultado: a regra já decidiu</span>
      ) : (
        <Nota p={r.probabilidade} limiar={r.limiar} />
      )),
    },
    {
      titulo: 'Resultado',
      faz: 'barra ou deixa chegar na aplicação',
      estado: !r ? 'vazia' : barrado ? 'barrou' : 'liberou',
      corpo: r && (barrado ? (
        <>
          <span className="decisao barrado">Barrado · {r.status}</span>
          <span className="pequeno">a aplicação nunca recebeu esse valor</span>
        </>
      ) : (
        <>
          <span className="decisao liberado">Liberado · 200</span>
          {r.respostaApp && (
            <>
              <span className="pequeno fraco">a aplicação respondeu:</span>
              <code className="resposta-app">{r.respostaApp}</code>
            </>
          )}
        </>
      )),
    },
  ];

  return (
    <div className="pipeline" key={r?.id ?? 'vazio'}>
      {etapas.map((e, i) => (
        <div key={e.titulo} className={`etapa ${e.estado}`} style={{ '--i': i }}>
          <span className="etapa-titulo">
            <span className="etapa-num">{i + 1}</span> {e.titulo}
          </span>
          <span className="etapa-faz">{e.faz}</span>
          {e.corpo && <div className="etapa-corpo">{e.corpo}</div>}
        </div>
      ))}
      {r?.latenciaBackend != null && (
        <p className="pipeline-tempo fraco">
          o WAF levou {numero(r.latenciaBackend, 1)} ms para decidir
        </p>
      )}
      {!r && <p className="pipeline-tempo fraco">Envie um valor para ver por onde ele passa e onde para.</p>}
    </div>
  );
}

function Normalizacao({ r }) {
  if (r.normalizado == null) return <span className="fraco">—</span>;
  const mudou = r.normalizado !== r.payloadEnviado;
  const soCaixa = mudou && r.normalizado === r.payloadEnviado.toLowerCase();
  return (
    <>
      <code className="texto-payload">{r.normalizado}</code>
      <span className="pequeno fraco">
        {!mudou ? 'nada a desfazer' : soCaixa ? 'passou para minúsculas' : 'disfarce desfeito'}
      </span>
    </>
  );
}

/** A nota do modelo numa régua de 0 a 1, com o limiar marcado. */
function Nota({ p, limiar }) {
  if (p == null) return <span className="fraco">—</span>;
  const acima = limiar != null && p >= limiar;
  return (
    <div className="nota-modelo">
      <div className="regua" role="img"
        aria-label={`nota ${numero(p, 2)}, limiar ${numero(limiar, 2)}`}>
        <div className={`regua-valor ${acima ? 'acima' : 'abaixo'}`} style={{ width: `${p * 100}%` }} />
        {limiar != null && <div className="regua-limiar" style={{ left: `${limiar * 100}%` }} />}
      </div>
      <span className="pequeno">
        nota <strong>{numero(p, 2)}</strong> {acima ? '≥' : '<'} limiar {numero(limiar, 2)}
      </span>
    </div>
  );
}
