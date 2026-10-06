"""
==============================================================================
TREINO E VALIDACAO DO MODELO DO WAF
==============================================================================
Este script faz quatro coisas, nesta ordem:

    1. Carrega o dataset e transforma texto em numeros.
    2. Mede o desempenho de forma honesta, com StratifiedGroupKFold.
    3. Escolhe o limiar de decisao (o corte entre "libera" e "bloqueia").
    4. Treina o modelo final e salva no disco.

Rodar:  python model_trainer.py

------------------------------------------------------------------------------
O QUE MUDOU EM RELACAO A VERSAO ANTERIOR, E POR QUE
------------------------------------------------------------------------------
A versao antiga fazia um `train_test_split` simples e reportava um numero unico.
Tres problemas, todos corrigidos aqui:

(a) VAZAMENTO DE IDF. O TF-IDF era ajustado (`fit`) sobre o dataset TODO, antes de
    separar treino e teste. O TF-IDF calcula "em quantos documentos cada n-grama
    aparece", entao ajustar antes do split faz essa estatistica incluir informacao
    do teste. O modelo entra na prova sabendo algo sobre a prova.
    -> Aqui o TF-IDF e ajustado SO no treino de cada fold.

(b) VAZAMENTO DE PAYLOAD. O CSIC 2010 manda cada requisicao duas vezes: uma como
    GET (parametros na URL) e outra como POST (mesmos parametros no corpo). Um
    split aleatorio joga a versao GET no treino e a POST no teste. O modelo le o
    payload, que e identico nas duas -> ele reencontra no teste o que estudou.
    -> Aqui uso StratifiedGroupKFold agrupando por payload (ver secao 2).

(c) UM NUMERO SO. Uma divisao unica com `random_state=42` produz um numero que
    depende do sorteio. Se der 0,72 nao sei se o modelo e bom ou se eu tive sorte.
    -> Aqui uso 5 folds e reporto media +- desvio padrao.
==============================================================================
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (confusion_matrix, f1_score, precision_recall_curve,
                            precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).resolve().parent
PASTA_MODELOS = RAIZ / 'models'
CSIC_PROCESSADO = RAIZ / 'datasets' / 'CSIC2010' / 'csic2010_processado.csv.gz'

N_FOLDS = 5
SEMENTE = 42
N_ARVORES = 100

# Alvo de falso positivo para a calibracao do limiar (secao 3).
# 0,01 = aceito bloquear no maximo 1% do trafego legitimo.
ALVO_FALSO_POSITIVO = 0.01


# =============================================================================
# 1. CARREGAR OS DADOS
# =============================================================================

def carregar_dados_csic() -> pd.DataFrame:
    """
    Carrega o CSIC 2010 processado. Esta e a fonte principal, usada para as metricas
    que vao para a monografia.

    Prefere o .csv.gz que ja esta versionado no repositorio. Se ele nao existir,
    reprocessa a partir dos .txt brutos (que exigem download separado).

    keep_default_na=False e importante: sem isso o pandas transforma payloads
    vazios e strings como 'null' ou 'NA' em NaN, e a coluna de texto quebra.
    """
    if CSIC_PROCESSADO.exists():
        print(f"[1/4] Carregando {CSIC_PROCESSADO.name}...")
        df = pd.read_csv(CSIC_PROCESSADO, keep_default_na=False)
        # O CSV nao sobrevive a um \x00: o pandas TRUNCA a string nele na releitura.
        # A ingestao grava o byte nulo como U+E000; aqui ele volta ao original, para
        # que o treino veja o mesmo payload que o middleware ve em producao.
        from ingestion_csic import restaurar_nulo
        df = restaurar_nulo(df)
    else:
        print("[1/4] Arquivo processado nao encontrado; reprocessando os brutos...")
        from ingestion_csic import carregar_supervisionado
        df = carregar_supervisionado()

    df['Sentence'] = df['Sentence'].astype(str)
    print(f"      {len(df)} requisicoes | "
          f"legitimas: {(df['Label'] == 0).sum()} | anomalas: {(df['Label'] == 1).sum()}")
    return df


def carregar_dados_demo() -> pd.DataFrame:
    """
    Carrega os datasets de payload SQLi/XSS, para treinar o MODELO DE DEMONSTRACAO.

    Por que existe um segundo modelo:

    Um WAF baseado em ML aprende o comportamento normal de UMA aplicacao. O modelo
    treinado no CSIC aprendeu o trafego da loja "tienda1" -- espanhol, parametros
    como `precio` e `cantidad`, valores num dominio especifico. Medi que ele bloqueia
    'tenis de corrida masculino' com p=0,90, porque portugues esta fora da
    distribuicao que ele viu.

    Isso NAO e um defeito do modelo, e uma propriedade da abordagem, e e justamente
    por isso que o CSIC distribui um conjunto de treino por aplicacao. Mas cria um
    problema pratico: a minha aplicacao-alvo de demonstracao e em portugues.

    Solucao: dois modelos com papeis distintos.
      models/         -> treinado no CSIC. E o artefato cientifico, de onde saem as
                         metricas da monografia.
      models/demo/    -> treinado nos datasets de payload, que incluem trafego
                         benigno em portugues. Serve para a demonstracao ao vivo.

    Na defesa eu declaro explicitamente qual modelo esta rodando e por que.
    """
    print("[1/4] Carregando datasets de payload SQLi/XSS (modelo de demonstracao)...")
    from ingestion import unificar_datasets

    df = unificar_datasets()
    df = df.sample(min(20000, len(df)), random_state=SEMENTE).reset_index(drop=True)
    df['Sentence'] = df['Sentence'].astype(str)

    # Estes datasets nao tem contexto HTTP (sao payloads soltos, sem requisicao).
    # Preencho com os mesmos valores que extractor.CONTEXTO_PADRAO usa na inferencia,
    # para que treino e inferencia vejam a mesma coisa. Como sao constantes, essas
    # colunas nao carregam informacao aqui -- o modelo de demo se apoia so no texto.
    df['metodo'] = 'GET'
    df['n_parametros'] = 1
    df['tem_corpo'] = 0
    df['content_length'] = 0
    df['n_headers'] = 11

    # Sem estrutura de requisicao, o grupo e o proprio payload normalizado: impede que
    # variantes triviais do mesmo payload caiam em lados opostos do split.
    from ingestion_csic import normalizar_payload
    df['grupo_payload'] = df['Sentence'].map(normalizar_payload)

    print(f"      {len(df)} payloads | "
          f"legitimos: {(df['Label'] == 0).sum()} | ataques: {(df['Label'] == 1).sum()}")
    return df


# =============================================================================
# 2. TRANSFORMAR TEXTO EM NUMEROS (FEATURES)
# =============================================================================
# Um modelo nao le texto, le numeros. Aqui monto a matriz onde cada linha e uma
# requisicao e cada coluna e uma caracteristica medida dela.
#
# Uso tres grupos de features, e o script mede a contribuicao de cada um:
#
#   HEURISTICAS  - contagens que eu programei com conhecimento de seguranca
#                  (quantas aspas, quantas palavras SQL, comprimento...).
#   TF-IDF       - o Scikit-Learn fatia o texto em blocos de 2-3 caracteres e mede
#                  a frequencia relativa de cada bloco. Pega padroes que eu nao
#                  listei manualmente.
#   CONTEXTO     - dados da requisicao HTTP que nao estao no texto do payload:
#                  metodo, quantos parametros, tamanho do corpo, quantos headers.
#                  Este grupo e novo nesta versao.
# =============================================================================

COLS_HEURISTICAS = ['comprimento', 'qtd_caracteres_especiais',
                    'qtd_keywords_sql', 'qtd_keywords_xss', 'qtd_url_encode']
COLS_CONTEXTO = ['n_parametros', 'tem_corpo', 'content_length', 'n_headers',
                 'metodo_GET', 'metodo_POST', 'metodo_PUT']


def preparar_colunas_auxiliares(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula as features heuristicas e transforma o metodo HTTP em colunas 0/1.

    Por que o metodo virou tres colunas? Um modelo nao entende "GET"/"POST" como
    texto. A conversao para colunas binarias (one-hot) evita tambem que ele
    interprete uma codificacao numerica (GET=0, POST=1, PUT=2) como se PUT fosse
    "maior" que GET, o que nao faz sentido.
    """
    from extractor import extrair_features_manuais

    df = extrair_features_manuais(df)
    for metodo in ['GET', 'POST', 'PUT']:
        df[f'metodo_{metodo}'] = (df['metodo'] == metodo).astype(int)
    return df


