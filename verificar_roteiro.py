"""
==============================================================================
CONFERE O ROTEIRO DE DEMONSTRACAO CONTRA O BACKEND
==============================================================================
Roda todos os casos de frontend/src/lib/baterias.js contra o WAF e confere se
cada um se comporta como esta declarado: o status HTTP e a CAMADA que resolve.

Por que isso existe: na gravacao eu nao posso descobrir ao vivo que um caso
mudou de comportamento. Se eu mexo numa regra de assinatura, um payload da
Bateria 5 (que deveria passar pela camada 1 e ser pego pelo modelo) pode
comecar a bater numa assinatura -- e ai aquele caso deixa de provar o que eu
digo que ele prova.

Rodar ANTES de gravar, com o backend em pe:

    WAF_MODELO=demo python api.py        (num terminal)
    python verificar_roteiro.py          (noutro)
==============================================================================
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).resolve().parent
BATERIAS_JS = RAIZ / 'frontend' / 'src' / 'lib' / 'baterias.js'
BASE = 'http://127.0.0.1:8000'


def extrair_casos():
    """
    Le os casos direto do baterias.js.

    Uso regex em vez de manter uma copia dos payloads em Python de proposito: se
    houver duas listas, elas divergem, e eu descobriria a divergencia no pior
    momento possivel. A fonte da verdade e o arquivo que o painel consome.
    """
    texto = BATERIAS_JS.read_text(encoding='utf-8')

    baterias = []
    for m_bat in re.finditer(r"titulo:\s*'([^']+)'", texto):
        baterias.append((m_bat.start(), m_bat.group(1)))

    casos = []
    padrao = re.compile(
        r"rota:\s*'([^']+)',\s*"
        r"parametro:\s*'([^']+)',\s*"
        r"payload:\s*(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'),\s*"
        r"esperado:\s*(\d+),"
        r"(?:\s*camadaEsperada:\s*(null|'[a-z]+'),)?",
        re.S,
    )
    for m in padrao.finditer(texto):
        titulo = 'desconhecida'
        for pos, t in baterias:
            if pos < m.start():
                titulo = t
        bruto = m.group(3)
        payload = bruto[1:-1]
        # Desescapa o que o JS escapa dentro de literal de string.
        payload = payload.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')
        camada = m.group(5)
        casos.append({
            'bateria': titulo,
            'rota': m.group(1),
            'parametro': m.group(2),
            'payload': payload,
            'esperado': int(m.group(4)),
            'camada_esperada': None if camada in (None, 'null') else camada.strip("'"),
            'declara_camada': camada is not None,
        })
    return casos


def bater(caso):
    url = f"{BASE}{caso['rota']}?{caso['parametro']}=" + urllib.parse.quote(
        caso['payload'], safe='')
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except urllib.error.URLError as e:
        raise SystemExit(
            f"\n[ERRO] Nao consegui falar com o backend em {BASE}.\n"
            f"       Suba com:  WAF_MODELO=demo python api.py\n"
            f"       Detalhe: {e}\n")


def main():
    casos = extrair_casos()
    print(__doc__)
    print(f"{len(casos)} casos lidos de {BATERIAS_JS.relative_to(RAIZ)}\n")

    with urllib.request.urlopen(f'{BASE}/api/waf/info', timeout=10) as r:
        info = json.loads(r.read())
    print(f"Modelo carregado : {info['modelo']}  (limiar {info['limiar_decisao']})")
    print(f"Assinaturas      : {info['n_assinaturas']} regras")
    tag = 'DEMONSTRACAO' if 'demo' in info['modelo'] else 'CSIC 2010'
    print(f"Modo             : {tag}\n")
    if 'demo' not in info['modelo']:
        print("  AVISO: o roteiro foi calibrado para o modelo de DEMONSTRACAO.")
        print("         Suba com WAF_MODELO=demo antes de gravar.\n")

    print(f"{'':2}{'payload':<44}{'status':>14}{'camada':>26}")
    print('-' * 88)

    falhas = []
    bateria_atual = None
    for caso in casos:
        if caso['bateria'] != bateria_atual:
            bateria_atual = caso['bateria']
            print(f"\n{bateria_atual}")
        st, corpo = bater(caso)
        camada = corpo.get('camada')

        ok_status = st == caso['esperado']
        ok_camada = (not caso['declara_camada']) or (camada == caso['camada_esperada'])
        ok = ok_status and ok_camada

        txt_status = f"{st}" + ('' if ok_status else f" (esperava {caso['esperado']})")
        rotulo = {'assinatura': 'camada 1', 'modelo': 'camada 2', None: '—'}[camada]
        if caso['declara_camada'] and not ok_camada:
            esperado_rot = {'assinatura': 'camada 1', 'modelo': 'camada 2',
                            None: 'nenhuma'}[caso['camada_esperada']]
            rotulo += f" (esperava {esperado_rot})"
        if camada == 'assinatura':
            rotulo += f" {corpo.get('regra_id', '')}"
        elif camada == 'modelo':
            rotulo += f" p={corpo.get('probabilidade_ataque', 0):.2f}"

        marca = 'ok ' if ok else '!! '
        print(f"{marca:<4}{caso['payload'][:42]:<44}{txt_status:>13}{rotulo:>25}")
        if not ok:
            falhas.append((caso, st, camada))

    print('\n' + '=' * 88)
    if falhas:
        print(f"{len(falhas)} DE {len(casos)} CASOS DIVERGIRAM — nao grave ainda.\n")
        for caso, st, camada in falhas:
            print(f"  [{caso['bateria']}]")
            print(f"    payload : {caso['payload']!r}")
            print(f"    esperava: {caso['esperado']} / {caso['camada_esperada']}")
            print(f"    veio    : {st} / {camada}\n")
        sys.exit(1)
    print(f"TODOS OS {len(casos)} CASOS CONFORME O DECLARADO. Pode gravar.")
    print('=' * 88)


if __name__ == '__main__':
    main()
