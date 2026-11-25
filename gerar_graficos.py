"""
GRÁFICOS DO ARTIGO — script de apoio escrito pelo Claude (assistente de IA) em 25/11/2026,
a pedido do Pedro. Não mede nada novo: lê os relatórios que os scripts de medição já
gravaram em docs/medicoes/ e desenha. Se um número mudar lá, rodar de novo atualiza a figura.

Origem de cada figura:
    fig1_recall_por_familia.png   <- avaliacao_hibrida.md §3      (avaliacao_hibrida.py)
    fig2_configuracoes.png        <- avaliacao_hibrida.md §1      (avaliacao_hibrida.py)
    fig3_complementaridade.png    <- avaliacao_hibrida.md §2      (avaliacao_hibrida.py)
    fig4_curva_limiar.png         <- curva_limiar.csv             (treino_modelo.py)
    fig5_algoritmos.png           <- comparacao_modelos.md        (comparar_modelos.py)
    fig6_latencia.png             <- latencia.md                  (medir_latencia.py)
    (a matriz de confusão já sai do medir_erros.py: matriz_confusao.png)

Uso:   venv\\Scripts\\python.exe gerar_graficos.py
Saída: docs/medicoes/figuras/
"""
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd

RAIZ = Path(__file__).resolve().parent
MED = RAIZ / 'docs' / 'medicoes'
SAIDA = MED / 'figuras'

# Paleta categórica validada (dataviz/validate_palette.js, modo claro): todas as checagens passam.
REGRAS = '#eb6834'      # laranja: camada 1, assinaturas
MODELO = '#2a78d6'      # azul: camada 2, modelo
JUNTOS = '#1baf7a'      # verde-água: as duas juntas (sempre com rótulo direto)
CINZA = '#9a9a96'
TINTA, TINTA2, GRADE = '#1f1f1e', '#5e5d59', '#e4e3df'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': GRADE,
    'axes.labelcolor': TINTA2, 'xtick.color': TINTA2, 'ytick.color': TINTA2,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.titlesize': 12,
    'axes.titleweight': 'bold', 'axes.titlecolor': TINTA, 'axes.titlelocation': 'left',
    'figure.dpi': 100, 'savefig.dpi': 220, 'savefig.bbox': 'tight',
})


def tabela_md(arquivo: Path, cabecalho: str) -> pd.DataFrame:
    """Lê a primeira tabela markdown do arquivo cuja linha de cabeçalho começa com `cabecalho`."""
    linhas = arquivo.read_text(encoding='utf-8').splitlines()
    inicio = next(i for i, l in enumerate(linhas) if l.startswith('| ' + cabecalho))
    bloco = []
    for l in linhas[inicio:]:
        if not l.startswith('|'):
            break
        bloco.append([c.strip().strip('*').strip('`') for c in l.strip('|').split('|')])
    return pd.DataFrame(bloco[2:], columns=bloco[0])


def num(texto: str) -> float:
    """'49.6%' -> 49.6 · '0.7824 ± 0.0088' -> 0.7824 · '+45.6 pp' -> 45.6"""
    m = re.search(r'-?\d+(?:\.\d+)?', texto.replace(',', ''))
    return float(m.group()) if m else float('nan')


def fonte(fig, texto):
    fig.text(0.0, -0.06, 'Fonte: ' + texto, fontsize=8, color=TINTA2, ha='left', va='top')


