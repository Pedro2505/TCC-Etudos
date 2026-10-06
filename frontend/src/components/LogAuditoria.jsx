import React from 'react';

/**
 * Log de auditoria em tempo real.
 *
 * Este componente carrega a minha melhor história do projeto. A primeira versão deste
 * painel era HTML puro e eu escrevia o payload interceptado com .innerHTML. Ao testar
 * `<img src=x onerror=alert(1)>`, o backend bloqueou corretamente com HTTP 403 — e um
 * popup abriu na minha tela de todo jeito. Eu tinha um DOM-based XSS no log de
 * auditoria do meu próprio WAF.
 *
 * Aqui uso JSX, que escapa o conteúdo por padrão. Nunca dangerouslySetInnerHTML.
 * A lição: blindar o backend com IA não isenta o frontend de sanitização, e o elo mais
 * fraco da corrente era o meu painel.
 */
export default function LogAuditoria({ registros, onLimpar }) {
  return (
    <section className="log-auditoria">
      <div className="painel-cabecalho">
        <h2>Log de auditoria</h2>
        {registros.length > 0 && (
          <button className="btn-limpar" onClick={onLimpar}>
            limpar ({registros.length})
          </button>
        )}
      </div>

      <p className="log-legenda">
        A cor do status é sempre semântica: <span className="amostra amostra-bloqueado">403 bloqueado</span>{' '}
        <span className="amostra amostra-permitido">200 permitido</span>. Se o caso vem de
        uma bateria, o selo de conformidade ao lado diz se o resultado bateu com o que eu
        previ — é ele que indica se o teste passou.
      </p>

      <p className="log-legenda">
        Todo bloqueio mostra <strong>qual camada resolveu</strong>.{' '}
        <span className="amostra amostra-camada1">camada 1</span> é uma assinatura, com o
        nome da regra.{' '}
        <span className="amostra amostra-camada2">camada 2</span> é o modelo, que só vê o
        que a primeira deixou passar.
      </p>

      {registros.length === 0 && (
        <p className="log-vazio">
          Nenhuma requisição ainda. Use as baterias ao lado ou os formulários acima.
        </p>
      )}

      <ol className="lista-log">
        {registros.map((r) => {
          const status = classeStatus(r);
          const conformidade = classeConformidade(r);
          return (
            <li
              key={r.id}
              className={`entrada entrada-${status}${
                conformidade === 'divergente' ? ' entrada-divergente' : ''
              }`}
            >
              <div className="entrada-topo">
                <span className={`badge badge-${status}`}>
                  {r.status === 0 ? 'ERRO' : r.status}
                </span>
                <span className="entrada-decisao">{textoDecisao(r)}</span>

                {r.camada && (
                  <span className={`selo selo-${r.camada === 'assinatura' ? 'camada1' : 'camada2'}`}>
                    {r.camada === 'assinatura'
                      ? `camada 1 · ${r.regraId}`
                      : 'camada 2 · modelo'}
                  </span>
                )}

                {/* Conformidade de CAMADA. É a verificação que corresponde à tese:
                    na Bateria 5 eu afirmo que a assinatura NÃO pega e o modelo pega.
                    Se a camada 1 resolvesse aqui, o caso não provaria nada — então
                    o painel confere e avisa. */}
                {camadaDivergente(r) && (
                  <span className="selo selo-divergente">
                    ✗ camada inesperada (previ {rotuloCamada(r.camadaEsperada)})
                  </span>
                )}

                {conformidade && (
                  <span className={`selo selo-${conformidade}`}>
                    {conformidade === 'conforme'
                      ? `✓ conforme (previ ${r.esperado})`
                      : `✗ divergente (previ ${r.esperado})`}
                  </span>
                )}

                <span className="entrada-hora">{r.hora}</span>
              </div>

              <span className="entrada-rota">{r.rota}</span>

              {/* Payload renderizado como texto. JSX escapa < e > automaticamente. */}
              <code className="entrada-payload">{r.payloadEnviado}</code>

              <div className="entrada-metricas">
                {r.regraNome && (
                  <span title="Assinatura que casou com o payload (camada 1)">
                    regra: <strong>{r.regraNome}</strong> ({r.regraFamilia})
                  </span>
                )}
                {r.probabilidade != null && (
                  <span title="Probabilidade de ataque atribuída pelo modelo">
                    p = <strong>{r.probabilidade.toFixed(3)}</strong>
                    {r.limiar != null && ` (limiar ${r.limiar.toFixed(3)})`}
                  </span>
                )}
                {r.latenciaBackend != null && (
                  <span title="Tempo de análise do WAF, medido no servidor">
                    WAF: <strong>{r.latenciaBackend.toFixed(1)} ms</strong>
                  </span>
                )}
                <span title="Round-trip completo, medido no navegador">
                  round-trip: {r.latenciaCliente.toFixed(0)} ms
                </span>
              </div>

              <p className="entrada-mensagem">{r.mensagem}</p>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

/**
 * Cor do status HTTP, sempre semântica.
 *
 * Eu tinha colorido por conformidade aqui, e ficou confuso: um 403 que batia o esperado
 * aparecia em verde, contradizendo o significado do próprio código. Agora o status manda
 * na cor e a conformidade tem selo próprio — dois sinais independentes, sem conflito.
 */
function classeStatus(r) {
  if (r.status === 0 || r.status === 503) return 'erro';
  if (r.status === 403) return 'bloqueado';
  return 'permitido';
}

/** Só existe quando o caso declarou um resultado esperado (veio de uma bateria). */
function classeConformidade(r) {
  if (r.esperado == null || !r.ok) return null;
  return r.status === r.esperado ? 'conforme' : 'divergente';
}

/** Só avalia quando o caso declarou uma camada esperada e a requisição completou. */
function camadaDivergente(r) {
  if (r.camadaEsperada === undefined || !r.ok) return false;
  return (r.camada ?? null) !== r.camadaEsperada;
}

function rotuloCamada(camada) {
  if (camada === 'assinatura') return 'camada 1';
  if (camada === 'modelo') return 'camada 2';
  return 'nenhuma';
}

function textoDecisao(r) {
  if (r.status === 0) return 'falha de conexão';
  if (r.status === 503) return 'erro interno — fail-close';
  if (r.status === 403) return 'requisição bloqueada pelo WAF';
  return 'requisição liberada';
}
