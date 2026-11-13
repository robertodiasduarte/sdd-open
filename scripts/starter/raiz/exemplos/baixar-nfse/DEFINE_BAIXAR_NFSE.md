# DEFINE: Baixar NFS-e

> Extensão Chrome em HTML/JS puro que baixa os XML de NFS-e de uma empresa pelo Ambiente Nacional, com o certificado já instalado no navegador, sem perder nota e sem declarar sucesso quando houve falha.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | BAIXAR_NFSE |
| **Date** | 2026-11-06 |
| **Author** | SDD Define by RDD |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Contador ou empresa precisa dos XML das NFS-e nacionais, emitidas e recebidas, numa pasta local, sem captcha e sem entregar o certificado a terceiros. Ferramentas desse tipo podem pular notas para sempre quando o controle de avanço anda antes da gravação, mostrar sucesso depois de uma falha e enviar dados a servidores próprios.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno do sdd-starter, em geral contador | Constrói a extensão com `/build` e baixa as notas de uma empresa com o certificado dela ou da matriz | Precisa de uma ferramenta que consiga construir e conferir, em vez de só acreditar numa tela de sucesso |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | Baixar de forma incremental os XML de um CNPJ pela API do Ambiente Nacional e gravá-los numa pasta escolhida pelo aluno, em `Ano/Mês/(Emitidas\|Recebidas\|Eventos\|Outros)` ou em `Sem-data/` |
| **MUST** | Lição 1: avançar o cursor (o marcador de até onde já baixou) somente depois da gravação confirmada de cada documento |
| **MUST** | Lição 2: nunca mostrar sucesso quando houve falha, parada ou resposta desconhecida |
| **MUST** | Lição 3: falar somente com `adn.nfse.gov.br`, sem ler nem guardar o certificado e sem enviar dado a terceiros |
| **MUST** | Oferecer uma página de testes dentro da extensão, sem instalar nada, que prova as três lições com rede e disco simulados e notas fictícias |
| **SHOULD** | Permitir recomeçar o download de um CNPJ do início, com confirmação |
| **SHOULD** | Mostrar o progresso durante o download |

---

## Success Criteria

- [ ] A página de testes termina com 100% dos testes aprovados, separados nos grupos Lição 1, Lição 2, Lição 3 e Geral.
- [ ] Nos cenários simulados de 100 notas fictícias com parada durante a gravação, falha ao gravar e queda no 2º lote, 0 nota fica sem gravar depois da execução seguinte.
- [ ] Em 100% dos cenários simulados de falha, a tela final é "Falhou" ou "Interrompido", nunca "Em dia".
- [ ] O manifesto tem exatamente 1 domínio em `host_permissions`, e 0 URL fora de `adn.nfse.gov.br` no código da extensão.
- [ ] Em 100% dos documentos simulados, o arquivo gravado é byte a byte igual ao XML decodificado.
- [ ] Em 100% dos cenários simulados com arquivo existente de bytes diferentes, o arquivo original fica intacto e a tela mostra "Falhou".
- [ ] No download real, numa pasta nova, o total gravado do resumo é igual à quantidade de XML na pasta.

---

## Acceptance Tests

