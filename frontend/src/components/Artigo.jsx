import { useEffect, useState } from 'react';
import {
  ABNT, CAPITULOS, DECISOES_ABERTAS, FICHAMENTO_COLUNAS, LIMITACOES, ORDEM_DE_ESCRITA, QUADRO1,
} from '../lib/artigo';
import { numero, pct } from '../lib/resultado';

/**
 * Mapa do artigo: o que entra em cada capítulo, as perguntas que o texto precisa
 * responder e os dados prontos para copiar. O texto em si é do Pedro.
 *
 * O checklist fica salvo no navegador (localStorage). Se o navegador não deixar
 * salvar, a página funciona igual, só esquece ao recarregar.
 */
const CHAVE = 'artigo-checklist-v1';

function lerFeitos() {
  try { return JSON.parse(localStorage.getItem(CHAVE)) ?? {}; } catch { return {}; }
}

export default function Artigo() {
  const [d, setD] = useState(null);
  const [feitos, setFeitos] = useState(lerFeitos);
  const [aberto, setAberto] = useState(ORDEM_DE_ESCRITA[0]);

  useEffect(() => {
    fetch('/resultados.json').then((r) => (r.ok ? r.json() : null)).then(setD).catch(() => {});
  }, []);

  function marcar(chave) {
    setFeitos((atual) => {
      const novo = { ...atual, [chave]: !atual[chave] };
      try { localStorage.setItem(CHAVE, JSON.stringify(novo)); } catch { /* sem armazenamento */ }
      return novo;
    });
  }

  const porId = Object.fromEntries(CAPITULOS.map((c) => [c.id, c]));
  const progresso = (c) => c.itens.filter((_, i) => feitos[`${c.id}:${i}`]).length;
  const total = CAPITULOS.reduce((s, c) => s + c.itens.length, 0);
  const feitosTotal = CAPITULOS.reduce((s, c) => s + progresso(c), 0);

  return (
    <div className="artigo">
      <p className="artigo-intro">
        Para cada capítulo: o que entra, as perguntas que o texto precisa responder e os
        dados prontos para colar no Word. <strong>O texto é seu</strong>: responda as
        perguntas com as suas palavras, uma ideia por frase.
      </p>

      <div className="progresso-geral">
        <div className="progresso-barra"><div style={{ width: `${(feitosTotal / total) * 100}%` }} /></div>
        <span className="pequeno fraco">{feitosTotal} de {total} itens feitos</span>
      </div>

      <section className="bloco">
        <h3>Antes de escrever: decisões em aberto</h3>
        <div className="decisoes">
          {DECISOES_ABERTAS.map((dec) => (
            <div key={dec.titulo} className="decisao-card">
              <strong>{dec.titulo}</strong>
              <p>{dec.porque}</p>
              {dec.caminhos.length > 0 && (
                <ul>{dec.caminhos.map((c) => <li key={c}>{c}</li>)}</ul>
              )}
              <span className="pequeno fraco">decidir com: {dec.com}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="bloco">
        <h3>Ordem para escrever</h3>
        <p className="bloco-explicacao">
          Comece pelo que já tem dado. Introdução e resumo por último, porque eles prometem o
          que os resultados entregam.
        </p>
        <ol className="ordem">
          {ORDEM_DE_ESCRITA.map((id) => {
            const c = porId[id];
            const p = progresso(c);
            return (
              <li key={id}>
                <button className={`ordem-item ${aberto === id ? 'ativo' : ''}`}
                  onClick={() => setAberto(id)}>
                  <span className="ordem-nome">{c.numero !== '—' && `${c.numero}. `}{c.titulo}</span>
                  <span className="pequeno fraco">{p}/{c.itens.length}</span>
                </button>
              </li>
            );
          })}
        </ol>
      </section>

      {aberto && (
        <Capitulo c={porId[aberto]} d={d} feitos={feitos} marcar={marcar} />
      )}

      <section className="bloco">
        <h3>Formatação (modelo da Unimar)</h3>
        <ul className="lista-simples">{ABNT.map((r) => <li key={r}>{r}</li>)}</ul>
      </section>
    </div>
  );
}

function Capitulo({ c, d, feitos, marcar }) {
  return (
    <section className="bloco capitulo">
      <div className="capitulo-topo">
        <h3>{c.numero !== '—' && `${c.numero}. `}{c.titulo}</h3>
        <span className="pequeno fraco">{c.paginas} páginas · {c.estado}</span>
      </div>

      <h4>O que entra</h4>
      <ul className="checklist">
        {c.itens.map((item, i) => {
          const chave = `${c.id}:${i}`;
          return (
            <li key={chave}>
              <label>
                <input type="checkbox" checked={!!feitos[chave]} onChange={() => marcar(chave)} />
                <span className={feitos[chave] ? 'riscado' : undefined}>{item}</span>
              </label>
            </li>
          );
        })}
      </ul>

      <h4>Perguntas que o texto precisa responder</h4>
      <ol className="perguntas">{c.perguntas.map((p) => <li key={p}>{p}</li>)}</ol>

      {c.frases?.length > 0 && (
        <>
          <h4>Frases suas que já existem</h4>
          {c.frases.map((f) => (
            <blockquote key={f.onde} className="frase-dele">
              <p>{f.texto}</p>
              <footer className="pequeno fraco">{f.onde}</footer>
            </blockquote>
          ))}
        </>
      )}

      {c.fatos?.length > 0 && (
        <>
          <h4>Fatos com número (cada um com o script de origem)</h4>
          <ul className="fatos-lista">
            {c.fatos.map(([texto, fonte]) => (
              <li key={texto}>
                <span>{texto}</span>
                <code className="fonte-fato">{fonte}</code>
              </li>
            ))}
          </ul>
        </>
      )}

      {c.elementos.length > 0 && <h4>Tabelas, figuras e dados</h4>}
      {c.elementos.map((id) => <Elemento key={id} id={id} d={d} />)}

      {c.cuidados.length > 0 && (
        <div className="cuidados">
          <strong>Cuidado</strong>
          <ul>{c.cuidados.map((x) => <li key={x}>{x}</li>)}</ul>
        </div>
      )}
    </section>
  );
}

/** Uma tabela/figura do inventário, com os dados quando eles existem. */
function Elemento({ id, d }) {
  const el = montarElemento(id, d);
  if (!el) return null;
  return (
    <div className="elemento">
      <div className="elemento-topo">
        <strong>{el.rotulo}</strong>
        {el.colunas && <BotaoCopiar colunas={el.colunas} linhas={el.linhas} />}
      </div>
      {el.aviso && <p className="aviso pequeno">{el.aviso}</p>}
      {el.colunas && (
        <table className={el.texto ? 'tabela-texto' : undefined}>
          <thead><tr>{el.colunas.map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>{el.linhas.map((l, i) => <tr key={i}>{l.map((x, j) => <td key={j}>{x}</td>)}</tr>)}</tbody>
        </table>
      )}
      {el.lista && <ul className="lista-simples">{el.lista.map((x) => <li key={x}>{x}</li>)}</ul>}
      {el.nota && <p className="pequeno fraco">{el.nota}</p>}
      {el.fonte && <p className="fonte">fonte: <code>{el.fonte}</code></p>}
    </div>
  );
}

/** Copia como tabela HTML (o Word cola como tabela de verdade) e como texto. */
function BotaoCopiar({ colunas, linhas }) {
  const [copiado, setCopiado] = useState(false);

  async function copiar() {
    const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const html = `<table><thead><tr>${colunas.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead>`
      + `<tbody>${linhas.map((l) => `<tr>${l.map((x) => `<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
    const texto = [colunas, ...linhas].map((l) => l.join('\t')).join('\n');
    try {
      await navigator.clipboard.write([new ClipboardItem({
        'text/html': new Blob([html], { type: 'text/html' }),
        'text/plain': new Blob([texto], { type: 'text/plain' }),
      })]);
    } catch {
      await navigator.clipboard.writeText(texto);
    }
    setCopiado(true);
    setTimeout(() => setCopiado(false), 1600);
  }

  return (
    <button className="discreto" onClick={copiar}>{copiado ? 'copiado' : 'copiar tabela'}</button>
  );
}

function montarElemento(id, d) {
  const semDados = { aviso: 'Os dados ainda não carregaram (rode python exportar_painel.py).' };

  switch (id) {
    case 'tab1': {
      if (!d?.dataset) return { rotulo: 'Tabela 1 · Composição do CSIC 2010', ...semDados };
      const ds = d.dataset;
      const ataques = d.hibrida.complementaridade.reduce((s, c) => s + c.n, 0);
      const nomes = {
        'normalTrafficTraining.txt': 'Normal (treino)',
        'normalTrafficTest.txt': 'Normal (teste)',
        'anomalousTrafficTest.txt': 'Anômalo',
      };
      return {
        rotulo: 'Tabela 1 · Composição do CSIC 2010',
        colunas: ['Etapa', 'Requisições'],
        linhas: [
          ...ds.arquivos.map((a) => [`${nomes[a.arquivo] ?? a.arquivo}: lidas`, numero(a.parseadas, 0)]),
          ['Com parâmetros (payload)', numero(ds.com_payload, 0)],
          ['Usadas no experimento', numero(ds.em_escopo, 0)],
          ['  normais', numero(ds.em_escopo - ataques, 0)],
          ['  anômalas', numero(ataques, 0)],
          ['Grupos de payload distintos', numero(ds.grupos, 0)],
        ],
        nota: 'Todas as requisições dos três arquivos foram lidas (bate com o número publicado pelo CSIC). Falta explicar a queda de 51.480 para 32.808.',
        fonte: ds.fonte,
      };
    }
    case 'tab2': {
      if (!d) return { rotulo: 'Tabela 2 · Tipos de anomalia', ...semDados };
      const fams = d.hibrida.familias.filter((f) => !f.familia.includes('escopo'));
      const total = fams.reduce((s, f) => s + f.n, 0);
      return {
        rotulo: 'Tabela 2 · Tipos de anomalia',
        colunas: ['Tipo', 'Requisições', '% das anomalias'],
        linhas: [...fams.map((f) => [f.familia, numero(f.n, 0), pct(f.n / total)]),
          ['Total', numero(total, 0), '100,0%']],
        nota: 'A concordância da rotulagem com a conferência manual (40 amostras) está em docs/medicoes/validacao_familias.md.',
        fonte: d.hibrida.fonte,
      };
    }
    case 'quadro1':
      return {
        rotulo: 'Quadro 1 · Features por bloco',
        texto: true,
        colunas: ['Bloco', 'Quantidade', 'O que mede'],
        linhas: [...QUADRO1, ['Total', '62', '']],
        fonte: 'models/model_metadata.json (lista de colunas)',
      };
    case 'tab3': {
      if (!d?.folds?.linhas?.length) return { rotulo: 'Tabela 3 · Validação cruzada', ...semDados };
      const cv = d.modelo_csic.validacao_cruzada;
      return {
        rotulo: 'Tabela 3 · Validação cruzada, fold a fold',
        colunas: ['Fold', 'F1', 'Precisão', 'Recall', 'Falso positivo'],
        linhas: [
          ...d.folds.linhas.map((f) => [f.fold, numero(f.f1, 4), pct(f.precisao), pct(f.recall), pct(f.taxa_fp, 2)]),
          ['Média ± desvio', `${numero(cv.f1.media, 4)} ± ${numero(cv.f1.desvio, 4)}`,
            `${pct(cv.precisao.media)} ± ${pct(cv.precisao.desvio)}`,
            `${pct(cv.recall.media)} ± ${pct(cv.recall.desvio)}`,
            `${pct(cv.taxa_fp.media, 2)} ± ${pct(cv.taxa_fp.desvio, 2)}`],
        ],
        nota: 'Limiar 0,5 (padrão da biblioteca), dentro de cada fold.',
        fonte: d.folds.fonte,
      };
    }
    case 'fig2': {
      if (!d) return { rotulo: 'Figura 2 · Curva do limiar', ...semDados };
      const alvos = [0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.8, 0.9];
      const pts = alvos.map((a) => d.curva_limiar.pontos.reduce((m, p) =>
        Math.abs(p.limiar - a) < Math.abs(m.limiar - a) ? p : m));
      return {
        rotulo: 'Figura 2 · Curva do limiar (o gráfico está na aba Resultados)',
        colunas: ['Limiar', 'Recall', 'Falso positivo', 'Precisão', 'F1'],
        linhas: pts.map((p) => [numero(p.limiar, 2), pct(p.recall), pct(p.taxa_fp, 2), pct(p.precisao), numero(p.f1, 3)]),
        nota: 'Para a figura: tire um print do gráfico na aba Resultados, ou refaça no Excel com esta tabela.',
        fonte: d.curva_limiar.fonte,
      };
    }
    case 'tab4': {
      if (!d?.ablacao?.configuracoes?.length) return { rotulo: 'Tabela 4 · Ablação', ...semDados };
      const nomes = {
        'Heuristicas + TF-IDF (modelo antigo)': 'Heurísticas + TF-IDF',
        'Apenas TF-IDF': 'Só TF-IDF',
        'Apenas contexto HTTP': 'Só contexto HTTP',
        'COMPLETO (+ contexto HTTP)': 'Os três blocos',
      };
      return {
        rotulo: 'Tabela 4 · Ablação: cada bloco de features ajuda?',
        colunas: ['Features', 'F1', 'Precisão', 'Recall', 'Falso positivo', 'ROC-AUC'],
        linhas: d.ablacao.configuracoes.map((c) => [nomes[c.nome] ?? c.nome,
          `${numero(c.f1, 3)} ± ${numero(c.f1_desvio, 3)}`, pct(c.precisao), pct(c.recall),
          pct(c.taxa_fp), numero(c.roc_auc, 3)]),
        nota: 'Média dos 5 folds, limiar 0,5. A comparação com as regras está na Tabela 5 (outra base de medida: não misture as duas na mesma tabela).',
        fonte: d.ablacao.fonte,
      };
    }
    case 'tab5': {
      if (!d) return { rotulo: 'Tabela 5 · Configurações', ...semDados };
      const nomes = { A: 'Só as regras', B: 'Só o modelo', C: 'Regras + modelo', D: 'Regras + modelo (limiar recalibrado)' };
      return {
        rotulo: 'Tabela 5 · Regras, modelo e os dois juntos',
        colunas: ['Configuração', 'Precisão', 'Recall', 'F1', 'Falso positivo', 'FP', 'FN'],
        linhas: d.hibrida.configuracoes.map((c) => [nomes[c.nome[0]] ?? c.nome, pct(c.precisao, 2),
          pct(c.recall, 2), numero(c.f1, 4), pct(c.taxa_fp, 2), numero(c.fp, 0), numero(c.fn, 0)]),
        nota: `Limiar ${numero(d.modelo_csic.limiar, 2)}, sobre as previsões de teste dos 5 folds juntas.`,
        fonte: d.hibrida.fonte,
      };
    }
    case 'tab6':
      return {
        rotulo: 'Tabela 6 · Latência',
        aviso: 'Sem script neste repositório. Os números do projeto antigo foram medidos sem script salvo e não podem ser citados.',
      };
    case 'tab7': {
      if (!d) return { rotulo: 'Tabela 7 · Quem pegou cada ataque', ...semDados };
      const total = d.hibrida.complementaridade.reduce((s, c) => s + c.n, 0);
      const nomes = {
        'Ambas as camadas': 'As duas camadas', 'Somente a assinatura': 'Só as regras',
        'Somente o modelo': 'Só o modelo', 'Nenhuma das duas': 'Nenhuma',
      };
      return {
        rotulo: 'Tabela 7 · Quem pegou cada ataque (resultado central)',
        colunas: ['Detectado por', 'Ataques', '% dos ataques'],
        linhas: [...d.hibrida.complementaridade.map((c) => [nomes[c.grupo] ?? c.grupo, numero(c.n, 0), pct(c.pct)]),
          ['Total', numero(total, 0), '100,0%']],
        fonte: d.hibrida.fonte,
      };
    }
    case 'tab8': {
      if (!d) return { rotulo: 'Tabela 8 · Recall por tipo de ataque', ...semDados };
      return {
        rotulo: 'Tabela 8 · Recall por tipo de ataque',
        colunas: ['Tipo', 'Ataques', 'Regras', 'Modelo', 'Juntas', 'Ganho do modelo'],
        linhas: d.hibrida.familias.map((f) => [f.familia, numero(f.n, 0), pct(f.assinaturas),
          pct(f.modelo), pct(f.combinado), `+${numero((f.combinado - f.assinaturas) * 100, 1)} pp`]),
        nota: 'O tipo foi atribuído por expressões regulares: a coluna "Regras" é otimista por construção.',
        fonte: d.hibrida.fonte,
      };
    }
    case 'fig1':
      return {
        rotulo: 'Figura 1 · Arquitetura',
        lista: ['requisição → normalização → regras (24) → modelo (Random Forest) → aplicação',
          'regra casou → barra com o nome da regra · nota ≥ limiar → barra com a nota · senão → libera'],
        nota: 'Desenhar no draw.io ou no próprio Word. A aba "Testar ao vivo" mostra o mesmo caminho.',
      };
    case 'fig3':
      return {
        rotulo: 'Figura 3 · Um bloqueio explicado (SHAP)',
        nota: 'Imagem pronta em docs/shap_explain_report.png (gerada com o modelo do CSIC).',
        fonte: 'explicacao.py',
      };
    case 'fichamento':
      return {
        rotulo: 'Modelo da tabela de fichamento',
        texto: true,
        colunas: FICHAMENTO_COLUNAS,
        linhas: [['', '', '', '', '']],
        nota: 'Uma linha por artigo. A última coluna, preenchida, já é o capítulo 3.',
      };
    case 'limitacoes':
      return { rotulo: 'Limitações já identificadas', lista: LIMITACOES };
    default:
      return null;
  }
}
