from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from starlette.concurrency import run_in_threadpool

# Caminho único de inferência, compartilhado com os scripts de teste.
# Antes eu duplicava a montagem da matriz aqui e em mais três arquivos, o que gerava
# divergência silenciosa quando eu alterava as features.
from extrator import carregar_artefatos, classificar

# CAMADA 1 do WAF híbrido. Ver o docstring de assinaturas.py para o enquadramento:
# este trabalho não propõe substituir um WAF de assinaturas pelo modelo, e sim somar
# as duas camadas, porque os perfis de erro são complementares.
import assinaturas

app = FastAPI(title="WAF Híbrido (assinaturas + ML) - TCC")

# 1. Liberando o CORS para o Frontend React (Porta 5173 do Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# --- CARREGANDO O MODELO ---
# Carrego uma única vez na inicialização. Desserializar um .pkl a cada requisição
# colocaria I/O de disco no caminho crítico; com o modelo em RAM, o custo por
# requisição é apenas a travessia das árvores.
#
# carregar_artefatos() também ajusta n_jobs=1: medi 28,54ms de inferência com
# n_jobs=-1 contra 7,95ms com n_jobs=1 para uma única amostra. O despacho ao pool de
# threads do joblib custa mais que percorrer as 100 árvores quando há uma linha só.
# Qual modelo carregar. Um WAF de ML aprende o comportamento normal de UMA aplicação:
# o modelo do CSIC 2010 conhece o tráfego da loja "tienda1" (espanhol) e bloqueia
# português com p≈0,90, porque está fora da distribuição que ele viu. Para a
# demonstração ao vivo, cuja aplicação-alvo é em português, uso o modelo de demo.
#
#   WAF_MODELO=demo python servidor.py     -> models/demo/  (demonstração)
#   python servidor.py                     -> models/       (modelo do CSIC, monografia)
PASTA_MODELO = 'models/demo' if os.getenv('WAF_MODELO') == 'demo' else 'models'

print(f"Carregando o modelo de {PASTA_MODELO}/...")
modelo_rf, vetorizador, METADATA = carregar_artefatos(PASTA_MODELO)
LIMIAR = METADATA.get('limiar_decisao', 0.5)
print(f"Dataset de treino: {METADATA.get('dataset', 'não informado')}")
print(f"Features: {METADATA.get('n_colunas', '?')} | "
      f"limiar de decisão calibrado: {LIMIAR:.3f}")
print(f"Validação: {METADATA.get('validacao', 'não informada')}")

# Cabeçalhos CORS repetidos nas respostas de bloqueio.
# Por que preciso deles manualmente: o @app.middleware("http") é registrado DEPOIS do
# CORSMiddleware, e no Starlette isso o coloca mais externo na pilha. Quando ele
# devolve uma resposta por conta própria, o CORSMiddleware não é executado e o browser
# recusaria a resposta por Same-Origin Policy — o frontend veria um erro de rede em vez
# do 403 com a explicação do bloqueio.
CABECALHOS_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}


