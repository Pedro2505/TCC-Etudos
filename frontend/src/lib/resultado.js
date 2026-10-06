// Funções pequenas usadas por mais de um componente.

/** Número no formato brasileiro, com casas fixas. */
export function numero(valor, casas) {
  if (valor == null) return '—';
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  });
}

/** Fração (0,594) como porcentagem ("59,4%"). */
export function pct(valor, casas = 1) {
  if (valor == null) return '—';
  return `${numero(valor * 100, casas)}%`;
}

/** Identifica um caso pela rota, parâmetro e valor enviado. */
export function chaveDoCaso(caso) {
  return `${caso.rota}|${caso.parametro}|${caso.payload}`;
}

/**
 * O resultado bateu com o que o caso do roteiro previa?
 * Confere o status e também a camada que decidiu. null = caso sem previsão.
 */
export function bateu(r) {
  if (!r || !r.ok || r.esperado == null) return null;
  const statusOk = r.status === r.esperado;
  const camadaOk = r.camadaEsperada === undefined || (r.camada ?? null) === r.camadaEsperada;
  return statusOk && camadaOk;
}
