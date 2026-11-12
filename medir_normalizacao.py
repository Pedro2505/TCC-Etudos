"""
Script de MEDIÇÃO DE APOIO — escrito pelo Claude (assistente de IA) em 12/11/2026,
pela exceção do CLAUDE.md ("script de medição de apoio"). Não é peça do TCC: não
treina, não decide, não altera nada. Só mede.

Pergunta que ele responde:
    "A normalização usada no servidor é a mesma do treino? Se não, quanto isso muda
    as decisões?"

O treino lê a coluna 'Sentence' do ingestao_csic.py: valores dos parâmetros com UM
URL-decode (unquote_plus). O servidor recebe os valores já decodificados uma vez pelo
Starlette e ainda aplica a decodificador_ofuscacao(): URL-decode recursivo, tentativa
de Base64 e minúsculas. Este script aplica as duas versões às 32.808 requisições em
escopo e conta quantas decisões mudam.

A função do servidor NÃO é copiada aqui: ela é lida do próprio servidor.py (via ast),
para que a medição acompanhe qualquer alteração que o Pedro fizer nela.

LIMITAÇÃO: usa o modelo final (treinado em todos os dados), portanto as
probabilidades são in-sample. Serve para medir a DIFERENÇA entre as duas
normalizações, não o desempenho do modelo.

Uso:  venv\\Scripts\\python.exe medir_normalizacao.py
Saída: docs/medicoes/normalizacao_treino_vs_servidor.md
"""
import ast
from pathlib import Path

import numpy as np
import pandas as pd

import assinaturas
from extrator import carregar_artefatos, preparar_para_inferencia
from ingestao_csic import carregar_supervisionado

RAIZ = Path(__file__).parent
SAIDA = RAIZ / 'docs' / 'medicoes' / 'normalizacao_treino_vs_servidor.md'


def carregar_funcao_do_servidor():
    """Extrai decodificador_ofuscacao de dentro do middleware do servidor.py."""
    fonte = (RAIZ / 'servidor.py').read_text(encoding='utf-8')
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, ast.FunctionDef) and no.name == 'decodificador_ofuscacao':
            modulo = ast.Module(body=[no], type_ignores=[])
            escopo = {}
            exec(compile("from urllib.parse import unquote\nimport base64\n", 'imp', 'exec'), escopo)
            exec(compile(modulo, 'servidor.py', 'exec'), escopo)
            return escopo['decodificador_ofuscacao']
    raise RuntimeError('decodificador_ofuscacao não encontrada em servidor.py')


def probabilidades(textos, modelo, vetorizador, meta, contextos):
    linhas = [preparar_para_inferencia(t, vetorizador, meta['colunas'], c)
              for t, c in zip(textos, contextos)]
    X = pd.concat(linhas, ignore_index=True).to_numpy()
    return modelo.predict_proba(X)[:, 1]


def main():
    decod = carregar_funcao_do_servidor()
    modelo, vetorizador, meta = carregar_artefatos(RAIZ / 'models')
    limiar = meta['limiar_decisao']

    df = carregar_supervisionado()
    treino = df['Sentence'].fillna('').astype(str)
    servidor = treino.map(decod)

    mudou_texto = (treino != servidor)
    mudou_so_caixa = mudou_texto & (treino.str.lower() == servidor)
    mudou_alem_caixa = mudou_texto & ~mudou_so_caixa

    # Camada 1
    c1_treino = treino.map(lambda t: assinaturas.avaliar(t) is not None)
    c1_serv = servidor.map(lambda t: assinaturas.avaliar(t) is not None)

    # Camada 2, com o contexto HTTP real de cada requisição
    contextos = df[['metodo', 'n_parametros', 'tem_corpo', 'content_length',
                    'n_headers']].to_dict('records')
    print('[*] Classificando com a normalização do treino...')
    p_treino = probabilidades(treino, modelo, vetorizador, meta, contextos)
    print('[*] Classificando com a normalização do servidor...')
    p_serv = probabilidades(servidor, modelo, vetorizador, meta, contextos)

    y = df['Label'].to_numpy()
    bloq_treino = c1_treino.to_numpy() | (p_treino >= limiar)
    bloq_serv = c1_serv.to_numpy() | (p_serv >= limiar)

    n = len(df)
    leg, atk = (y == 0), (y == 1)
    fp_t, fp_s = bloq_treino[leg].sum(), bloq_serv[leg].sum()
    tp_t, tp_s = bloq_treino[atk].sum(), bloq_serv[atk].sum()
    viraram = (bloq_treino != bloq_serv)

    exemplos = df.loc[mudou_alem_caixa, 'Sentence'].head(8).tolist()
    exemplos_dec = [decod(e) for e in exemplos]

    linhas = [
        '# Normalização: treino × servidor',
        '',
        'Gerado por `medir_normalizacao.py` (script de medição de apoio, escrito pelo Claude).',
        f'Base: {n} requisições em escopo do CSIC 2010. Modelo final de `models/`, '
        f'limiar {limiar:.3f}. **Probabilidades in-sample**: mede a diferença entre as '
        'normalizações, não o desempenho do modelo.',
        '',
        '## Quanto o texto muda',
        '',
        '| | n | % |',
        '| :--- | ---: | ---: |',
        f'| Texto idêntico | {(~mudou_texto).sum()} | {(~mudou_texto).mean():.2%} |',
        f'| Muda só maiúsculas/minúsculas | {mudou_so_caixa.sum()} | {mudou_so_caixa.mean():.2%} |',
        f'| Muda além da caixa (decode recursivo ou Base64) | {mudou_alem_caixa.sum()} | {mudou_alem_caixa.mean():.2%} |',
        '',
        '## Quanto a decisão muda (camada 1 OU camada 2)',
        '',
        '| | Normalização do treino | Normalização do servidor |',
        '| :--- | ---: | ---: |',
        f'| Ataques bloqueados (de {atk.sum()}) | {tp_t} ({tp_t/atk.sum():.2%}) | {tp_s} ({tp_s/atk.sum():.2%}) |',
        f'| Legítimas bloqueadas (de {leg.sum()}) | {fp_t} ({fp_t/leg.sum():.2%}) | {fp_s} ({fp_s/leg.sum():.2%}) |',
        f'| Assinatura disparou | {c1_treino.sum()} | {c1_serv.sum()} |',
        '',
        f'Decisões que trocam de lado: **{viraram.sum()}** de {n} ({viraram.mean():.2%}) — '
        f'{(viraram & leg).sum()} legítimas e {(viraram & atk).sum()} ataques.',
        '',
        '## Exemplos de texto que muda além da caixa',
        '',
        '| Treino vê | Servidor vê |',
        '| :--- | :--- |',
    ]
    for a, b in zip(exemplos, exemplos_dec):
        linhas.append(f'| `{a[:70]!r}` | `{b[:70]!r}` |')
    SAIDA.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print('\n'.join(linhas))
    print(f'\n[OK] {SAIDA}')


if __name__ == '__main__':
    main()
