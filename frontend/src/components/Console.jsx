import { useState } from 'react';
import { BATERIAS } from '../lib/baterias';

/**
 * Onde se escolhe o que mandar: um campo livre ou um dos exemplos prontos.
 *
 * As duas rotas da aplicação são vulneráveis de propósito:
 *   login       monta a query SQL concatenando o que foi digitado
 *   comentário  devolve o texto sem escapar HTML
 */
const ALVOS = {
  login: { rota: '/api/login_alvo', parametro: 'usuario', rotulo: 'Login', dica: 'vai para uma query SQL' },
  comentario: { rota: '/api/comentarios', parametro: 'texto', rotulo: 'Comentário', dica: 'volta para a página como HTML' },
};

const NOMES_GRUPO = {
  legitimo: 'Normais',
  sqli: 'SQL injection',
  xss: 'XSS',
  evasao: 'Disfarçados',
  'so-modelo': 'Só o modelo pega',
  limites: 'Onde ele erra',
};

/** `children` é o caminho da requisição: fica entre o campo e os exemplos. */
export default function Console({ onEnviar, ocupado, children }) {
  const [alvo, setAlvo] = useState('login');
  const [valor, setValor] = useState('');

  function enviar(e) {
    e.preventDefault();
    if (!valor.trim()) return;
    const { rota, parametro } = ALVOS[alvo];
    onEnviar({ rota, parametro, payload: valor });
  }

  function usarExemplo(caso) {
    setAlvo(caso.rota === ALVOS.login.rota ? 'login' : 'comentario');
    setValor(caso.payload);
    onEnviar(caso);
  }

  return (
    <section className="console">
      <form onSubmit={enviar}>
        <div className="alvos" role="radiogroup" aria-label="Onde enviar">
          {Object.entries(ALVOS).map(([id, a]) => (
            <button
              key={id}
              type="button"
              role="radio"
              aria-checked={alvo === id}
              className={alvo === id ? 'ativo' : undefined}
              onClick={() => setAlvo(id)}
            >
              {a.rotulo} <span className="fraco">· {a.dica}</span>
            </button>
          ))}
        </div>

        <div className="linha-envio">
          <label className="so-leitor" htmlFor="valor">Valor a enviar</label>
          <input
            id="valor"
            type="text"
            value={valor}
            onChange={(e) => setValor(e.target.value)}
            placeholder="digite qualquer coisa, ou clique num exemplo abaixo"
            spellCheck={false}
            autoComplete="off"
          />
          <button type="submit" disabled={ocupado || !valor.trim()}>Enviar</button>
        </div>
      </form>

      {children}

      <h2 className="titulo-exemplos">Exemplos prontos</h2>
      <div className="exemplos">
        {BATERIAS.map((bateria) => (
          <div key={bateria.id} className="grupo-exemplos">
            <span className="grupo-nome">{NOMES_GRUPO[bateria.id] ?? bateria.titulo}</span>
            <div className="chips">
              {bateria.casos.map((caso) => (
                <button
                  key={caso.payload}
                  className="chip"
                  onClick={() => usarExemplo(caso)}
                  disabled={ocupado}
                  title={`enviar para ${caso.rota}`}
                >
                  {/* texto puro: o JSX escapa < e > */}
                  {caso.payload}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
