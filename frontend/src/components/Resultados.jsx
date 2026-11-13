import { useEffect, useState } from 'react';
import { numero, pct } from '../lib/resultado';
import {
  BarraEmpilhada, BarrasH, BarrasPareadas, CurvaLimiar, VerEmTabela,
} from './Graficos';

/**
 * Os números do modelo, lidos de public/resultados.json.
 *
 * Esse arquivo é gerado por exportar_painel.py a partir das medições que
 * treino_modelo.py e avaliacao_hibrida.py gravaram. Esta tela não calcula nada:
 * cada bloco mostra o script de onde o número veio.
 */
const NOMES_ABLACAO = {
  'Heuristicas + TF-IDF (modelo antigo)': 'heurísticas + TF-IDF',
  'Apenas TF-IDF': 'só TF-IDF',
  'Apenas contexto HTTP': 'só contexto HTTP',
  'COMPLETO (+ contexto HTTP)': 'os três blocos',
};

const NOMES_CONFIG = {
  A: 'Só as regras',
  B: 'Só o modelo',
  C: 'Regras + modelo',
  D: 'Regras + modelo, limiar recalibrado',
};

const PARTES = {
  'Ambas as camadas': ['as duas pegaram', 'ambas'],
  'Somente a assinatura': ['só as regras pegaram', 'assinatura'],
  'Somente o modelo': ['só o modelo pegou', 'modelo'],
  'Nenhuma das duas': ['nenhuma pegou', 'nenhuma'],
};

