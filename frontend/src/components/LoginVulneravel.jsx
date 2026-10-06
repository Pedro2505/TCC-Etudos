import React, { useState } from 'react';
import iconeUser from '../assets/user.svg';

/**
 * Formulário de login deliberadamente vulnerável.
 *
 * A rota /api/login_alvo monta a query por interpolação direta de string
 * (f"SELECT * FROM usuarios WHERE username = '{usuario}'"), sem nenhuma sanitização.
 * É intencional: se o WAF deixar passar, a injeção chega ao "banco".
 *
 * Removi o alert() que eu usava antes e passei a mandar o resultado para o log
 * compartilhado — na defesa, um popup por requisição interrompe o raciocínio e
 * esconde a probabilidade e a latência, que são o que importa mostrar.
 */
export default function LoginVulneravel({ onEnviar, desabilitado }) {
  const [usuario, setUsuario] = useState('');

  async function submeter(e) {
    e.preventDefault();
    if (!usuario.trim()) return;
    await onEnviar({
      rota: '/api/login_alvo',
      parametro: 'usuario',
      payload: usuario,
    });
  }

  return (
    <div className="card">
      <div className="card-cabecalho">
        <h3>Área Restrita</h3>
        <span className="tag tag-alvo">alvo de SQLi</span>
      </div>
      <p className="card-nota">
        A rota interpola o valor direto na query SQL. Sem WAF, <code>' OR 1=1--</code>{' '}
        autentica sem senha.
      </p>
      <form onSubmit={submeter}>
        <div className="input-icon">
          <img src={iconeUser} alt="" width="18" />
          <input
            type="text"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            placeholder="usuário ou payload"
            spellCheck={false}
          />
        </div>
        <button type="submit" disabled={desabilitado || !usuario.trim()}>
          Enviar para /api/login_alvo
        </button>
      </form>
    </div>
  );
}
