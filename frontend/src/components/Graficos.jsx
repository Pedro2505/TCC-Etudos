import { useState } from 'react';
import { numero, pct } from '../lib/resultado';

/*
 * Gráficos feitos à mão, sem biblioteca. Duas cores de identidade em tudo:
 * azul = modelo, laranja = assinaturas. Todo valor aparece escrito ao lado da
 * marca, e cada gráfico tem a tabela por baixo ("ver em tabela").
 */

/** Barras horizontais de uma série. `valor` em 0..1, `erro` opcional (desvio). */
export function BarrasH({ itens, cor = 'modelo', formato = (v) => pct(v), max = 1, destaque }) {
  return (
    <div className="barras">
      {itens.map((it) => (
        <div key={it.rotulo} className={`barra-linha ${destaque === it.rotulo ? 'em-destaque' : ''}`}
          title={`${it.rotulo}: ${formato(it.valor)}${it.erro != null ? ` ± ${formato(it.erro)}` : ''}`}>
          <span className="barra-rotulo">{it.rotulo}</span>
          <div className="barra-trilho">
            <div className={`barra ${cor}`} style={{ width: `${(it.valor / max) * 100}%` }} />
            {it.erro != null && (
              <div className="barra-erro" style={{
                left: `${((it.valor - it.erro) / max) * 100}%`,
                width: `${((2 * it.erro) / max) * 100}%`,
              }} />
            )}
          </div>
          <span className="barra-valor">
            {formato(it.valor)}
            {it.erro != null && <span className="fraco"> ± {formato(it.erro)}</span>}
          </span>
        </div>
      ))}
    </div>
  );
}

