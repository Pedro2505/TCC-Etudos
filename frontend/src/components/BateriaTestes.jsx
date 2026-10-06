import React, { useState } from 'react';
import { BATERIAS, TODOS_OS_CASOS } from '../lib/baterias';

/**
 * Baterias de teste executáveis com um clique.
 *
 * Substituí o roteiro em Markdown que eu mantinha em docs/ por esta interface. O
 * motivo é prático: na defesa eu não quero digitar payload à mão, arriscando errar
 * um caractere e ter que explicar um resultado que não era o previsto. Cada caso
 * declara o status que eu espero, e o painel marca se bateu ou divergiu.
 */
export default function BateriaTestes({ onExecutar, executando }) {
  const [expandido, setExpandido] = useState('legitimo');
  const [rodandoTudo, setRodandoTudo] = useState(false);

  async function executarBateria(casos) {
    for (const caso of casos) {
      await onExecutar(caso);
      // Pausa curta entre requisições: sem ela o log rola rápido demais para a banca
      // acompanhar, e o valor pedagógico se perde.
      await new Promise((r) => setTimeout(r, 320));
    }
  }

  async function executarTudo() {
    setRodandoTudo(true);
    await executarBateria(TODOS_OS_CASOS);
    setRodandoTudo(false);
  }

  const ocupado = executando || rodandoTudo;

  return (
    <section className="baterias">
      <div className="painel-cabecalho">
        <h2>Roteiro de demonstração</h2>
        <button
          className="btn-executar-tudo"
          onClick={executarTudo}
          disabled={ocupado}
        >
          {rodandoTudo ? 'Executando…' : `Executar as ${TODOS_OS_CASOS.length} baterias`}
        </button>
      </div>

      <p className="baterias-intro">
        Cada caso diz o status que eu espero e <strong>qual camada deveria resolver</strong>.
        A segunda parte é a que importa: bloquear as duas camadas bloqueiam, a questão é
        qual delas. Clique no payload para disparar.
      </p>

      {BATERIAS.map((bateria) => {
        const aberta = expandido === bateria.id;
        return (
          <div
            key={bateria.id}
            className={`bateria bateria-${bateria.cor}${
              bateria.destaque ? ' bateria-destaque' : ''
            }`}
          >
            <button
              className="bateria-titulo"
              onClick={() => setExpandido(aberta ? null : bateria.id)}
              aria-expanded={aberta}
            >
              <span className="seta">{aberta ? '▾' : '▸'}</span>
              <span style={{ flex: 1, minWidth: 0 }}>
                {bateria.titulo}
                {bateria.resumo && (
                  <span className="bateria-resumo">{bateria.resumo}</span>
                )}
              </span>
              {bateria.destaque && <span className="marca-tese">a tese</span>}
              <span className="bateria-contagem">{bateria.casos.length} casos</span>
            </button>

            {aberta && (
              <div className="bateria-corpo">
                <p className="bateria-objetivo">{bateria.objetivo}</p>

                <button
                  className="btn-bateria"
                  onClick={() => executarBateria(bateria.casos)}
                  disabled={ocupado}
                >
                  Executar esta bateria
                </button>

                <ul className="lista-casos">
                  {bateria.casos.map((caso, i) => (
                    <li key={i} className="caso">
                      <div className="caso-topo">
                        <button
                          className="caso-payload"
                          onClick={() => onExecutar(caso)}
                          disabled={ocupado}
                          title="Clique para enviar este payload"
                        >
                          {/* JSX escapa por padrão. Foi exatamente aqui que eu errei
                              antes, no painel HTML antigo: usei .innerHTML e o payload
                              de XSS executou na minha própria tela de auditoria. */}
                          <code>{caso.payload}</code>
                        </button>
                        <span
                          className={`esperado ${
                            caso.esperado === 403 ? 'esperado-bloqueio' : 'esperado-passe'
                          }`}
                        >
                          espero {caso.esperado}
                        </span>
                        {/* A camada esperada é a expectativa que corresponde à tese:
                            na Bateria 5 eu afirmo que a camada 1 NÃO resolve. */}
                        {caso.camadaEsperada !== undefined && (
                          <span className={`camada-esperada ${classeCamada(caso.camadaEsperada)}`}>
                            {rotuloCamada(caso.camadaEsperada)}
                          </span>
                        )}
                      </div>
                      <p className="caso-porque">
                        {caso.esperadoEhFalha && (
                          <strong className="marca-limite">limitação conhecida — </strong>
                        )}
                        {caso.porque}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

function rotuloCamada(camada) {
  if (camada === 'assinatura') return 'camada 1';
  if (camada === 'modelo') return 'camada 2';
  return 'nenhuma camada';
}

function classeCamada(camada) {
  if (camada === 'assinatura') return 'camada-esperada-1';
  if (camada === 'modelo') return 'camada-esperada-2';
  return 'camada-esperada-0';
}
