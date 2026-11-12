# Roteiro do vídeo para o orientador (12/11/2026)

> Pedido do Paulo: um **vídeo explicando o sistema** e um **texto**. Este arquivo diz **o que
> mostrar e que ideia passar** em cada bloco. As frases são do Pedro: ele fala, não lê.
> Duração-alvo: **6 a 8 minutos**.

## Antes de gravar

1. Suba o sistema (ver `como-usar-o-sistema.md`), com `$env:WAF_MODELO='demo'`.
2. Rode `venv\Scripts\python.exe verificar_roteiro.py` e confira se dá **26 de 26**.
3. Abra http://localhost:5173 em tela cheia e feche as outras abas e notificações.
4. Gravar: **Win + Alt + R** (Xbox Game Bar, já vem no Windows) grava a janela com o
   microfone. Ou use o OBS Studio, que é gratuito, se quiser a tela inteira.
5. Faça **um ensaio sem gravar**, com cronômetro.

## Os blocos

| # | Tempo | Na tela | A ideia que você tem que passar |
| :-- | :-- | :-- | :-- |
| 1 | 0:30 | o título no painel | quem você é, o título do TCC e o problema em uma frase: o WAF de regras não pega o que não conhece |
| 2 | 1:00 | um desenho ou o `README` | **a arquitetura**: requisição → normalização → camada 1 (assinaturas) → camada 2 (Random Forest). O ML **soma** ao WAF e não o substitui |
| 3 | 0:30 | o cabeçalho do painel | **avise antes**: o modelo que está rodando é o da demo; os números são do modelo do CSIC 2010 (a receita é a mesma e o bolo é outro) |
| 4 | 3:00 | Testar ao vivo | os 4 casos, um de cada vez, lendo o caminho na tela (abaixo) |
| 5 | 1:30 | aba Resultados | **o resultado principal**, com os números abaixo e a origem de cada um |
| 6 | 1:00 | — (pode ser só você falando) | **as limitações**, ditas por você antes que alguém pergunte |
| 7 | 0:30 | — | o que falta até a entrega |

### Bloco 4: os 4 casos

| Caso | Onde | Valor | O que acontece | O que você diz |
| :-- | :-- | :-- | :-- | :-- |
| 1 | Login | `pedro.almeida` | 200, passa | tráfego normal não é bloqueado |
| 2 | Login | `' OR 1=1--` | 403, camada 1, SQLI-001 | a regra pega o ataque conhecido, **com o nome** |
| 3 | Login | `admin'/**/oR/**/1` | 403, camada 2, p≈0,57 | nenhuma regra casou e o modelo pegou. **Esta é a tese.** |
| 4 | Comentário | `aprenda SELECT e JOIN em SQL` | 403, camada 2, p≈0,97 | o modelo também erra: um falso positivo. Mostrar isso é honestidade |

### Bloco 5: os números (todos com script)

| Número | De onde vem |
| :-- | :-- |
| 32.808 requisições em escopo (18.620 legítimas / 14.188 anômalas) | `ingestao_csic.py` |
| F1 0,7824 ± 0,0088, em 5 folds agrupados por payload | `treino_modelo.py` |
| Assinaturas sozinhas: precisão 100%, recall 23,4%, 0 falso positivo | `avaliacao_hibrida.py` |
| **36,4% dos ataques só o modelo pega** | `avaliacao_hibrida.py` (concordância) |
| Manipulação de parâmetros: de 4,0% para 49,6% de recall (**+45,6 pp**) | `avaliacao_hibrida.py` (por família) |
| SQLi e XSS: as regras já pegam 100%, o ganho do ML é 0 | `avaliacao_hibrida.py` (por família) |
| ~11 ms por requisição quando o modelo decide (p95 13 ms) | `medir_latencia.py` |

> Não cite nenhum número que não esteja nesta tabela.

### Bloco 6: as limitações que você tem que dizer

- No CSIC, as regras já pegam todo SQLi e XSS. O ganho do ML está em manipulação de parâmetros.
- O modelo do CSIC só conhece o tráfego normal de uma loja. Em outro site, é preciso **treinar de
  novo** com o tráfego normal daquele site.
- O WAF olha só os valores da query string: 22,3% dos ataques do CSIC estão no path.
- Uso de IA: diga o que foi usado e pergunte ao Paulo como ele quer que você declare.

## O texto que acompanha o vídeo

**Escrito por você.** Uma página basta. Ele precisa responder a cinco perguntas, nesta ordem:

1. O que o sistema faz? (uma frase)
2. Como ele é montado? (as duas camadas)
3. O que foi medido, e com qual dado?
4. O que deu? (os números do bloco 5)
5. O que ele **não** faz? (as limitações do bloco 6)

No fim, as perguntas para o Paulo: a data exata da entrega, se as 20 páginas contam as
referências, a regra de uso de IA e o objetivo 5.

Quando terminar, mande o rascunho para o Claude revisar. Ele aponta os erros e não reescreve.
