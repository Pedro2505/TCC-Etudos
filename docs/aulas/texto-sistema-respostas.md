# Texto para o orientador: respostas do Pedro (12/11/2026)

> As respostas estão **com as palavras dele**, sem reescrever. Juntas, viram o texto que
> acompanha o vídeo. Ao lado, os fatos com o script de origem, para ele conferir.

## 1. O que o sistema faz?
*(pendente)*

## 2. Como ele é montado?
*(pendente; a explicação está no chat de 12/11: middleware → normalização → camada 1 → camada 2)*

## 3. O que foi medido, e com qual dado?
- Pedro: "seria o data set http csic 2010"
- Pedro: "só com as regras e com regras mais o modelo"
- Fatos: CSIC 2010 é público, com tráfego de uma loja virtual espanhola; 32.808 requisições
  (18.620 normais / 14.188 ataques), de `ingestao_csic.py`.

## 4. O que deu?
- Pedro: "o ganho esta em detectar a manipulacao de parametros"
- Fatos: só regras pegam 23,4% dos ataques; regras + modelo, 59,8%. Manipulação de
  parâmetros passa de 4,0% para 49,6% (+45,6 pontos). Custo: 1,0% de falso positivo (184 de
  18.620). Tudo de `avaliacao_hibrida.py`.
- Pedro: "custou que ele está barrando 1%, ou seja, 1% de falso positivo" (chamou de
  "falso negativo" duas vezes antes de acertar, com a pergunta "o alarme tocou? tinha ladrão?")

## 4b. Conceito levantado por ele
- Pedro: "esses inocente barrados seriam falso positivo né" (correto). Só regras: 0 de
  18.620; regras + modelo: 184 de 18.620 (1,0%), de `avaliacao_hibrida.py`.

## 5. O que ele não faz?
- Pedro: "ele n substitui um waf padrao" (é decisão de projeto, não limitação: vai para a
  pergunta 2)
- Pedro: "ele n funciona em outro site sem treinar de novo" (correto: o modelo do CSIC
  bloqueia português legítimo com p = 0,88–0,98, de `verificar_roteiro.py` contra o modelo
  do CSIC, 06/10)
- Pedro respondeu primeiro "cerca de 30%" para o ganho em SQLi/XSS. **Errado.** O ganho é
  +0,0 pontos (as regras já pegam 100%). Corrigido na hora. Ele acertou em seguida que o
  ganho de +45,6 pontos é em "manipulação de parâmetros" (`avaliacao_hibrida.py`).
  **Vigiar:** não deixar nenhum número de ganho em SQLi/XSS entrar no texto.


O que o sistema faz? R: ele detecta requisições maliciosa e bloqueia antes de chegar na aplicação, usando assinatura e modelo

Como ele é montado? R: oo sistema e montado assim: 
1: onde fica o middleware o (servidor.py) ele fica na frente da aplicacao e intercepta qualquer requisiçao antes de chegar nela 
2: normalização ele desfaz os disfarces  ex: %27 vira ',  <ScRiPt> vira <script> 
3: camada de assinatura onde tem  padrão de ataque conhecido e onde sao barrados 23,4%
4: o modelo de ML onde as requisições q passam pela camada de assinatura sao barradas pelo modelo treinado com um dataset HTTP DATASET CSIC 2010, se passar do limiar ele e barrado se n passa pra aplicacao

O que foi medido, e com qual dado?  eu usei o dataset HTTP DATASET CSIC 2010 (de uma loja virtual espanhola, dados publicos), 32.808 requisições: 18.620 normais e 14.188 ataques. oq eu medi: só com as regras e com regras mais o modelo

O que deu?  
o ganho esta em detectar a manipulacao de parametros
custou que ele está barrando 1%, ou seja, 1% de falso positivo

O que ele não faz?
ele n funciona em outro site sem treinar de novo