# --- O MIDDLEWARE (O ESCUDO INVISÍVEL) ---
@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    """
    Toda requisição HTTP que chegar (GET, POST, etc) cai aqui ANTES de chegar na aplicação.
    """
    start_time = time.time()
    
    # 1. Extração do "Payload" real (O que o usuário digitou)
    # ERRO GRAVE ANTERIOR: Estávamos passando a URL inteira (http://localhost:8000/busca?q=...).
    # O modelo foi treinado apenas com o texto do ataque. A URL inteira contém barras (/),
    # dois pontos (:) e interrogações (?) que confundiam o modelo, gerando Falsos Positivos!
    # NOVO: CAMADA DE NORMALIZAÇÃO E DESOFUSCAÇÃO (O(1))
    # Hackers usam Base64 e URL Encoding duplo para enganar os WAFs.
    from urllib.parse import unquote
    import base64
    
    def decodificador_ofuscacao(texto: str) -> str:
        if not texto: return texto
        
        # 1. URL Decode Recursivo (Remove as cascas da cebola de ofuscação %2527 -> %27 -> ')
        texto_descascado = unquote(texto)
        while texto_descascado != texto:
            texto = texto_descascado
            texto_descascado = unquote(texto)
            
        # 2. Heurística de Base64 Decode
        # Tentamos decodificar tudo que se pareça minimamente com Base64. 
        # A operação try/except com b64decode adiciona <1ms de latência.
        try:
            # Adiciona paddings '=' caso faltem, para evitar padding error
            padded = texto + '=' * (4 - len(texto) % 4)
            decodificado_b64 = base64.b64decode(padded).decode('utf-8')
            # Se for texto legível e não lixo binário, assumimos que era B64
            if decodificado_b64.isprintable():
                texto = decodificado_b64
        except Exception:
            pass
            
        # 3. Homogeneização Lexical (Prevenindo Case Mixing como <ScRiPt>)
        return texto.lower()

    # --- EXCEÇÃO PARA ARQUIVOS ESTÁTICOS ---
    # BUG CORRIGIDO: a versão anterior testava `"/static" in payload_url`, onde
    # payload_url é o payload DECODIFICADO DA QUERY, não o path. Isso criava um bypass
    # completo do WAF: bastava enviar ?q=/static<script>alert(1)</script> para desligar
    # a proteção. Agora o teste é sobre o path, que é o que se pretendia verificar.
    caminho = request.url.path
    if caminho == "/" or caminho.startswith("/static") or caminho.endswith(
            (".css", ".js", ".ico", ".svg", ".png", ".jpg", ".woff", ".woff2")):
        return await call_next(request)

    # 1. Extração do payload: apenas os VALORES dos query params.
    # Passei a URL inteira ao modelo numa versão anterior, e as barras, dois-pontos e
    # interrogações da URL deslocavam as contagens de caracteres especiais o
    # suficiente para inverter decisões.
    #
    # LIMITAÇÃO DECLARADA: não inspeciono corpo POST, headers, cookies nem o path.
    # Medi que 22,3% dos ataques do CSIC 2010 estão no path, portanto são invisíveis
    # para esta superfície de inspeção. É limite de arquitetura, não de modelo.
    valores_parametros = list(request.query_params.values())
    payload_bruto = " ".join(valores_parametros)
    if not payload_bruto.strip():
        # Sem parâmetro não há payload a classificar. Antes eu caía para o path aqui,
        # o que fazia o modelo julgar strings de rota que ele nunca viu no treino.
        return await call_next(request)

    payload = decodificador_ofuscacao(payload_bruto)

    # ========================================================================
    # CAMADA 1 — ASSINATURAS
    # ========================================================================
    # Ordem deliberada: barata e certa primeiro, cara e abrangente depois.
    #
    # Medi sobre o CSIC 2010 que esta camada tem PRECISÃO DE 100% e ZERO falso
    # positivo em 18.620 requisições legítimas. Quando ela dispara, não há
    # dúvida a resolver — e o bloqueio sai com uma regra NOMEADA, que é o que o
    # log de auditoria precisa para ser operacionalmente útil.
    #
    # Uma nota de honestidade que eu declaro na defesa: em termos de DECISÃO,
    # esta cascata é equivalente a "assinatura OU modelo". Ordenar não aumenta o
    # recall. O que a ordem entrega é (i) proveniência do bloqueio, (ii) o custo
    # da inferência evitado quando a camada 1 já resolveu, e (iii) o orçamento de
    # falso positivo, que a camada 1 quase não consome.
    regra = assinaturas.avaliar(payload)
    if regra is not None:
        latencia_ms = (time.time() - start_time) * 1000
        print(f"[WAF][CAMADA 1] BLOQUEADO  regra={regra.id} ({regra.familia}) | "
              f"Payload: {payload[:120]!r} | {latencia_ms:.2f}ms")
        return JSONResponse(
            status_code=403,
            content={
                "detail": f"Acesso Negado: assinatura {regra.id} — {regra.nome}.",
                "camada": "assinatura",
                "regra_id": regra.id,
                "regra_nome": regra.nome,
                "regra_familia": regra.familia,
                "payload_normalizado": payload,
                "latencia_ms": latencia_ms,
            },
            headers=CABECALHOS_CORS,
        )

    # ========================================================================
    # CAMADA 2 — MODELO DE MACHINE LEARNING
    # ========================================================================
    # Julga o que a camada 1 liberou. É aqui que está a contribuição do trabalho:
    # medi que 36,6% dos ataques do CSIC são detectados SOMENTE por esta camada —
    # requisições que um WAF de assinaturas operando sozinho deixaria passar
    # inteiras, porque não contêm assinatura nenhuma para casar.

    # 2. Contexto HTTP real da requisição.
    # Estas features valem 6,7 pontos de F1 na validação cruzada, e aqui eu tenho os
    # valores verdadeiros — diferente dos scripts de teste, que usam padrões.
    contexto = {
        'metodo': request.method,
        'n_parametros': len(request.query_params),
        'tem_corpo': int(bool(request.headers.get('content-length', '0') != '0')),
        'content_length': int(request.headers.get('content-length') or 0),
        'n_headers': len(request.headers),
    }

    # 3. Inferência em threadpool, para não bloquear o event loop assíncrono.
    try:
        eh_ataque, probabilidade = await run_in_threadpool(
            classificar, payload, modelo_rf, vetorizador, METADATA, contexto)
    except Exception as e:
        # FAIL-CLOSE HONESTO.
        # A versão anterior devolvia 403 com a mensagem "ATAQUE NEUTRALIZADO PELO
        # MODELO!" para qualquer exceção interna. Isso contaminava o log de auditoria:
        # falha técnica aparecia como detecção, inflando as métricas de detecção com
        # bugs meus. Continuo bloqueando (fail-close é a postura correta para um WAF),
        # mas o log e a resposta agora dizem a verdade sobre o que aconteceu.
        print(f"[WAF][ERRO INTERNO] {type(e).__name__}: {e} | "
              f"Payload: {payload_bruto[:120]!r} | Fail-close aplicado")
        return JSONResponse(
            status_code=503,
            content={
                "detail": "WAF indisponível: falha interna na análise. "
                          "Requisição recusada por precaução (fail-close).",
                "erro_interno": True,
                "latencia_ms": (time.time() - start_time) * 1000,
            },
            headers=CABECALHOS_CORS,
        )

    latencia_ms = (time.time() - start_time) * 1000

    # 4. O veredito, usando o limiar CALIBRADO em vez do 0,5 implícito do .predict().
    # O limiar foi escolhido em treino_modelo.py sob um alvo declarado de falso
    # positivo (≤1%), sobre probabilidades out-of-fold.
    if eh_ataque:
        print(f"[WAF][CAMADA 2] BLOQUEADO  p={probabilidade:.3f} (limiar {LIMIAR:.3f}) | "
              f"Payload: {payload[:120]!r} | {latencia_ms:.2f}ms")
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Acesso Negado: anomalia detectada pelo modelo — "
                          "nenhuma assinatura casou com este payload.",
                "camada": "modelo",
                "probabilidade_ataque": round(probabilidade, 4),
                "limiar": LIMIAR,
                "payload_normalizado": payload,
                "latencia_ms": latencia_ms,
            },
            headers=CABECALHOS_CORS,
        )

    print(f"[WAF] PERMITIDO  p={probabilidade:.3f} (limiar {LIMIAR:.3f}) | "
          f"sem assinatura | Payload: {payload[:120]!r} | {latencia_ms:.2f}ms")

    request.state.waf_latency = latencia_ms
    request.state.waf_probabilidade = probabilidade
    request.state.waf_normalizado = payload
    return await call_next(request)


