"""
==============================================================================
TESTE DE FALSO POSITIVO EM TRAFEGO BENIGNO REALISTA
==============================================================================
Por que este script existe:

A metrica de falso positivo reportada no relatorio (0.23%) foi medida no
conjunto de teste dos datasets de SQLi. Nesses datasets, a classe "benigna" e
composta por CONSULTAS SQL LEGITIMAS (ex: "SELECT COUNT(thumb) FROM elephant").

Mas o WAF nao roda na camada de banco de dados. Ele roda na camada HTTP, onde o
trafego benigno real e outra coisa: termos de busca em linguagem natural, nomes,
e-mails, enderecos, precos, datas, IDs. O modelo praticamente nunca viu esse
tipo de string rotulada como 0 durante o treino.

Consequencia: a taxa de falso positivo de 0.23% descreve a tarefa
"distinguir SQL malicioso de SQL legitimo" — que NAO e a tarefa que o WAF
executa em producao. Este script mede a taxa na tarefa correta.

LIMITACAO DECLARADA: o corpus abaixo e sintetico e pequeno, construido por
categoria de trafego. Ele serve para EVIDENCIAR o problema, nao para ser a
metrica final da monografia. A metrica final vem da validacao cruzada sobre o
CSIC 2010, em model_trainer.py.

------------------------------------------------------------------------------
QUAL MODELO ESTE SCRIPT MEDE, E POR QUE ISSO IMPORTA
------------------------------------------------------------------------------
Rodar:  python false_positive_test.py            -> models/demo/  (padrao)
        python false_positive_test.py --csic     -> models/       (CSIC 2010)

O corpus aqui e em portugues. O modelo treinado no CSIC 2010 aprendeu o trafego
da loja "tienda1", que e em espanhol e tem parametros proprios (`precio`,
`cantidad`), entao portugues esta FORA da distribuicao que ele viu. Medi 97,4% de
falso positivo ao aponta-lo para este corpus.

Esse numero nao mede falso positivo: mede FALHA DE TRANSFERENCIA ENTRE DOMINIOS.
E um resultado legitimo e importante -- confirma que um WAF de ML aprende o
comportamento de UMA aplicacao e nao transfere para outra sem retreino, que e
justamente por que o CSIC distribui um conjunto de treino por aplicacao. Mas nao
e a taxa de falso positivo do sistema operando no dominio para o qual foi
treinado; essa e de 3,89% (limiar padrao) ou 0,97% (limiar calibrado), medida por
validacao cruzada no proprio CSIC.

Por padrao aponto para models/demo/, cujo treino inclui trafego benigno em
portugues, para que o numero medido seja falso positivo de verdade.
==============================================================================
"""

import sys

from extractor import carregar_artefatos, classificar

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Corpus de trafego benigno, agrupado pelas categorias que um WAF realmente ve.
# Inclui de proposito os casos-limite honestos: texto que MENCIONA SQL sem
# atacar, expressoes matematicas, e strings muito curtas.
TRAFEGO_BENIGNO = {
    'Busca em linguagem natural': [
        'tenis de corrida masculino', 'camisa polo azul tamanho M',
        'notebook dell inspiron 15 3000', 'como configurar roteador tp-link',
        'livro de machine learning em portugues', 'melhor cafeteira eletrica 2026',
    ],
    'Dados pessoais e cadastro': [
        'pedro.juliani@gmail.com', 'Joao da Silva', 'Dr. Andre Souza - cardiologista',
        'Rua das Flores, 120 - apto 43', 'CPF 123.456.789-00', '(11) 98765-4321',
    ],
    'Identificadores e numeros': [
        'usuario123', 'pedido #99381 status', '2026-07-28', 'R$ 1.299,90',
        '50% de desconto', 'SKU-4471-B',
    ],
    'Texto livre / comentarios': [
        '5 estrelas! Amei o produto, chegou rapido', 'ola, tudo bem?',
        'Preco: 100 - 50 = 50 reais', 'math: (2+3)*4 = 20', 'C++ e Python',
        'nota 10/10 -- recomendo', 'ler mais >>',
    ],
    'Mencoes legitimas a SQL (casos-limite)': [
        'Curso de SQL para iniciantes', 'aprenda SELECT e JOIN em SQL',
        'O que e uma query SELECT?', 'select um produto da lista',
        'update do sistema disponivel', 'delete a conta antiga',
        'relatorio de insert de dados', 'documentacao: DROP e irreversivel',
    ],
    'Strings curtas e degeneradas': [
        'a', '1', 'ok', '<3', 'joao&maria', '   ',
    ],
}


