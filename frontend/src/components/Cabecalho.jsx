import { useEffect, useState } from 'react';
import { buscarInfoWaf } from '../lib/waf';
import { numero } from '../lib/resultado';

/**
 * Título, e qual modelo está carregado no servidor.
 *
 * Existem dois modelos: o do CSIC 2010, de onde saem os números do artigo, e o de
 * demonstração, treinado com tráfego em português. A tela diz qual está rodando
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
        Antes de chegar na aplicação, cada requisição passa por regras de assinatura e,
        se nenhuma disparar, por um modelo de Machine Learning (Random Forest). A
        aplicação embaixo é vulnerável de propósito: toda a proteção está no WAF.
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
          {ehDemo
            ? 'Este modelo foi treinado com tráfego em português, só para a demonstração. ' +
              'Os números do artigo vêm do modelo do CSIC 2010, que aprendeu o tráfego de ' +
              'uma loja espanhola e por isso barra texto comum em português.'
            : 'Este é o modelo do CSIC 2010, o mesmo dos números do artigo. Ele aprendeu o ' +
              'tráfego de uma loja espanhola e barra texto comum em português. Para a ' +
              'apresentação, use o modelo de demonstração.'}
        </p>
      )}
    </header>
  );
}
