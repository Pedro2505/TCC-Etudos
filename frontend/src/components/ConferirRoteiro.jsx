import { useState } from 'react';
import { TODOS_OS_CASOS } from '../lib/baterias';
import { bateu } from '../lib/resultado';
import Veredito from './Veredito';

/**
 * Antes de apresentar: manda todos os exemplos e confere se cada um deu o
 * resultado previsto em lib/baterias.js (status e camada). Mesma conferência do
 * verificar_roteiro.py, só que pela tela.
 */
export default function ConferirRoteiro({ onEnviar, ocupado }) {
  const [rodando, setRodando] = useState(false);
  const [resultados, setResultados] = useState(null);

  async function conferir() {
    setRodando(true);
    const obtidos = [];
    for (const caso of TODOS_OS_CASOS) {
      obtidos.push(await onEnviar(caso));
      await new Promise((r) => setTimeout(r, 120));
    }
    setResultados(obtidos);
    setRodando(false);
  }

  const divergentes = resultados?.filter((r) => bateu(r) === false) ?? [];

  return (
    <section className="secao conferir">
      <div className="secao-topo">
        <h2>Conferir antes de apresentar</h2>
        <button className="discreto" onClick={conferir} disabled={ocupado || rodando}>
          {rodando ? 'conferindo…' : `mandar os ${TODOS_OS_CASOS.length} exemplos`}
        </button>
      </div>

      {resultados && divergentes.length === 0 && (
        <p className="tudo-certo">
          Os {resultados.length} exemplos deram o resultado previsto.
        </p>
      )}

      {divergentes.length > 0 && (
        <>
          <p className="aviso">
            {divergentes.length} de {resultados.length} exemplos não deram o previsto:
          </p>
          <ul className="historico">
            {divergentes.map((r) => (
              <li key={r.id} className="nao-bateu">
                <code className="payload-texto">{r.payloadEnviado}</code>
                <span className="fraco pequeno">previsto: {r.esperado}</span>
                <span className="obtido"><Veredito r={r} /></span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