def montar_matriz(df: pd.DataFrame, idx_treino: np.ndarray, idx_teste: np.ndarray,
                  usar_heuristicas: bool, usar_tfidf: bool, usar_contexto: bool):
    """
    Monta as matrizes de treino e teste para um fold.

    O DETALHE MAIS IMPORTANTE DESTA FUNCAO: o TF-IDF usa `fit_transform` no treino
    e apenas `transform` no teste.

        fit_transform -> aprende o vocabulario e as estatisticas, E transforma
        transform     -> apenas aplica o que ja foi aprendido

    Se eu chamasse `fit_transform` no teste tambem, ele recalcularia as
    estatisticas usando os dados de teste, e isso e vazamento. Esse era o bug (a)
    da versao antiga.

    Devolve: (X_treino, X_teste, nomes_das_colunas, vetorizador_ajustado)
    """
    blocos_treino, blocos_teste, nomes = [], [], []

    if usar_heuristicas:
        blocos_treino.append(csr_matrix(df[COLS_HEURISTICAS].iloc[idx_treino].to_numpy(float)))
        blocos_teste.append(csr_matrix(df[COLS_HEURISTICAS].iloc[idx_teste].to_numpy(float)))
        nomes += COLS_HEURISTICAS

    if usar_contexto:
        blocos_treino.append(csr_matrix(df[COLS_CONTEXTO].iloc[idx_treino].to_numpy(float)))
        blocos_teste.append(csr_matrix(df[COLS_CONTEXTO].iloc[idx_teste].to_numpy(float)))
        nomes += COLS_CONTEXTO

    vetorizador = None
    if usar_tfidf:
        vetorizador = TfidfVectorizer(max_features=50, analyzer='char_wb',
                                      ngram_range=(2, 3))
        blocos_treino.append(vetorizador.fit_transform(df['Sentence'].iloc[idx_treino]))
        blocos_teste.append(vetorizador.transform(df['Sentence'].iloc[idx_teste]))
        nomes += [f'tfidf_{c}' for c in vetorizador.get_feature_names_out()]

    return hstack(blocos_treino), hstack(blocos_teste), nomes, vetorizador


