import { useState } from 'react';
import { HABITO, REUNIAO, SEMANAS } from '../lib/plano';
import ComLinks from './ComLinks';

/**
 * Pauta da reunião com o orientador (com campo para anotar o que ele respondeu)
 * e o plano semana a semana até a defesa. Tudo fica salvo no navegador.
 */
const CHAVE = 'plano-v1';

function ler() {
  try { return JSON.parse(localStorage.getItem(CHAVE)) ?? {}; } catch { return {}; }
}

export default function Plano() {
  const [estado, setEstado] = useState(ler);

  function gravar(chave, valor) {
    setEstado((e) => {
      const novo = { ...e, [chave]: valor };
      try { localStorage.setItem(CHAVE, JSON.stringify(novo)); } catch { /* sem armazenamento */ }
      return novo;
    });
  }

  return (
    <div className="plano">
      <section className="bloco">
        <h3>{REUNIAO.titulo}</h3>

        <h4>Antes de ir</h4>
        <Checklist itens={REUNIAO.preparar} prefixo="prep" estado={estado} gravar={gravar} />

        <h4>Perguntas para ele (anote a resposta embaixo de cada uma)</h4>
        <ol className="pauta">
          {REUNIAO.perguntas.map((p) => (
            <li key={p.id}>
              <p>{p.texto}</p>
              <label className="so-leitor" htmlFor={`resp-${p.id}`}>Resposta do orientador</label>
              <textarea
                id={`resp-${p.id}`}
                rows={2}
                value={estado[`resp:${p.id}`] ?? ''}
                onChange={(e) => gravar(`resp:${p.id}`, e.target.value)}
                placeholder="o que o Paulo respondeu"
              />
            </li>
          ))}
        </ol>
        <p className="pequeno fraco">{REUNIAO.depois}</p>
      </section>

      <section className="bloco">
        <h3>Semana a semana até a defesa</h3>
        <p className="bloco-explicacao">
          As datas de outubro supõem entrega em 31/10. Confirme na reunião e ajuste.
        </p>
        <div className="semanas">
          {SEMANAS.map((s) => {
            const feitas = s.tarefas.filter((_, i) => estado[`${s.id}:${i}`]).length;
            return (
              <div key={s.id} className="semana">
                <div className="semana-topo">
                  <strong>{s.periodo}</strong>
                  <span className="pequeno fraco">{feitas}/{s.tarefas.length}</span>
                </div>
                <span className="semana-foco">{s.foco}</span>
                <Checklist itens={s.tarefas} prefixo={s.id} estado={estado} gravar={gravar} />
              </div>
            );
          })}
        </div>
      </section>

      <section className="bloco">
        <h3>Todo dia</h3>
        <ul className="lista-simples">{HABITO.map((h) => <li key={h}><ComLinks texto={h} /></li>)}</ul>
      </section>
    </div>
  );
}

function Checklist({ itens, prefixo, estado, gravar }) {
  return (
    <ul className="checklist">
      {itens.map((item, i) => {
        const chave = `${prefixo}:${i}`;
        return (
          <li key={chave}>
            <label>
              <input type="checkbox" checked={!!estado[chave]} onChange={() => gravar(chave, !estado[chave])} />
              <span className={estado[chave] ? 'riscado' : undefined}><ComLinks texto={item} /></span>
            </label>
          </li>
        );
      })}
    </ul>
  );
}