Coluna Gate: "testes" é verificado na página de testes da extensão; "real" é verificado no download com certificado. Os dois caminhos entram no mesmo Verify Gate.

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o aluno informa um CNPJ válido, escolhe a pasta e clica em Baixar, a extensão **shall** pedir `https://adn.nfse.gov.br/contribuintes/DFe/{cursor}?lote=true&cnpjConsulta={cnpj}` com `cache: 'no-store'` e `credentials: 'include'` | manual-ux (testes) |
| AT-002 | Unwanted | **If** o CNPJ informado não tem 14 caracteres ou tem dígito verificador errado, **then** a extensão **shall** mostrar "CNPJ inválido" e não fazer nenhuma chamada | manual-ux (testes) |
| AT-003 | Event-driven | **When** o CNPJ informado tem pontuação, letras minúsculas ou letras do formato alfanumérico, a extensão **shall** normalizá-lo para 14 caracteres maiúsculos sem pontuação e validá-lo pelo cálculo do formato alfanumérico | manual-ux (testes) |
| AT-004 | Event-driven | **When** um CNPJ não tem cursor salvo, a extensão **shall** pedir o NSU 0 | manual-ux (testes) |
| AT-005 | Event-driven | **When** um lote termina de gravar, a extensão **shall** pedir o lote seguinte com o último NSU gravado, sem somar 1 | manual-ux (testes) |
| AT-006 | Event-driven | **When** o aluno usa dois CNPJs diferentes, a extensão **shall** manter um cursor separado para cada um | manual-ux (testes) |
| AT-007 | Event-driven | **When** o `ArquivoXml` vem em gzip + base64, a extensão **shall** gravar o XML descomprimido; **When** vem em base64 de texto puro, **shall** gravar esse texto | manual-ux (testes) |
| AT-008 | Event-driven | **When** o `TipoDocumento` é `EVENTO`, a extensão **shall** gravar o documento na pasta `Eventos` do mês de `dhEvento` ou, na falta dele, de `dhProc` | manual-ux (testes) |
| AT-009 | Event-driven | **When** o CNPJ de `emit` ou `prest` é o CNPJ consultado, a extensão **shall** gravar a nota na pasta `Emitidas` do mês de `dCompet` | manual-ux (testes) |
| AT-010 | Event-driven | **When** o CNPJ de `toma` ou `tomador` é o CNPJ consultado e o de `emit` ou `prest` não é, a extensão **shall** gravar a nota na pasta `Recebidas` do mês de `dCompet` | manual-ux (testes) |
| AT-011 | Event-driven | **When** o CNPJ consultado não aparece como prestador nem como tomador (por exemplo, quando é intermediário), a extensão **shall** gravar a nota na pasta `Outros` do mês de `dCompet` e contá-la no resumo | manual-ux (testes) |
| AT-012 | Unwanted | **If** o documento decodificado não tem data legível ou o XML está malformado, **then** a extensão **shall** gravar o conteúdo sem alteração em `Sem-data/` e contá-lo no resumo | manual-ux (testes) |
| AT-013 | Ubiquitous | A extensão **shall** gravar exatamente os bytes do XML decodificado, sem reformatar | manual-ux (testes) |
| AT-014 | Unwanted | **If** a `ChaveAcesso` contém caracteres inválidos em nome de arquivo ou tenta subir de pasta, **then** a extensão **shall** ignorá-la no nome e no caminho, porque o nome do arquivo é só `<CNPJ>_<NSU>.xml` | manual-ux (testes) |
| AT-015 | Ubiquitous | O nome do arquivo **shall** ser formado só pelo CNPJ consultado e pelo NSU, de modo que o mesmo documento use sempre o mesmo arquivo e o mesmo NSU em dois CNPJs nunca use o mesmo arquivo | manual-ux (testes) |
| AT-101 | Event-driven | **When** o Chrome confirma a gravação de um documento (`close()`), a extensão **shall** salvar o NSU dele como cursor antes de gravar o documento seguinte | manual-ux (testes) |
| AT-102 | Event-driven | **When** o lote vem fora de ordem ou com `NSU` em texto, a extensão **shall** gravar em ordem numérica crescente de NSU | manual-ux (testes) |
| AT-103 | Unwanted | **If** a gravação de um documento falha, **then** a extensão **shall** parar, manter o cursor no documento anterior e não gravar os seguintes | manual-ux (testes) |
| AT-104 | Event-driven | **When** a execução seguinte começa depois de uma falha, a extensão **shall** pedir a partir do cursor salvo e gravar o documento que tinha falhado | manual-ux (testes) |
| AT-105 | Event-driven | **When** o aluno clica em Parar, a extensão **shall** terminar o documento em andamento e não gravar os seguintes, com o cursor no último documento gravado | manual-ux (testes) |
| AT-106 | Event-driven | **When** um documento já gravado é baixado de novo com os mesmos bytes, a extensão **shall** manter o arquivo existente, sem criar cópia, avançar o cursor e contá-lo em "Já existiam" | manual-ux (testes) |
| AT-107 | Unwanted | **If** o `ArquivoXml` não decodifica nem como gzip nem como texto, **then** a extensão **shall** parar, manter o cursor no documento anterior e mostrar o NSU do documento | manual-ux (testes) |
| AT-108 | Unwanted | **If** já existe arquivo com bytes diferentes no caminho do documento, **then** a extensão **shall** recusar a gravação, manter o arquivo intacto, manter o cursor no documento anterior e mostrar "Falhou" com o NSU e o caminho | manual-ux (testes) |
| AT-109 | Unwanted | **If** o arquivo existente no caminho do documento tem 0 byte, **then** a extensão **shall** tratá-lo como resto de gravação interrompida e gravar o documento nele, sem acusar diferença | manual-ux (testes) |
| AT-201 | Event-driven | **When** a API responde 404 com `E2220`, `NENHUM_DOCUMENTO_LOCALIZADO` ou lote vazio, a extensão **shall** mostrar "Em dia" com o resumo da execução, o último NSU baixado e o aviso de que documentos anteriores estão na pasta usada naquela ocasião | manual-ux (testes) |
| AT-202 | Ubiquitous | A extensão **shall** mostrar "Em dia" somente no caso de AT-201 | manual-ux (testes) |
| AT-203 | Event-driven | **When** o aluno clica em Parar, a extensão **shall** mostrar "Interrompido" com o total gravado | manual-ux (testes) |
| AT-204 | Unwanted | **If** a resposta é 429, 502, 503, 504, timeout, erro de rede ou 200 com corpo HTML, vazio ou JSON inválido, **then** a extensão **shall** tentar de novo com espera crescente, até 5 tentativas | manual-ux (testes) |
| AT-205 | Unwanted | **If** as 5 tentativas se esgotam, **then** a extensão **shall** mostrar "Falhou" com o motivo e a orientação de rodar de novo, mantendo o cursor no último documento gravado | manual-ux (testes) |
| AT-206 | Unwanted | **If** a API responde `E2245`, **then** a extensão **shall** mostrar "Falhou" sem nova tentativa, explicar que o certificado não tem procuração e orientar a fechar o Chrome inteiro para trocar de certificado | manual-ux (testes) |
| AT-207 | Unwanted | **If** a API responde `E2214`, **then** a extensão **shall** mostrar "Falhou" sem nova tentativa e explicar que o certificado é inválido para a transmissão | manual-ux (testes) |
| AT-208 | Unwanted | **If** a resposta é um JSON sem os campos esperados, traz `REJEICAO` com outro código, combina um sinal de fim com documentos ou com outro erro, ou traz um NSU que não avança em relação ao cursor, **then** a extensão **shall** mostrar "Falhou" com o que recebeu, sem tratar como fim, mantendo o cursor no último documento gravado | manual-ux (testes) |
| AT-209 | Unwanted | **If** uma falha acontece depois de lotes já gravados, **then** a extensão **shall** mostrar "Falhou" com o total já gravado, e não uma mensagem de conclusão | manual-ux (testes) |
| AT-301 | Ubiquitous | O manifesto **shall** declarar somente `https://adn.nfse.gov.br/*` em `host_permissions`, somente `storage` e `sidePanel` em `permissions`, e nenhum `content_scripts` ou `externally_connectable` | manual-ux (testes) |
| AT-302 | Ubiquitous | O código da extensão fora da pasta de testes **shall** conter somente URLs de `adn.nfse.gov.br` e nenhum uso de `eval`, `new Function`, `innerHTML`, `importScripts`, `sendBeacon` ou `WebSocket` | manual-ux (testes) |
| AT-303 | Ubiquitous | A extensão **shall** chamar somente `adn.nfse.gov.br` em todos os cenários simulados | manual-ux (testes) |
| AT-304 | Ubiquitous | A extensão **shall** não oferecer campo de senha nem de arquivo de certificado, e **shall** deixar a escolha do certificado com o Chrome | manual-ux (testes) |
| AT-305 | Ubiquitous | O armazenamento da extensão **shall** guardar somente cursores por CNPJ, nunca o conteúdo de nota | manual-ux (testes) |
| AT-306 | Unwanted | **If** um texto da API ou do XML contém HTML, **then** a extensão **shall** mostrá-lo como texto, sem interpretá-lo | manual-ux (testes) |
| AT-307 | Ubiquitous | O manifesto **shall** declarar uma política de conteúdo (CSP) que só permite conexões com a própria extensão e com `https://adn.nfse.gov.br`, para o navegador bloquear qualquer outro destino | manual-ux (testes) |
| AT-401 | State-driven | **While** um download está em andamento, a extensão **shall** manter o botão Baixar desativado e o botão Parar ativo | manual-ux (testes) |
| AT-402 | Event-driven | **When** a execução termina, a extensão **shall** mostrar um único estado final e o total por `Emitidas`, `Recebidas`, `Eventos`, `Outros`, `Sem-data` e `Já existiam` | manual-ux (testes) |
| AT-403 | Unwanted | **If** o aluno não concede a permissão da pasta, **then** a extensão **shall** não fazer nenhuma chamada à API e pedir a pasta de novo | manual-ux (testes) |
| AT-404 | Event-driven | **When** o aluno confirma "Recomeçar do início", a extensão **shall** voltar para 0 o cursor do CNPJ que estava no campo no clique em Recomeçar; sem a confirmação, **shall** manter o cursor | manual-ux (testes) |
| AT-405 | Event-driven | **When** o aluno baixa as notas de uma empresa com o certificado dela ou da matriz, a extensão **shall** gravar os XML nas pastas e mostrar um total gravado igual à quantidade de XML numa pasta nova | manual-ux (real) |
| AT-406 | Event-driven | **When** uma chamada falha sem resposta do servidor e ainda não houve resposta desde que a tela foi aberta, a extensão **shall** abrir o endereço da API, sem o CNPJ, numa aba em segundo plano para o Chrome pedir o certificado, fechar essa aba e tentar de novo | manual-ux (testes e real) |
| AT-407 | Ubiquitous | A ligação real da tela (`sidepanel.js`) **shall** conseguir chamar o `fetch` do navegador, o que um teste comprova carregando essa ligação | manual-ux (testes) |
| AT-408 | State-driven | **While** a extensão espera uma nova tentativa, o lote seguinte ou a aba do certificado, um clique em Parar **shall** encerrar a espera em até 1 segundo e mostrar "Interrompido" | manual-ux (testes) |
| AT-409 | Unwanted | **If** já há um download em andamento em outra tela da extensão, **then** a extensão **shall** recusar iniciar outro, sem nenhuma chamada à API, e explicar o motivo | manual-ux (testes) |

