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

---

## 3. Pendências que viram parágrafo de limitações

- **Zero-day.** Palavra ausente do vocabulário do treino é ignorada pelo TF-IDF. Isso limita
  o que o modelo pode prometer sobre ataque nunca visto. A seção 1.2 da entrega parcial
  promete zero-day; ou suaviza, ou declara aqui. *(19/08)*
- **Acurácia** entra na versão final como **contraexemplo**, não como métrica de resultado.
- **Cortes de escopo declarados:** Etapa 11 em versão mínima; `datasets/SQL Injection/` e
  `datasets/XSS/` fora de escopo.

Detalhamento das pendências herdadas da entrega parcial: `estrutura-do-artigo.md` §1b.

---

## 4. Correções de texto pendentes na entrega parcial

`algoritimo` → algoritmo · `traffics analysis` → traffic analysis · ``system`s`` → system's