# =============================================================================
# 3. MEDIR O DESEMPENHO DE FORMA HONESTA
# =============================================================================
# StratifiedGroupKFold combina duas ideias:
#
#   K-Fold      -> divide os dados em 5 partes. Treina em 4, testa em 1, e repete
#                  5 vezes trocando qual parte e o teste. Assim toda requisicao e
#                  testada exatamente uma vez, e eu tenho 5 medidas em vez de 1.
#
#   Stratified  -> garante que cada parte tenha a mesma proporcao de ataques que o
#                  dataset completo. Sem isso, um fold poderia ficar com poucos
#                  ataques e a metrica dele nao significaria nada.
#
#   Group       -> garante que requisicoes do mesmo grupo nunca fiquem em partes
#                  diferentes. E isso que impede o vazamento (b): as versoes GET e
#                  POST do mesmo payload sempre caem juntas.
#
# O sklearn tenta satisfazer Stratified e Group ao mesmo tempo. Nem sempre da
# perfeito (grupos grandes forcam desbalanceamento), e por isso o script reporta
# a proporcao de ataques em cada fold, para eu conferir.
# =============================================================================

def validar(df: pd.DataFrame, usar_heuristicas=True, usar_tfidf=True,
            usar_contexto=True, verboso=True):
    """
    Executa a validacao cruzada e devolve as metricas por fold e as probabilidades
    out-of-fold.

    "Out-of-fold" (OOF) significa: a probabilidade de cada requisicao, prevista
    pelo modelo do fold em que ela foi TESTE, nunca por um modelo que a viu no
    treino. Junto todas essas previsoes e uso na secao 4 para calibrar o limiar,
    de forma que a calibracao nao veja dado de treino.
    """
    y = df['Label'].to_numpy()
    grupos = df['grupo_payload'].to_numpy()

    cv = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEMENTE)

    prob_oof = np.zeros(len(df))       # probabilidade prevista para cada requisicao
    metricas_por_fold = []

    for n_fold, (idx_tr, idx_te) in enumerate(cv.split(df, y, groups=grupos), start=1):
        X_tr, X_te, _, _ = montar_matriz(df, idx_tr, idx_te,
                                         usar_heuristicas, usar_tfidf, usar_contexto)

        modelo = RandomForestClassifier(n_estimators=N_ARVORES, random_state=SEMENTE,
                                        n_jobs=-1)
        modelo.fit(X_tr, y[idx_tr])

        prob = modelo.predict_proba(X_te)[:, 1]
        prob_oof[idx_te] = prob
        pred = (prob >= 0.5).astype(int)     # limiar padrao; calibrado na secao 4

        tn, fp, fn, tp = confusion_matrix(y[idx_te], pred, labels=[0, 1]).ravel()
        metricas_por_fold.append({
            'fold': n_fold,
            'n_teste': len(idx_te),
            'pct_ataques': y[idx_te].mean(),
            'precisao': precision_score(y[idx_te], pred, zero_division=0),
            'recall': recall_score(y[idx_te], pred, zero_division=0),
            'f1': f1_score(y[idx_te], pred, zero_division=0),
            'roc_auc': roc_auc_score(y[idx_te], prob),
            'fp': int(fp), 'fn': int(fn),
            'taxa_fp': fp / (fp + tn) if (fp + tn) else 0.0,
        })

        if verboso:
            m = metricas_por_fold[-1]
            print(f"      fold {n_fold}/{N_FOLDS}: "
                  f"F1={m['f1']:.4f}  precisao={m['precisao']:.4f}  "
                  f"recall={m['recall']:.4f}  FP={m['fp']:4}  "
                  f"taxa_FP={m['taxa_fp']:6.2%}  ({m['pct_ataques']:.1%} de ataques no fold)")

    return pd.DataFrame(metricas_por_fold), prob_oof