---

## Clarifications

### Session 2026-11-06

O mantenedor autorizou seguir sem novas paradas. Os itens marcados como "proposta do agente" não vieram do Brainstorm e podem ser revistos na revisão externa.

- [x] (Done signal) Existe um comando que devolve 0 quando funciona? → Não nesta stack: sem Node, e o caminho do Chrome muda em cada sistema. Vale `manual-ux`, apoiado numa página de testes que roda dentro da extensão; integrado em Verify Gate
- [x] (Done signal) Como provar as três lições sem Node? → Com a página de testes em grupos por lição, usando rede e disco simulados e notas fictícias. Ela roda dentro da extensão para poder ler o manifesto e os próprios arquivos; integrado em Goals e AT-301, AT-302
- [x] (Data model) O cursor avança por lote ou por documento? → Por documento, conforme o Brainstorm; integrado em AT-101, AT-103 e AT-105
- [x] (Data model) CNPJ alfanumérico entra? → Sim, proposta do agente: empresas novas já podem ter esse formato, e aceitar só dígitos recusaria um CNPJ válido. A aceitação pelo ADN continua como hipótese em A-006; integrado em AT-003
- [x] (Scope) Como o aluno baixa tudo de novo depois de apagar a pasta? → Com "Recomeçar do início", com confirmação, proposta do agente: o cursor é por CNPJ e, sem isso, a tela diria "Em dia" para uma pasta vazia. Não é o backup de NSU, que continua fora; integrado em AT-404
- [x] (Edge cases) XML decodificado, mas malformado? → É tratado como sem data legível: grava em `Sem-data/` sem alterar, proposta do agente alinhada ao Brainstorm; integrado em AT-012
- [x] (Edge cases) O painel é fechado durante o download? → A execução para, o cursor fica no último documento gravado, e a execução seguinte continua dali. É consequência de AT-101 e não pede tela própria, proposta do agente
- [x] (NFRs) Há meta de tempo ou volume? → Nenhuma definida. O Brainstorm deixou TBD, e o exemplo não depende disso. O limite de tentativas (5) vem do comportamento observado na ferramenta analisada; integrado em AT-204
- [x] (Terminology) O que é "mês" da pasta? → Mês de `dCompet` para nota e de `dhEvento` ou `dhProc` para evento, lido do texto do XML, sem converter fuso; integrado em AT-008 a AT-011
- [x] (Integrations) O que a documentação oficial confirma? → O Manual dos Contribuintes do ADN v1.0, de 12/02/2026, confirma `GET /DFe/{NSU}`, o parâmetro de CNPJ de consulta com validação do CNPJ raiz do certificado e que o contribuinte pode figurar como emitente, tomador ou intermediário. Ele não detalha a resposta nem os códigos de erro, que continuam como hipótese em A-001 a A-004; integrado em Assumptions
- [x] (Data model) A extensão guarda a pasta escolhida? → Não, proposta do agente: o aluno escolhe a pasta a cada abertura do painel, o que evita guardar referência em banco local e tratar permissão vencida. O cursor continua por CNPJ; integrado em AT-305

