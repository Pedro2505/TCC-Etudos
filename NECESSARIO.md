# NECESSARIO — material bruto do artigo

> Coletor. Tudo que sai de uma sessão e tem destino no artigo cai aqui primeiro.
> **Não é o artigo.** É a matéria-prima dele, para não depender da memória em outubro.
>
> Inventário das 12 tabelas e figuras: [`docs/aulas/estrutura-do-artigo.md`](docs/aulas/estrutura-do-artigo.md) §2.
> Estrutura dos 7 capítulos: mesmo arquivo, §1. Não duplicar aqui.

## Regra deste arquivo

Nada entra sem **origem**. Frase minha ou decisão tomada em sessão, com a data.
Número só entra com o script que o gerou. Se não sei qual script, escrevo "não medi".

---

## 1. Frases já prontas (minhas, saíram das sessões)

**Sobre acurácia** — 13/08, Tarefa 0:

> A acurácia não distingue um detector que funciona de um que não faz nada. No cenário
> testado, um classificador que libera todo o tráfego obtém os mesmos 95% do detector
> avaliado.

**Sobre o enquadramento (por que somar e não substituir)** — 13/08:

> Não faz sentido trocar algo que já funciona por algo novo. Substituir significaria abrir
> mão de um detector com precisão altíssima e proveniência auditável em troca de um que
> erra mais em tráfego legítimo e responde "probabilidade 0,87" quando o analista pergunta
> por que bloqueou.

**Primeira frase do capítulo 2 escrita por ele** — 19/08, seção 2.4:

> O vazamento de dados (*data leakage*) ocorre quando os dados de teste vazam e vão para os
> dados de treino.

*Estado:* frase 1 fechada. A **frase 2** falta e tem que dizer duas coisas: o recall fica
alto **no experimento**, e isso sugere um desempenho que o sistema não terá em produção.

*Como ela nasceu (vale para o diário):* ele definiu vazamento como causa de **overfitting**
na primeira tentativa. Corrigiu sozinho depois da pergunta dos dois alunos que receberam o
gabarito — o aluno que estudou também tirou 98, logo o defeito está na **medição**, não no
modelo. Também escreveu que o vazamento "deixa o recall ruim"; corrigiu para **alto** ao
lembrar que a nota do gabarito foi 98.

---

## 2. Conteúdo levantado, ainda por escrever (eu escrevo)

Cada item abaixo é um parágrafo que ainda não existe. A ideia está fechada; o texto não.

| # | Conteúdo | Vai para | Levantado em |
| :--- | :--- | :--- | :--- |
| 1 | `predict_proba` é fração de árvores que votou "ataque", não probabilidade calibrada — logo o limiar precisa ser escolhido, não herdado do 0,5 | Metodologia (limiar) | 13/08, revisto 19/08 |
| 2 | Uma divisão treino/teste só mede sorte; reportar média ± desvio entre folds | Metodologia (validação) | 19/08 |
| 3 | TF-IDF ajustado por fold, nunca sobre o dataset inteiro — 5 vocabulários, não 1 | Metodologia (validação) | 19/08 |
| 4 | Agrupamento por payload no split: GET e POST do mesmo ataque não podem cair em lados opostos. Dedup exata não resolve | Metodologia (validação) | 19/08 |
| 5 | Comparação `KFold` × `GroupKFold` como evidência de validação honesta — o recall cai, e a queda é o resultado | Resultados | 19/08 |
| 6 | Rodar `KFold` comum contra `StratifiedGroupKFold` agrupado por payload e mostrar o recall inflar sem o agrupamento | Resultados + Metodologia | 19/08 |
| 7 | Complementaridade das camadas: quantos ataques só a assinatura pega, quantos só o modelo pega, quantos nenhuma | Resultados (**resultado central**) | 19/08 |
| 8 | Latência por etapa do pipeline e o efeito do `n_jobs` na inferência unitária — o custo do delta | Resultados | 19/08 |
| 9 | Por que cascata e união são equivalentes em decisão, e por que a cascata existe mesmo assim (proveniência do bloqueio e custo evitado) | Desenvolvimento | 19/08 |

---

## 2b. Números da auditoria de 19/08 — **NENHUM PODE SER CITADO AINDA**

