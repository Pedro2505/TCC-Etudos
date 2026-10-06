import { useCallback, useMemo, useState } from 'react';
import Cabecalho from './components/Cabecalho';
import Fluxo from './components/Fluxo';
import TesteManual from './components/TesteManual';
import Roteiro from './components/Roteiro';
import Historico from './components/Historico';
import { chaveDoCaso } from './lib/resultado';
import { enviarRequisicao } from './lib/waf';

export default function App() {
  const [registros, setRegistros] = useState([]);
  const [ocupado, setOcupado] = useState(false);

  // Toda requisição passa por aqui, venha do roteiro ou do teste manual, para que
  // o histórico e o fluxo registrem tudo do mesmo jeito.
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

  // Resultado mais recente de cada caso, para mostrar na linha dele no roteiro.
  const ultimoPorChave = useMemo(() => {
    const mapa = {};
    for (const r of registros) if (!(r.chave in mapa)) mapa[r.chave] = r;
    return mapa;
  }, [registros]);

  return (
    <main className="pagina">
      <Cabecalho />
      <Fluxo registros={registros} />
      <TesteManual onEnviar={enviar} ocupado={ocupado} />
      <Roteiro onEnviar={enviar} ocupado={ocupado} ultimoPorChave={ultimoPorChave} />
      <Historico registros={registros} onLimpar={() => setRegistros([])} />
    </main>
  );
}
