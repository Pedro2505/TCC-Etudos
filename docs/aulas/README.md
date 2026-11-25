# docs/aulas — material de orientação

Índice de tudo que foi discutido nas sessões. **Nada fica só no terminal** — o histórico é
cortado, os arquivos não.

Isto é material de **orientação e estudo**. A monografia/artigo e os relatórios que o Pedro
escreve vão em `docs/`, um nível acima.

---

## Arquivos

| Arquivo | O que tem |
| :--- | :--- |
| [`etapa-00-fundamentos-parte-1.md`](Etapa%2000/etapa-00-fundamentos-parte-1.md) | Como se mede um detector: matriz de confusão, precisão/recall/FPR, F1, por que acurácia engana. **+ enunciado da Tarefa 0.** |
| [`etapa-00-fundamentos-parte-2.md`](Etapa%2000/etapa-00-fundamentos-parte-2.md) | Random Forest: árvore → floresta → voto, as duas aleatoriedades, `predict_proba` como placar de votação, e por que 0,5 é default e não escolha. |
| [`etapa-00-explicacao-do-porteiro.md`](Etapa%2000/etapa-00-explicacao-do-porteiro.md) | **A mesma coisa sem fórmula.** A analogia do porteiro da loja: os dois tipos de erro, quem sofre com cada um, e por que a acurácia engana. **Se a matemática confundir, começar por aqui.** |
| [`etapa-00-fundamentos-parte-2-bloco-2.md`](Etapa%2000/etapa-00-fundamentos-parte-2-bloco-2.md) | **Validação cruzada K-Fold e vazamento de dados.** Por que uma divisão só mede sorte, média ± desvio, previsões out-of-fold, e as **três formas de vazamento** deste projeto (TF-IDF fora do fold, par GET/POST, limiar medido no próprio teste). Fecha a Etapa 0. |
| [`videos-em-portugues.md`](videos-em-portugues.md) | Vídeos de apoio em português por tema (métricas, Random Forest, validação cruzada), com as três regras de como assistir. Nenhum verificado. |
| [`arquivo/cronograma-ate-outubro.md`](arquivo/cronograma-ate-outubro.md) | **Arquivado (prazo vencido).** As 24 sessões (quintas e sextas) até 31/10, os cortes de escopo decididos, e o que cabe em novembro. |
| [`estrutura-do-artigo.md`](estrutura-do-artigo.md) | Estrutura do artigo ABNT, orçamento de páginas, inventário das 12 tabelas/figuras, e a seção de trabalhos relacionados. |
| [`como-usar-o-sistema.md`](como-usar-o-sistema.md) | Guia de uso do sistema e do painel. |
| [`roteiro-video.md`](roteiro-video.md) | Roteiro do vídeo de demonstração para o orientador. |
| [`texto-sistema-respostas.md`](texto-sistema-respostas.md) | Texto enviado ao Paulo em 12/11: o sistema explicado com as palavras do Pedro, por pergunta. |

O kit para escrever o artigo longe do PC está em [`../artigo/README.md`](../artigo/README.md).

---

## Decisões já tomadas (não reabrir sem motivo)

| Decisão | Data |
| :--- | :--- |
| **Enquadramento: a camada de ML é acrescentada ao WAF de assinaturas, não o substitui.** O resultado do trabalho é o **delta** (detecção ganha × FP introduzido), não o F1 do modelo. Ver `estrutura-do-artigo.md` §0 | 2026-08-13 |
| Formato: **artigo** ABNT NBR 6022, mínimo 20 páginas | 2026-08-13 |
| Entrega **outubro/2026** · defesa **novembro/2026** | 2026-08-13 |
| Regime: **quintas e sextas**, ~24 sessões | 2026-08-13 |
| Etapa 11 (SHAP) em versão mínima; sai se apertar | 2026-08-13 |
| Etapa 9 (middleware) funcional e medido, sem otimização | 2026-08-13 |
| `datasets/SQL Injection/` e `datasets/XSS/` **fora de escopo** neste prazo | 2026-08-13 |
| Etapas 2, 3, 5, 7 e 10 são **intocáveis** | 2026-08-13 |

## As duas regras de sessão

1. **Toda sessão fecha com uma tabela ou figura do artigo produzida** — e o parágrafo que a
   analisa, escrito na mesma sessão.
2. **Toda sessão vira uma entrada no `diario.md`.** Inclusive as ruins. Principalmente as
   ruins.

## Pendências abertas

- [ ] Data exata da entrega em outubro (o plano assume ~31/10)
- [ ] As 20 páginas incluem referências e pré-textuais?
---

## Estado atual

**ETAPA 0 ENCERRADA em 2026-08-19.** Parte 1 (métricas), parte 2 bloco 1 (Random Forest) e
parte 2 bloco 2 (validação cruzada e vazamento). O critério de fechamento — dar três
exemplos diferentes de vazamento, de cabeça — foi cumprido.

**Próximo — Etapa 1 (sessão de 20/08):** ingestão do CSIC 2010. Fecha com a **Tabela 1** do
artigo (composição por partição) e o parágrafo que a analisa.

O ponto de retomada completo está em [`../../CONTINUAR.md`](../../CONTINUAR.md).
