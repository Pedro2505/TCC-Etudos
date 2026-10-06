"""
Junta os resultados ja medidos num JSON para a secao "Resultados" do frontend.

Nao calcula nada novo: so le o que treino_modelo.py e avaliacao_hibrida.py gravaram
e anota, em cada bloco, o script de origem. Assim todo numero que aparece na tela
tem um script que o gerou.

Rodar:  python exportar_painel.py      (depois de treino_modelo.py e avaliacao_hibrida.py)
Gera:   frontend/public/resultados.json
"""

import csv
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).resolve().parent
MEDICOES = RAIZ / 'docs' / 'medicoes'
DESTINO = RAIZ / 'frontend' / 'public' / 'resultados.json'


def ler_metadata(pasta: Path) -> dict | None:
    arquivo = pasta / 'model_metadata.json'
    if not arquivo.exists():
        return None
    meta = json.loads(arquivo.read_text(encoding='utf-8'))
    colunas = meta.get('colunas', [])
    tfidf = sum(c.startswith('tfidf_') for c in colunas)
    contexto = sum(c in ('n_parametros', 'tem_corpo', 'content_length', 'n_headers')
                   or c.startswith('metodo_') for c in colunas)
    return {
        'dataset': meta.get('dataset'),
        'validacao': meta.get('validacao'),
        'n_amostras': meta.get('n_amostras_treino'),
        'n_arvores': meta.get('n_arvores'),
        'limiar': meta.get('limiar_decisao'),
        'alvo_fp': meta.get('alvo_falso_positivo'),
        'features': {'total': len(colunas), 'heuristicas': len(colunas) - tfidf - contexto,
                     'contexto': contexto, 'tfidf': tfidf},
        'validacao_cruzada': meta.get('metricas_validacao_cruzada', {}),
    }


def ler_curva(arquivo: Path, passo: float = 0.01) -> list[dict]:
    """A curva tem um ponto por valor de probabilidade; guardo um a cada `passo`."""
    with open(arquivo, encoding='utf-8') as f:
        linhas = [{k: float(v) for k, v in l.items()} for l in csv.DictReader(f)]
    pontos, proximo = [], 0.0
    for l in sorted(linhas, key=lambda l: l['limiar']):
        if l['limiar'] >= proximo - 1e-9:
            pontos.append({'limiar': l['limiar'], 'taxa_fp': l['taxa_fp'],
                           'recall': l['recall'], 'precisao': l['precisao'], 'f1': l['f1']})
            proximo = l['limiar'] + passo
    return pontos


def tabelas_markdown(texto: str) -> dict[str, list[list[str]]]:
    """Devolve as tabelas do .md indexadas pelo titulo '## N. ...' que as precede."""
    tabelas, secao = {}, None
    for linha in texto.splitlines():
        if linha.startswith('## '):
            secao = re.sub(r'^##\s*\d+\.\s*', '', linha).strip()
        elif linha.startswith('|') and secao and not re.match(r'^\|\s*:?-', linha):
            celulas = [c.strip().strip('*').strip('`') for c in linha.strip('|').split('|')]
            tabelas.setdefault(secao, []).append(celulas)
    return tabelas


def pct(texto: str) -> float:
    return float(texto.replace('%', '').replace(',', '.')) / 100


def ler_avaliacao_hibrida(arquivo: Path) -> dict:
    tabelas = tabelas_markdown(arquivo.read_text(encoding='utf-8'))

    def tabela(prefixo):
        for titulo, linhas in tabelas.items():
            if titulo.startswith(prefixo):
                return linhas[1:]  # sem o cabecalho
        return []

    configuracoes = [{
        'nome': l[0], 'precisao': pct(l[1]), 'recall': pct(l[2]), 'f1': float(l[3]),
        'taxa_fp': pct(l[4]), 'fp': int(l[5]), 'fn': int(l[6]),
    } for l in tabela('As quatro')]

    complementaridade = [{'grupo': l[0], 'n': int(l[1]), 'pct': pct(l[2])}
                         for l in tabela('Complementaridade')]

    familias = [{
        'familia': l[0], 'n': int(l[1]), 'assinaturas': pct(l[2]), 'modelo': pct(l[3]),
        'combinado': pct(l[4]),
    } for l in tabela('Recall por fam')]

    regras = [{'id': l[0], 'nome': l[1], 'disparos': int(l[2])}
              for l in tabela('Regras que mais')]

    return {'configuracoes': configuracoes, 'complementaridade': complementaridade,
            'familias': familias, 'regras': regras}


