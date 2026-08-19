# TCC — reconstrução à mão

**Pedro Henrique Juliani**
Detecção de anomalias em aplicações web usando Machine Learning — WAF em duas camadas.

Este repositório é a reconstrução do zero, escrita à mão, do trabalho que está em
`C:\Dev\Tcc`. O objetivo não é chegar mais rápido ao mesmo resultado: é chegar ao mesmo
resultado **entendendo cada decisão**.

## Por onde começar

1. Leia o **[ROTEIRO.md](ROTEIRO.md)** inteiro, de ponta a ponta, antes de escrever
   qualquer linha. Uma leitura só, sem parar para implementar.
2. Comece pela **Etapa 0** — fundamentos de ML, sem computador.
3. Registre cada sessão no **[diario.md](diario.md)**.

## Regras

1. Todo número citado tem um script que o gerou. Se não sabe qual, não cita.
2. Nada de copiar e colar de `C:\Dev\Tcc`. Consulta só **depois** da própria tentativa.
3. Etapa só fecha quando passa no teste de propriedade (definido no ROTEIRO).

## O que já está aqui

```
datasets/
  CSIC2010/            HTTP DATASET CSIC 2010, arquivos brutos
    normalTrafficTraining.txt    tráfego legítimo, partição de treino
    normalTrafficTest.txt        tráfego legítimo, partição de teste
    anomalousTrafficTest.txt     tráfego anômalo
  SQL Injection/       payloads de SQLi rotulados (sqli.csv, sqliv2.csv, SQLiV3.csv)
  XSS/                 payloads de XSS rotulados (xss_dataset.csv)
docs/                  (vazio — a monografia e os relatórios vão nascer aqui)
models/                (vazio — os artefatos treinados vão nascer aqui)
```

## O que NÃO está aqui, de propósito

O `csic2010_processado.csv.gz` do repositório antigo **não foi copiado**. Ele é a *saída*
da Etapa 1 — o resultado do parser que você vai escrever. Tê-lo aqui seria começar pela
resposta.

Ele continua em `C:\Dev\Tcc\datasets\CSIC2010\`, e serve para uma coisa só: **conferir as
contagens** depois que o seu parser rodar. Só abra depois de ter o seu.

## Ambiente

```powershell
cd C:\Dev\tccNovo
python -m venv venv
.\venv\Scripts\Activate.ps1
git init
```

Instale as bibliotecas conforme a etapa pedir, e vá anotando em `requirements.txt` à
medida que precisar — não copie a lista pronta do projeto antigo. Saber por que cada
dependência está lá também é parte do trabalho.
