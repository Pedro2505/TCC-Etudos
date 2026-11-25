import json
import re
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def extrair_features_manuais(df: pd.DataFrame, coluna_texto: str = 'Sentence',
                             verboso: bool = True) -> pd.DataFrame:
    """
    Abordagem 1: Engenharia de Features Manual (Heurística).
    Transforma a string da requisição HTTP em números baseando-se em conhecimento de AppSec.

    verboso=False silencia o print: na inferência esta função é chamada a cada
    requisição HTTP, e imprimir em toda chamada poluiria o log do servidor.
    """
    if verboso:
        print("Extraindo features manuais...")
    df_features = df.copy()
    
    # Certificar-se de que tudo é string e tratar nulos
    df_features[coluna_texto] = df_features[coluna_texto].astype(str).fillna('')
    
    # Garantir que a coluna Label seja 100% numérica
    if 'Label' in df_features.columns:
        df_features['Label'] = pd.to_numeric(df_features['Label'], errors='coerce').fillna(0).astype(int)
    
    # 1. Comprimento da String
    # Ataques de SQLi tendem a ser maiores que parâmetros normais
    df_features['comprimento'] = df_features[coluna_texto].apply(len)
    
    # 2. Contagem de Caracteres Especiais (MUITO comuns em injeções)
    # Procuramos por: ' " ; - % ( ) = < >
    padrao_especiais = r'[\'";\-%()=<>]'
    df_features['qtd_caracteres_especiais'] = df_features[coluna_texto].apply(
        lambda x: len(re.findall(padrao_especiais, x))
    )
    
    # 3. Quantidade de palavras-chave suspeitas de SQLi
    padrao_sql = r'(?i)\b(select|union|drop|insert|update|delete|or|and|from|where)\b'
    df_features['qtd_keywords_sql'] = df_features[coluna_texto].apply(lambda x: len(re.findall(padrao_sql, str(x))))
    
    # 3.1. Quantidade de palavras-chave suspeitas de XSS (A Nova Sprint)
    padrao_xss = r'(?i)\b(script|alert|onerror|onload|javascript|document\.cookie|img|src|prompt)\b'
    df_features['qtd_keywords_xss'] = df_features[coluna_texto].apply(lambda x: len(re.findall(padrao_xss, str(x))))
    
    # 4. Presença de Ofuscações comuns em Hex/URL Encode (ex: %20, %27)
    padrao_encode = r'(%[0-9a-fA-F]{2})'
    df_features['qtd_url_encode'] = df_features[coluna_texto].apply(
        lambda x: len(re.findall(padrao_encode, x))
    )

    return df_features

def extrair_features_tfidf(df: pd.DataFrame, coluna_texto: str = 'Sentence') -> tuple:
    """
    Abordagem 2: Vetorização Estatística (TF-IDF).
    Delega a matemática para o Scikit-Learn encontrar os fragmentos mais relevantes.
    """
    print("Extraindo features TF-IDF (Estatística)...")
    
    # Inicializando o vetorizador (limitamos a 50 features para não estourar a memória agora)
    # analyzer='char_wb' ajuda muito em cibersegurança pois olha para pedaços de palavras/caracteres
    vetorizador = TfidfVectorizer(max_features=50, analyzer='char_wb', ngram_range=(2, 3))
    
    textos = df[coluna_texto].astype(str).fillna('')
    matriz_tfidf = vetorizador.fit_transform(textos)
    
    # Transformando a matriz matemática do Scikit-Learn de volta para um DataFrame do Pandas
    # para ficar fácil da gente enxergar
    nomes_colunas = vetorizador.get_feature_names_out()
    df_tfidf = pd.DataFrame(matriz_tfidf.toarray(), columns=[f"tfidf_{c}" for c in nomes_colunas])
    
    return df_tfidf, vetorizador

# ==============================================================================
# CAMINHO ÚNICO DE INFERÊNCIA
# ==============================================================================
# Por que esta seção existe:
#
# Eu tinha o código de montagem da matriz duplicado em quatro lugares (servidor.py,
# explicacao.py, debug_model.py e teste_falso_positivo.py). Toda vez que eu mudava as
# features, precisava editar os quatro — e quando esqueci um, o erro foi silencioso
# até o sklearn reclamar de contagem de colunas.
#
# Agora existe uma função só. Ela lê a lista de colunas de models/model_metadata.json
# e monta a matriz NESSA ORDEM, com reindex explícito. Se algo divergir, falha alto em
# vez de produzir uma predição errada.
# ==============================================================================

PASTA_MODELOS_PADRAO = Path(__file__).resolve().parent / 'models'

# Valores usados quando o contexto HTTP não está disponível (scripts de teste que
# analisam uma string solta, sem requisição real). São as medianas do CSIC 2010.
CONTEXTO_PADRAO = {
    'metodo': 'GET',
    'n_parametros': 1,
    'tem_corpo': 0,
    'content_length': 0,
    'n_headers': 11,
}