def ler_ablacao(log: Path) -> list[dict]:
    """Resumo de cada conjunto de features, do log do treino_modelo.py."""
    if not log.exists():
        return []
    texto = log.read_text(encoding='utf-8', errors='replace')
    blocos = re.findall(
        r'RESUMO — (.+?)\n\s+F1\s+([\d.]+) ± ([\d.]+)\n\s+Precisao\s+([\d.]+) ± [\d.]+\n'
        r'\s+Recall\s+([\d.]+) ± [\d.]+\n\s+ROC-AUC\s+([\d.]+) ± [\d.]+\n'
        r'\s+Taxa de FP\s+([\d.]+)% ± ([\d.]+)%', texto)
    return [{'nome': b[0].strip(), 'f1': float(b[1]), 'f1_desvio': float(b[2]),
             'precisao': float(b[3]), 'recall': float(b[4]), 'roc_auc': float(b[5]),
             'taxa_fp': float(b[6]) / 100} for b in blocos]


def ler_dataset(log_ingestao: Path, log_treino: Path) -> dict:
    """Composicao do CSIC 2010 (Tabela 1), dos logs de ingestao e treino."""
    dados = {'arquivos': [], 'com_payload': None, 'em_escopo': None, 'grupos': None}
    if log_ingestao.exists():
        texto = log_ingestao.read_text(encoding='utf-8', errors='replace')
        for nome, n, esperado in re.findall(
                r'\[\*\] (\S+\.txt): (\d+) requisicoes parseadas \(esperado: (\d+)\)', texto):
            dados['arquivos'].append({'arquivo': nome, 'parseadas': int(n), 'esperado': int(esperado)})
        if m := re.search(r'payload: (\d+) restantes', texto):
            dados['com_payload'] = int(m.group(1))
        if m := re.search(r'Total de requisicoes: (\d+)', texto):
            dados['em_escopo'] = int(m.group(1))
    if log_treino.exists():
        texto = log_treino.read_text(encoding='utf-8', errors='replace')
        if m := re.search(r'(\d+) grupos de payload distintos', texto):
            dados['grupos'] = int(m.group(1))
    return dados


def ler_folds(log: Path, configuracao: str = 'COMPLETO') -> list[dict]:
    """Metricas de cada fold de uma configuracao (Tabela 3), do log do treino."""
    if not log.exists():
        return []
    texto = log.read_text(encoding='utf-8', errors='replace')
    trecho = texto.split(f'>>> {configuracao}', 1)
    if len(trecho) < 2:
        return []
    trecho = trecho[1].split('RESUMO', 1)[0]
    return [{'fold': int(f[0]), 'f1': float(f[1]), 'precisao': float(f[2]),
             'recall': float(f[3]), 'fp': int(f[4]), 'taxa_fp': float(f[5]) / 100}
            for f in re.findall(r'fold (\d)/\d: F1=([\d.]+)\s+precisao=([\d.]+)\s+'
                                r'recall=([\d.]+)\s+FP=\s*(\d+)\s+taxa_FP=\s*([\d.]+)%', trecho)]


def main() -> None:
    log_treino = RAIZ / 'logs' / 'model_trainer_rerun1.log'
    log_ingestao = RAIZ / 'logs' / 'ingestion_csic.log'
    dados = {
        'modelo_csic': {'fonte': 'treino_modelo.py → models/model_metadata.json',
                        **(ler_metadata(RAIZ / 'models') or {})},
        'modelo_demo': {'fonte': 'treino_modelo.py --demo → models/demo/model_metadata.json '
                                 '(copiado do projeto antigo, não rerodado aqui)',
                        **(ler_metadata(RAIZ / 'models' / 'demo') or {})},
        'curva_limiar': {'fonte': 'treino_modelo.py → docs/medicoes/curva_limiar.csv',
                         'pontos': ler_curva(MEDICOES / 'curva_limiar.csv')},
        'hibrida': {'fonte': 'avaliacao_hibrida.py → docs/medicoes/avaliacao_hibrida.md',
                    **ler_avaliacao_hibrida(MEDICOES / 'avaliacao_hibrida.md')},
        'ablacao': {'fonte': 'treino_modelo.py (log da execução de 06/10)',
                    'configuracoes': ler_ablacao(log_treino)},
        'folds': {'fonte': 'treino_modelo.py (log da execução de 06/10), modelo completo, limiar 0,5',
                  'linhas': ler_folds(log_treino)},
        'dataset': {'fonte': 'ingestao_csic.py e treino_modelo.py (logs da execução de 06/10)',
                    **ler_dataset(log_ingestao, log_treino)},
    }

    DESTINO.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding='utf-8')
    h = dados['hibrida']
    print(f"Gravado {DESTINO.relative_to(RAIZ)}")
    print(f"  configuracoes: {len(h['configuracoes'])} · complementaridade: "
          f"{len(h['complementaridade'])} · familias: {len(h['familias'])} · "
          f"regras: {len(h['regras'])}")
    print(f"  curva: {len(dados['curva_limiar']['pontos'])} pontos · "
          f"ablacao: {len(dados['ablacao']['configuracoes'])} configuracoes")


if __name__ == '__main__':
    main()