/** Duas barras por categoria: assinaturas e modelo. */
export function BarrasPareadas({ itens }) {
  return (
    <div className="barras pareadas">
      <Legenda itens={[['assinatura', 'Regras (camada 1)'], ['modelo', 'Modelo (camada 2)']]} />
      {itens.map((it) => (
        <div key={it.rotulo} className="par">
          <span className="par-rotulo">
            {it.rotulo} <span className="fraco">· {numero(it.n, 0)} ataques</span>
          </span>
          {[['assinatura', it.a], ['modelo', it.b]].map(([cls, v]) => (
            <div key={cls} className="barra-linha compacta" title={`${it.rotulo}: ${pct(v)}`}>
              <div className="barra-trilho">
                <div className={`barra ${cls}`} style={{ width: `${v * 100}%` }} />
              </div>
              <span className="barra-valor">{pct(v)}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

/** Uma barra que soma 100%, dividida em partes. */
export function BarraEmpilhada({ partes, total, soContagem = false }) {
  return (
    <div>
      <div className="empilhada" role="img"
        aria-label={partes.map((p) => `${p.rotulo}: ${pct(p.n / total)}`).join('; ')}>
        {partes.map((p) => (
          <div key={p.rotulo} className={`parte ${p.cls}`}
            style={{ flexGrow: p.n }} title={`${p.rotulo}: ${numero(p.n, 0)} (${pct(p.n / total)})`} />
        ))}
      </div>
      <ul className="legenda-empilhada">
        {partes.map((p) => (
          <li key={p.rotulo}>
            <span className={`amostra ${p.cls}`} aria-hidden="true" />
            <span>{p.rotulo}</span>
            {soContagem ? (
              <strong>{numero(p.n, 0)}</strong>
            ) : (
              <>
                <strong>{pct(p.n / total)}</strong>
                <span className="fraco">{numero(p.n, 0)}</span>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Uma métrica em função do limiar, com o limiar escolhido marcado.
 * Passar o mouse mostra os valores naquele ponto.
 */
export function CurvaLimiar({ pontos, campo, titulo, limiarEscolhido, referencia, maxY = 1 }) {
  const [hover, setHover] = useState(null);
  const L = 600, A = 200, m = { e: 44, d: 12, t: 12, b: 28 };
  const x = (v) => m.e + v * (L - m.e - m.d);
  const y = (v) => m.t + (1 - Math.min(v, maxY) / maxY) * (A - m.t - m.b);
  const caminho = pontos.map((p, i) => `${i ? 'L' : 'M'}${x(p.limiar)},${y(p[campo])}`).join(' ');
  const escolhido = pontos.reduce((a, p) =>
    Math.abs(p.limiar - limiarEscolhido) < Math.abs(a.limiar - limiarEscolhido) ? p : a);
  const marcas = [0, 0.25, 0.5, 0.75, 1].map((f) => f * maxY);

  function mover(e) {
    const caixa = e.currentTarget.getBoundingClientRect();
    const lim = ((e.clientX - caixa.left) / caixa.width * L - m.e) / (L - m.e - m.d);
    if (lim < 0 || lim > 1) return setHover(null);
    setHover(pontos.reduce((a, p) => (Math.abs(p.limiar - lim) < Math.abs(a.limiar - lim) ? p : a)));
  }

  return (
    <figure className="curva">
      <figcaption>{titulo}</figcaption>
      <div className="curva-area">
        <svg viewBox={`0 0 ${L} ${A}`} onMouseMove={mover} onMouseLeave={() => setHover(null)}
          role="img" aria-label={`${titulo} em função do limiar`}>
          {marcas.map((v) => (
            <g key={v}>
              <line x1={m.e} x2={L - m.d} y1={y(v)} y2={y(v)} className="grade" />
              <text x={m.e - 6} y={y(v) + 4} className="eixo" textAnchor="end">
                {pct(v, 0)}
              </text>
            </g>
          ))}
          {[0, 0.2, 0.4, 0.6, 0.8, 1].map((v) => (
            <text key={v} x={x(v)} y={A - 8} className="eixo" textAnchor="middle">{numero(v, 1)}</text>
          ))}
          {referencia && (
            <g>
              <line x1={m.e} x2={L - m.d} y1={y(referencia.valor)} y2={y(referencia.valor)}
                className="referencia" />
              <text x={L - m.d} y={y(referencia.valor) - 5} textAnchor="end" className="eixo">
                {referencia.rotulo}
              </text>
            </g>
          )}
          <line x1={x(limiarEscolhido)} x2={x(limiarEscolhido)} y1={m.t} y2={A - m.b}
            className="limiar-escolhido" />
          <path d={caminho} className="linha-curva" />
          <circle cx={x(escolhido.limiar)} cy={y(escolhido[campo])} r="5" className="ponto-escolhido" />
          <text x={x(escolhido.limiar) + 8} y={y(escolhido[campo]) - 8} className="rotulo-ponto">
            {numero(limiarEscolhido, 2)} → {pct(escolhido[campo])}
          </text>
          {hover && (
            <g>
              <line x1={x(hover.limiar)} x2={x(hover.limiar)} y1={m.t} y2={A - m.b} className="mira" />
              <circle cx={x(hover.limiar)} cy={y(hover[campo])} r="4" className="ponto-mira" />
            </g>
          )}
        </svg>
        {hover && (
          <div className="dica" style={{ left: `${(x(hover.limiar) / L) * 100}%` }}>
            limiar {numero(hover.limiar, 2)}<br />
            recall {pct(hover.recall)} · FP {pct(hover.taxa_fp, 2)}<br />
            precisão {pct(hover.precisao)} · F1 {numero(hover.f1, 3)}
          </div>
        )}
      </div>
    </figure>
  );
}

export function Legenda({ itens }) {
  return (
    <ul className="legenda">
      {itens.map(([cls, rotulo]) => (
        <li key={cls}><span className={`amostra ${cls}`} aria-hidden="true" />{rotulo}</li>
      ))}
    </ul>
  );
}

/** Tabela recolhida por baixo de um gráfico. */
export function VerEmTabela({ colunas, linhas }) {
  return (
    <details className="ver-tabela">
      <summary>ver em tabela</summary>
      <table>
        <thead><tr>{colunas.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>
          {linhas.map((l, i) => <tr key={i}>{l.map((c, j) => <td key={j}>{c}</td>)}</tr>)}
        </tbody>
      </table>
    </details>
  );
}
