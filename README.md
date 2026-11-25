# Detecção de Anomalias em Aplicações Web usando Machine Learning

**Autor:** Pedro Henrique Juliani · **Orientador:** Paulo Rogerio de Mello Cardoso · Unimar, 2026

WAF (*Web Application Firewall*) em duas camadas, como middleware Python (FastAPI):

1. **Camada 1 — assinaturas** (`assinaturas.py`): 24 expressões regulares nomeadas.
2. **Camada 2 — Random Forest** (`treino_modelo.py`, `extrator.py`): julga o que a camada 1
   deixou passar, com features heurísticas, TF-IDF de caracteres e contexto HTTP.

A camada de ML é **acrescentada** ao WAF de assinaturas e não o substitui. A pergunta medida
é: *dado um WAF de assinaturas, quanto de detecção a mais a camada de ML traz, e a que custo
de falso positivo?*

Base de avaliação: **HTTP DATASET CSIC 2010**, com 32.808 requisições em escopo (18.620 legítimas
e 14.188 anômalas).

---

## Como rodar

Requisitos: Python 3.11 e Node 20 (o Node é só para o painel).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Dados.** Os arquivos do CSIC 2010 não estão no repositório, por causa da restrição de
redistribuição da fonte. Coloque `normalTrafficTraining.txt`, `normalTrafficTest.txt` e
`anomalousTrafficTest.txt` em `datasets/CSIC2010/`.

**Modelos.** Os `.pkl` também ficam fora do Git. Para gerá-los:

```powershell
python ingestao_csic.py          # parse e contagens do dataset
python treino_modelo.py          # validação cruzada, ablação, limiar, modelo final -> models/
python avaliacao_hibrida.py      # assinaturas x modelo x cascata -> docs/medicoes/
```

### Demonstração com o modelo avaliado (o do artigo)

```powershell
python servidor.py                             # modelo do CSIC, models/
python demo_csic.py                            # reenvia requisições reais do CSIC e mostra qual camada decide
```

O `demo_csic.py` manda requisições GET reais do CSIC (legítimas, SQLi, XSS e tampering) para o
path original da loja. 403 = o WAF bloqueou; 404 = o WAF deixou passar. **Mostra o mecanismo, não
o desempenho:** o modelo de `models/` foi treinado com todas as 32.808 requisições, inclusive estas.
O desempenho é o das probabilidades out-of-fold (`docs/medicoes/avaliacao_hibrida.md`).

### Demonstração com o painel (outro modelo)

```powershell
$env:WAF_MODELO='demo'; python servidor.py     # API em http://127.0.0.1:8000
cd frontend; npm install; npm run dev          # painel em http://localhost:5173
python verificar_roteiro.py                    # confere os 26 casos do roteiro
```

> **Atenção: o painel usa outro modelo, e nenhum número do artigo vem dele.** `models/demo/`
> foi treinado com datasets públicos de SQLi e com um dataset de XSS **sintético**, gerado no
> projeto antigo a partir de 24 frases-modelo (`generate_xss.py`). O modelo do CSIC conhece só o
> tráfego "normal" da loja espanhola do dataset e bloqueia entradas legítimas em português; por
> isso o painel, que é em português, usa o modelo de demonstração. A rota `/api/waf/info` mostra
> qual modelo está carregado.

---

## De onde vem cada número

Todo número do artigo sai de um script deste repositório:

