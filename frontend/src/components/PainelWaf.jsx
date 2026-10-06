import React, { useEffect, useState } from 'react';
import { buscarInfoWaf } from '../lib/waf';

/**
 * Painel de transparência do modelo.
 *
 * Eu mantenho dois modelos com papéis diferentes: o treinado no CSIC 2010, que gera
 * as métricas da monografia, e o de demonstração, treinado com tráfego benigno em
 * português. Apresentar um como se fosse o outro seria desonesto, então o painel lê
 * os metadados do backend e mostra na tela qual está carregado.
 */
export default function PainelWaf({ metricas }) {
  const [info, setInfo] = useState(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    buscarInfoWaf().then((dados) => {
      setInfo(dados);
      setCarregando(false);
    });
  }, []);

  const ehDemo = info?.modelo?.includes('demo');

  return (
    <section className="painel-waf">
      <div className="painel-cabecalho">
        <h2>Modelo carregado</h2>
        {carregando && <span className="tag tag-neutra">consultando backend…</span>}
        {!carregando && !info && (
          <span className="tag tag-erro">backend fora do ar</span>
        )}
        {info && (
          <span className={`tag ${ehDemo ? 'tag-alerta' : 'tag-ok'}`}>
            {ehDemo ? 'modelo de DEMONSTRAÇÃO' : 'modelo do CSIC 2010'}
          </span>
        )}
      </div>

      {!carregando && !info && (
        <p className="aviso-erro">
          Não consegui falar com o backend na porta 8000. Suba com{' '}
          <code>WAF_MODELO=demo python api.py</code>.
        </p>
      )}

      {info && (
        <>
          <div className="grid-info">
            <Dado rotulo="Dataset de treino" valor={info.dataset_treino} largo />
            <Dado rotulo="Validação" valor={info.validacao} largo />
            <Dado rotulo="Limiar de decisão" valor={info.limiar_decisao?.toFixed(3)} />
            <Dado
              rotulo="Alvo de falso positivo"
              valor={
                info.alvo_falso_positivo != null
                  ? `≤ ${(info.alvo_falso_positivo * 100).toFixed(1)}%`
                  : '—'
              }
            />
            <Dado rotulo="Features" valor={info.n_features} />
            <Dado rotulo="Árvores" valor={info.n_arvores} />
            <Dado
              rotulo="Amostras de treino"
              valor={info.n_amostras_treino?.toLocaleString('pt-BR')}
            />
            <Dado
              rotulo="F1 (validação cruzada)"
              valor={
                info.f1_medio != null
                  ? `${info.f1_medio.toFixed(4)} ± ${info.f1_desvio?.toFixed(4)}`
                  : '—'
              }
            />
          </div>

          {ehDemo && (
            <p className="nota-modelo">
              <strong>Por que o modelo de demonstração?</strong> Um modelo desses aprende
              o que é normal em <em>uma</em> aplicação específica. O do CSIC 2010 aprendeu
              o tráfego de uma loja em espanhol, então ele dá p≈0,90 para{' '}
              <code>tênis de corrida masculino</code> e bloqueia: português está fora do
              que ele viu. Cheguei a medir 97,4% de falso positivo assim. Não é bug, é
              como a abordagem funciona, e é por isso que o próprio CSIC distribui um
              treino separado por aplicação. Como esta demo é em português, uso aqui um
              modelo treinado com tráfego parecido. Os números da monografia saem do
              modelo do CSIC.
            </p>
          )}
        </>
      )}

      <div className="grid-metricas">
        <Metrica rotulo="Requisições" valor={metricas.total} />
        <Metrica rotulo="Bloqueadas" valor={metricas.bloqueadas} classe="vermelho" />
        <Metrica rotulo="Permitidas" valor={metricas.permitidas} classe="verde" />
        <Metrica
          rotulo="Status conforme"
          valor={
            metricas.comEsperado > 0
              ? `${metricas.conforme}/${metricas.comEsperado}`
              : '—'
          }
          classe={
            metricas.comEsperado > 0 && metricas.conforme === metricas.comEsperado
              ? 'verde'
              : 'amarelo'
          }
        />
        {/* A verificação que corresponde à tese: não basta bloquear, tem que ser a
            camada certa. É este contador que prova a complementaridade ao vivo. */}
        <Metrica
          rotulo="Camada conforme"
          valor={
            metricas.comCamadaEsperada > 0
              ? `${metricas.camadaConforme}/${metricas.comCamadaEsperada}`
              : '—'
          }
          classe={
            metricas.comCamadaEsperada > 0 &&
            metricas.camadaConforme === metricas.comCamadaEsperada
              ? 'verde'
              : 'amarelo'
          }
        />
        <Metrica
          rotulo="Latência média (WAF)"
          valor={metricas.latenciaMedia ? `${metricas.latenciaMedia.toFixed(1)} ms` : '—'}
        />
        <Metrica
          rotulo="Latência p95 (WAF)"
          valor={metricas.latenciaP95 ? `${metricas.latenciaP95.toFixed(1)} ms` : '—'}
        />
      </div>
    </section>
  );
}

function Dado({ rotulo, valor, largo }) {
  return (
    <div className={`dado ${largo ? 'dado-largo' : ''}`}>
      <span className="dado-rotulo">{rotulo}</span>
      <span className="dado-valor">{valor ?? '—'}</span>
    </div>
  );
}

function Metrica({ rotulo, valor, classe = '' }) {
  return (
    <div className={`metrica ${classe}`}>
      <span className="metrica-valor">{valor}</span>
      <span className="metrica-rotulo">{rotulo}</span>
    </div>
  );
}