def resumir(nome: str, tabela: pd.DataFrame) -> dict:
    """Imprime media +- desvio padrao das metricas e devolve o resumo."""
    resumo = {}
    print(f"\n      RESUMO — {nome}")
    for metrica, rotulo in [('f1', 'F1'), ('precisao', 'Precisao'),
                            ('recall', 'Recall'), ('roc_auc', 'ROC-AUC'),
                            ('taxa_fp', 'Taxa de FP')]:
        media, desvio = tabela[metrica].mean(), tabela[metrica].std()
        resumo[metrica] = {'media': float(media), 'desvio': float(desvio)}
        if metrica == 'taxa_fp':
            print(f"        {rotulo:12} {media:7.2%} ± {desvio:.2%}")
        else:
            print(f"        {rotulo:12} {media:7.4f} ± {desvio:.4f}")
    print(f"        {'FP total':12} {int(tabela['fp'].sum()):7} "
          f"| FN total: {int(tabela['fn'].sum())}")
    return resumo


# =============================================================================
# 4. ESCOLHER O LIMIAR DE DECISAO
# =============================================================================
# O `.predict()` do sklearn decide "ataque" quando a probabilidade passa de 0,5.
# Esse 0,5 e so o padrao da biblioteca, nao uma escolha justificada.
#
# Num WAF os dois erros custam coisas diferentes: deixar passar um ataque e ruim,
# mas bloquear um cliente legitimo tambem e. Subir o limiar (ex: 0,8) deixa o WAF
# mais permissivo -> menos falso positivo, mais ataque passando. Descer faz o
# oposto. Entao o limiar e uma decisao de negocio, e eu preciso escolhe-lo
# explicitamente em vez de aceitar o padrao.
#
# Aqui eu escolho o menor limiar que mantem a taxa de falso positivo dentro do
# alvo (ALVO_FALSO_POSITIVO), usando as probabilidades out-of-fold.
# =============================================================================