| Resultado | Script | Saída |
| :--- | :--- | :--- |
| Composição do dataset (97.065 → 51.480 com payload → 32.808 após deduplicação) | `ingestao_csic.py` | log no console |
| Validação cruzada (StratifiedGroupKFold 5, agrupado por payload), ablação por bloco de features, limiar | `treino_modelo.py` | `models/model_metadata.json`, `docs/medicoes/curva_limiar.csv` |
| Camada 1 × camada 2 × união × cascata, matriz de concordância, recall por família | `avaliacao_hibrida.py` | `docs/medicoes/avaliacao_hibrida.md`, `recall_por_familia.csv` |
| Falso positivo em tráfego legítimo | `teste_falso_positivo.py` | `docs/medicoes/teste_falso_positivo*.md` |
| Latência por etapa e ponta a ponta | `medir_latencia.py` ¹ | `docs/medicoes/latencia.md` |
| Normalização do treino × do servidor | `medir_normalizacao.py` ¹ | `docs/medicoes/normalizacao_treino_vs_servidor.md` |
| Comparação entre algoritmos (objetivo 5) | `comparar_modelos.py` ² | `docs/medicoes/comparacao_modelos.md` |
| Matriz de confusão, falsos positivos e falsos negativos | `medir_erros.py` ¹ | `docs/medicoes/erros.md`, `matriz_confusao.png` |
| Validação manual da família atribuída | `validar_familias.py` | `docs/medicoes/validacao_familias.md` |
| Explicabilidade (SHAP) | `explicacao.py` | `docs/shap_explain_report.png` |

² Escrito com assistente de IA (Claude) a pedido do autor, em 25/11/2026. Usa a mesma
validação do `treino_modelo.py` e não grava modelo.

¹ Scripts de medição de apoio escritos com assistente de IA (Claude). Eles não treinam
nem decidem nada, só medem. O cabeçalho de cada um declara isso.

## Estrutura

```
servidor.py            middleware FastAPI: normalização -> camada 1 -> camada 2
assinaturas.py         camada 1 (regras nomeadas)
extrator.py            features e caminho único de inferência
treino_modelo.py       treino e validação da camada 2
ingestao_csic.py       parser do CSIC 2010, rotulagem por família, deduplicação, grupos
ingestao.py            datasets do modelo de demonstração
avaliacao_hibrida.py   avaliação das duas camadas juntas
teste_falso_positivo.py, validar_familias.py, explicacao.py   medições complementares
medir_latencia.py, medir_normalizacao.py                      medições de apoio ¹
exportar_painel.py, verificar_roteiro.py                      apoio ao painel e à demo
frontend/              painel React (testar ao vivo, resultados)
models/                metadados dos modelos (os .pkl ficam fora do Git)
logs/                  saída de console das rodadas que geraram os números
docs/medicoes/         todas as medições geradas pelos scripts
docs/artigo/           o artigo: modelo ABNT da Unimar e a 1ª entrega (cap. 1)
docs/aulas/            material de orientação e estudo (índice em docs/aulas/README.md)
CONTINUAR.md           ponto de retomada: estado atual e plano dia a dia
NECESSARIO.md          matéria-prima do artigo: números (com script), decisões, limitações
ROTEIRO.md, diario.md  plano das 13 etapas e registro das sessões
```

Os scripts ficam na raiz de propósito: eles se importam entre si (`servidor.py` usa
`extrator.py` e `assinaturas.py`) e gravam em caminhos relativos (`models/`, `docs/medicoes/`).
Movê-los para uma subpasta exigiria mexer no código que gera os números do artigo.

## Limitações conhecidas

- **SQLi e XSS do CSIC são pegos 100% pelas assinaturas.** O ganho da camada de ML está nas
  anomalias sem assinatura (manipulação de parâmetros): de 4,0% para 49,6% de recall.
- **As famílias foram atribuídas por regex**, porque o CSIC rotula só normal/anômalo. Por isso,
  o recall das assinaturas por família é otimista por construção.
- **O middleware inspeciona só os valores da query string.** 22,3% dos ataques do CSIC estão
  no path, fora dessa superfície.
- **Treino e servidor normalizam o texto de formas diferentes.** No CSIC, isso não muda nenhuma
  decisão (0 de 32.808, ver `normalizacao_treino_vs_servidor.md`).
- **O modelo não generaliza para outra aplicação sem novo treino** (ver a seção da demonstração).
- **A latência foi medida com uma requisição por vez**, sem carga concorrente.
