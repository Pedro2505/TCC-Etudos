import { useState } from 'react';
import { BATERIAS, TODOS_OS_CASOS } from '../lib/baterias';
import { bateu, chaveDoCaso } from '../lib/resultado';
import Veredito from './Veredito';

/**
 * O roteiro da apresentação: os casos de lib/baterias.js, cada um com o resultado
 * que deveria dar. O mesmo arquivo é conferido por verificar_roteiro.py antes de
 * cada apresentação.
 */
export default function Roteiro({ onEnviar, ocupado, ultimoPorChave }) {
  const [rodando, setRodando] = useState(false);

  async function rodar(casos) {
    setRodando(true);
    for (const caso of casos) {
      await onEnviar(caso);
      // pausa curta, para dar tempo de acompanhar na tela
      await new Promise((r) => setTimeout(r, 300));
    }
    setRodando(false);
  }

  const travado = ocupado || rodando;

  return (
    <section className="secao">
      <div className="secao-topo">
        <h2>Roteiro</h2>
        <button onClick={() => rodar(TODOS_OS_CASOS)} disabled={travado}>
          {rodando ? 'Rodando…' : `Rodar os ${TODOS_OS_CASOS.length} casos`}
        </button>
      </div>

      {BATERIAS.map((bateria, i) => (
        <div key={bateria.id} className="bateria">
          <div className="bateria-topo">
            <h3>
              <span className="fraco">{i + 1}.</span> {tituloCurto(bateria.titulo)}
            </h3>
            <button className="discreto" onClick={() => rodar(bateria.casos)} disabled={travado}>
              rodar estes {bateria.casos.length}
            </button>
          </div>
          {bateria.resumo && <p className="bateria-resumo">{bateria.resumo}</p>}

          <ul className="casos">
            {bateria.casos.map((caso) => {
              const r = ultimoPorChave[chaveDoCaso(caso)];
              const ok = bateu(r);
              return (
                <li key={chaveDoCaso(caso)} className={ok === false ? 'nao-bateu' : undefined}>
                  <button
                    className="payload"
                    onClick={() => onEnviar(caso)}
                    disabled={travado}
                    title={caso.porque}
                  >
                    {/* O payload aparece como texto: o JSX escapa < e >. */}
                    <code>{caso.payload}</code>
                  </button>
                  <span className="previsto">
                    {previsao(caso)}
                    {caso.esperadoEhFalha && ' (erro conhecido)'}
                  </span>
                  <span className="obtido">
                    {r ? <Veredito r={r} /> : <span className="fraco">—</span>}
                    {ok === false && <strong className="aviso"> · não bateu</strong>}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </section>
  );
}

function tituloCurto(titulo) {
  return titulo.replace(/^Bateria \d+\s*[—-]\s*/, '');
}

function previsao(caso) {
  if (caso.esperado === 200) return 'deve passar';
  if (caso.camadaEsperada === 'assinatura') return 'regra deve barrar';
  if (caso.camadaEsperada === 'modelo') return 'só o modelo barra';
  return 'deve ser barrado';
}
