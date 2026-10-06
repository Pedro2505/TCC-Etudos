/**
 * O caminho da requisição numa linha só, com a etapa que decidiu por último em
 * destaque e a contagem da sessão embaixo de cada camada.
 */
export default function Fluxo({ registros }) {
  const validos = registros.filter((r) => r.ok);
  const ultimo = validos[0];

  const decidiu = !ultimo
    ? null
    : ultimo.camada === 'assinatura'
      ? 'regras'
      : ultimo.camada === 'modelo'
        ? 'modelo'
        : ultimo.status === 200
          ? 'aplicacao'
          : null;

  const etapas = [
    { id: 'requisicao', nome: 'requisição', conta: registros.length, unidade: 'enviadas' },
    { id: 'normalizacao', nome: 'normalização' },
    {
      id: 'regras',
      nome: 'regras',
      conta: validos.filter((r) => r.camada === 'assinatura').length,
      unidade: 'barradas',
    },
    {
      id: 'modelo',
      nome: 'modelo',
      conta: validos.filter((r) => r.camada === 'modelo').length,
      unidade: 'barradas',
    },
    {
      id: 'aplicacao',
      nome: 'aplicação',
      conta: validos.filter((r) => r.status === 200).length,
      unidade: 'liberadas',
    },
  ];

  return (
    <ol className="fluxo" aria-label="Caminho da requisição">
      {etapas.map((e) => (
        <li key={e.id} className={decidiu === e.id ? 'decidiu' : undefined}>
          <span className="fluxo-nome">{e.nome}</span>
          {e.conta != null && (
            <span className="fluxo-conta">
              {e.conta} <span className="fraco">{e.unidade}</span>
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}
