# Como usar o sistema, passo a passo

> Gravado em 12/11/2026. Conferido: `verificar_roteiro.py` deu 26 de 26 casos conforme.

## 1. Subir (dois terminais PowerShell)

**Terminal 1, o WAF (porta 8000):**
```powershell
cd C:\Dev\tccNovo
$env:WAF_MODELO='demo'
venv\Scripts\python.exe servidor.py
```
Espere aparecer `Uvicorn running on http://127.0.0.1:8000`.

**Terminal 2, o painel (porta 5173):**
```powershell
cd C:\Dev\tccNovo\frontend
npm run dev
```
Abra **http://localhost:5173** no navegador.

**Para desligar:** `Ctrl+C` em cada terminal.

> Sem a linha `$env:WAF_MODELO='demo'` sobe o **modelo do CSIC**, que é o modelo dos números
> do artigo. Ele bloqueia português legítimo ("pedro.almeida"). Para a demonstração,
> use sempre o demo, e diga isso à banca.

## 2. O caminho de uma requisição

```
você digita  →  normalização  →  CAMADA 1: assinaturas  →  CAMADA 2: Random Forest  →  aplicação
                (decodifica,      (24 regras; casou?        (nota de 0 a 1;
                 minúsculas)       bloqueia com o nome)       acima do limiar? bloqueia)
```

- **403 + "camada 1" + nome da regra (ex.: SQLI-001):** a assinatura pegou.
- **403 + "camada 2" + p=0,xx:** nenhuma regra casou, o modelo achou suspeito.
- **200:** passou pelas duas camadas e chegou à aplicação.

## 3. As abas do painel

| Aba | Para que serve |
| :--- | :--- |
| **Testar ao vivo** | Manda requisições e mostra a requisição passando pelas duas camadas |
| **Resultados do modelo** | Gráficos das medições (limiar, recall por família, concordância) |
| **Artigo** | Mapa por capítulo: tabelas, perguntas, limitações |
| **Banca** | 30 perguntas com pista, e o simulado de 3 min por pergunta |
| **Plano** | Pauta da reunião com o orientador |

## 4. Testar ao vivo

1. Escolha **para onde enviar**:
   - **Login** (`/api/login_alvo`), que monta uma query SQL. É o alvo de SQLi.
   - **Comentário** (`/api/comentarios`), que devolve o texto como HTML. É o alvo de XSS.
2. Digite um valor, ou clique num exemplo das baterias.
3. Clique em **Enviar** e leia o caminho etapa por etapa, e depois o histórico.

## 5. As 6 baterias, e o que cada uma prova

| Bateria | Exemplo | Resultado | O que prova |
| :--- | :--- | :--- | :--- |
| 1. Legítimo | `pedro.almeida` | 200 | o WAF não bloqueia uso normal |
| 2. SQLi | `' OR 1=1--` | 403 camada 1 SQLI-001 | a assinatura pega o ataque conhecido, com nome |
| 3. XSS | `<script>alert(document.cookie)</script>` | 403 camada 1 XSS-001 | idem, para XSS |
| 4. Ofuscação | `%253Cscript%253E...` | 403 camada 1 | a normalização desfaz a ofuscação **antes** das regras |
| 5. Só o modelo | `admin'/**/oR/**/1` | 403 camada 2 p=0,57 | **a tese**: nenhuma regra casou, o ML pegou |
| 6. Onde erra | `aprenda SELECT e JOIN em SQL` | 403 camada 2 p=0,97 | falso positivo: honestidade sobre o limite |

**Roteiro de 30 segundos para a banca:** um caso da bateria 1 (passa) → `' OR 1=1--`
(camada 1, com o nome da regra) → `admin'/**/oR/**/1` (camada 2) → um caso da bateria 6.

## 6. Antes de apresentar

```powershell
venv\Scripts\python.exe verificar_roteiro.py
```
Tem que terminar com `TODOS OS 26 CASOS CONFORME O DECLARADO`. Se algum caso divergir, não
apresente aquele caso.

## Pergunta de banca garantida

> "A bateria 5 roda no modelo demo. O seu artigo mede o modelo do CSIC. O ganho que você
> mostra ao vivo é o mesmo que você mediu?"

Resposta honesta: não é o mesmo modelo. O demo existe porque o modelo do CSIC só conhece a
loja espanhola do dataset. O número do artigo é o do CSIC, e a demo ilustra o mecanismo.