Revisão de governança (`GOVERNANCA_REVIEW_BAIXAR_NFSE.md`, na pasta do exemplo no GitHub; o build não precisa dele), com decisões tomadas pelo agente sob a autorização do mantenedor para seguir sem paradas:

- [x] (Edge cases) G08: nota já gravada pode ser trocada em silêncio? → Não: recusar quando os bytes divergem. Registro de SHA-256 adiado; integrado em AT-106 e AT-108
- [x] (Data model) G10: o que identifica um arquivo? → CNPJ consultado e NSU, porque cada CNPJ tem sequência própria; integrado em AT-015
- [x] (UX flow) G12, parcial: "Em dia" engana quando a pasta foi trocada? → A tela mostra o último NSU e avisa onde estão os documentos anteriores. A conciliação fica para depois; integrado em AT-201
- [x] (Scope) G04 e G13: registro por execução e recusa de misturar CNPJs numa pasta? → Adiados, com o risco registrado no relatório: não evitam perda de nota depois de AT-015 e AT-108; integrado em Out of Scope

Ensaio do build com um agente sem contexto (achados medidos em Chromium):

- [x] (Edge cases) Arquivo de 0 byte: `getFileHandle` com criação já deixa um arquivo vazio antes de `close()`, e a recusa de bytes diferentes travaria o CNPJ depois de qualquer falha de gravação → 0 byte é tratado como ausente; integrado em AT-109
- [x] (Integrations) A ligação real não tinha teste, e o painel podia falhar em toda execução com a página de testes verde → teste que carrega `sidepanel.js`; integrado em AT-407
- [x] (UX flow) Parar durante uma espera demorava até 60 s → Parar encerra a espera; integrado em AT-408
- [x] (Terminology) "Sessão" tinha quatro leituras → vale "desde que a tela foi aberta", em memória, sem gravar nada; integrado em AT-406
- [x] (Edge cases) NSU com caractere inválido não chega a virar nome de arquivo, porque falha antes por AT-208 → AT-014 fica só para a `ChaveAcesso`
- [x] (Integrations) Aba do certificado com o CNPJ deixaria esse dado no histórico do Chrome → a aba abre o endereço sem o CNPJ; integrado em AT-406