Vieram de `C:\Dev\Tcc\docs\medicoes\`, geradas pelo projeto antigo. **Regra nº 1: só entram
no artigo depois de rerodados por script deste repositório.** Estão aqui como referência do
que esperar, e para detectar se a reprodução der diferente.

Base: CSIC 2010, 32.808 requisições em escopo (18.620 legítimas / 14.188 anômalas).
Validação `StratifiedGroupKFold(5)` agrupada por payload, TF-IDF por fold, probabilidades
out-of-fold, limiar 0,650.

| Configuração | Precisão | Recall | F1 | Taxa de FP |
| :--- | ---: | ---: | ---: | ---: |
| Camada 1 isolada (24 assinaturas) | 100,00% | 23,36% | 0,3787 | 0,00% |
| Camada 2 isolada (modelo) | 97,86% | 59,43% | 0,7395 | 0,99% |
| União / cascata | 97,88% | 59,78% | 0,7422 | 0,99% |

Complementaridade sobre os 14.188 ataques: ambas 23,0% · **só assinatura 0,3%** ·
**só modelo 36,4%** · nenhuma 40,2%.

Recall por família — **a tabela que decide a defesa**:

| Família | n | Assinaturas | Modelo | Ganho da camada 2 |
| :--- | ---: | ---: | ---: | ---: |
| Tampering sem assinatura | 11.332 | 4,0% | 49,6% | **+45,6 pp** |
| SQLi | 1.018 | 100,0% | 99,9% | +0,0 pp |
| XSS | 952 | 100,0% | 100,0% | +0,0 pp |
| CRLF Injection | 388 | 100,0% | 98,5% | +0,0 pp |
| Injeção SSI/Comando | 384 | 100,0% | 100,0% | +0,0 pp |
| Caractere de Controle/Nulo | 114 | 100,0% | 63,2% | +0,0 pp |

Latência (300 execuções por etapa): extração de features 2,28 ms média / 2,71 ms p95 ·
inferência 28,54 ms / 30,50 ms · pipeline completo 31,94 ms / 34,33 ms. Com `n_jobs=1` a
inferência cai para 7,95 ms — 3,6×.

**Viés a declarar junto da tabela por família:** a família é atribuída por regex, e as
assinaturas descrevem os mesmos fenômenos — o recall da camada 1 por família é otimista por
construção. Os números imunes a esse viés são os das duas primeiras tabelas, medidos contra
o rótulo real do dataset.

---

## 3. Pendências que viram parágrafo de limitações

- **Zero-day.** Palavra ausente do vocabulário do treino é ignorada pelo TF-IDF. Isso limita
  o que o modelo pode prometer sobre ataque nunca visto. A seção 1.2 da entrega parcial
  promete zero-day; ou suaviza, ou declara aqui. *(19/08)*
- **Acurácia** entra na versão final como **contraexemplo**, não como métrica de resultado.
- **Cortes de escopo declarados:** Etapa 11 em versão mínima; `datasets/SQL Injection/` e
  `datasets/XSS/` fora de escopo.

- **Ganho zero no escopo declarado.** Assinaturas pegam 100% de SQLi e XSS; a camada de ML
  acrescenta +0,0 pp nessas duas famílias. Ou o escopo alarga, ou se mede ganho sobre
  SQLi/XSS ofuscados. Decisão marcada para **10/09**. *(19/08)*
- **Objetivo específico 5 não cumprido pelo projeto antigo:** só Random Forest, sem
  comparação entre modelos diferentes. Resolver em **11/09** rodando +2 classificadores sob
  a mesma validação. *(19/08)*
- **Nenhum objetivo específico prevê a camada de assinaturas**, mas ela produz o resultado
  central. Falar com o Paulo antes da versão final.
- **Uso de IA no trabalho:** descobrir a regra da Unimar e declarar o que for exigido.
  Pergunta para o Paulo. *(19/08)*

Detalhamento das pendências herdadas da entrega parcial: `estrutura-do-artigo.md` §1b.

---

## 4. Correções de texto pendentes na entrega parcial

`algoritimo` → algoritmo · `traffics analysis` → traffic analysis · ``system`s`` → system's