def carregar_artefatos(pasta: Optional[Path] = None) -> tuple:
    """
    Carrega modelo, vetorizador e metadata de uma vez.

    Devolve (modelo, vetorizador, metadata). O metadata traz a ordem das colunas e o
    limiar de decisão calibrado — sem ele não há como garantir que a inferência use
    a mesma disposição de features do treino.
    """
    pasta = Path(pasta) if pasta else PASTA_MODELOS_PADRAO
    modelo = joblib.load(pasta / 'waf_model.pkl')
    vetorizador = joblib.load(pasta / 'tfidf_vectorizer.pkl')

    caminho_meta = pasta / 'model_metadata.json'
    if caminho_meta.exists():
        with open(caminho_meta, encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        # Compatibilidade com modelos antigos, treinados antes do metadata existir.
        metadata = {'limiar_decisao': 0.5, 'colunas': None}

    # n_jobs=1 na inferência: distribuir o trabalho entre threads custa mais que
    # percorrer as 100 árvores quando há só uma linha para classificar. Com n_jobs=1 a
    # inferência mede 6,31 ms em média (medir_latencia.py); n_jobs=-1 não foi medido aqui.
    modelo.n_jobs = 1
    return modelo, vetorizador, metadata


def preparar_para_inferencia(payload: str, vetorizador, colunas: Optional[list] = None,
                            contexto: Optional[dict] = None) -> pd.DataFrame:
    """
    Transforma um payload de texto na matriz de uma linha que o modelo espera.

    payload   : o texto já normalizado (URL-decoded, minúsculas)
    colunas   : lista de colunas do metadata; se informada, o resultado é reindexado
                nessa ordem exata
    contexto  : dict com metodo/n_parametros/tem_corpo/content_length/n_headers.
                Ausente -> usa CONTEXTO_PADRAO.

    Uma nota de honestidade sobre o contexto padrão: quando ele é usado, o modelo
    recebe valores inventados para 7 das 62 features. A predição continua válida, mas
    é menos informada do que a de uma requisição real. Os scripts que analisam
    strings soltas estão nessa situação, e por isso não servem para medir desempenho
    do sistema em produção — servem para inspecionar o comportamento do modelo diante
    de um texto.
    """
    ctx = {**CONTEXTO_PADRAO, **(contexto or {})}

    df = pd.DataFrame({'Sentence': [payload]})
    df = extrair_features_manuais(df, verboso=False)

    # Contexto HTTP, com o método em colunas binárias (one-hot)
    df['n_parametros'] = ctx['n_parametros']
    df['tem_corpo'] = ctx['tem_corpo']
    df['content_length'] = ctx['content_length']
    df['n_headers'] = ctx['n_headers']
    for metodo in ['GET', 'POST', 'PUT']:
        df[f'metodo_{metodo}'] = int(ctx['metodo'] == metodo)

    # TF-IDF
    matriz = vetorizador.transform([payload])
    df_tfidf = pd.DataFrame(matriz.toarray(),
                            columns=[f'tfidf_{c}' for c in vetorizador.get_feature_names_out()])

    pronto = pd.concat([df.drop(columns=['Sentence', 'tipo_ataque'], errors='ignore'),
                        df_tfidf], axis=1)

    if colunas:
        faltando = set(colunas) - set(pronto.columns)
        if faltando:
            raise ValueError(
                f"Features ausentes na inferência: {sorted(faltando)}. "
                "O modelo foi treinado com um conjunto de features diferente do que "
                "este código monta — retreine com treino_modelo.py ou atualize esta função."
            )
        pronto = pronto[colunas]      # reindex explícito: garante a MESMA ordem do treino

    return pronto


def classificar(payload: str, modelo, vetorizador, metadata: dict,
                contexto: Optional[dict] = None) -> tuple:
    """
    Classifica um payload. Devolve (é_ataque, probabilidade).

    Aplica o limiar calibrado do metadata em vez do 0,5 implícito do `.predict()`.
    """
    X = preparar_para_inferencia(payload, vetorizador, metadata.get('colunas'), contexto)

    # .to_numpy() de proposito: o modelo foi treinado sobre uma matriz esparsa, que
    # nao carrega nomes de coluna. Passar um DataFrame nomeado aqui faz o sklearn
    # emitir UserWarning ("fitted without feature names") a cada requisicao. Como a
    # ordem já foi garantida pelo reindex em preparar_para_inferencia(), entregar o
    # array cru e correto e silencioso. O DataFrame nomeado continua disponivel para
    # o SHAP e para inspecao.
    probabilidade = float(modelo.predict_proba(X.to_numpy())[0][1])
    limiar = metadata.get('limiar_decisao', 0.5)
    return probabilidade >= limiar, probabilidade