Revisão adversarial externa (revisor, auditor e desempate de outros fornecedores):

- [x] (Integrations) `E2220` em qualquer status daria "Em dia" até num 503 → status transitório é avaliado antes de qualquer sinal de fim, e `E2220` só encerra em 404; integrado em Design, Pattern 6
- [x] (Edge cases) Painel e aba baixando juntos: a limpeza depois de uma falha podia apagar um arquivo confirmado pela outra tela, com o cursor já adiante → uma execução por vez, com trava do navegador; integrado em AT-409
- [x] (Data model) A `ChaveAcesso` é opcional e mudaria o nome do mesmo documento → o nome é só CNPJ e NSU; integrado em AT-014 e AT-015

Varredura das nove categorias: Scope, Data model, UX flow, Integrations, Edge cases, Constraints, Terminology e Done signal estão `Clear`. NFRs está `Partial` sem bloquear, porque não há meta de tempo ou volume.

---

## Verify Gate

```yaml
verify_gate:
  kind: manual-ux
  cmd: "N/A (manual-ux)"
  pass_when: "checklist signed"
  threshold: "—"
  manual_fallback: "Eu abri a página de testes da extensão e vi a Lição 1 (cursor só avança com gravação confirmada) com todos os testes aprovados. Eu abri a página de testes e vi a Lição 2 (falha nunca aparece como sucesso) com todos os testes aprovados. Eu abri a página de testes e vi a Lição 3 (privacidade por desenho) e o grupo Geral com todos os testes aprovados. Eu baixei numa pasta nova as notas de uma empresa com o certificado dela ou da matriz e vi os XML nas pastas Ano/Mês, com o total gravado do resumo igual à quantidade de XML que a busca do meu sistema achou na pasta. Eu rodei de novo e vi 'Em dia' sem arquivo novo, depois desliguei a internet, rodei mais uma vez e vi 'Falhou', nunca 'Em dia'."
```

---

## Out of Scope

