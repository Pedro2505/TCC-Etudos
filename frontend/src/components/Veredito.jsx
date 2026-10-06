import { numero } from '../lib/resultado';

/**
 * Uma linha dizendo o que o WAF fez com a requisição, e quem decidiu.
 *
 * Usado na lista do roteiro, no teste manual e no histórico, para que as três
 * partes da tela falem a mesma língua.
 */
export default function Veredito({ r }) {
  if (!r) return null;

  if (r.status === 0) {
    return <span className="veredito erro">sem conexão com o servidor</span>;
  }
  if (r.status === 503) {
    return <span className="veredito erro">erro interno, requisição barrada</span>;
  }

  if (r.status === 403) {
    return (
      <span className="veredito barrado">
        <strong>barrado</strong>{' '}
        {r.camada === 'assinatura' ? (
          <>
            pela regra <code>{r.regraId}</code>
            {r.regraNome && <span className="fraco"> ({r.regraNome})</span>}
          </>
        ) : (
          <>
            pelo modelo, p = {numero(r.probabilidade, 2)}
            {r.limiar != null && <span className="fraco"> (limiar {numero(r.limiar, 2)})</span>}
          </>
        )}
        <Tempo ms={r.latenciaBackend} />
      </span>
    );
  }

  return (
    <span className="veredito liberado">
      <strong>liberado</strong>
      <Tempo ms={r.latenciaBackend} />
    </span>
  );
}

function Tempo({ ms }) {
  if (ms == null) return null;
  return <span className="fraco"> · {numero(ms, 1)} ms</span>;
}
