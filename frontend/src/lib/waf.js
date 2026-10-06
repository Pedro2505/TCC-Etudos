// ============================================================================
// Cliente do WAF: centralizo aqui toda a comunicação com o backend.
//
// Eu tinha esse fetch duplicado nos dois componentes de formulário, e cada um
// tratava a resposta de um jeito. Como o painel de auditoria precisa registrar
// TODA requisição de forma uniforme, unifiquei numa função só.
// ============================================================================

const BASE = 'http://127.0.0.1:8000';

/**
 * Envia uma requisição para a aplicação-alvo e devolve o veredito do WAF.
 *
 * Meço a latência aqui no cliente (round-trip completo) além de ler a latência
 * que o backend reporta. Os dois números são diferentes e vale mostrar os dois:
 * o do backend é o custo da análise do WAF, o do cliente inclui rede e
 * serialização — é o que o usuário final de fato sente.
 */
export async function enviarRequisicao({ rota, parametro, valor }) {
  const url = `${BASE}${rota}?${parametro}=${encodeURIComponent(valor)}`;
  const t0 = performance.now();

  try {
    const resposta = await fetch(url);
    const latenciaCliente = performance.now() - t0;
    const corpo = await resposta.json().catch(() => ({}));
    // Quando o WAF libera, o que ele viu vem dentro de `waf`, junto da resposta da rota.
    const waf = corpo.waf ?? corpo;

    return {
      ok: true,
      bloqueado: resposta.status === 403,
      erroInterno: resposta.status === 503,
      status: resposta.status,
      probabilidade: waf.probabilidade_ataque ?? null,
      limiar: waf.limiar ?? null,
      normalizado: waf.payload_normalizado ?? null,
      // Proveniência do bloqueio no WAF híbrido: 'assinatura' (camada 1) ou
      // 'modelo' (camada 2). Um log que só diz "403" é operacionalmente
      // incompleto — quem opera precisa saber se foi uma regra nomeada ou uma
      // decisão probabilística para distinguir ataque real de falso positivo.
      camada: corpo.camada ?? null,
      regraId: corpo.regra_id ?? null,
      regraNome: corpo.regra_nome ?? null,
      regraFamilia: corpo.regra_familia ?? null,
      latenciaBackend: waf.latencia_ms ?? null,
      latenciaCliente,
      mensagem: corpo.detail ?? corpo.mensagem ?? '(sem mensagem)',
      // Resposta da rota vulnerável. Só existe quando o WAF liberou.
      respostaApp: resposta.status === 200 ? corpo.mensagem ?? null : null,
      payloadEnviado: valor,
      rota,
    };
  } catch (erro) {
    return {
      ok: false,
      status: 0,
      mensagem:
        'Falha de conexão. O servidor está rodando na porta 8000?',
      payloadEnviado: valor,
      rota,
      latenciaCliente: performance.now() - t0,
      erroBruto: String(erro),
    };
  }
}

/** Busca os metadados do modelo carregado, para o painel de transparência. */
export async function buscarInfoWaf() {
  try {
    const resposta = await fetch(`${BASE}/api/waf/info`);
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch {
    return null;
  }
}
