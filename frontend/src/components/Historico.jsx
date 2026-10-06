import { bateu } from '../lib/resultado';
import Veredito from './Veredito';

/**
 * Placar da sessão e tudo o que foi enviado, do mais novo para o mais antigo.
 *
 * O payload é mostrado como texto, nunca como HTML. A primeira versão deste painel
 * usava .innerHTML, e <img src=x onerror=alert(1)> executou na minha própria tela,
 * mesmo com o servidor tendo respondido 403. O JSX escapa por padrão.
 */
export default function Historico({ registros, onLimpar }) {
  const validos = registros.filter((r) => r.ok);
  const placar = [
    { rotulo: 'barrados pelas regras', n: validos.filter((r) => r.camada === 'assinatura').length, cls: 'assinatura' },
    { rotulo: 'barrados pelo modelo', n: validos.filter((r) => r.camada === 'modelo').length, cls: 'modelo' },
    { rotulo: 'liberados', n: validos.filter((r) => r.status === 200).length, cls: 'liberado' },
  ];

  return (
    <section className="secao">
      <div className="secao-topo">
        <h2>Nesta sessão</h2>
        {registros.length > 0 && (
          <button className="discreto" onClick={onLimpar}>limpar</button>
        )}
      </div>

      <div className="placar">
        {placar.map((p) => (
          <div key={p.cls} className={`placar-item ${p.cls}`}>
            <span className="placar-n">{p.n}</span>
            <span className="placar-rotulo">{p.rotulo}</span>
          </div>
        ))}
      </div>

      {registros.length > 0 && (
        <ol className="historico">
          {registros.map((r) => (
            <li key={r.id} className={bateu(r) === false ? 'nao-bateu' : undefined}>
              <span className="hora fraco">{r.hora}</span>
              <code className="payload-texto">{r.payloadEnviado}</code>
              <span className="obtido">
                <Veredito r={r} />
                {bateu(r) === false && <strong className="aviso"> · diferente do previsto</strong>}
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