def veredito_do_waf(request: Request) -> dict:
    """O que o WAF viu numa requisição que ele liberou. Só para o painel de demonstração."""
    estado = request.state
    probabilidade = getattr(estado, 'waf_probabilidade', None)
    return {
        "probabilidade_ataque": round(probabilidade, 4) if probabilidade is not None else None,
        "limiar": LIMIAR,
        "payload_normalizado": getattr(estado, 'waf_normalizado', None),
        "latencia_ms": getattr(estado, 'waf_latency', None),
    }

# --- ROTA DE TRANSPARÊNCIA DO WAF ---

@app.get("/api/waf/info")
def informacoes_do_waf():
    """
    Expõe qual modelo está carregado e sob qual metodologia foi validado.

    Criei esta rota para a defesa. Eu mantenho dois modelos com papéis diferentes (o
    do CSIC 2010, que gera as métricas da monografia, e o de demonstração, treinado
    com tráfego benigno em português), e apresentar um como se fosse o outro seria
    desonesto. Com esta rota o painel mostra na tela qual está rodando, então a banca
    não precisa acreditar na minha palavra.

    Não recebe parâmetros, portanto o middleware a libera sem classificar.
    """
    metricas = METADATA.get('metricas_validacao_cruzada', {})
    return {
        "arquitetura": "cascata: assinaturas (camada 1) -> modelo (camada 2)",
        "n_assinaturas": len(assinaturas.REGRAS),
        "familias_assinatura": assinaturas.FAMILIAS_COBERTAS,
        "modelo": PASTA_MODELO,
        "dataset_treino": METADATA.get('dataset', 'não informado'),
        "validacao": METADATA.get('validacao', 'não informada'),
        "limiar_decisao": LIMIAR,
        "alvo_falso_positivo": METADATA.get('alvo_falso_positivo'),
        "n_features": METADATA.get('n_colunas'),
        "n_arvores": METADATA.get('n_arvores'),
        "n_amostras_treino": METADATA.get('n_amostras_treino'),
        "f1_medio": (metricas.get('f1') or {}).get('media'),
        "f1_desvio": (metricas.get('f1') or {}).get('desvio'),
        "recall_medio": (metricas.get('recall') or {}).get('media'),
        "precisao_media": (metricas.get('precisao') or {}).get('media'),
    }


# --- ROTAS DA APLICAÇÃO ALVO (O que estamos protegendo) ---

@app.get("/api/login_alvo")
def login_fake_vulneravel(usuario: str = "", request: Request = None):
    # Rota que finge ser um login. Se o WAF deixar passar, ela executa a query.
    consulta_sql = f"SELECT * FROM usuarios WHERE username = '{usuario}'"
    return {"mensagem": f"Consulta '{consulta_sql}' executada no banco de dados.",
            "waf": veredito_do_waf(request)}

@app.get("/api/comentarios")
def rota_busca(texto: str = "", request: Request = None):
    # Rota alvo de XSS. Se passar pelo WAF, o "XSS" foi guardado.
    return {"mensagem": f"O comentário '{texto}' foi salvo com sucesso!",
            "waf": veredito_do_waf(request)}

# Montar arquivos estáticos (Dashboard Web)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor web na porta 8000
    uvicorn.run("servidor:app", host="127.0.0.1", port=8000, reload=True)