def escolher_limiar(y: np.ndarray, prob_oof: np.ndarray, alvo_fp: float):
    """
    Encontra o melhor limiar que respeita o alvo de falso positivo.

    Criterio: entre os limiares com taxa de FP <= alvo, escolhe o de maior F1.

    Por que F1 e nao "maior recall": maximizar recall sob a restricao empurra a
    escolha sempre para o limite do orcamento de falso positivo, mesmo quando o
    ganho de recall e irrelevante. Medi isso no modelo de demonstracao: o limiar
    0,170 dava recall de 99,77% com 0,97% de FP, enquanto 0,500 dava 99,63% de
    recall com 0,25% de FP -- eu estaria gastando 4x mais falso positivo para
    ganhar 0,14 ponto de recall. Escolher por F1 dentro do orcamento evita esse
    desperdicio, porque o F1 penaliza a perda de precisao.
    """
    n_legitimas = int((y == 0).sum())
    candidatos = np.unique(np.round(prob_oof, 3))

    linhas = []
    for limiar in candidatos:
        pred = (prob_oof >= limiar).astype(int)
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

    dentro_do_alvo = curva[curva['taxa_fp'] <= alvo_fp]
    if dentro_do_alvo.empty:
        # Nenhum limiar atinge o alvo. Isso e informacao, nao erro: significa que
        # o modelo nao consegue operar nesse nivel de falso positivo.
        melhor = curva.loc[curva['f1'].idxmax()]
        print(f"\n      ATENCAO: nenhum limiar atinge FP <= {alvo_fp:.1%}.")
        print(f"      Menor taxa de FP alcancavel: {curva['taxa_fp'].min():.2%}")
        print(f"      Usando o limiar de melhor F1 como alternativa.")
    else:
        melhor = dentro_do_alvo.loc[dentro_do_alvo['f1'].idxmax()]

    print(f"\n      Limiar escolhido: {melhor['limiar']:.3f}")
    print(f"        taxa de FP: {melhor['taxa_fp']:.2%}  (alvo: <= {alvo_fp:.1%})")
    print(f"        recall:     {melhor['recall']:.2%}  "
          f"(pega {melhor['recall']:.1%} dos ataques)")
    print(f"        precisao:   {melhor['precisao']:.2%}")
    print(f"        F1:         {melhor['f1']:.4f}  (maior F1 dentro do orcamento de FP)")

    print(f"\n      Como o limiar afeta o trade-off:")
    print(f"        {'limiar':>8} {'taxa FP':>10} {'recall':>9} {'F1':>8}")
    for lim in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        linha = curva.iloc[(curva['limiar'] - lim).abs().argmin()]
        marca = '  <- escolhido' if abs(linha['limiar'] - melhor['limiar']) < 1e-9 else ''
        print(f"        {linha['limiar']:8.3f} {linha['taxa_fp']:9.2%} "
              f"{linha['recall']:8.2%} {linha['f1']:8.4f}{marca}")

    return float(melhor['limiar']), curva


# =============================================================================
# 5. RECALL POR FAMILIA DE ATAQUE
# =============================================================================
# Por que esta secao e indispensavel no meu TCC:
#
# O tema do trabalho e deteccao de SQLi e XSS. Mas no CSIC 2010, SQLi e XSS somam
# apenas 6,6% das anomalias (468 + 472 de 14.188) -- 89,9% e *parameter tampering*
# sem assinatura. Ou seja, um F1 global calculado sobre o dataset inteiro mede
# principalmente deteccao de tampering, e quase nao informa sobre SQLi/XSS.
#
# Reportar so o numero global seria repetir o erro que me custou os 0,23%: apresentar
# uma metrica que mede uma tarefa diferente da que eu afirmo avaliar. O recall por
# familia e o que responde a pergunta do trabalho.
# =============================================================================

def recall_por_familia(df: pd.DataFrame, prob_oof: np.ndarray, limiar: float) -> pd.DataFrame:
    """
    Calcula recall por familia de ataque usando as probabilidades out-of-fold.

    Recall e a metrica correta aqui: precisao nao e definivel por familia, porque um
    falso positivo e uma requisicao LEGITIMA classificada como ataque, e ela nao
    pertence a nenhuma familia.
    """
    ataques = df[df['Label'] == 1].copy()
    ataques['prob'] = prob_oof[df['Label'] == 1]
    ataques['detectado'] = ataques['prob'] >= limiar

    linhas = []
    for familia, grupo in ataques.groupby('familia_ataque'):
        linhas.append({
            'familia': familia,
            'n': len(grupo),
            'pct_do_total': len(grupo) / len(ataques),
            'detectados': int(grupo['detectado'].sum()),
            'recall': float(grupo['detectado'].mean()),
            'prob_media': float(grupo['prob'].mean()),
        })
    tabela = pd.DataFrame(linhas).sort_values('n', ascending=False)

    # Agregado de SQLi + XSS: e o numero que corresponde ao tema declarado do TCC.
    alvo = ataques[ataques['familia_ataque'].isin(['SQLi', 'XSS'])]
    return tabela, {
        'n': len(alvo),
        'recall': float(alvo['detectado'].mean()) if len(alvo) else float('nan'),
        'prob_media': float(alvo['prob'].mean()) if len(alvo) else float('nan'),
    }


