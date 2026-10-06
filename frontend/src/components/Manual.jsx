import { useState } from 'react';
import { MODULOS } from '../lib/manual';
import ComLinks from './ComLinks';
import { rolarParaAbas } from '../lib/rolar';

/**
 * Manual de estudo: um módulo por assunto, na ordem em que um assunto depende do
 * anterior. Marcar "estudei" fica salvo no navegador.
 */
const CHAVE = 'manual-estudado-v1';

function lerEstudados() {
  try { return JSON.parse(localStorage.getItem(CHAVE)) ?? {}; } catch { return {}; }
}

export default function Manual({ onTestar, avaliacao }) {
  const [estudados, setEstudados] = useState(lerEstudados);
  const [atual, setAtual] = useState(() => MODULOS.find((m) => !lerEstudados()[m.id])?.id ?? MODULOS[0].id);

  function marcar(id) {
    setEstudados((e) => {
      const novo = { ...e, [id]: !e[id] };
      try { localStorage.setItem(CHAVE, JSON.stringify(novo)); } catch { /* sem armazenamento */ }
      return novo;
    });
  }

  function ir(id) {
    setAtual(id);
    rolarParaAbas(true);
  }

  const indice = MODULOS.findIndex((m) => m.id === atual);
  const m = MODULOS[indice];
  const proximo = MODULOS[indice + 1];
  const firmes = m.cartoes.filter((id) => avaliacao[id] === 'sei').length;

  return (
    <div className="manual">
      <p className="aviso-manual">
        Isto é para você <strong>entender</strong>. Não copie para o artigo: a banca percebe
        texto que não é seu, e a regra do trabalho é que a redação seja sua.
      </p>

      <div className="manual-corpo">
        <nav className="manual-indice" aria-label="Módulos">
          <ol>
            {MODULOS.map((mod, i) => (
              <li key={mod.id}>
                <button className={`modulo-link ${mod.id === atual ? 'ativo' : ''}`} onClick={() => ir(mod.id)}>
                  <span className={`marca ${estudados[mod.id] ? 'feito' : ''}`} aria-hidden="true">
                    {estudados[mod.id] ? '✓' : i + 1}
                  </span>
                  {mod.titulo}
                </button>
              </li>
            ))}
          </ol>
          <p className="pequeno fraco">
            {Object.values(estudados).filter(Boolean).length} de {MODULOS.length} estudados
          </p>
        </nav>

        <article className="modulo">
          <span className="pequeno fraco">Módulo {indice + 1} de {MODULOS.length}</span>
          <h3>{m.titulo}</h3>
          <p className="modulo-frase">{m.frase}</p>

          {m.blocos.map((b) => <p key={b} className="modulo-texto">{b}</p>)}

          <div className="no-projeto">
            <strong>No seu projeto</strong>
            <ul>{m.noProjeto.map((x) => <li key={x}><ComLinks texto={x} /></li>)}</ul>
          </div>

          <div className="cuidados">
            <strong>Armadilha</strong>
            <p>{m.armadilha}</p>
          </div>

          <div className="modulo-acoes">
            <label className="estudei">
              <input type="checkbox" checked={!!estudados[m.id]} onChange={() => marcar(m.id)} />
              estudei este módulo
            </label>
            {m.cartoes.length > 0 && (
              <button onClick={() => onTestar(m.cartoes)}>
                Testar com os {m.cartoes.length} cartões
                {firmes > 0 && ` (${firmes} já firmes)`}
              </button>
            )}
            {proximo && (
              <button className="discreto" onClick={() => ir(proximo.id)}>
                próximo: {proximo.titulo} →
              </button>
            )}
          </div>
        </article>
      </div>
    </div>
  );
}