def grade(ax, eixo='x'):
    ax.grid(axis=eixo, color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def fig1_recall_por_familia():
    t = tabela_md(MED / 'avaliacao_hibrida.md', 'Família')
    t = t[~t['Família'].str.contains('escopo')].iloc[::-1]
    nomes = (t['Família'].str.replace('Tampering sem assinatura', 'Tampering')
             .str.replace('Injecao', 'Injeção').str.replace('Caractere de Controle/Nulo', 'Caractere nulo'))
    nomes = [f'{n}  (n = {int(c):,})'.replace(',', '.') for n, c in zip(nomes, t['n'])]
    r1, r2 = t.iloc[:, 2].map(num), t.iloc[:, 3].map(num)
    y = range(len(t))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh([i + 0.2 for i in y], r1, height=0.38, color=REGRAS, label='Só assinaturas')
    ax.barh([i - 0.2 for i in y], r2, height=0.38, color=MODELO, label='Modelo')
    for i, (a, b) in enumerate(zip(r1, r2)):
        ax.text(a + 1, i + 0.2, f'{a:.1f}%'.replace('.', ','), va='center', fontsize=8, color=TINTA2)
        ax.text(b + 1, i - 0.2, f'{b:.1f}%'.replace('.', ','), va='center', fontsize=8, color=TINTA2)
    ax.set_yticks(list(y), nomes)
    ax.set_xlim(0, 112)
    ax.set_xlabel('Recall (% dos ataques da família detectados)')
    ax.set_title('Recall por família de ataque')
    ax.legend(frameon=False, loc='lower right', bbox_to_anchor=(1, 1.0), ncol=2)
    grade(ax)
    fonte(fig, 'avaliacao_hibrida.py (docs/medicoes/avaliacao_hibrida.md, §3). CSIC 2010, '
               'probabilidades out-of-fold, limiar 0,65.')
    fig.savefig(SAIDA / 'fig1_recall_por_familia.png')
    plt.close(fig)


def fig2_configuracoes():
    t = tabela_md(MED / 'avaliacao_hibrida.md', 'Configuração').iloc[:3]
    nomes = ['Só assinaturas', 'Só modelo', 'Assinaturas + modelo']
    cores = [REGRAS, MODELO, JUNTOS]
    recall, fp = t['Recall'].map(num), t['Taxa de FP'].map(num)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.3), sharey=True)
    for ax, valores, titulo, lim in [(a1, recall, 'Recall (ataques detectados)', 70),
                                     (a2, fp, 'Taxa de falso positivo (legítimos bloqueados)', 1.3)]:
        ax.barh(nomes[::-1], list(valores)[::-1], color=cores[::-1], height=0.55)
        for i, v in enumerate(list(valores)[::-1]):
            ax.text(v + lim * 0.015, i, f'{v:.2f}%'.replace('.', ','), va='center', fontsize=9, color=TINTA)
        ax.set_xlim(0, lim)
        ax.set_title(titulo, fontsize=10.5)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:g}'.replace('.', ',')))
        grade(ax)
    fig.suptitle('O ganho de detecção e o custo em falso positivo', x=0.0, ha='left',
                 fontweight='bold', fontsize=12, color=TINTA, y=1.04)
    fonte(fig, 'avaliacao_hibrida.py (docs/medicoes/avaliacao_hibrida.md, §1). 32.808 requisições.')
    fig.savefig(SAIDA / 'fig2_configuracoes.png')
    plt.close(fig)


def fig3_complementaridade():
    t = tabela_md(MED / 'avaliacao_hibrida.md', 'Detectado por')
    rot = ['As duas camadas', 'Só a assinatura', 'Só o modelo', 'Nenhuma']
    pct = list(t['% dos ataques'].map(num))
    cores = [JUNTOS, REGRAS, MODELO, CINZA]
    fig, ax = plt.subplots(figsize=(9, 1.9))
    esq = 0
    for r, p, c in zip(rot, pct, cores):
        ax.barh([0], [p], left=esq, color=c, height=0.5, edgecolor='white', linewidth=2)
        if p >= 5:
            ax.text(esq + p / 2, 0, f'{r}\n{p:.1f}%'.replace('.', ','), ha='center', va='center',
                    fontsize=9, color='white', fontweight='bold')
        else:
            ax.annotate(f'{r}: {p:.1f}%'.replace('.', ','), (esq + p / 2, 0.25), (esq + p / 2, 0.62),
                        ha='center', fontsize=8.5, color=TINTA2,
                        arrowprops=dict(arrowstyle='-', color=TINTA2, lw=0.8))
        esq += p
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.4, 0.8)
    ax.axis('off')
    ax.set_title('Quem detectou cada um dos 14.188 ataques', pad=14)
    fonte(fig, 'avaliacao_hibrida.py (docs/medicoes/avaliacao_hibrida.md, §2).')
    fig.savefig(SAIDA / 'fig3_complementaridade.png')
    plt.close(fig)


def fig4_curva_limiar():
    c = pd.read_csv(MED / 'curva_limiar.csv')
    c = c[c['taxa_fp'] <= 0.10]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(c['taxa_fp'] * 100, c['recall'] * 100, color=MODELO, linewidth=2)
    ax.axvline(1, color=TINTA2, linewidth=1, linestyle='--')
    ax.text(1.12, 30, 'alvo: no máximo\n1% de falso positivo', fontsize=8.5, color=TINTA2)
    esc = c.iloc[(c['limiar'] - 0.65).abs().argmin()]
    ax.scatter([esc['taxa_fp'] * 100], [esc['recall'] * 100], s=60, color=MODELO,
               edgecolor='white', linewidth=2, zorder=3)
    ax.annotate(f"limiar 0,65\nFP {esc['taxa_fp']*100:.2f}% · recall {esc['recall']*100:.1f}%".replace('.', ','),
                (esc['taxa_fp'] * 100, esc['recall'] * 100), (3.2, esc['recall'] * 100 - 14),
                fontsize=9, color=TINTA, arrowprops=dict(arrowstyle='-', color=TINTA2, lw=0.8))
    ax.set_xlabel('Taxa de falso positivo (%)')
    ax.set_ylabel('Recall (%)')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    ax.set_title('O que o limiar troca: falso positivo × recall (só o modelo)')
    grade(ax, 'both')
    fonte(fig, 'treino_modelo.py (docs/medicoes/curva_limiar.csv). Probabilidades out-of-fold.')
    fig.savefig(SAIDA / 'fig4_curva_limiar.png')
    plt.close(fig)


