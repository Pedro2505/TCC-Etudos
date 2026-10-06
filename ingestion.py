import pandas as pd
import glob
import os
import gc
from pathlib import Path
from typing import List, Optional

# ==============================================================================
# PIPELINE DE INGESTÃO E SANITIZAÇÃO DE DADOS
# Leitura, padronização de schema e deduplicação dos datasets de SQLi e XSS.
# ==============================================================================

# Regex de reescrita heurística de labels. Fica exposta aqui (em vez de embutida na
# função) porque baseline_comparison.py precisa da MESMA regex para construir o
# baseline de assinaturas com que o modelo de ML é comparado.
# Grupo non-capturing (?:...) de proposito: com grupo de captura o pandas emite
# UserWarning em str.contains.
REGEX_KEYWORDS_SQL = r'(?i)\b(?:select|union|drop|insert|delete)\b'

def extrair_e_sanitizar_csv(caminho_arquivo: str, tipo_ataque: str,
                            reescrever_labels: bool = True) -> Optional[pd.DataFrame]:
    """
    Realiza a leitura de um CSV aplicando otimizações de memória (Pushdown) e 
    sanitização imediata.
    
    Por que não pd.read_csv() puro?
    1. Memory Overhead: Ler o CSV inteiro aloca memória para colunas inúteis.
    2. Lazy Evaluation vs Eager: Em Big Data, filtramos no ato da leitura.
    """
    print(f"[*] Processando: {caminho_arquivo}")
    try:
        # TENTATIVA 1: Leitura com UTF-8. 
        # Cibersegurança frequentemente tem payloads malformados que quebram parsers.
        try:
            # chunksize não é usado aqui pois os arquivos cabem na RAM, mas limitamos 
            # as colunas (usecols) para complexidade de espaço O(K) onde K = 2 colunas.
            df = pd.read_csv(caminho_arquivo, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
            # Fallback para UTF-16LE, muito comum em dumps de SQL Server antigos
            df = pd.read_csv(caminho_arquivo, encoding='utf-16le', on_bad_lines='skip')
            
        # PADRONIZAÇÃO DE SCHEMA (Prevenindo Divergência)
        # Em vez de confiar nos nomes das colunas, nós as renomeamos de forma autoritária 
        # se elas baterem com aliases conhecidos.
        aliases_payload = ['Sentence', 'Query', 'payload', 'text']
        aliases_label = ['Label', 'Class', 'is_attack']
        
        # Encontra as colunas alvo através da intersecção de conjuntos O(1)
        col_payload = next((col for col in df.columns if col in aliases_payload), None)
        col_label = next((col for col in df.columns if col in aliases_label), None)
        
        if not col_payload or not col_label:
            print(f"[!] AVISO: Schema incompatível em {caminho_arquivo}. Ignorando.")
            return None
            
        # Filtragem O(N) e projeção de colunas no momento T0
        df = df[[col_payload, col_label]].rename(columns={col_payload: 'Sentence', col_label: 'Label'})
        
        # SANITIZAÇÃO E CASTING ESTRITO (Prevenção contra Data Drift)
        df = df.dropna()
        df['Sentence'] = df['Sentence'].astype(str)
        
        # Converte para numérico forçado. Textos "vazados" viram NaN e caem no dropna O(N)
        df['Label'] = pd.to_numeric(df['Label'], errors='coerce')
        df = df.dropna(subset=['Label'])
        
        # Downcasting de Memória: Label só precisa ser 0 ou 1 (int8 ocupa 1 byte, int64 ocupa 8 bytes)
        # Economia de 87% de RAM na coluna de Target!
        df['Label'] = df['Label'].astype('int8')
        
        # Marca a origem, para permitir métricas separadas por classe de ataque no relatório
        df['tipo_ataque'] = tipo_ataque

        # REESCRITA HEURÍSTICA DE LABELS (weak supervision)
        # O SQLiV3 rotula como 0 algumas queries que contêm injeção estrutural.
        # ATENÇÃO METODOLÓGICA: esta regex usa as MESMAS palavras-chave que a feature
        # 'qtd_keywords_sql' do extractor.py conta. Ao aplicá-la, o label passa a ser
        # função quase determinística de uma feature -> vazamento circular.
        # Por isso é opcional: baseline_comparison.py mede o impacto dos dois cenários.
        if reescrever_labels:
            mask = df['Sentence'].str.contains(REGEX_KEYWORDS_SQL, na=False, regex=True)
            df.loc[mask, 'Label'] = 1

        return df

    except Exception as e:
        print(f"[!] ERRO CRÍTICO ao processar {caminho_arquivo}: {e}")
        return None

RAIZ_PROJETO = Path(__file__).resolve().parent


def unificar_datasets(pasta_sqli: Optional[str] = None,
                      pasta_xss: Optional[str] = None,
                      reescrever_labels: bool = True) -> pd.DataFrame:
    """
    Ponto de entrada do Pipeline. Funde dados de múltiplas fontes resolvendo
    problemas de Schema e garantindo integridade.

    reescrever_labels=False devolve os labels originais dos CSVs, sem a correção
    heurística por regex (ver extrair_e_sanitizar_csv).
    """
    pasta_sqli = pasta_sqli or str(RAIZ_PROJETO / "datasets" / "SQL Injection")
    pasta_xss = pasta_xss or str(RAIZ_PROJETO / "datasets" / "XSS")

    arquivos_sqli = glob.glob(os.path.join(pasta_sqli, "*.csv"))
    arquivos_xss = glob.glob(os.path.join(pasta_xss, "*.csv"))

    lista_dfs: List[pd.DataFrame] = []

    # Processa SQLi
    for arq in arquivos_sqli:
        df_limpo = extrair_e_sanitizar_csv(arq, "SQLi", reescrever_labels)
        if df_limpo is not None:
            lista_dfs.append(df_limpo)

    # Processa XSS
    for arq in arquivos_xss:
        df_limpo = extrair_e_sanitizar_csv(arq, "XSS", reescrever_labels)
        if df_limpo is not None:
            lista_dfs.append(df_limpo)

    if not lista_dfs:
        raise ValueError("Nenhum dado válido extraído! O Pipeline falhou.")
        
    # FUSÃO (Concatenation)
    # Por que concat em vez de append em loop?
    # Pandas DataFrames são imutáveis em memória. Usar concat de uma vez (Bulk operation) 
    # aloca memória apenas uma vez O(N). Fazer append iterativo causaria realocação O(N^2).
    print("\n[*] Consolidando a Matrix Master de Dados...")
    df_master = pd.concat(lista_dfs, ignore_index=True)
    
    # Liberação explícita de memória do Garbage Collector do Python
    del lista_dfs
    gc.collect()
    
    # REMOÇÃO DE DUPLICATAS (Prevenção de Data Leakage)
    linhas_antes = len(df_master)
    df_master = df_master.drop_duplicates(subset=['Sentence'], keep='first')
    linhas_depois = len(df_master)
    
    print(f"[*] Pipeline Concluído. {linhas_antes - linhas_depois} duplicatas mortas.")
    print(f"[*] Distribuição de Classes (Target):")
    print(df_master['Label'].value_counts())
    
    return df_master

if __name__ == "__main__":
    df = unificar_datasets()