- Página didática da plataforma: tem especificação própria fora deste kit, e o `/build` do aluno não a constrói.
- Publicação na Chrome Web Store: a extensão é carregada em modo desenvolvedor.
- Consulta por CPF.
- Lista de empresas, procuração em lote e pasta por empresa.
- Excel, DANFSe/PDF e relatório HTML.
- Modo portal (`www.nfse.gov.br`) e consulta de razão social.
- Backup e importação de NSU.
- Janela anônima e certificado A3 com SafeSign.
- Guardar o conteúdo bruto de documento que não decodifica para seguir adiante.
- Registro por execução na pasta, SHA-256 por arquivo e recusa de misturar CNPJs numa pasta: adiados na revisão de governança.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | HTML/JS puro: sem Node, npm, bundler ou TypeScript; zero biblioteca externa | Código carregado diretamente pelo Chrome, e testes abertos no navegador |
| Technical | Chrome MV3, versão 120 ou superior, com `DecompressionStream` e File System Access | Não funciona em janela anônima |
| Technical | Único domínio permitido: `adn.nfse.gov.br` | Sem consulta de razão social nem serviço de terceiros |
| Timeline | N/A | — |
| Resource | N/A | — |
| Other | Nenhum dado real de nota, CNPJ de cliente ou certificado no repositório | Os testes usam notas fictícias, e CNPJ de teste com dígito válido é calculado na hora, para não ser recusado pelo alarme de commit |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | Repositório do aluno, com a extensão carregada em `chrome://extensions` | Sem servidor; roda só no navegador do aluno |
| **KB Domains** | N/A | Os fatos da API estão no Brainstorm e nas hipóteses abaixo |
| **IaC Impact** | None | Sem recurso de infraestrutura |
| **LLM Prompts** | false | Download e classificação por regra, sem IA em execução |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O contrato da API (`lote=true`, `cnpjConsulta`, `LoteDFe`, `ArquivoXml` em gzip + base64) é o lido no código da ferramenta analisada; o manual oficial confirma só o método e a existência do parâmetro | Ajustar o módulo de rede; o download real do Verify Gate revela a diferença | no |
| A-002 | O ADN devolve NSU estritamente maior que o pedido, e 0 traz o início da caixa | Risco de pular ou repetir documento; AT-208 faz a extensão parar se o NSU não avançar | no |
| A-003 | 404 com `E2220`, `NENHUM_DOCUMENTO_LOCALIZADO` e lote vazio são os únicos sinais de fim | Outro sinal apareceria como "Falhou", nunca como falso sucesso | no |
| A-004 | Os erros `E2245` e `E2214` vêm em `Erros[]` com `Codigo`, `Descricao` e `Mensagem` | A mensagem cairia no caso desconhecido de AT-208, ainda como falha | no |
| A-005 | O seletor de pasta funciona dentro do painel lateral | O aluno abre a mesma tela numa aba da extensão, pelo link do próprio painel | no |
| A-006 | O ADN aceita CNPJ alfanumérico em `cnpjConsulta`, com o mesmo nome de parâmetro | A API recusaria, e a extensão mostraria "Falhou" com o motivo | no |
| A-007 | Abrir o endereço da API numa aba em segundo plano faz o Chrome mostrar o seletor de certificado | O seletor pode não aparecer e a aba fechar em 60 s; a tela orienta a abrir o endereço à mão. O download real revela | no |
| A-008 | O aluno tem um certificado instalado e uma empresa com notas | Sem isso, o build fica bloqueado no Verify Gate, com os itens de download real pendentes; as lições continuam provadas pela página de testes | yes |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Dor, usuário e impacto concretos |
| Users | 3 | Um único perfil, com a situação de uso definida |
| Goals | 3 | Três lições como MUST e cortes já feitos |
| Success | 2 | Critérios medidos nos testes e no download real, sem meta de tempo ou volume |
| Scope | 3 | Fora de escopo explícito e confirmado no Brainstorm |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-06 | SDD Define by RDD | Initial version |
| 1.1 | 2026-11-06 | SDD Define by RDD | Revisão de governança: AT-015, AT-108; AT-106, AT-201 e AT-402 reescritos |
| 1.2 | 2026-11-07 | SDD Define by RDD | Achados do ensaio do build: AT-109, AT-407, AT-408; AT-014, AT-204, AT-205, AT-208, AT-302, AT-405 e AT-406 reescritos |
| 1.3 | 2026-11-07 | SDD Define by RDD | Revisão adversarial: AT-409; AT-014 e AT-015 reescritos |
| 1.4 | 2026-11-07 | SDD Define by RDD | Segundo ensaio do build: AT-404 e AT-408 precisados |

---

## Next Step

Execute o **SDD Design by RDD**.
