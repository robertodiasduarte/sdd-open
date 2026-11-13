# GOVERNANÇA: BAIXAR_NFSE

| Feature | Data | Padrão do projeto | DEFINE |
|---|---|---|---|
| BAIXAR_NFSE | 2026-11-06 | uso = só eu · multi_cnpj = sim · IA grava sozinha = não · guarda = até a prescrição (todos inferidos do DEFINE, sem confirmação) | exemplos/baixar-nfse/DEFINE_BAIXAR_NFSE.md (versão com SHA-256 iniciado em `3b651a6d3810`) |

**Gatilhos encontrados:** nota fiscal (linhas 3 e 19; AT-008 a AT-012) · CNPJ (AT-001 a AT-003, AT-006, AT-009 a AT-011, AT-305) · dado pessoal (CPF: linha 147 como consulta fora de escopo; o XML gravado pode trazer CPF, conforme a linha 33 do Brainstorm).

**Cobertura:** 20 itens: 0 já cobertos · 4 lacunas · 13 N.A. · 3 na 2ª camada

**Como ler esta execução:** a revisão foi feita por um revisor que não escreveu o DEFINE, sem profissional disponível para responder. O padrão do projeto é proposta inferida. As decisões foram tomadas pelo agente do fluxo, sob a autorização do mantenedor para seguir sem paradas, e o mantenedor pode revê-las. O DEFINE citado é a versão 1.0, então os números de linha se referem a ela. Nenhuma lacuna tem prova por script, porque não há banco: tudo se prova pelo roteiro, na página de testes da extensão, com disco e rede simulados e notas fictícias.

**Leitura do zero em "já cobertos":** o DEFINE é forte no que ele se propõe (fidelidade dos bytes, cursor, falha que não vira sucesso, custódia do certificado). O zero reflete o rigor do item: cobertura parcial conta como lacuna ou 2ª camada, com a parte que falta.

**Ordem sugerida, se o exemplo precisar ficar menor:** G08 e G10 evitam perda silenciosa de documento; G13 evita mistura entre empresas; G04 só documenta e é o primeiro a adiar.

## Lacunas

### G04 — Trilha de auditoria do negócio · severidade alta

**O que muda no app:** cada execução e cada "Recomeçar do início" acrescentam uma linha a um registro na pasta escolhida; hoje o resumo some quando o painel fecha, e voltar o cursor não deixa rastro.

**Por quê:** a extensão não muda dado contábil, mas muda o que controla a guarda da cópia fiscal: o cursor e o conteúdo da pasta. Sem registro, ninguém responde depois em que data aquela pasta foi baixada, até qual NSU, com qual resultado, nem se o cursor foi voltado e por quê. O item não cabe inteiro aqui, e o limite precisa ficar dito: não há login e o certificado não é lido, então o "quem" e o "de onde" ficam de fora; e, numa pasta do próprio usuário, a extensão não impede edição externa, então o "INSERT direto falha" do catálogo não tem equivalente. Fechar o painel no meio da execução também não deixa linha (linha 120); a execução seguinte mostra o salto no "cursor antes". O registro fica na pasta, não no armazenamento da extensão, e por isso não contraria AT-305. **Base legal:** o catálogo não aponta base legal para este item — o fundamento técnico vale por si.

**Requisito (EARS):** **If** uma execução termina, ou o aluno confirma "Recomeçar do início", e a linha correspondente não pode ser acrescentada ao registro da pasta (data e hora em UTC, CNPJ consultado, cursor antes e depois, estado final, totais e, no Recomeçar, o motivo), **then** a extensão **shall** mostrar "Falhou", nunca "Em dia", e, no Recomeçar, **shall** manter o cursor. **If** o registro já tem linhas, **then** a extensão **shall** apenas acrescentar, sem reescrever nem apagar linha anterior.

**Como provar:**
1. Rode uma execução com notas fictícias: o registro ganha 1 linha com data e hora em UTC, CNPJ, cursor antes e depois, estado final e totais.
2. Rode de novo: a 1ª linha continua igual e entra uma 2ª.
3. Confirme "Recomeçar do início" sem motivo: é recusado, o cursor fica e não entra linha. Com motivo: entra 1 linha com o motivo e o cursor vai a 0.
4. Simule falha ao acrescentar a linha numa execução sem pendência: a tela mostra "Falhou", nunca "Em dia".
5. Simule a mesma falha no Recomeçar: o cursor continua onde estava.

