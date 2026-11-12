import { useEffect, useState } from 'react';
import { buscarInfoWaf } from '../lib/waf';
import { numero } from '../lib/resultado';
import ComLinks from './ComLinks';

/**
 * Título, e qual modelo está carregado no servidor.
 *
 * Existem dois modelos: o do CSIC 2010, de onde saem os números do artigo, e o de
 * demonstração, treinado com datasets públicos de payloads de SQLi e XSS. A tela diz qual está rodando
 * para que um nunca seja apresentado como se fosse o outro.
 */
export default function Cabecalho() {
  const [info, setInfo] = useState(undefined); // undefined = consultando

  useEffect(() => {
    buscarInfoWaf().then(setInfo);
  }, []);

  const ehDemo = info?.modelo?.includes('demo');

  return (
    <header className="cabecalho">
      <h1>WAF em duas camadas</h1>
      <p className="autor">
        Pedro Henrique Juliani · TCC de Ciência da Computação
      </p>
      <p className="resumo">
        Um firewall de aplicação web que barra ataques como SQL injection e XSS em duas etapas: primeiro
        regras de ataques conhecidos, depois um modelo de Machine Learning para o que as
        regras deixaram passar. A aplicação protegida é vulnerável de propósito.
      </p>

      <p className="estado">
        {info === undefined && <span className="fraco">consultando o servidor…</span>}

        {info === null && (
          <>
            <span className="ponto desligado" aria-hidden="true" />
            Servidor desligado. Suba com{' '}
            <code>$env:WAF_MODELO=&apos;demo&apos;; python servidor.py</code>
          </>
        )}

        {info && (
          <>
            <span className="ponto ligado" aria-hidden="true" />
            Servidor ligado · {ehDemo ? 'modelo de demonstração' : 'modelo do CSIC 2010'} ·
            limiar {numero(info.limiar_decisao, 2)}
          </>
        )}
      </p>

      {info && (
        <p className="nota">
          <ComLinks texto={ehDemo
            ? 'Modelo de demonstração, treinado com datasets públicos de payloads de SQLi e XSS (texto variado: nomes, e-mails, números, frases). Os números do artigo são do modelo do CSIC 2010 (aba Resultados).'
            : 'Este modelo aprendeu o tráfego de uma loja espanhola e barra texto comum em português. Para demonstrar, use o modelo de demonstração.'} />
        </p>
      )}
    </header>
  );
}
