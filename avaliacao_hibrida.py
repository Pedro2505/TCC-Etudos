"""
==============================================================================
AVALIACAO DA ARQUITETURA HIBRIDA — ASSINATURAS + MACHINE LEARNING
==============================================================================
Pergunta que este script responde:

    "Somar uma camada de ML a um WAF de assinaturas detecta mais do que
     qualquer uma das duas camadas sozinha, e a que custo de falso positivo?"

Ate aqui o trabalho comparava ML CONTRA assinaturas, como concorrentes. Este
script muda o enquadramento para o que de fato acontece em producao: as duas
camadas somadas, em cascata.

--- O QUE E MEDIDO ---------------------------------------------------------
Quatro configuracoes, no MESMO conjunto e com a MESMA metodologia de validacao
(StratifiedGroupKFold(5) agrupado por payload, probabilidades out-of-fold):

    A) Camada 1 isolada    -> so assinaturas (assinaturas.py)
    B) Camada 2 isolada    -> so o modelo, no limiar calibrado 0,660
    C) Uniao               -> bloqueia se QUALQUER camada disparar
    D) Cascata recalibrada -> camada 1 primeiro; a camada 2 julga o resto, com
                              o limiar reescolhido sob o MESMO orcamento total
                              de falso positivo (<= 1%)

E a matriz de concordancia entre as duas camadas, que e a evidencia direta de
complementaridade: quantos ataques SO a assinatura pega, quantos SO o modelo
pega, quantos ambos pegam e quantos escapam dos dois.

--- POR QUE C E D EXISTEM SEPARADAS ----------------------------------------
Em termos de DECISAO, cascata e uniao sao equivalentes: bloquear se a camada 1
disparar, senao consultar a camada 2, produz exatamente o mesmo conjunto
bloqueado que "camada 1 OU camada 2". Nao ha ganho de recall em ordenar.

O que a cascata muda e outra coisa, e vale a pena declarar com precisao:

  1. PROVENIENCIA. Cada bloqueio sai com a causa: uma regra nomeada ou uma
     probabilidade com laudo SHAP. Um log de auditoria que so diz "403" e
     operacionalmente incompleto.
  2. CUSTO. O que a camada 1 resolve nao paga os ~10ms da camada 2.
  3. ORCAMENTO DE FALSO POSITIVO. Este e o ponto tecnico interessante. A
     camada 1 consome parte do orcamento de FP. Se ela consome pouco, sobra
     margem para BAIXAR o limiar da camada 2 e ganhar recall sem estourar o
     alvo declarado. A configuracao D mede exatamente isso.

--- VIES DECLARADO: A CIRCULARIDADE DA ATRIBUICAO DE FAMILIA ---------------
O CSIC 2010 rotula apenas normal/anomalo. A familia de ataque e atribuida por
mim, com as regexes de `ingestion_csic.FAMILIAS_PAYLOAD`. As regras da camada 1
foram escritas de forma independente (ver o docstring de assinaturas.py), mas
descrevem os mesmos fenomenos e portanto se sobrepoem.

    => O recall da camada 1 medido POR FAMILIA e OTIMISTA por construcao.
       Uma familia definida por "casa com regex de SQLi" tende a ser detectada
       por um detector de assinaturas de SQLi.

Os numeros IMUNES a esse vies sao os medidos contra o rotulo real do CSIC:
recall sobre o conjunto anomalo inteiro, taxa de falso positivo sobre o
trafego legitimo, e a matriz de concordancia. Sao esses que sustentam a tese.

A linha de 'Tampering sem assinatura' merece uma nota propria. Que a camada 1
tenha recall zero nela e tautologico: a familia e DEFINIDA como "nao casou com
nenhuma assinatura". Mas a tautologia e o proprio argumento -- "ataque sem
assinatura" e "assinaturas nao detectam" sao a mesma afirmacao, e ela vale para
qualquer WAF de regras, nao so para o meu. O que NAO e tautologico, e e o
resultado deste trabalho, e quanto desses ataques a camada 2 detecta.

Rodar:  python avaliacao_hibrida.py
Saida:  docs/medicoes/avaliacao_hibrida.md
==============================================================================
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score

import assinaturas
from model_trainer import (ALVO_FALSO_POSITIVO, N_FOLDS, carregar_dados_csic,
                           preparar_colunas_auxiliares, validar)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / 'docs' / 'medicoes' / 'avaliacao_hibrida.md'


def metricas(y, pred) -> dict:
    """Painel de metricas de um detector. n_fp e a grandeza operacional do WAF."""
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        'precisao': tp / (tp + fp) if (tp + fp) else 0.0,
        'recall': tp / (tp + fn) if (tp + fn) else 0.0,
        'f1': f1_score(y, pred, zero_division=0),
        'taxa_fp': fp / (fp + tn) if (fp + tn) else 0.0,
        'fp': int(fp), 'fn': int(fn), 'tp': int(tp), 'tn': int(tn),
    }


def recalibrar_camada2(y: np.ndarray, prob_oof: np.ndarray, disparou: np.ndarray,
                       alvo_fp: float) -> tuple:
    """
    Escolhe o limiar da camada 2 sob o orcamento de falso positivo TOTAL.

    A diferenca em relacao a `model_trainer.escolher_limiar` e o que entra na
    conta do falso positivo: aqui, uma requisicao legitima ja bloqueada pela
    camada 1 conta como FP do sistema INDEPENDENTEMENTE do limiar. O orcamento
    disponivel para a camada 2 e o que sobra depois disso.

    Criterio mantido identico ao do model_trainer, para que os dois numeros
    sejam comparaveis: entre os limiares que respeitam o alvo, o de maior F1.
    """
    n_legitimas = int((y == 0).sum())
    fp_camada1 = int(((y == 0) & disparou).sum())

    linhas = []
    for limiar in np.unique(np.round(prob_oof, 3)):
        # Cascata: bloqueado = disparou na camada 1 OU passou do limiar na 2.
        pred = (disparou | (prob_oof >= limiar)).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        linhas.append({
            'limiar': float(limiar),
            'taxa_fp': fp / n_legitimas,
            'recall': tp / (tp + fn) if (tp + fn) else 0.0,
            'precisao': tp / (tp + fp) if (tp + fp) else 0.0,
            'f1': f1_score(y, pred, zero_division=0),
            'fp': int(fp), 'fn': int(fn),
        })
    curva = pd.DataFrame(linhas)

    dentro = curva[curva['taxa_fp'] <= alvo_fp]
    if dentro.empty:
        # A camada 1 sozinha ja estourou o orcamento: nenhum limiar salva.
        # Isso e informacao, nao erro -- significaria que as assinaturas sao
        # agressivas demais para o alvo declarado.
        melhor = curva.loc[curva['f1'].idxmax()]
        print(f"      ATENCAO: a camada 1 sozinha ja gera {fp_camada1} FP "
              f"({fp_camada1 / n_legitimas:.2%}), acima do alvo de {alvo_fp:.1%}.")
    else:
        melhor = dentro.loc[dentro['f1'].idxmax()]

    return float(melhor['limiar']), curva, fp_camada1


def matriz_concordancia(y: np.ndarray, disparou: np.ndarray, detectou_ml: np.ndarray) -> dict:
    """
    A tabela 2x2 que e a evidencia direta de complementaridade.

    Calculada sobre os ATAQUES (y == 1): de todo ataque real, qual camada o
    pegou? Se as duas camadas errassem nas mesmas requisicoes, 'so assinatura'
    e 'so modelo' seriam ~zero e somar as camadas nao valeria nada.
    """
    ataque = y == 1
    a, m = disparou[ataque], detectou_ml[ataque]
    return {
        'n_ataques': int(ataque.sum()),
        'ambos': int((a & m).sum()),
        'so_assinatura': int((a & ~m).sum()),
        'so_modelo': int((~a & m).sum()),
        'nenhum': int((~a & ~m).sum()),
    }


def tabela_por_familia(df: pd.DataFrame, disparou: np.ndarray,
                       detectou_ml: np.ndarray) -> pd.DataFrame:
    """Recall de cada camada e do sistema combinado, por familia de ataque."""
    ataques = df[df['Label'] == 1].copy()
    ataques['camada1'] = disparou[df['Label'].to_numpy() == 1]
    ataques['camada2'] = detectou_ml[df['Label'].to_numpy() == 1]
    ataques['combinado'] = ataques['camada1'] | ataques['camada2']

    linhas = []
    for familia, grupo in ataques.groupby('familia_ataque'):
        linhas.append({
            'familia': familia,
            'n': len(grupo),
            'recall_camada1': float(grupo['camada1'].mean()),
            'recall_camada2': float(grupo['camada2'].mean()),
            'recall_combinado': float(grupo['combinado'].mean()),
            'ganho_camada2': float(grupo['combinado'].mean() - grupo['camada1'].mean()),
        })
    tabela = pd.DataFrame(linhas).sort_values('n', ascending=False)

    # Agregado SQLi + XSS: o escopo declarado do TCC.
    alvo = ataques[ataques['familia_ataque'].isin(['SQLi', 'XSS'])]
    agregado = {
        'familia': 'SQLi + XSS (escopo do TCC)',
        'n': len(alvo),
        'recall_camada1': float(alvo['camada1'].mean()),
        'recall_camada2': float(alvo['camada2'].mean()),
        'recall_combinado': float(alvo['combinado'].mean()),
        'ganho_camada2': float(alvo['combinado'].mean() - alvo['camada1'].mean()),
    }
    return tabela, agregado


# =============================================================================
def main() -> None:
    print(__doc__)

    # --- 1. Dados e features -------------------------------------------------
    df = carregar_dados_csic()
    df = preparar_colunas_auxiliares(df)
    y = df['Label'].to_numpy()
    n_legitimas, n_ataques = int((y == 0).sum()), int((y == 1).sum())

    # --- 2. Camada 1: assinaturas -------------------------------------------
    print(f"\n[1/4] Camada 1 — avaliando {len(assinaturas.REGRAS)} assinaturas...")
    resultado_assinaturas = assinaturas.avaliar_serie(df['Sentence'])
    disparou = resultado_assinaturas['disparou'].to_numpy()
    print(f"      disparou em {disparou.sum()} das {len(df)} requisicoes")

    # --- 3. Camada 2: modelo, com a mesma validacao da monografia ------------
    print(f"\n[2/4] Camada 2 — validacao cruzada StratifiedGroupKFold({N_FOLDS})...")
    print("      (mesma metodologia do model_trainer.py: TF-IDF ajustado por fold,")
    print("       agrupamento por payload, probabilidades out-of-fold)")
    _, prob_oof = validar(df, usar_heuristicas=True, usar_tfidf=True, usar_contexto=True)

    caminho_meta = RAIZ / 'models' / 'model_metadata.json'
    with open(caminho_meta, encoding='utf-8') as f:
        limiar_monografia = json.load(f)['limiar_decisao']
    print(f"\n      Limiar calibrado da monografia: {limiar_monografia:.3f}")

    detectou_ml = prob_oof >= limiar_monografia

    # --- 4. As quatro configuracoes -----------------------------------------
    print(f"\n[3/4] Comparando as quatro configuracoes...")

    limiar_cascata, curva_cascata, fp_camada1 = recalibrar_camada2(
        y, prob_oof, disparou, ALVO_FALSO_POSITIVO)
    print(f"      Limiar da camada 2 recalibrado sob orcamento total: "
          f"{limiar_cascata:.3f} (era {limiar_monografia:.3f})")
    print(f"      Falso positivo consumido pela camada 1: {fp_camada1} "
          f"({fp_camada1 / n_legitimas:.2%} do trafego legitimo)")

    configs = {
        'A) Camada 1 isolada (assinaturas)': disparou.astype(int),
        f'B) Camada 2 isolada (modelo, limiar {limiar_monografia:.3f})':
            detectou_ml.astype(int),
        f'C) Uniao (limiar {limiar_monografia:.3f})': (disparou | detectou_ml).astype(int),
        f'D) Cascata recalibrada (limiar {limiar_cascata:.3f})':
            (disparou | (prob_oof >= limiar_cascata)).astype(int),
    }
    resultados = {nome: metricas(y, pred) for nome, pred in configs.items()}

    # --- 5. Complementaridade ------------------------------------------------
    conc = matriz_concordancia(y, disparou, detectou_ml)
    fam, agregado = tabela_por_familia(df, disparou, detectou_ml)

    # --- 6. Saida ------------------------------------------------------------
    print(f"\n{'=' * 84}\nDESEMPENHO DAS QUATRO CONFIGURACOES\n{'=' * 84}")
    print(f"{'Configuracao':<46}{'Precisao':>10}{'Recall':>9}{'F1':>9}{'Taxa FP':>10}")
    print('-' * 84)
    for nome, m in resultados.items():
        print(f"{nome:<46}{m['precisao']:>9.2%}{m['recall']:>9.2%}"
              f"{m['f1']:>9.4f}{m['taxa_fp']:>10.2%}")

    print(f"\n{'=' * 84}\nMATRIZ DE CONCORDANCIA — sobre os {conc['n_ataques']} ataques"
          f"\n{'=' * 84}")
    print(f"  Detectados pelas DUAS camadas      {conc['ambos']:>7} "
          f"({conc['ambos'] / conc['n_ataques']:>6.1%})")
    print(f"  SO pela assinatura                 {conc['so_assinatura']:>7} "
          f"({conc['so_assinatura'] / conc['n_ataques']:>6.1%})")
    print(f"  SO pelo modelo                     {conc['so_modelo']:>7} "
          f"({conc['so_modelo'] / conc['n_ataques']:>6.1%})")
    print(f"  Por nenhuma das duas               {conc['nenhum']:>7} "
          f"({conc['nenhum'] / conc['n_ataques']:>6.1%})")

    print(f"\n{'=' * 84}\nRECALL POR FAMILIA — cada camada e o sistema combinado\n{'=' * 84}")
    print(f"{'Familia':<32}{'n':>7}{'camada 1':>11}{'camada 2':>11}"
          f"{'combinado':>12}{'ganho C2':>10}")
    print('-' * 84)
    for _, r in fam.iterrows():
        print(f"{r['familia']:<32}{r['n']:>7}{r['recall_camada1']:>11.1%}"
              f"{r['recall_camada2']:>11.1%}{r['recall_combinado']:>12.1%}"
              f"{r['ganho_camada2']:>+10.1f}pp".replace('pp', ' pp'))
    print('-' * 84)
    print(f"{agregado['familia']:<32}{agregado['n']:>7}"
          f"{agregado['recall_camada1']:>11.1%}{agregado['recall_camada2']:>11.1%}"
          f"{agregado['recall_combinado']:>12.1%}"
          f"{agregado['ganho_camada2'] * 100:>+9.1f} pp")

    escrever_relatorio(df, resultados, conc, fam, agregado, limiar_monografia,
                       limiar_cascata, fp_camada1, n_legitimas, n_ataques,
                       resultado_assinaturas)
    curva_cascata.to_csv(RAIZ / 'docs' / 'medicoes' / 'curva_limiar_cascata.csv',
                         index=False)
    print(f"\n[4/4] Relatorio: {DESTINO.relative_to(RAIZ)}")
    print(f"      Curva:      docs/medicoes/curva_limiar_cascata.csv")


def escrever_relatorio(df, resultados, conc, fam, agregado, limiar_mono, limiar_casc,
                       fp_camada1, n_legitimas, n_ataques, resultado_assinaturas) -> None:
    """Exporta em Markdown, para ser citado direto na monografia."""
    L = []
    A = L.append
    A('# Avaliação da arquitetura híbrida — assinaturas + Machine Learning\n')
    A('Gerado por `avaliacao_hibrida.py`. **Não editar à mão.**\n')
    A(f'HTTP DATASET CSIC 2010 em escopo: {len(df)} requisições '
      f'({n_legitimas} legítimas / {n_ataques} anômalas). '
      f'Validação `StratifiedGroupKFold({N_FOLDS})` agrupada por payload, '
      f'TF-IDF ajustado dentro de cada fold, probabilidades *out-of-fold*.\n')
    A(f'Camada 1: {len(assinaturas.REGRAS)} assinaturas '
      f'(`assinaturas.py`), inspecionando a mesma superfície do modelo.\n')

    A('\n## 1. As quatro configurações\n')
    A('| Configuração | Precisão | Recall | F1 | Taxa de FP | FP | FN |')
    A('| :--- | ---: | ---: | ---: | ---: | ---: | ---: |')
    for nome, m in resultados.items():
        A(f"| {nome} | {m['precisao']:.2%} | {m['recall']:.2%} | {m['f1']:.4f} | "
          f"{m['taxa_fp']:.2%} | {m['fp']} | {m['fn']} |")

    A('\n> **Cascata e união são equivalentes em decisão.** Bloquear na camada 1 e '
      'consultar a camada 2 só para o que passou produz o mesmo conjunto bloqueado que '
      '"camada 1 OU camada 2". A cascata não existe para ganhar recall: ela existe pela '
      'proveniência do bloqueio, pelo custo evitado e pelo orçamento de falso positivo '
      '— que é o que a configuração D explora.\n')

    A('\n## 2. Complementaridade dos detectores\n')
    A(f'Sobre os **{conc["n_ataques"]} ataques** do conjunto:\n')
    A('| Detectado por | n | % dos ataques |')
    A('| :--- | ---: | ---: |')
    for rotulo, chave in [('Ambas as camadas', 'ambos'),
                          ('**Somente a assinatura**', 'so_assinatura'),
                          ('**Somente o modelo**', 'so_modelo'),
                          ('Nenhuma das duas', 'nenhum')]:
        A(f'| {rotulo} | {conc[chave]} | {conc[chave] / conc["n_ataques"]:.1%} |')
    A(f'\nSomar duas camadas só compensa quando elas erram em requisições diferentes. '
      f'As células "somente" quantificam exatamente isso: **{conc["so_modelo"]} ataques '
      f'({conc["so_modelo"] / conc["n_ataques"]:.1%}) seriam perdidos por um WAF de '
      f'assinaturas operando sozinho**, e {conc["so_assinatura"]} '
      f'({conc["so_assinatura"] / conc["n_ataques"]:.1%}) seriam perdidos pelo modelo '
      f'operando sozinho.\n')

    A('\n## 3. Recall por família — onde cada camada contribui\n')
    A('| Família | n | Camada 1 (assinaturas) | Camada 2 (modelo) | Combinado | Ganho da camada 2 |')
    A('| :--- | ---: | ---: | ---: | ---: | ---: |')
    for _, r in fam.iterrows():
        A(f"| {r['familia']} | {r['n']} | {r['recall_camada1']:.1%} | "
          f"{r['recall_camada2']:.1%} | {r['recall_combinado']:.1%} | "
          f"{r['ganho_camada2'] * 100:+.1f} pp |")
    A(f"| **{agregado['familia']}** | **{agregado['n']}** | "
      f"**{agregado['recall_camada1']:.1%}** | **{agregado['recall_camada2']:.1%}** | "
      f"**{agregado['recall_combinado']:.1%}** | "
      f"**{agregado['ganho_camada2'] * 100:+.1f} pp** |")

    A('\n### Viés declarado nesta tabela\n')
    A('O CSIC 2010 rotula apenas normal/anômalo. A **família é atribuída por regex** '
      '(`ingestion_csic.classificar_familia_ataque`). As regras da camada 1 foram '
      'escritas de forma independente, mas descrevem os mesmos fenômenos, então há '
      'sobreposição inevitável.\n')
    A('**Consequência:** o recall da camada 1 por família é **otimista por construção** '
      '— uma família definida como "casa com regex de SQLi" tende a ser detectada por um '
      'detector de assinaturas de SQLi. Os números imunes a esse viés são os da Seção 1 '
      'e da Seção 2, medidos contra o rótulo real do dataset.\n')
    A('A linha de *tampering sem assinatura* é o caso extremo: a camada 1 tem recall zero '
      'nela **por tautologia**, já que a família é definida como "não casou com nenhuma '
      'assinatura". Mas a tautologia é o próprio argumento — "ataque sem assinatura" e '
      '"assinaturas não detectam" são a mesma afirmação, e ela vale para qualquer WAF de '
      'regras. O que não é tautológico é quanto desses ataques a camada 2 detecta.\n')

    A('\n## 4. Orçamento de falso positivo\n')
    A(f'| | |')
    A(f'| :--- | ---: |')
    A(f'| Alvo declarado de falso positivo | ≤ {ALVO_FALSO_POSITIVO:.1%} |')
    A(f'| FP consumido pela camada 1 | {fp_camada1} ({fp_camada1 / n_legitimas:.2%}) |')
    A(f'| Limiar da camada 2 na monografia | {limiar_mono:.3f} |')
    A(f'| Limiar da camada 2 recalibrado na cascata | {limiar_casc:.3f} |')
    A('\nA camada 2 não precisa mais cobrir sozinha todo o recall: parte dele vem da '
      'camada 1, a um custo de falso positivo que esta tabela mede. O limiar recalibrado '
      'é a consequência direta disso — é o mesmo critério de calibração do '
      '`model_trainer.py` (maior F1 dentro do orçamento), aplicado ao sistema completo em '
      'vez de ao modelo isolado. Curva completa em `curva_limiar_cascata.csv`.\n')

    A('\n## 5. Regras que mais dispararam\n')
    disparos = resultado_assinaturas[resultado_assinaturas['disparou']]
    contagem = disparos.groupby(['regra_id', 'regra_nome']).size().sort_values(ascending=False)
    A('| Regra | Nome | Disparos |')
    A('| :--- | :--- | ---: |')
    for (rid, rnome), n in contagem.head(12).items():
        A(f'| `{rid}` | {rnome} | {n} |')

    A('\n## 6. Limitações desta medição\n')
    A('1. **A camada 1 não é o OWASP CRS.** São ~25 regras inspiradas nas famílias de '
      'detecção do CRS. Um CRS real tem centenas de regras e pontuação de anomalia. A '
      'comparação com o CRS de verdade continua sendo trabalho futuro declarado.')
    A('2. **A camada 1 inspeciona a mesma superfície que o modelo** (valores de parâmetro '
      'decodificados). Um ModSecurity real também veria path, headers, cookies e corpo. '
      'Logo esta camada 1 é *mais fraca* que um WAF real, e o ganho medido para a camada 2 '
      'é uma estimativa **conservadora**.')
    A('3. **Sem regra de impressão digital de scanner.** O CSIC foi gerado com o Paros '
      'Proxy e 748 ataques carregam a string `Paros` no payload. Uma regra assim teria '
      'recall inflado por artefato do dataset; foi deliberadamente excluída.')
    A('4. **A atribuição de família é heurística**, validada manualmente em 40 amostras '
      '(ver `validacao_familias.md`), não *ground truth*.')

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
