import React from 'react';

/**
 * Diagrama vivo da cascata do WAF híbrido.
 *
 * Este componente é o centro visual da demonstração. A tese do trabalho não é
 * "o WAF bloqueou" — é que existem DUAS camadas com perfis de erro
 * complementares, e que uma pega o que a outra não pega. Um log de texto não
 * comunica isso; um diagrama que acende a camada que decidiu, sim.
 *
 * Os contadores são da sessão corrente, ao vivo. Ao rodar as baterias na ordem,
 * o operador vê a camada 1 acumular nas baterias 2-4 e a camada 2 acumular na
 * bateria 5 — que é exatamente o argumento do trabalho, desenhado na tela.
 */
export default function ArquiteturaCamadas({ metricas, ultimaCamada }) {
  return (
    <section className="arquitetura">
      <div className="painel-cabecalho">
        <h2>Arquitetura em cascata</h2>
        <span className="tag tag-neutra">assinaturas + Machine Learning</span>
      </div>

      <p className="arq-tese">
        A ideia não é trocar o WAF de assinaturas pelo modelo, é{' '}
        <strong>somar os dois</strong>. Eles erram em coisas diferentes: a assinatura
        deixa passar o que ninguém catalogou ainda, e o modelo às vezes bloqueia texto
        normal. Rodando no CSIC 2010, <strong>36,4% dos ataques só o modelo pegou</strong>.
      </p>

      <div className="fluxo">
        <Etapa
          rotulo="Requisição"
          detalhe="só os valores dos parâmetros"
          valor={metricas.total}
          unidade="recebidas"
          classe="etapa-entrada"
        />

        <Seta />

        <Etapa
          rotulo="Normalização"
          detalhe="URL-decode em laço, Base64, minúsculas"
          classe="etapa-normalizacao"
        />

        <Seta />

        <Etapa
          rotulo="Camada 1 · Assinaturas"
          detalhe="24 regras, nenhum falso positivo no CSIC"
          valor={metricas.porAssinatura}
          unidade="bloqueios"
          classe="etapa-camada1"
          ativa={ultimaCamada === 'assinatura'}
        />

        <Seta rotulo="não casou" />

        <Etapa
          rotulo="Camada 2 · Modelo"
          detalhe="Random Forest, 62 features, limiar calibrado"
          valor={metricas.porModelo}
          unidade="bloqueios"
          classe="etapa-camada2"
          ativa={ultimaCamada === 'modelo'}
        />

        <Seta rotulo="abaixo do limiar" />

        <Etapa
          rotulo="Aplicação"
          detalhe="a rota vulnerável"
          valor={metricas.permitidas}
          unidade="liberadas"
          classe="etapa-saida"
          ativa={ultimaCamada === null && metricas.total > 0}
        />
      </div>
    </section>
  );
}

function Etapa({ rotulo, detalhe, valor, unidade, classe, ativa }) {
  return (
    <div className={`etapa ${classe} ${ativa ? 'etapa-ativa' : ''}`}>
      <span className="etapa-rotulo">{rotulo}</span>
      {valor != null && (
        <span className="etapa-valor">
          {valor}
          <span className="etapa-unidade"> {unidade}</span>
        </span>
      )}
      <span className="etapa-detalhe">{detalhe}</span>
    </div>
  );
}

function Seta({ rotulo }) {
  return (
    <div className="seta-fluxo">
      <span className="seta-glifo">→</span>
      {rotulo && <span className="seta-rotulo">{rotulo}</span>}
    </div>
  );
}
