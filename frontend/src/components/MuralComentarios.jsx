import React, { useState } from 'react';

/**
 * Mural de comentários deliberadamente vulnerável.
 *
 * A rota /api/comentarios devolve o texto recebido sem escapar nada. Se o WAF
 * liberar, o payload de XSS é "armazenado" e voltaria para o navegador.
 *
 * Detalhe que eu faço questão de mostrar na defesa: o texto que volta do backend é
 * renderizado como CONTEÚDO no log, nunca como HTML. Foi aqui que eu tomei a lição
 * mais dura do projeto — a primeira versão do painel usava .innerHTML e o payload
 * `<img src=x onerror=alert(1)>` executou na minha tela apesar de o backend ter
 * devolvido 403 corretamente. Eu tinha um DOM-based XSS no log de auditoria do meu
 * próprio WAF.
 */
export default function MuralComentarios({ onEnviar, desabilitado }) {
  const [comentario, setComentario] = useState('');

  async function submeter(e) {
    e.preventDefault();
    if (!comentario.trim()) return;
    await onEnviar({
      rota: '/api/comentarios',
      parametro: 'texto',
      payload: comentario,
    });
  }

  return (
    <div className="card">
      <div className="card-cabecalho">
        <h3>Mural Público</h3>
        <span className="tag tag-alvo">alvo de XSS</span>
      </div>
      <p className="card-nota">
        A rota devolve o texto sem escapar. Sem WAF,{' '}
        <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> seria armazenado.
      </p>
      <form onSubmit={submeter}>
        <textarea
          rows="3"
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          placeholder="comentário ou payload"
          spellCheck={false}
        />
        <button
          type="submit"
          className="secondary-btn"
          disabled={desabilitado || !comentario.trim()}
        >
          Enviar para /api/comentarios
        </button>
      </form>
    </div>
  );
}