def fig5_algoritmos():
    t1 = tabela_md(MED / 'comparacao_modelos.md', 'Algoritmo | F1 (0,5)')
    t2 = tabela_md(MED / 'comparacao_modelos.md', 'Algoritmo | Limiar')
    nomes = ['Random Forest', 'Regressão logística', 'Árvore de decisão']
    f1 = t1['F1 (0,5)'].map(lambda s: float(s.split('±')[0]))
    dp = t1['F1 (0,5)'].map(lambda s: float(s.split('±')[1]))
    rec = t2['Recall'].map(num)
    fp = t2['Taxa de FP'].map(num)
    cores = [MODELO, CINZA, CINZA]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.3), sharey=True)
    a1.barh(nomes[::-1], list(f1)[::-1], xerr=list(dp)[::-1], color=cores[::-1], height=0.55,
            error_kw=dict(ecolor=TINTA2, lw=1, capsize=3))
    for i, (v, d) in enumerate(zip(list(f1)[::-1], list(dp)[::-1])):
        a1.text(v + d + 0.02, i, f'{v:.3f}'.replace('.', ','), va='center', fontsize=9, color=TINTA)
    a1.set_xlim(0, 1)
    a1.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:.1f}'.replace('.', ',')))
    a1.set_title('F1 médio nos 5 folds (± desvio)', fontsize=10.5)
    for i, (n, r, f) in enumerate(zip(nomes[::-1], list(rec)[::-1], list(fp)[::-1])):
        if f > 1.05:
            a2.text(1, i, f'não opera com FP ≤ 1%\n(mínimo: {18.17:.2f}%)'.replace('.', ','),
                    va='center', fontsize=8.5, color=TINTA2)
        else:
            a2.barh([n], [r], color=cores[::-1][i], height=0.55)
            a2.text(r + 1, i, f'{r:.1f}%'.replace('.', ','), va='center', fontsize=9, color=TINTA)
    a2.set_xlim(0, 70)
    a2.set_title('Recall com no máximo 1% de falso positivo', fontsize=10.5)
    for ax in (a1, a2):
        grade(ax)
    fig.suptitle('Comparação entre algoritmos, nas mesmas condições', x=0.0, ha='left',
                 fontweight='bold', fontsize=12, color=TINTA, y=1.04)
    fonte(fig, 'comparar_modelos.py (docs/medicoes/comparacao_modelos.md). Mesmos folds, features e critério de limiar.')
    fig.savefig(SAIDA / 'fig5_algoritmos.png')
    plt.close(fig)


def fig6_latencia():
    t = tabela_md(MED / 'latencia.md', 'Etapa')
    t = t[~t['Etapa'].str.contains('Total')].iloc[:4]
    nomes = ['Normalização', 'Camada 1: assinaturas', 'Montagem das features', 'Inferência (Random Forest)']
    media, p95 = t['média'].map(num), t['p95'].map(num)
    fig, ax = plt.subplots(figsize=(8, 2.9))
    ax.barh(nomes[::-1], list(media)[::-1], color=MODELO, height=0.55)
    for i, (m, p) in enumerate(zip(list(media)[::-1], list(p95)[::-1])):
        ax.text(m + 0.12, i, f'{m:.2f} ms  (p95 {p:.2f})'.replace('.', ','), va='center', fontsize=9, color=TINTA)
    ax.set_xlim(0, 10)
    ax.set_xlabel('Tempo médio por requisição (ms)')
    ax.set_title('Onde o tempo é gasto — total até a decisão do modelo: 10,99 ms')
    grade(ax)
    fonte(fig, 'medir_latencia.py (docs/medicoes/latencia.md). 300 requisições do CSIC, uma por vez, n_jobs=1.')
    fig.savefig(SAIDA / 'fig6_latencia.png')
    plt.close(fig)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    for f in (fig1_recall_por_familia, fig2_configuracoes, fig3_complementaridade,
              fig4_curva_limiar, fig5_algoritmos, fig6_latencia):
        f()
        print('ok', f.__name__)
    print(f'Figuras em {SAIDA}')


if __name__ == '__main__':
    main()