**Decisão:** **adiar**. O revisor recomendou aplicar em forma reduzida e indicou este item como o primeiro a adiar. O exemplo não muda dado contábil, e o registro não evita perda de nota: o foco didático fica nas três lições.

### G08 — Documento-fonte imutável · severidade alta

**O que muda no app:** uma nota já gravada deixa de ser sobrescrita por conteúdo diferente: se o arquivo existe e os bytes divergem, o download para em "Falhou" e o original fica intacto; e cada XML gravado deixa o seu SHA-256 registrado.

**Por quê:** o XML é o documento-fonte de quem vai escriturar depois. AT-013 garante a fidelidade na hora de gravar, mas AT-106 manda regravar sem comparar: depois de um "Recomeçar", ou de uma colisão de nome (ver G10), a cópia é trocada em silêncio, e a tela segue normal. Sem hash, também não há como mostrar que o arquivo de hoje é o que foi recebido. O limite: a extensão recusa a própria sobrescrita e deixa evidência, mas não impede alteração feita fora dela. O vínculo "lançamento aponta para a origem" não se aplica, porque aqui não há lançamento. Pontos para o Design conferir: o hash sai da função nativa do navegador, sem biblioteca, e o disco simulado precisa imitar a gravação atômica, porque uma parada que deixasse arquivo parcial viraria "bytes diferentes" e travaria a execução seguinte, contra o segundo critério de sucesso. O custo é o mesmo já aceito na decisão 9 do Brainstorm: um conflito bloqueia os documentos seguintes até alguém resolver. **Base legal:** o catálogo não aponta base legal para este item — o fundamento técnico vale por si.

**Requisito (EARS):** **If** a extensão vai gravar um documento num caminho onde já existe arquivo com bytes diferentes, **then** a extensão **shall** recusar a gravação, manter o arquivo existente intacto, manter o cursor no documento anterior e mostrar "Falhou" com o NSU e o caminho. **If** o SHA-256 dos bytes gravados não pode ser registrado, **then** a extensão **shall** não avançar o cursor e **shall** mostrar "Falhou".

**Como provar:**
1. Grave a nota fictícia de NSU 10: o arquivo existe e o SHA-256 registrado confere com os bytes gravados.
2. Baixe de novo a mesma nota, com os mesmos bytes: a contagem de arquivos não muda e a execução segue.
3. Troque a resposta simulada do NSU 10 por bytes diferentes e rode "Recomeçar do início": a extensão para em "Falhou" e mostra o NSU e o caminho.
4. Confira: o arquivo mantém os bytes originais e o cursor não passou do documento anterior.
5. Simule falha ao registrar o SHA-256: o cursor não avança e a tela mostra "Falhou".

**Decisão:** **aplicar a recusa de sobrescrita e adiar o SHA-256**, a redução sugerida pelo revisor. A extensão existe para guardar cópia fiel, e a recusa reforça as Lições 1 e 2. O registro de hash criaria mais um arquivo e mais um modo de falha num exemplo didático.

### G10 — Importação idempotente · severidade alta

**O que muda no app:** o nome do arquivo passa a ser definido no DEFINE, a partir do CNPJ consultado e do NSU: o mesmo documento nunca vira dois arquivos, e documentos diferentes nunca disputam o mesmo arquivo.

**Por quê:** para o mesmo CNPJ na mesma pasta, AT-106 e o último passo do Verify Gate já provam que rebaixar não duplica. O que falta é a chave natural. O DEFINE diz "o mesmo arquivo" sem dizer o que torna dois documentos o mesmo; o Brainstorm (decisão 10) só diz "NSU no nome do arquivo". Só que cada CNPJ tem sequência própria (linha 29 do Brainstorm): o mesmo NSU em dois CNPJs são documentos diferentes. Como a pasta é escolhida a cada abertura do painel e nada a liga a um CNPJ, um nome só com NSU faz a nota de uma empresa substituir a de outra em silêncio, e AT-106 aprova isso. O corte em 80 caracteres de AT-014 tem de preservar a chave: truncar nunca pode cortar CNPJ nem NSU. **Base legal:** o catálogo não aponta base legal para este item — o fundamento técnico vale por si.

