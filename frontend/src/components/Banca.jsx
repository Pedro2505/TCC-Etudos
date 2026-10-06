import { useEffect, useState } from 'react';
import { PERGUNTAS, TEMAS } from '../lib/banca';

/**
 * Treino para a banca.
 *
 * Duas formas de usar:
 *   lista     -> escolhe o tema, responde em voz alta, abre a ajuda e se avalia
 *   simulado  -> uma pergunta por vez, sorteada entre as que ainda não estão firmes,
 *                com 3 minutos no relógio
 *
 * A avaliação fica salva no navegador (localStorage).
 */
const CHAVE = 'banca-avaliacao-v1';
const NIVEIS = {
  sei: 'sei explicar',
  quase: 'mais ou menos',
  nao: 'não sei',
};

function lerAvaliacao() {
  try { return JSON.parse(localStorage.getItem(CHAVE)) ?? {}; } catch { return {}; }
}

export default function Banca() {
  const [avaliacao, setAvaliacao] = useState(lerAvaliacao);
  const [tema, setTema] = useState('todos');
  const [modo, setModo] = useState('lista');

  function avaliar(id, nivel) {
    setAvaliacao((atual) => {
      const novo = { ...atual, [id]: nivel };
      try { localStorage.setItem(CHAVE, JSON.stringify(novo)); } catch { /* sem armazenamento */ }
      return novo;
    });
  }

  const contagem = Object.keys(NIVEIS).map((n) => [n, PERGUNTAS.filter((p) => avaliacao[p.id] === n).length]);
  const semResposta = PERGUNTAS.filter((p) => !avaliacao[p.id]).length;
  const visiveis = PERGUNTAS.filter((p) => tema === 'todos' || p.tema === tema);

  return (
    <div className="banca">
      <p className="artigo-intro">
        Responda <strong>em voz alta, sem olhar nada</strong>, antes de abrir a ajuda. Mental
        não vale: mental engana. A ajuda dá uma pista e as palavras que não podem faltar,
        não a resposta pronta.
      </p>

      <div className="placar-banca">
        {contagem.map(([n, q]) => (
          <span key={n} className={`selo-nivel ${n}`}>{q} {NIVEIS[n]}</span>
        ))}
        <span className="selo-nivel">{semResposta} sem avaliar</span>
      </div>

      <div className="modos">
        <button className={modo === 'lista' ? 'ativo' : 'discreto'} onClick={() => setModo('lista')}>
          Estudar por tema
        </button>
        <button className={modo === 'simulado' ? 'ativo' : 'discreto'} onClick={() => setModo('simulado')}>
          Simulado (3 min por pergunta)
        </button>
      </div>

      {modo === 'simulado' ? (
        <Simulado avaliacao={avaliacao} avaliar={avaliar} />
      ) : (
        <>
          <div className="filtro-temas">
            {[['todos', 'Todos'], ...Object.entries(TEMAS)].map(([id, nome]) => (
              <button key={id} className={`chip ${tema === id ? 'chip-ativo' : ''}`} onClick={() => setTema(id)}>
                {nome}
              </button>
            ))}
          </div>
          <div className="cartoes">
            {visiveis.map((p) => (
              <Cartao key={p.id} p={p} nivel={avaliacao[p.id]} avaliar={avaliar} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function Cartao({ p, nivel, avaliar }) {
  const [aberto, setAberto] = useState(false);
  return (
    <article className={`cartao ${nivel ?? ''}`}>
      <div className="cartao-topo">
        <span className="pequeno fraco">{TEMAS[p.tema]}</span>
        <span className="perigo" title="quanto a banca pode cavar aqui">
          {'●'.repeat(p.perigo)}{'○'.repeat(3 - p.perigo)}
        </span>
      </div>
      <p className="cartao-pergunta">{p.pergunta}</p>

      {!aberto ? (
        <button className="discreto" onClick={() => setAberto(true)}>respondi em voz alta — abrir ajuda</button>
      ) : (
        <div className="ajuda">
          <p><strong>Pista:</strong> {p.pista}</p>
          <p><strong>Não pode faltar:</strong></p>
          <ul className="chaves">{p.chaves.map((c) => <li key={c}>{c}</li>)}</ul>
          <p className="pequeno fraco">onde conferir: <code>{p.onde}</code></p>
        </div>
      )}

      <div className="avaliar" role="group" aria-label="Como foi sua resposta">
        {Object.entries(NIVEIS).map(([n, rotulo]) => (
          <button key={n} className={`nivel ${n} ${nivel === n ? 'marcado' : ''}`}
            onClick={() => avaliar(p.id, n)} aria-pressed={nivel === n}>
            {rotulo}
          </button>
        ))}
      </div>
    </article>
  );
}

function Simulado({ avaliacao, avaliar }) {
  const [atual, setAtual] = useState(() => sortear(avaliacao));
  const [restante, setRestante] = useState(180);
  const [rodando, setRodando] = useState(false);

  useEffect(() => {
    if (!rodando || restante <= 0) return undefined;
    const t = setTimeout(() => setRestante((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [rodando, restante]);

  function proxima() {
    setAtual(sortear(avaliacao, atual?.id));
    setRestante(180);
    setRodando(false);
  }

  if (!atual) return <p className="tudo-certo">Todas as perguntas estão marcadas como "sei explicar".</p>;

  const mm = String(Math.floor(restante / 60));
  const ss = String(restante % 60).padStart(2, '0');

  return (
    <div className="simulado">
      <div className="relogio-linha">
        <span className={`relogio ${restante === 0 ? 'acabou' : ''}`}>{mm}:{ss}</span>
        <button onClick={() => setRodando((r) => !r)} disabled={restante === 0}>
          {rodando ? 'pausar' : restante === 180 ? 'começar' : 'continuar'}
        </button>
        <button className="discreto" onClick={proxima}>outra pergunta</button>
      </div>
      {restante === 0 && <p className="aviso">Tempo esgotado. Resposta longa na banca é interrompida.</p>}
      <Cartao key={atual.id} p={atual} nivel={avaliacao[atual.id]} avaliar={avaliar} />
    </div>
  );
}

/** Sorteia entre as que não estão firmes, dando mais peso às perigosas. */
function sortear(avaliacao, evitar) {
  const peso = { nao: 3, quase: 2, undefined: 2 };
  const candidatas = PERGUNTAS.filter((p) => avaliacao[p.id] !== 'sei' && p.id !== evitar);
  if (!candidatas.length) return null;
  const sacola = candidatas.flatMap((p) => Array(peso[avaliacao[p.id]] * p.perigo).fill(p));
  return sacola[Math.floor(Math.random() * sacola.length)];
}