if __name__ == '__main__':
    print(__doc__)

    usar_csic = '--csic' in sys.argv
    pasta = 'models' if usar_csic else 'models/demo'
    modelo, vetorizador, metadata = carregar_artefatos(pasta)
    limiar = metadata.get('limiar_decisao', 0.5)

    print(f"Modelo: {pasta}/")
    print(f"Treinado em: {metadata.get('dataset', 'nao informado')}")
    print(f"Limiar de decisao: {limiar:.3f}")
    if usar_csic:
        print("AVISO: corpus em portugues contra modelo treinado em espanhol. O numero")
        print("resultante mede falha de transferencia entre dominios, nao falso positivo.")
    print()

    todos, total_fp = [], 0
    linhas_md = ['| Categoria | Amostras | Falsos Positivos | Taxa |',
                 '| :--- | ---: | ---: | ---: |']

    for categoria, textos in TRAFEGO_BENIGNO.items():
        resultados = [classificar(t.lower(), modelo, vetorizador, metadata) for t in textos]
        fp = sum(1 for bloqueado, _ in resultados if bloqueado)
        total_fp += fp
        todos.extend(textos)

        print(f"--- {categoria} ({fp}/{len(textos)} bloqueados) ---")
        for t, (bloqueado, prob) in zip(textos, resultados):
            marca = 'BLOQUEADO  ' if bloqueado else 'permitido  '
            print(f"  [{marca} p={prob:.2f}] {t!r}")
        print()
        linhas_md.append(f"| {categoria} | {len(textos)} | {fp} | {fp / len(textos):.1%} |")

    taxa = total_fp / len(todos)
    rotulo = ('FALHA DE TRANSFERENCIA ENTRE DOMINIOS' if usar_csic
              else 'TAXA DE FALSO POSITIVO')
    print(f"{'=' * 78}")
    print(f"{rotulo}: {total_fp}/{len(todos)} = {taxa:.1%}")
    print('=' * 78)

    linhas_md.append(f"| **TOTAL** | **{len(todos)}** | **{total_fp}** | **{taxa:.1%}** |")

    sufixo = '_csic' if usar_csic else ''
    destino = f'docs/medicoes/false_positive_test{sufixo}.md'
    with open(destino, 'w', encoding='utf-8') as f:
        f.write('# Falsos Positivos em Tráfego Benigno Realista\n\n')
        f.write(f'Gerado por `false_positive_test.py` contra `{pasta}/`.\n\n')
        f.write(f'- Dataset de treino: {metadata.get("dataset", "não informado")}\n')
        f.write(f'- Limiar de decisão: {limiar:.3f}\n\n')
        if usar_csic:
            f.write('> **Atenção.** Corpus em português contra modelo treinado em '
                    'espanhol (CSIC/tienda1). O número abaixo mede falha de '
                    'transferência entre domínios, **não** falso positivo. A taxa de '
                    'falso positivo do modelo no seu próprio domínio é de 3,89% '
                    '(limiar padrão) ou 0,97% (limiar calibrado).\n\n')
        f.write('Corpus sintético agrupado por categoria de tráfego HTTP real. '
                'Ver limitação declarada no cabeçalho do script.\n\n')
        f.write('\n'.join(linhas_md) + '\n\n')
        f.write(f'Taxa medida: **{taxa:.1%}**.\n')
    print(f"\n[OK] Relatório exportado para {destino}")