**Requisito (EARS):** **If** chega um documento com CNPJ consultado e NSU já gravados, **then** a extensão **shall** não criar um segundo arquivo. **If** chega um documento com o mesmo NSU de outro CNPJ, **then** a extensão **shall** gravá-lo em arquivo próprio, sem tocar no existente; para isso, o nome do arquivo **shall** conter o CNPJ consultado e o NSU, inteiros.

**Como provar:**
1. Baixe 100 notas fictícias do CNPJ fictício A e anote a contagem de arquivos.
2. Rode "Recomeçar do início" com o mesmo CNPJ: a contagem não muda e nenhum nome novo aparece.
3. Gere o nome de arquivo do NSU 10 para o CNPJ fictício A e para o B: os nomes são diferentes e cada um contém o seu CNPJ e o NSU.
4. Direto na função de gravação (sem passar pela recusa de G13, se ela for aplicada), grave no disco simulado o NSU 10 de A e o NSU 10 de B, com conteúdos diferentes: ficam 2 arquivos, cada um com os seus bytes.
5. Gere o nome com NSU e `ChaveAcesso` longos: o resultado tem até 80 caracteres e mantém CNPJ e NSU inteiros.

**Decisão:** **aplicar**. Custa uma regra de nome e um teste, e fecha uma perda silenciosa que os testes aprovariam.

### G13 — Isolamento entre clientes · severidade alta

**O que muda no app:** a pasta passa a ser de um CNPJ só: pedir o download de outro CNPJ numa pasta já usada é recusado antes de qualquer chamada, e a tela pede outra pasta.

**Por quê:** é lacuna pela exceção do procedimento, com `multi_cnpj = sim`, e essa é uma inferência a confirmar. Não há segundo usuário, então o risco não é de acesso: é de mistura. AT-006 prevê dois CNPJs no mesmo navegador, a pasta é escolhida a cada abertura do painel (linha 124) e "pasta por empresa" está fora de escopo (linha 148). Nada impede juntar notas de duas empresas nas mesmas pastas `Ano/Mês`, e a pasta de um cliente pode acabar entregue a ele com nota de outro. O requisito não cria pasta por empresa, só recusa a mistura, e por isso não conflita com o fora de escopo. A marca que liga a pasta ao CNPJ tem de ficar na própria pasta, porque AT-305 não deixa guardar referência de pasta. Limites: quem apaga a marca perde a proteção (G10 segue evitando a substituição), e matriz e filial, por serem CNPJs diferentes, usam pastas diferentes. Na resposta da API, a contagem de `Outros` (AT-011) é o único sinal de documento alheio, porque o intermediário é caso legítimo e não dá para recusar por documento. **Base legal:** o catálogo não aponta base legal para este item — o fundamento técnico vale por si.

**Requisito (EARS):** **If** o aluno pede o download de um CNPJ numa pasta que já recebeu documentos de outro CNPJ, **then** a extensão **shall** recusar antes de qualquer chamada à API, manter os cursores e os arquivos como estão, mostrar os dois CNPJs e pedir outra pasta.

**Como provar:** o catálogo pede teste com 2 usuários; aqui, por só haver um, o teste usa 2 CNPJs fictícios.
1. Baixe as notas do CNPJ fictício A na pasta simulada: os arquivos ficam na pasta.
2. Peça o CNPJ fictício B na mesma pasta: é recusado e a mensagem cita os dois CNPJs.
3. Confira na rede simulada: nenhuma chamada foi feita para B.
4. Confira: o cursor de B e os arquivos de A não mudaram.
5. Controle: peça o CNPJ B numa pasta vazia: o download roda normalmente, o que prova que a recusa veio da regra.

**Decisão:** **adiar**. O revisor recomendou aplicar. Com AT-015 e AT-108, misturar empresas numa pasta não substitui nem perde nota, e o nome de cada arquivo traz o CNPJ. O risco restante é de organização, tratado por orientação na tela, sem marca na pasta nem regra adicional.

## Já coberto

| Item | Onde no DEFINE (linha ou AT) |
|---|---|
| Nenhum | Nenhum item está coberto por inteiro com teste da ação proibida. As coberturas parciais estão em G08 (AT-013), G10 (AT-106) e G16 (AT-304, AT-305) |

## N.A.

