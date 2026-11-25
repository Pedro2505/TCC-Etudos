# Ficha técnica do projeto — todos os fatos num lugar só

> Montada em 25/11/2026. **Só fatos e números, cada um com a origem.** Não tem texto do
> artigo: a explicação de cada item é sua (ver as perguntas em [`PEDIDOS-DO-PAULO.md`](PEDIDOS-DO-PAULO.md)).
> ❓ = informação que só você tem e que ainda não está registrada em lugar nenhum.

---

## 1. Dataset

| Item | Valor | Origem |
| :--- | :--- | :--- |
| Nome | HTTP DATASET CSIC 2010 | `ingestao_csic.py:3` |
| Quem publicou | Conselho Superior de Investigações Científicas (CSIC), Espanha | — (confirmar na referência) |
| Fonte original | `http://www.isi.csic.es/dataset/` (instável) | `ingestao_csic.py:22` |
| Espelhos | GitHub `msudol/Web-Application-Attack-Datasets`; Kaggle, "CSIC 2010 Web Application Attacks" | `ingestao_csic.py:23`–`24` |
| **De onde você baixou** | **Kaggle**, "CSIC 2010 Web Application Attacks" | dito pelo Pedro em 25/11 |
| Quando | cópia mais antiga no disco: **28/07/2026** (`C:\Dev\Tcc\datasets\CSIC2010\`); copiada para este repositório em 12/08 | data dos arquivos no disco: é a data em que o arquivo chegou ao disco, **não é prova da data do download** |
| Link exato da página no Kaggle | `https://www.kaggle.com/datasets/ispangler/csic-2010-web-application-attacks` (usuário do upload: `ispangler`) | dito pelo Pedro em 25/11 |
| Data de acesso (para a ABNT) | ❓ use a data em que você abrir a página para conferir | |
| Aplicação de origem | loja virtual espanhola (`/tienda1/`), tráfego gerado | `ingestao_csic.py:28` |
| Encoding | percent-encoding em ISO-8859-1, não UTF-8 | `ingestao_csic.py:39`, `:195` |
| Arquivos | `normalTrafficTraining.txt` (36.000) · `normalTrafficTest.txt` (36.000) · `anomalousTrafficTest.txt` (25.065) | `ingestao_csic.py:17`–`20`, conferido no log |
| Onde ficam | `datasets/CSIC2010/` (fora do Git: restrição de redistribuição) | `README.md` |
| Rótulos | só normal / anômalo. **Não diz o tipo de ataque** | `ingestao_csic.py:264` |

### Do bruto ao conjunto em escopo (Tabela 1)

| Etapa | Requisições | Removidas | Origem |
| :--- | ---: | ---: | :--- |
| Total parseado | 97.065 | — | `logs/ingestion_csic.log` |
| Com payload (parâmetro na query ou no corpo) | 51.480 | 45.585 sem parâmetro | idem |
| Após deduplicação | **32.808** | 18.672 | idem, linha 62 |
| — legítimas | 18.620 | | `docs/medicoes/avaliacao_hibrida.md` |
| — anômalas | 14.188 | | idem |

- Chave da deduplicação: `Sentence`, `path`, `metodo`, `Label` (`ingestao_csic.py:362`)
- Ataques sem parâmetro (só no path): 5.585 de 25.065 = **22,3%** (log do `ingestao_csic.py`)
- Família de cada ataque: atribuída **por regex** (`ingestao_csic.FAMILIAS_PAYLOAD`), porque
  o dataset não tem esse rótulo

### Dataset do modelo de demonstração (não é o do artigo)

| Item | Valor | Origem |
| :--- | :--- | :--- |
| Pastas | `datasets/SQL Injection/` e `datasets/XSS/` (CSVs) | `ingestao.py:106`–`107` |
| Tamanho | 57.465 exemplos, 23.765 legítimos | `NECESSARIO.md` §3 (12/11) |
| `datasets/XSS/xss_dataset.csv` | **sintético, não baixado.** Gerado por `C:\Dev\Tcc\generate_xss.py` (commit inicial do projeto antigo, 28/07/2026): 12 payloads XSS e 12 frases "normais" em português ("tênis de corrida masculino", "pedro", "camisa polo azul"…), sorteados 1.000 vezes cada, com números aleatórios | lido em 25/11 |
| `datasets/SQL Injection/` (`sqli.csv`, `sqliv2.csv`, `SQLiV3.csv`) | ❓ os nomes batem com um dataset público de SQLi do Kaggle, mas **não há registro**. Não citar origem sem achar a página | — |

---

## 2. Bibliotecas e ambiente

Versões fixadas em [`requirements.txt`](../../requirements.txt).

| Para quê | Biblioteca | Versão |
| :--- | :--- | :--- |
| API / middleware do WAF | FastAPI · Uvicorn · Starlette | 0.140.7 · 0.51.0 · 1.3.1 |
| Modelo, TF-IDF, validação, métricas | scikit-learn | 1.9.0 |
| Dados | pandas · NumPy · SciPy | 3.0.5 · 2.4.6 · 1.17.1 |
| Salvar o modelo (`.pkl`) | joblib | 1.5.3 |
| Explicabilidade | SHAP | 0.51.0 |
| Gráficos | Matplotlib | 3.11.1 |
| Scripts de teste por HTTP | requests | 2.34.2 |
| Painel | React + Vite | `frontend/package.json` |

Da biblioteca padrão do Python: `urllib.parse` (decodificação), `base64`, `re` (assinaturas).

Máquina das medições: AMD64 (Family 23 Model 96) · Windows · Python 3.11.9 (`docs/medicoes/latencia.md:4`).

---

## 3. Arquitetura (onde está cada coisa no código)

| Etapa | Arquivo e linha |
| :--- | :--- |
| Escolha do modelo carregado (`WAF_MODELO=demo` ou não) | `servidor.py:42`–`48` |
| Entrada da requisição (middleware) | `servidor.py:69` |
| Normalização / desofuscação | `servidor.py:84` |
| Camada 1: assinaturas | `servidor.py:151` → `assinaturas.py` |
| Bloqueio pela camada 1 | `servidor.py:159` |
| Camada 2: features + modelo | `servidor.py:171` → `extrator.py` |
| Bloqueio pela camada 2 (compara com o limiar) | `servidor.py:215`–`219` |
| Encaminhamento à aplicação | `servidor.py:235` |
| O que é inspecionado | só os **valores da query string** (`README.md`, limitações) |

### Camada 1 — assinaturas

- Número de regras e famílias: `python assinaturas.py` imprime (`assinaturas.py:255`).
  Conferido em 25/11: **24 regras em 6 famílias**.
- Famílias cobertas: SQLi, XSS, CRLF, SSI/Comando, Caractere de controle/nulo (tabela por família, §5)

### Camada 2 — modelo

| Parâmetro | Valor | Origem |
| :--- | :--- | :--- |
| Algoritmo | `RandomForestClassifier` | `treino_modelo.py:279` |
| Nº de árvores | 100 | `treino_modelo.py:61` |
| Semente | 42 | `treino_modelo.py:60` |
| Features heurísticas | comprimento, caracteres especiais, keywords SQL, keywords XSS, URL-encode | `treino_modelo.py:171`, `models/model_metadata.json` |
| Features de contexto HTTP | nº de parâmetros, tem corpo, content-length, nº de headers, método (GET/POST/PUT) | `treino_modelo.py:173` |
| TF-IDF | `char_wb`, n-gramas de 2 a 3, 50 termos | `treino_modelo.py:225` |
| Validação | `StratifiedGroupKFold`, 5 folds, agrupado por payload | `treino_modelo.py:59`, `:270` |
| TF-IDF ajustado | dentro de cada fold (só no treino do fold) | `treino_modelo.py:225`–`228` |
| Alvo para o limiar | 1% de falso positivo, sobre probabilidades out-of-fold | `treino_modelo.py:65`, `:344` |

### Os dois modelos

| | Avaliado (artigo) | Demo |
| :--- | :--- | :--- |
| Pasta | `models/` | `models/demo/` |
| Dados | CSIC 2010, 32.808 | SQLi/XSS fora de escopo, 57.465 |
| Limiar | **0,65** | **0,46** |
| Fonte do limiar | `models/model_metadata.json` | `models/demo/model_metadata.json` |

---

## 4. Como reproduzir (ordem dos scripts)

```powershell
pip install -r requirements.txt
python ingestao_csic.py          # Tabela 1
python treino_modelo.py          # validação, ablação, limiar, modelo final -> models/
python avaliacao_hibrida.py      # regras x modelo x combinação -> docs/medicoes/avaliacao_hibrida.md
python medir_latencia.py         # latência -> docs/medicoes/latencia.md (precisa do servidor no ar)
```

Lista completa de script → resultado: tabela "De onde vem cada número" no [`README.md`](../../README.md) da raiz.

---

## 5. Resultados (todos rerodados neste repositório)

### Regras × modelo × combinação — `avaliacao_hibrida.py`

| Configuração | Precisão | Recall | F1 | Taxa de FP | FP | FN |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Camada 1 isolada (assinaturas) | 100,00% | 23,36% | 0,3787 | 0,00% | 0 | 10.874 |
| Camada 2 isolada (modelo, limiar 0,65) | 97,86% | 59,43% | 0,7395 | 0,99% | 184 | 5.756 |
| União / cascata | 97,88% | 59,78% | 0,7422 | 0,99% | 184 | 5.707 |

Matriz de confusão — `medir_erros.py` → `docs/medicoes/erros.md` e **figura
[`docs/medicoes/matriz_confusao.png`](../medicoes/matriz_confusao.png)** (A, B e C lado a lado).
Os FP e FN batem com a tabela acima. Tente a conta à mão antes de olhar (pergunta 5a).

### Os erros da união — `medir_erros.py` → `docs/medicoes/erros.md`

- **Os 5.707 ataques que passaram (40,2%) são 100% tampering.** Nenhum SQLi, XSS, CRLF, SSI ou
  caractere nulo passou. Probabilidade mediana deles: 0,360 (limiar 0,65).
- **Os 184 falsos positivos** se concentram em três páginas: `autenticar.jsp` (124),
  `editar.jsp` (29) e `registro.jsp` (22). Probabilidade mediana 0,730.
- As requisições em si ficam em `datasets/CSIC2010/erros_exemplos.csv` (fora do Git). **Abra e
  olhe uns 10 de cada**: o Paulo pediu para explicar *por que* o legítimo foi bloqueado.

### Complementaridade sobre os 14.188 ataques — `avaliacao_hibrida.py`

ambas as camadas 23,0% · só assinatura 0,3% · só modelo 36,4% · **nenhuma 40,2%**

### Recall por família — `avaliacao_hibrida.py` → `docs/medicoes/recall_por_familia.csv`

| Família | n | Assinaturas | Modelo | Ganho da camada 2 |
| :--- | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 11.332 | 4,0% | 49,6% | +45,6 pp |
| SQLi | 1.018 | 100,0% | 99,9% | +0,0 pp |
| XSS | 952 | 100,0% | 100,0% | +0,0 pp |
| CRLF Injection | 388 | 100,0% | 98,5% | +0,0 pp |
| Injeção SSI/Comando | 384 | 100,0% | 100,0% | +0,0 pp |
| Caractere de controle/nulo | 114 | 100,0% | 63,2% | +0,0 pp |

Viés: a família é atribuída por regex parecido com as assinaturas, então o recall delas por
família é otimista por construção.

### Comparação entre algoritmos (objetivo 5) — `comparar_modelos.py` → `docs/medicoes/comparacao_modelos.md`, `logs/comparar_modelos.log`

Mesmos folds, features e critério de limiar; só o algoritmo muda.

| Algoritmo | F1 (0,5), 5 folds | ROC-AUC | Recall no FP ≤ 1% | F1 no FP ≤ 1% | Recall tampering |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Random Forest** | **0,7824 ± 0,0088** | **0,8880** | **59,43%** | **0,7395** | **49,6%** |
| Regressão logística | 0,5359 ± 0,0119 | 0,7193 | 34,17% | 0,5044 | 18,6% |
| Árvore de decisão | 0,7410 ± 0,0090 | 0,7785 | **não opera**: FP mínimo 18,17% | — | — |

O RF repetiu exatamente o F1 do log de 06/10 e o limiar 0,650, o que mostra que a mudança na
`validar` não alterou nada. **Por que a árvore não chega a 1% de FP:** pergunta para você.
Pista: quantos valores diferentes de "probabilidade" uma árvore só consegue dar, e quantos dá
uma floresta de 100?

### Ablação por bloco de features — `treino_modelo.py` → `logs/model_trainer.log`

F1 médio ± desvio, 5 folds: completo **0,7824 ± 0,0088** · heurísticas + TF-IDF 0,7182 ± 0,0126 ·
só TF-IDF 0,6686 ± 0,0085 · só contexto HTTP 0,4312 ± 0,0077.
**Não substitui a comparação entre algoritmos** (Paulo, ponto 3).

### Latência — `medir_latencia.py` → `docs/medicoes/latencia.md`

Condições: 300 payloads reais do CSIC (150 legítimos / 150 anômalos), 20 de aquecimento,
`n_jobs=1`, **uma requisição por vez**, sem carga concorrente. Em ms, média (p95):

normalização 0,02 · assinaturas 0,06 (0,10) · features 4,60 (5,86) · inferência 6,31 (7,35) ·
**total até a decisão da camada 2: 10,99 (13,21)**. Pelo middleware: decidido na camada 1
0,09 · na camada 2 11,16 (13,04).
**Não usar os 31,94 ms do projeto antigo.**

### Normalização treino × servidor — `medir_normalizacao.py`

0 de 32.808 decisões mudam. 20 textos (0,06%) mudam além da caixa.

### Modelo do CSIC em texto legítimo em português — `verificar_roteiro.py` (06/10)

4 casos legítimos bloqueados (p = 0,88–0,98). Com o modelo demo, os 26 casos passam.

---

## 6. Pendências que esta ficha encontrou

- ✅ CSIC: Kaggle, usuário `ispangler` (25/11).
- ⚠️ **XSS da demo é sintético** (`generate_xss.py`, 24 frases-modelo repetidas). Parte do
  "normal" da demo são exatamente as frases em português do roteiro. Isso pesa no ponto 4 do Paulo.
- ❓ SQLi da demo: origem desconhecida.
- ⚠️ `docs/medicoes/teste_falso_positivo_csic.md` diz "gerado por `false_positive_test.py`",
  com limiar 0,651. Esse script não existe com esse nome neste repositório (o atual é
  `teste_falso_positivo.py`). **Rerode antes de citar qualquer número desse arquivo.**
- ✅ Assinaturas: **24 regras em 6 famílias** (`python assinaturas.py`, 25/11).
- ✅ Comparação entre algoritmos (`comparar_modelos.py`, 25/11).
- ⚠️ O comentário de `treino_modelo.py` (~linha 412) diz que SQLi e XSS são "6,6% das
  anomalias (468 + 472)". O medido é 1.018 + 952 de 14.188 = 13,9%. **Não citar o comentário.**
- ✅ Figura da matriz de confusão (`medir_erros.py`, 25/11).
- ✅ Quais são os 184 falsos positivos e os 5.707 que passaram (`medir_erros.py`, 25/11).
- ❓ Declaração de uso de IA e de código de terceiros (ponto 1).
