import { useCallback, useEffect, useState } from 'react';
import Cabecalho from './components/Cabecalho';
import Console from './components/Console';
import Pipeline from './components/Pipeline';
import Historico from './components/Historico';
import ConferirRoteiro from './components/ConferirRoteiro';
import Resultados from './components/Resultados';
import Artigo from './components/Artigo';
import { chaveDoCaso } from './lib/resultado';
import { enviarRequisicao } from './lib/waf';

const ABAS = { vivo: 'Testar ao vivo', resultados: 'Resultados do modelo', artigo: 'Artigo' };

function abaDaUrl() {
  const aba = window.location.hash.slice(1);
  return aba in ABAS ? aba : 'vivo';
}

export default function App() {
  const [aba, setAba] = useState(abaDaUrl);
  const [registros, setRegistros] = useState([]);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    const aoMudar = () => setAba(abaDaUrl());
    window.addEventListener('hashchange', aoMudar);
    return () => window.removeEventListener('hashchange', aoMudar);
  }, []);

  // Toda requisição passa por aqui, para que o caminho, o placar e o histórico
  // registrem tudo do mesmo jeito.
  const enviar = useCallback(async (caso) => {
    setOcupado(true);
    const resultado = await enviarRequisicao({
      rota: caso.rota,
      parametro: caso.parametro,
      valor: caso.payload,
    });
    const registro = {
      ...resultado,
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      hora: new Date().toLocaleTimeString('pt-BR'),
      chave: chaveDoCaso(caso),
      esperado: caso.esperado ?? null,
      camadaEsperada: caso.camadaEsperada,
    };
    setRegistros((anteriores) => [registro, ...anteriores]);
    setOcupado(false);
    return registro;
  }, []);

  return (
    <main className="pagina">
      <Cabecalho />

      <nav className="abas" aria-label="Seções">
        {Object.entries(ABAS).map(([id, nome]) => (
          <a key={id} href={`#${id}`} aria-current={aba === id ? 'page' : undefined}>{nome}</a>
        ))}
      </nav>

      {aba === 'vivo' && (
        <>
          <Console onEnviar={enviar} ocupado={ocupado}>
            <Pipeline r={registros[0]} />
          </Console>
          <Historico registros={registros} onLimpar={() => setRegistros([])} />
          <ConferirRoteiro onEnviar={enviar} ocupado={ocupado} />
        </>
      )}
      {aba === 'resultados' && <Resultados />}
      {aba === 'artigo' && <Artigo />}
    </main>
  );
}
