import { useState } from 'react';
import Veredito from './Veredito';

/**
 * Campo livre para testar qualquer valor, nas duas rotas vulneráveis:
 *
 *   /api/login_alvo  monta a query SQL concatenando o usuário, sem sanitizar
 *   /api/comentarios devolve o texto sem escapar
 *
 * Sem o WAF, ' OR 1=1-- entra no login e <script> seria guardado no mural.
 */
const ALVOS = {
  login: { rota: '/api/login_alvo', parametro: 'usuario', rotulo: 'login (SQL)' },
  comentario: { rota: '/api/comentarios', parametro: 'texto', rotulo: 'comentário (HTML)' },
};

export default function TesteManual({ onEnviar, ocupado }) {
  const [alvo, setAlvo] = useState('login');
  const [valor, setValor] = useState('');
  const [resultado, setResultado] = useState(null);

  async function enviar(e) {
    e.preventDefault();
    if (!valor.trim()) return;
    const { rota, parametro } = ALVOS[alvo];
    setResultado(await onEnviar({ rota, parametro, payload: valor }));
  }

  return (
    <section className="secao">
      <h2>Testar um valor</h2>
      <form className="teste-manual" onSubmit={enviar}>
        <label className="so-leitor" htmlFor="alvo">Rota</label>
        <select id="alvo" value={alvo} onChange={(e) => setAlvo(e.target.value)}>
          {Object.entries(ALVOS).map(([id, a]) => (
            <option key={id} value={id}>{a.rotulo}</option>
          ))}
        </select>

        <label className="so-leitor" htmlFor="valor">Valor</label>
        <input
          id="valor"
          type="text"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
          placeholder="' OR 1=1--"
          spellCheck={false}
          autoComplete="off"
        />

        <button type="submit" disabled={ocupado || !valor.trim()}>Enviar</button>
      </form>

      {resultado && (
        <p className="resultado-manual">
          <Veredito r={resultado} />
        </p>
      )}
    </section>
  );
}
