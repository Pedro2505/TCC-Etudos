import React, { useCallback, useMemo, useState } from 'react';
import LoginVulneravel from './components/LoginVulneravel';
import MuralComentarios from './components/MuralComentarios';
import PainelWaf from './components/PainelWaf';
import ArquiteturaCamadas from './components/ArquiteturaCamadas';
import BateriaTestes from './components/BateriaTestes';
import LogAuditoria from './components/LogAuditoria';
import { enviarRequisicao } from './lib/waf';
import './index.css';

export default function App() {
  const [registros, setRegistros] = useState([]);
  const [executando, setExecutando] = useState(false);
  // Camada que decidiu a ÚLTIMA requisição, para acender a etapa correspondente
  // no diagrama. `undefined` = nada rodou ainda; `null` = a requisição passou.
  const [ultimaCamada, setUltimaCamada] = useState(undefined);

  /**
   * Ponto único por onde toda requisição passa.
   *
   * Centralizei aqui porque o log precisa registrar tudo de forma uniforme — venha do
   * roteiro de baterias ou dos formulários. Antes cada componente fazia seu próprio
   * fetch e tratava a resposta do seu jeito, e nada ficava registrado.
   */
  const executar = useCallback(async (caso) => {
    setExecutando(true);
    const resultado = await enviarRequisicao({
      rota: caso.rota,
      parametro: caso.parametro,
      valor: caso.payload,
    });

    setRegistros((anteriores) => [
      {
        ...resultado,
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        hora: new Date().toLocaleTimeString('pt-BR'),
        esperado: caso.esperado ?? null,
        camadaEsperada: caso.camadaEsperada ?? undefined,
        esperadoEhFalha: caso.esperadoEhFalha ?? false,
      },
      ...anteriores,
    ]);

    setUltimaCamada(resultado.camada ?? null);
    setExecutando(false);
    return resultado;
  }, []);

  const metricas = useMemo(() => calcularMetricas(registros), [registros]);

  return (
    <div className="app-container">
      <header>
        <h1>
          WAF Híbrido <span>— assinaturas + Machine Learning</span>
        </h1>
        <p className="subtitulo">
          Detecção de anomalias em aplicações web com Machine Learning · Pedro Henrique
          Juliani · TCC em Ciência da Computação
        </p>
        <p className="explicacao">
          Escrevi um middleware em FastAPI que pega toda requisição antes dela chegar na
          rota e passa por <strong>duas camadas</strong>. Primeiro 24 assinaturas no
          estilo do OWASP CRS. O que sobra vai para um Random Forest com 62 features do
          payload. A aplicação aqui embaixo é <strong>vulnerável de propósito</strong>:
          as rotas montam a query SQL concatenando string e devolvem o texto sem
          sanitizar nada. Toda a proteção está no middleware.
        </p>
      </header>

      <ArquiteturaCamadas metricas={metricas} ultimaCamada={ultimaCamada} />

      <PainelWaf metricas={metricas} />

      <main className="layout-principal">
        <div className="coluna-esquerda">
          <BateriaTestes onExecutar={executar} executando={executando} />
        </div>

        <div className="coluna-direita">
          <section className="alvos">
            <h2>Aplicação-alvo (entrada manual)</h2>
            <p className="alvos-intro">
              Uso estes formulários quando a banca quer testar um payload próprio. O
              resultado vai para o mesmo log.
            </p>
            <LoginVulneravel onEnviar={executar} desabilitado={executando} />
            <MuralComentarios onEnviar={executar} desabilitado={executando} />
          </section>

          <LogAuditoria registros={registros} onLimpar={() => setRegistros([])} />
        </div>
      </main>

      <footer>
        <p>
          <strong>O que eu não escondo:</strong> no CSIC 2010 o sistema alcança 100% de
          recall em SQLi e XSS (1.970 ataques), mas cai a 49,6% em{' '}
          <em>parameter tampering</em> — 79,9% das anomalias, e o limite ali é estrutural,
          não de ajuste: 12,8% delas são indistinguíveis de tráfego legítimo na
          representação que uso. Todo o falso positivo (0,99%) vem da camada 2; a camada 1
          não produziu nenhum em 18.620 requisições legítimas. Além disso, 22,3% dos
          ataques daquele dataset estão no <em>path</em>, que este middleware não
          inspeciona. A <strong>Bateria 6</strong> demonstra essas limitações ao vivo,
          incluindo dois falsos positivos e dois falsos negativos reais.
        </p>
      </footer>
    </div>
  );
}

function calcularMetricas(registros) {
  const validos = registros.filter((r) => r.ok);
  const comEsperado = validos.filter((r) => r.esperado != null);
  const latencias = validos
    .map((r) => r.latenciaBackend)
    .filter((v) => v != null)
    .sort((a, b) => a - b);

  // Conformidade de CAMADA: só conta os casos que declararam qual camada deveria
  // resolver. É a verificação que corresponde à tese — não basta bloquear, tem que
  // ser a camada certa que bloqueou.
  const comCamadaEsperada = validos.filter((r) => r.camadaEsperada !== undefined);

  return {
    total: registros.length,
    bloqueadas: validos.filter((r) => r.bloqueado).length,
    permitidas: validos.filter((r) => !r.bloqueado && !r.erroInterno).length,
    porAssinatura: validos.filter((r) => r.camada === 'assinatura').length,
    porModelo: validos.filter((r) => r.camada === 'modelo').length,
    comCamadaEsperada: comCamadaEsperada.length,
    camadaConforme: comCamadaEsperada.filter((r) => (r.camada ?? null) === r.camadaEsperada)
      .length,
    comEsperado: comEsperado.length,
    conforme: comEsperado.filter((r) => r.status === r.esperado).length,
    latenciaMedia: latencias.length
      ? latencias.reduce((a, b) => a + b, 0) / latencias.length
      : null,
    // p95 por índice: com poucas amostras é aproximação, mas mostra a cauda, que é o
    // que importa num componente que fica no caminho crítico da requisição.
    latenciaP95: latencias.length
      ? latencias[Math.min(latencias.length - 1, Math.floor(latencias.length * 0.95))]
      : null,
  };
}