def imprimir_por_familia(tabela: pd.DataFrame, alvo: dict, limiar: float) -> None:
    print(f"\n{'=' * 78}")
    print(f"RECALL POR FAMILIA DE ATAQUE (limiar {limiar:.3f})")
    print('=' * 78)
    print(f"{'Familia':32}{'n':>7}{'% total':>10}{'detectados':>12}{'recall':>9}{'p media':>10}")
    print('-' * 78)
    for _, r in tabela.iterrows():
        print(f"{r['familia']:32}{r['n']:7}{r['pct_do_total']:9.1%}"
              f"{r['detectados']:12}{r['recall']:9.1%}{r['prob_media']:10.3f}")
    print('-' * 78)
    print(f"{'SQLi + XSS (tema do TCC)':32}{alvo['n']:7}{'':>10}"
          f"{'':>12}{alvo['recall']:9.1%}{alvo['prob_media']:10.3f}")
    print('=' * 78)


# =============================================================================
# 6. TREINAR O MODELO FINAL E SALVAR
# =============================================================================

def treinar_final(df: pd.DataFrame, limiar: float, resumo: dict,
                  pasta_destino: Path, descricao_dataset: str) -> None:
    """
    Treina no dataset completo e salva os artefatos.

    Por que treinar no dataset TODO agora? Porque a etapa de medicao ja acabou. Os
    numeros que eu reporto vem da validacao cruzada; o modelo que vai para producao
    deve aproveitar todos os dados disponiveis.

    Salvo tres arquivos:
      waf_model.pkl        - o modelo
      tfidf_vectorizer.pkl - o vetorizador (precisa ser o MESMO do treino)
      model_metadata.json  - ordem das colunas, limiar e metricas

    O metadata resolve um risco real: a ordem das colunas na inferencia tem que
    ser identica a do treino. Hoje o api.py monta o DataFrame na mao e funciona por
    coincidencia de construcao. Com a lista salva, da para reindexar
    explicitamente e falhar alto se algo divergir.
    """
    print("\n[4/4] Treinando o modelo final sobre o dataset completo...")
    todos = np.arange(len(df))
    X, _, nomes, vetorizador = montar_matriz(df, todos, todos[:1],
                                             usar_heuristicas=True, usar_tfidf=True,
                                             usar_contexto=True)

    modelo = RandomForestClassifier(n_estimators=N_ARVORES, random_state=SEMENTE,
                                    n_jobs=-1)
    modelo.fit(X, df['Label'].to_numpy())

    # n_jobs=1 para a inferencia. Medi que com n_jobs=-1 uma predicao de amostra
    # unica leva 28,54ms, contra 7,95ms com n_jobs=1: o custo de distribuir o
    # trabalho entre threads supera o de percorrer as 100 arvores. Paralelizar
    # ajuda no treino (milhares de amostras) e atrapalha na inferencia unitaria.
    modelo.n_jobs = 1

    pasta_destino.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, pasta_destino / 'waf_model.pkl')
    joblib.dump(vetorizador, pasta_destino / 'tfidf_vectorizer.pkl')

    metadata = {
        'limiar_decisao': limiar,
        'colunas': nomes,
        'n_colunas': len(nomes),
        'n_amostras_treino': int(len(df)),
        'n_arvores': N_ARVORES,
        'alvo_falso_positivo': ALVO_FALSO_POSITIVO,
        'metricas_validacao_cruzada': resumo,
        'dataset': descricao_dataset,
        'validacao': f'StratifiedGroupKFold({N_FOLDS}) agrupado por payload',
    }
    with open(pasta_destino / 'model_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    rel = pasta_destino.relative_to(RAIZ)
    print(f"      {rel}/waf_model.pkl        ({len(nomes)} colunas, {N_ARVORES} arvores)")
    print(f"      {rel}/tfidf_vectorizer.pkl")
    print(f"      {rel}/model_metadata.json  (limiar={limiar:.3f})")


# =============================================================================
def main() -> None:
    print(__doc__)

    # Modo de demonstracao: treina sobre os datasets de payload, que incluem trafego
    # benigno em portugues, e salva em models/demo/. Ver carregar_dados_demo().
    modo_demo = '--demo' in sys.argv
    if modo_demo:
        print(">>> MODO DEMONSTRACAO: treinando sobre os datasets de payload.")
        print(">>> As metricas deste modelo NAO vao para a monografia — use o modelo")
        print(">>> do CSIC (rodar sem --demo) para isso.\n")
        df = carregar_dados_demo()
        pasta_destino = PASTA_MODELOS / 'demo'
        descricao = 'Datasets de payload SQLi/XSS (modelo de demonstracao)'
    else:
        df = carregar_dados_csic()
        pasta_destino = PASTA_MODELOS
        descricao = 'HTTP DATASET CSIC 2010'

    print("\n[2/4] Calculando features...")
    df = preparar_colunas_auxiliares(df)
    n_grupos = df['grupo_payload'].nunique()
    print(f"      {n_grupos} grupos de payload distintos "
          f"({len(df) / n_grupos:.1f} requisicoes por grupo)")

    # --- Comparacao de conjuntos de features ---
    # Rodo a validacao cruzada em quatro configuracoes. Isso responde "cada grupo
    # de features esta pagando o proprio custo?" com dado, em vez de suposicao.
    print(f"\n[3/4] Validacao cruzada StratifiedGroupKFold({N_FOLDS})...")

    configuracoes = [
        ('Heuristicas + TF-IDF (modelo antigo)', dict(usar_heuristicas=True,  usar_tfidf=True,  usar_contexto=False)),
        ('Apenas TF-IDF',                        dict(usar_heuristicas=False, usar_tfidf=True,  usar_contexto=False)),
        ('Apenas contexto HTTP',                 dict(usar_heuristicas=False, usar_tfidf=False, usar_contexto=True)),
        ('COMPLETO (+ contexto HTTP)',           dict(usar_heuristicas=True,  usar_tfidf=True,  usar_contexto=True)),
    ]

    resultados, oof_completo, resumo_completo = {}, None, None
    for nome, opcoes in configuracoes:
        print(f"\n    >>> {nome}")
        tabela, prob_oof = validar(df, **opcoes)
        resumo = resumir(nome, tabela)
        resultados[nome] = resumo
        if nome.startswith('COMPLETO'):
            oof_completo, resumo_completo = prob_oof, resumo

    # --- Tabela comparativa ---
    print(f"\n{'=' * 78}\nCOMPARACAO DOS CONJUNTOS DE FEATURES (media dos {N_FOLDS} folds)\n{'=' * 78}")
    print(f"{'Configuracao':40}{'F1':>16}{'Recall':>16}{'Taxa FP':>10}")
    print('-' * 78)
    for nome, r in resultados.items():
        print(f"{nome:40}"
              f"{r['f1']['media']:9.4f} ±{r['f1']['desvio']:.3f}"
              f"{r['recall']['media']:9.4f} ±{r['recall']['desvio']:.3f}"
              f"{r['taxa_fp']['media']:10.2%}")

    # --- Calibracao do limiar sobre o modelo completo ---
    print(f"\n{'=' * 78}\nCALIBRACAO DO LIMIAR DE DECISAO\n{'=' * 78}")
    limiar, curva = escolher_limiar(df['Label'].to_numpy(), oof_completo,
                                    ALVO_FALSO_POSITIVO)

    sufixo = '_demo' if modo_demo else ''
    destino_curva = RAIZ / 'docs' / 'medicoes' / f'curva_limiar{sufixo}.csv'
    destino_curva.parent.mkdir(parents=True, exist_ok=True)
    curva.to_csv(destino_curva, index=False)
    print(f"\n      Curva completa salva em {destino_curva.relative_to(RAIZ)}")

    # --- Recall por familia: o numero que corresponde ao tema do TCC ---
    if 'familia_ataque' in df.columns:
        for lim, rotulo in [(0.5, 'limiar padrao'), (limiar, 'limiar calibrado')]:
            tabela_fam, alvo = recall_por_familia(df, oof_completo, lim)
            print(f"\n>>> {rotulo}")
            imprimir_por_familia(tabela_fam, alvo, lim)
            if abs(lim - limiar) < 1e-9:
                tabela_fam.to_csv(
                    RAIZ / 'docs' / 'medicoes' / f'recall_por_familia{sufixo}.csv', index=False)

    treinar_final(df, limiar, resumo_completo, pasta_destino, descricao)
    print(f"\n{'=' * 78}\nConcluido.\n{'=' * 78}")


if __name__ == '__main__':
    main()