export default function Resultados() {
  const [d, setD] = useState(undefined);

  useEffect(() => {
    fetch('/resultados.json')
      .then((r) => (r.ok ? r.json() : null))
      .then(setD)
      .catch(() => setD(null));
  }, []);

  if (d === undefined) return <p className="fraco">carregando…</p>;
  if (d === null) {
    return (
      <p className="aviso">
        Não achei <code>resultados.json</code>. Rode <code>python exportar_painel.py</code>.
      </p>
    );
  }

  const m = d.modelo_csic;
  const cv = m.validacao_cruzada;
  const h = d.hibrida;
  const ataques = h.complementaridade.reduce((s, c) => s + c.n, 0);
  const ponto = d.curva_limiar.pontos;

  return (
    <div className="resultados">
      <Resumo d={d} ataques={ataques} />

      <Bloco titulo="O modelo" fonte={m.fonte}>
        <dl className="fatos">
          <Fato rotulo="Dados de treino" valor={m.dataset} />
          <Fato rotulo="Requisições" valor={numero(m.n_amostras, 0)}
            extra={`${numero(m.n_amostras - ataques, 0)} normais · ${numero(ataques, 0)} ataques`} />
          <Fato rotulo="Algoritmo" valor={`Random Forest, ${m.n_arvores} árvores`} />
          <Fato rotulo="Limiar de decisão" valor={numero(m.limiar, 2)}
            extra={`escolhido para errar em no máximo ${pct(m.alvo_fp, 0)} do tráfego normal`} />
          <Fato rotulo="Validação" valor="5 partes, sem repetir payload entre treino e teste"
            extra={m.validacao} />
        </dl>

        <h4>O que o modelo olha em cada requisição: {m.features.total} números</h4>
        <BarraEmpilhada total={m.features.total} soContagem partes={[
          { rotulo: 'contagens de segurança (aspas, palavras SQL, tamanho…)', n: m.features.heuristicas, cls: 'f1' },
          { rotulo: 'contexto HTTP (método, nº de parâmetros, headers…)', n: m.features.contexto, cls: 'f2' },
          { rotulo: 'pedaços de 2–3 letras mais frequentes (TF-IDF)', n: m.features.tfidf, cls: 'f3' },
        ]} />
      </Bloco>

      <Bloco titulo="Quanto ele acerta, sozinho"
        explicacao="Média das 5 rodadas da validação cruzada, com o corte padrão da biblioteca (0,5). O ± é a variação entre as rodadas."
        fonte={m.fonte}>
        <div className="tiles">
          <Tile rotulo="F1" valor={numero(cv.f1.media, 3)} desvio={numero(cv.f1.desvio, 3)} />
          <Tile rotulo="Precisão" valor={pct(cv.precisao.media)} desvio={pct(cv.precisao.desvio)}
            dica="quando barra, quantas vezes era ataque" />
          <Tile rotulo="Recall" valor={pct(cv.recall.media)} desvio={pct(cv.recall.desvio)}
            dica="dos ataques, quantos pegou" />
          <Tile rotulo="Falso positivo" valor={pct(cv.taxa_fp.media)} desvio={pct(cv.taxa_fp.desvio)}
            dica="do tráfego normal, quanto barrou" />
          <Tile rotulo="ROC-AUC" valor={numero(cv.roc_auc.media, 3)} desvio={numero(cv.roc_auc.desvio, 3)} />
        </div>
      </Bloco>

      <Bloco titulo="Onde fazer o corte"
        explicacao={`O modelo dá uma nota de 0 a 1. Acima do limiar, barra. Limiar baixo pega mais ataques e incomoda mais gente normal; o escolhido foi ${numero(m.limiar, 2)}. Passe o mouse para ver cada ponto.`}
        fonte={d.curva_limiar.fonte}>
        <div className="curvas">
          <CurvaLimiar pontos={ponto} campo="recall" titulo="Ataques pegos (recall)"
            limiarEscolhido={m.limiar} />
          <CurvaLimiar pontos={ponto} campo="taxa_fp" titulo="Tráfego normal barrado (falso positivo)"
            limiarEscolhido={m.limiar} maxY={0.2}
            referencia={{ valor: m.alvo_fp, rotulo: `teto de ${pct(m.alvo_fp, 0)}` }} />
        </div>
        <VerEmTabela colunas={['limiar', 'recall', 'falso positivo', 'precisão', 'F1']}
          linhas={ponto.filter((_, i) => i % 5 === 0).map((p) => [
            numero(p.limiar, 2), pct(p.recall), pct(p.taxa_fp, 2), pct(p.precisao), numero(p.f1, 3)])} />
      </Bloco>

      {d.ablacao.configuracoes.length > 0 && (
        <Bloco titulo="Cada grupo de números ajuda?"
          explicacao="O mesmo modelo treinado só com parte das features. F1 médio das 5 rodadas, limiar 0,5."
          fonte={d.ablacao.fonte}>
          <BarrasH
            itens={d.ablacao.configuracoes.map((c) => ({
              rotulo: NOMES_ABLACAO[c.nome] ?? c.nome, valor: c.f1, erro: c.f1_desvio,
            }))}
            formato={(v) => numero(v, 3)}
            destaque="os três blocos" />
          <VerEmTabela colunas={['features', 'F1', 'precisão', 'recall', 'falso positivo', 'ROC-AUC']}
            linhas={d.ablacao.configuracoes.map((c) => [
              NOMES_ABLACAO[c.nome] ?? c.nome, `${numero(c.f1, 3)} ± ${numero(c.f1_desvio, 3)}`,
              pct(c.precisao), pct(c.recall), pct(c.taxa_fp), numero(c.roc_auc, 3)])} />
        </Bloco>
      )}

      <Bloco titulo="As duas camadas juntas"
        explicacao={`Os mesmos ${numero(ataques, 0)} ataques, e quem pegou cada um.`}
        fonte={h.fonte}>
        <BarraEmpilhada total={ataques} partes={h.complementaridade.map((c) => ({
          rotulo: PARTES[c.grupo]?.[0] ?? c.grupo, n: c.n, cls: PARTES[c.grupo]?.[1] ?? 'nenhuma',
        }))} />

        <table className="tabela-config">
          <thead>
            <tr><th>Configuração</th><th>Precisão</th><th>Recall</th><th>F1</th><th>Falso positivo</th></tr>
          </thead>
          <tbody>
            {h.configuracoes.map((c) => (
              <tr key={c.nome}>
                <td>{NOMES_CONFIG[c.nome[0]] ?? c.nome}</td>
                <td>{pct(c.precisao, 2)}</td><td>{pct(c.recall, 2)}</td>
                <td>{numero(c.f1, 3)}</td><td>{pct(c.taxa_fp, 2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="pequeno fraco">
          Com o limiar {numero(m.limiar, 2)}, sobre as previsões de teste das 5 rodadas juntas.
        </p>
      </Bloco>

      <Bloco titulo="Por tipo de ataque"
        explicacao="Dos ataques de cada tipo, quantos cada camada pega sozinha."
        fonte={h.fonte}>
        <BarrasPareadas itens={h.familias.map((f) => ({
          rotulo: f.familia.replace(' (escopo do TCC)', ' (tema do TCC)'),
          n: f.n, a: f.assinaturas, b: f.modelo,
        }))} />
        <p className="pequeno fraco">
          O tipo de cada ataque foi atribuído por expressões regulares, parecidas com as próprias
          regras. Por isso a coluna das regras tende a sair alta.
        </p>
        <VerEmTabela colunas={['tipo', 'ataques', 'regras', 'modelo', 'juntas']}
          linhas={h.familias.map((f) => [f.familia, numero(f.n, 0), pct(f.assinaturas),
            pct(f.modelo), pct(f.combinado)])} />
      </Bloco>

      <Bloco titulo="Regras que mais dispararam" fonte={h.fonte}>
        <BarrasH cor="assinatura"
          itens={h.regras.map((r) => ({ rotulo: `${r.id} · ${r.nome}`, valor: r.disparos }))}
          max={Math.max(...h.regras.map((r) => r.disparos))}
          formato={(v) => numero(v, 0)} />
      </Bloco>

      {d.modelo_demo?.validacao_cruzada?.f1 && (
        <Bloco titulo="E o modelo da demonstração?" fonte={d.modelo_demo.fonte}>
          <p className="resumo">
            A aba ao vivo usa outro modelo, treinado com {numero(d.modelo_demo.n_amostras, 0)} exemplos
            de datasets públicos de SQLi e XSS, cujos exemplos legítimos são texto variado (nomes, e-mails,
            números, frases). Ele existe porque o modelo do CSIC barra texto
            em português. Os números dele <strong>não</strong> entram no artigo: os dados são
            mais fáceis, e o F1 de {numero(d.modelo_demo.validacao_cruzada.f1.media, 3)} não é
            comparável com o de cima.
          </p>
        </Bloco>
      )}
    </div>
  );
}

/**
 * Os números principais do trabalho numa tabela só, cada um com o script que o gerou.
 * Não calcula nada novo: só junta o que os outros blocos já leem de resultados.json.
 */
function Resumo({ d, ataques }) {
  const h = d.hibrida;
  const cv = d.modelo_csic.validacao_cruzada;
  const config = (letra) => h.configuracoes.find((c) => c.nome.startsWith(`${letra})`));
  const familia = (nome) => h.familias.find((f) => f.familia === nome);
  const soModelo = h.complementaridade.find((c) => c.grupo === 'Somente o modelo');
  const regras = config('A');
  const juntas = config('C');
  const tamp = familia('Tampering sem assinatura');
  const sqli = familia('SQLi');
  const xss = familia('XSS');
  const total = (d.latencia?.por_etapa || []).find((l) => l.etapa.startsWith('Total'));
  const pp = (f) => `${f.combinado - f.assinaturas >= 0 ? '+' : ''}${numero((f.combinado - f.assinaturas) * 100, 1)} pontos`;

  const linhas = [
    ['Requisições avaliadas (CSIC 2010)', numero(d.dataset.em_escopo, 0),
      `${numero(d.dataset.em_escopo - ataques, 0)} normais e ${numero(ataques, 0)} ataques`,
      'ingestao_csic.py'],
    ['Nota F1 do modelo', `${numero(cv.f1.media, 3)} ± ${numero(cv.f1.desvio, 3)}`,
      'média de 5 rodadas; o mesmo payload nunca aparece no treino e no teste ao mesmo tempo',
      'treino_modelo.py'],
    ['Ataques que as regras pegam sozinhas', pct(regras?.recall),
      `acertam ${pct(regras?.precisao)} das vezes que barram e barram ${pct(regras?.taxa_fp)} de quem é inocente`,
      'avaliacao_hibrida.py'],
    ['Ataques que regras e modelo pegam juntos', pct(juntas?.recall),
      `acertam ${pct(juntas?.precisao)} das vezes que barram e barram ${pct(juntas?.taxa_fp)} de quem é inocente`,
      'avaliacao_hibrida.py'],
    ['Ataques que só o modelo pega', pct(soModelo?.pct),
      `${numero(soModelo?.n, 0)} ataques que passariam se só existissem as regras`,
      'avaliacao_hibrida.py'],
    ['Ganho do modelo em manipulação de parâmetros', tamp ? pp(tamp) : '—',
      tamp ? `as regras pegam ${pct(tamp.assinaturas)}; com o modelo, ${pct(tamp.combinado)}` : '',
      'avaliacao_hibrida.py'],
    ['Ganho do modelo em SQLi e XSS', sqli && xss ? `${pp(sqli)} / ${pp(xss)}` : '—',
      sqli && xss ? `as regras sozinhas já pegam ${pct(sqli.assinaturas)} e ${pct(xss.assinaturas)}; não sobra nada para o modelo` : '',
      'avaliacao_hibrida.py'],
    ['Tempo do WAF por requisição', total ? `${numero(total.p50, 1)} ms` : '—',
      total ? `metade leva menos que isso e 95% levam até ${numero(total.p95, 1)} ms (uma requisição por vez)` : 'rode medir_latencia.py',
      'medir_latencia.py'],
  ];

  return (
    <Bloco titulo="Resumo: os números do trabalho"
      explicacao="Tudo aqui vem do modelo treinado no CSIC 2010, e não do que roda na demonstração. Ao lado de cada número está o script que o gerou.">
      <table className="tabela-texto">
        <thead><tr><th>O quê</th><th>Número</th><th>O que isso quer dizer</th><th>Script</th></tr></thead>
        <tbody>
          {linhas.map(([oque, valor, leitura, script]) => (
            <tr key={oque}>
              <td>{oque}</td>
              <td><strong>{valor}</strong></td>
              <td className="fraco">{leitura}</td>
              <td><code>{script}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </Bloco>
  );
}

function Bloco({ titulo, explicacao, fonte, children }) {
  return (
    <section className="bloco">
      <h3>{titulo}</h3>
      {explicacao && <p className="bloco-explicacao">{explicacao}</p>}
      {children}
      {fonte && <p className="fonte">fonte: <code>{fonte}</code></p>}
    </section>
  );
}

function Fato({ rotulo, valor, extra }) {
  return (
    <div className="fato">
      <dt>{rotulo}</dt>
      <dd>{valor}{extra && <span className="fraco pequeno">{extra}</span>}</dd>
    </div>
  );
}

function Tile({ rotulo, valor, desvio, dica }) {
  return (
    <div className="tile">
      <span className="tile-rotulo">{rotulo}</span>
      <span className="tile-valor">{valor}</span>
      <span className="tile-desvio">± {desvio}</span>
      {dica && <span className="tile-dica">{dica}</span>}
    </div>
  );
}