| Item | Motivo |
|---|---|
| G01 — Lançamento que não se apaga | A extensão não cria nem altera lançamento. A imutabilidade da cópia fiscal é tratada em G08 |
| G02 — Partidas dobradas no banco | Não há débito, crédito nem banco |
| G03 — Fechamento de período | Não há lançamento nem período a fechar; `dCompet` só escolhe a pasta |
| G05 — Log forense de segurança | N.A. por porte: uso = só eu |
| G06 — Prova de que o log não foi editado | N.A. por porte: uso = só eu |
| G07 — Segregação de funções | N.A. por porte: uso = só eu; também não há aprovação |
| G09 — Aritmética exata | A extensão não lê, soma nem arredonda valor monetário; só conta documentos |
| G11 — Regra com vigência e memória de cálculo | Não há regra fiscal nem cálculo: a classificação em pastas lê campos do XML e não produz resultado a reproduzir |
| G15 — Backup com restauração testada | N.A. por porte: uso = só eu |
| G17 — IA sugere, humano confirma | Sem IA em execução (linha 177) |
| G18 — Registro da decisão da IA | Sem IA em execução (linha 177) |
| G19 — Taxa de correção | Sem IA em execução (linha 177) |
| G20 — Responsabilidade técnica | Sem IA em execução (linha 177) |

## 2ª camada

| Item | Por que ficou para depois |
|---|---|
| G12 — Conciliação com totais de controle | Não obrigatório nesta feature. É o item de maior valor desta camada: AT-405 compara o total com o que a própria execução gravou, sem controle externo; e, como o cursor não está ligado à pasta, a tela diz "Em dia" para pasta vazia ou trocada (linhas 118 e 124). Parte aplicada: AT-201 agora mostra o último NSU e avisa onde estão os documentos anteriores. Um requisito futuro: conferir, por lote, documentos recebidos contra gravados e avisar quando a pasta não tem o que o cursor diz que já foi baixado |
| G14 — Retenção × proteção de dados | Não obrigatório nesta feature. A extensão não apaga nada, nem no "Recomeçar", e a guarda fica com quem tem a pasta. O DEFINE não fala de prazo, e o XML pode trazer CPF |
| G16 — Certificado digital e segredos | Não obrigatório nesta feature. A custódia está bem resolvida: a extensão nunca toca no certificado (AT-304, AT-305, linha 166). Faltam, para contar como coberto, um teste que procure certificado no repositório e o registro de uso, que hoje não existe porque quem apresenta o certificado é o navegador |

## Riscos aceitos

| Item | Quem | Quando | Por quê |
|---|---|---|---|
| G04, adiado | Agente do fluxo, sob autorização do mantenedor | 2026-11-06 | Sem registro por execução, não há rastro de quando a pasta foi baixada nem de um "Recomeçar". Aceito num exemplo didático de um usuário, que não altera lançamento |
| G08, SHA-256 adiado | Agente do fluxo, sob autorização do mantenedor | 2026-11-06 | Sem hash, não se prova depois que o arquivo é o recebido. A recusa de sobrescrita cobre a alteração feita pela própria extensão |
| G13, adiado | Agente do fluxo, sob autorização do mantenedor | 2026-11-06 | A mistura de empresas numa pasta continua possível, sem perda de nota. Orientação na tela |

## Aplicado no DEFINE

Versão do DEFINE depois da aplicação: 1.1.

| Lacuna | AT novo | AT reescrito | Clarity Score antes → depois |
|---|---|---|---|
| G08 | AT-108 | AT-106: mantém o arquivo quando os bytes são iguais | 14/15 → 14/15 |
| G10 | AT-015 | — | 14/15 → 14/15 |
| G12, parcial | — | AT-201: mostra o último NSU e avisa onde estão os anteriores. AT-402: conta "Já existiam" | 14/15 → 14/15 |

Com G08 e G10, a decisão 10 do Brainstorm foi refinada: o nome do arquivo leva CNPJ e NSU, e bytes diferentes são recusados. Depois desta revisão, o ensaio do build acrescentou AT-109 para arquivo de 0 byte, e a revisão adversarial tirou a `ChaveAcesso` do nome, de modo que o limite de 80 caracteres citado acima deixou de ser necessário.

---

> A skill recomenda; o profissional decide e responde.
>
> No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura (`information_schema`,
> `pg_policies`, `pg_trigger`) que o SQL criou o que estes itens exigem: os itens com `prova pós-build = sim`
> no catálogo têm o que conferir no banco depois de aplicada a migration.
