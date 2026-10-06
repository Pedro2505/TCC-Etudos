import { bateu } from '../lib/resultado';
import Veredito from './Veredito';

/**
 * Tudo o que foi enviado nesta sessão, do mais novo para o mais antigo.
 *
 * O payload é mostrado como texto, nunca como HTML. A primeira versão deste painel
 * usava .innerHTML, e <img src=x onerror=alert(1)> executou na minha própria tela,
 * mesmo com o servidor tendo respondido 403. O JSX escapa por padrão.
 */
export default function Historico({ registros, onLimpar }) {
  return (
    <section className="secao">
      <div className="secao-topo">
        <h2>Histórico</h2>
        {registros.length > 0 && (
          <button className="discreto" onClick={onLimpar}>limpar</button>
        )}
      </div>

      {registros.length === 0 ? (
        <p className="fraco">Nada enviado ainda.</p>
      ) : (
        <ol className="historico">
          {registros.map((r) => (
            <li key={r.id} className={bateu(r) === false ? 'nao-bateu' : undefined}>
              <span className="hora fraco">{r.hora}</span>
              <code className="payload-texto">{r.payloadEnviado}</code>
              <span className="rota fraco">{r.rota}</span>
              <span className="obtido">
                <Veredito r={r} />
                {bateu(r) === false && <strong className="aviso"> · não bateu</strong>}
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
