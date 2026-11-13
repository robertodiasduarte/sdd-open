# BRAINSTORM: Baixar NFS-e

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | BAIXAR_NFSE |
| Date | 2026-11-06 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "deixar prontos BRAINSTORM, DEFINE e DESIGN de um exemplo didático para alunos — extensão Chrome (MV3, HTML/JS puro, sem backend, zero biblioteca externa) que baixa os XML de NFS-e do Ambiente Nacional pela API oficial `adn.nfse.gov.br/contribuintes/DFe/{nsu}?lote=true&cnpjConsulta=…` usando o certificado digital já instalado no Chrome, para UMA empresa por vez, gravando em pastas Ano/Mês/(Emitidas|Recebidas|Eventos) com resumo na tela. O aluno roda o /build (sdd-build) no repositório dele." Durante a sessão: "quero a pagina didatica com o passo a passo".

**Context Gathered:**

Fornecido pelo mantenedor do exemplo:
- O exemplo responde à pergunta "que aplicação dá para fazer com o sdd-starter?": o aluno recebe os três documentos prontos e roda o `/build` no repositório dele.
- Uma página comum de site não resolve: o navegador bloqueia a chamada para outro domínio, e nenhum site usa o certificado do usuário nessas chamadas. Uma extensão resolve, porque tem permissão para o domínio e o Chrome apresenta o certificado na conexão.
- O exemplo existe para ensinar três lições: o cursor só avança com gravação confirmada; falha nunca aparece como sucesso; privacidade por desenho.

Lido do código de uma extensão do mercado, **ainda não confirmado contra respostas reais do ADN**:
- **Chamada:** `GET https://adn.nfse.gov.br/contribuintes/DFe/{nsu}?lote=true&cnpjConsulta={14 dígitos}`, exigindo `cache: 'no-store'`, porque o Chrome pode servir o lote de outro certificado. Para uma filial: CNPJ da filial no parâmetro e certificado da matriz.
- **Certificado:** o Chrome escolhe uma vez por sessão do navegador; para trocar, é preciso fechar o Chrome inteiro. Se a chamada não abrir o seletor, abrir o endereço numa aba em segundo plano o força.
- **Resposta 200:** `{ StatusProcessamento, LoteDFe: [ { NSU, TipoDocumento, ChaveAcesso, ArquivoXml } ] }`, com `ArquivoXml` em gzip + base64 e `NSU` podendo vir como texto. Os lotes têm cerca de 50 documentos.
- **Sequência:** o ADN devolve NSU estritamente maior que o pedido, então a continuação é `DFe/{ultimoNSU}`, sem somar 1. Cada CNPJ tem sequência própria, compartilhada por notas e eventos.
- **Fim normal:** 404 com `E2220`, `StatusProcessamento` igual a `NENHUM_DOCUMENTO_LOCALIZADO`, ou lote vazio.
- **Erros definitivos:** 403 com `E2245` (certificado sem procuração) e `E2214` (certificado de transmissão inválido), no formato `{ StatusProcessamento: "REJEICAO", Erros: [{ Codigo, Descricao, Mensagem }] }`.
- **Erros transitórios:** 429, 502, 503, 504 e 200 com corpo HTML ou vazio (manutenção).
- **Chaves do XML:** `dCompet` (competência), `dhEvento`, `emit|prest` e `toma|tomador` com `CNPJ|CPF`; `TipoDocumento === 'EVENTO'` identifica eventos.

Observado em teste local com rede e disco simulados sobre uma ferramenta desse tipo: quando o cursor avança antes da gravação, parar o download ou uma falha ao gravar deixa notas puladas para sempre, enquanto a tela mostra sucesso. É esse defeito que a primeira lição combate.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | Documentos em `exemplos/baixar-nfse/`; a extensão nasce no repositório do aluno | O `/build` roda fora do sdd-starter |
| Relevant KB Domains | N/A | Os fatos da API ficam nos próprios documentos do kit |
| IaC Patterns | N/A | Sem backend e sem infraestrutura |

## Discovery Questions & Answers

Perguntas registradas em síntese; foram respondidas numa conversa anterior, no mesmo dia, antes da retomada na etapa de amostras.

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Quem usa a v1 e para quantas empresas? | Uma empresa por vez: CNPJ informado + certificado dela ou da matriz | Lista de empresas e procuração em lote ficam fora da v1 |
| 2 | Quais lições o exemplo precisa ensinar de propósito? | As três: cursor só avança com gravação confirmada; falha nunca vira sucesso; privacidade por desenho | Cada lição vira teste de aceitação e entrada do Verify Gate |
| 3 | Qual é a saída? | XML em pastas `Ano/Mês/(Emitidas\|Recebidas\|Eventos)` + resumo na tela | Zero biblioteca externa: sem planilha, sem PDF, sem ZIP |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | N/A | 0 | Decisão do mantenedor: a amostra é a extensão analisada, não XML real. Nenhum dado real de nota, CNPJ de cliente ou certificado entra no kit |
| Output examples | N/A | 0 | A estrutura de pastas foi definida nas decisões desta sessão |
| Ground truth | N/A | 0 | A confirmação virá do teste manual com certificado real, fora do kit |
| Related code | Material local do mantenedor, fora do git | 2 | Uma extensão do mercado com o mesmo propósito e um teste com rede e disco simulados. Serve para extrair fatos de interoperabilidade; nenhum trecho é copiado |

**How samples will be used:**
- Extrair como a API funciona e quais falhas importam, nada além disso.
- Os testes do aluno usam notas fictícias, escritas à mão com a estrutura esperada.
- O teste com rede e disco simulados serve de modelo para os testes de cursor.

## Approaches Explored

### Approach A: Painel + pasta escolhida — Recommended

**Description:** O painel lateral da extensão recebe o CNPJ e a pasta, busca os lotes com `fetch` e grava cada XML na pasta escolhida com File System Access (o recurso do Chrome para gravar numa pasta). O cursor fica em `chrome.storage.local`.

**Pros:**
- A gravação termina com uma confirmação clara (`close()`), e só depois o cursor avança.
- Grava em qualquer pasta do computador.
- Não pede permissão de downloads, o que reforça a lição de privacidade.

**Cons:**
- O Chrome pode pedir a permissão da pasta de novo.
- Não funciona em janela anônima.
- Falta confirmar se o seletor de pasta funciona bem dentro do painel lateral; se não funcionar, a tela passa para uma aba própria da extensão.

**Why Recommended:** É a abordagem que deixa as três lições mais fáceis de ver e testar.

### Approach B: Pasta Downloads do Chrome

**Description:** Cada XML é salvo em subpastas de Downloads com `chrome.downloads`. Substituiu a ideia inicial de popup + ZIP, porque o ZIP exigiria biblioteca externa e o popup fecha ao perder o foco, o que interromperia o download.

**Pros:**
- Não pede pasta e funciona sem seletor.

**Cons:**
- Mais uma permissão no manifesto.
- A confirmação de gravação é assíncrona e depende de esperar o evento de cada download.
- Centenas de itens no histórico de downloads, e só grava em Downloads.

### Approach C: Tudo em segundo plano

**Description:** O service worker (a parte da extensão sem tela) baixa os lotes, e a tela só mostra o progresso.

**Pros:**
- Separa rede e tela.

**Cons:**
- O seletor de pasta não existe em segundo plano, então a gravação volta para a tela.
- O Chrome pode encerrar esse processo durante o download.
- Mais peças para quem está começando depurar.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | Confirmada na conversa em 2026-11-06 |
| Reasoning | Confirmação clara de gravação antes de o cursor avançar, com o custo aceito de o Chrome às vezes pedir a pasta de novo |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Extensão Chrome MV3 | Única forma de chamar a API com o certificado instalado, sem guardar certificado em lugar nenhum | Página comum (bloqueada pelo navegador); backend com arquivo `.pfx` (custódia do certificado) |
| 2 | HTML/JS puro, zero biblioteca externa | É a stack do aluno | Node, npm, bundler, TypeScript, bibliotecas de planilha, PDF ou ZIP |
| 3 | Uma empresa por vez, com cursor separado por CNPJ | Cada CNPJ tem sequência própria, e o exemplo fica pequeno | Lista de empresas e procuração em lote |
| 4 | Cursor avança a cada documento gravado, em ordem crescente de NSU | Nunca passa de uma nota não gravada, e o Parar preserva o que já foi salvo | Avançar antes da gravação; avançar só no fim de cada lote |
| 5 | "Em dia" só com os sinais explícitos de fim da API; qualquer resposta desconhecida é falha | Falha nunca aparece como sucesso | Tratar o que não se reconhece como fim da caixa |
| 6 | Um único domínio no manifesto (`adn.nfse.gov.br`) e nenhuma chamada a terceiros | Privacidade por desenho: o certificado nunca é lido, e o CNPJ só vai para o ADN | Consulta de razão social em API de terceiros |
| 7 | Quarta pasta `Outros`, com contagem no resumo | Pode vir nota em que o CNPJ não é nem prestador nem tomador; sem lugar para ela, a nota se perderia em silêncio | Só as três pastas originais |
| 8 | Documento decodificado sem data legível vai para `Sem-data/`, com contagem no resumo | A nota é guardada mesmo sem Ano/Mês | Descartar ou parar por falta de data |
| 9 | Documento que não decodifica interrompe o download e mostra o NSU | Pular perderia uma nota em silêncio; o custo aceito é um documento corrompido bloquear os seguintes até alguém resolver | Pular; guardar o conteúdo bruto e seguir (adiado) |
| 10 | NSU no nome do arquivo; baixar de novo apenas regrava (refinada no Define: o nome também leva o CNPJ, e bytes diferentes são recusados) | Se tudo cair entre gravar e avançar o cursor, nada se perde nem duplica | Nome só com número da nota, que se repetiria entre documentos e eventos |
| 11 | Passo a passo do aluno no README do kit e numa página didática da plataforma, com especificação própria fora do kit | O aluno tem uma entrada guiada, e o `/build` dele não tenta construir a página | Só README no GitHub; página descrita no DEFINE do kit |
| 12 | Kit e página não citam a extensão analisada nem o fabricante | Os achados valem só para uma versão e, em material público, podem virar acusação contra uma empresa identificada | Estudo de caso nomeado |
| 13 | Amostra é a extensão analisada; os testes do aluno usam notas fictícias | Nenhum dado real entra no kit público | Trazer XML e lote reais para o repositório |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Página separada `baixar.html` | O painel lateral basta como tela única; volta só se o seletor de pasta não funcionar nele | Yes |
| Consulta por CPF | A v1 atende uma empresa por CNPJ | Yes |
| Estudo de caso da engenharia reversa | Não é preciso para construir a extensão | Yes |
| Lista de empresas, procuração em lote e pasta por empresa | A v1 é uma empresa por vez | Yes |
| Excel | Exigiria biblioteca externa; o resumo na tela basta | Yes |
| DANFSe/PDF | Exigiria biblioteca externa | Yes |
| Relatório HTML | O resumo na tela basta | Yes |
| Modo portal (`www.nfse.gov.br`) | Pediria um segundo domínio, e a API resolve o problema central | Yes |
| Consulta de razão social | Exigiria chamar terceiros, contra a lição de privacidade | No |
| Backup e importação de NSU | Não é necessário para baixar as notas | Yes |
| Janela anônima | File System Access não funciona nela | No |
| Certificado A3 com SafeSign | Limitação conhecida: a saída disponível rebaixa o TLS de toda a navegação, então não será apresentada como solução | N/A |
| Guardar o conteúdo bruto de documento corrompido e seguir | Adiado em favor de parar e mostrar o NSU | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Peças da extensão, página didática e limites | Yes | Aprovado, com a pasta `Outros`, a regra de acesso da página e a decisão de não citar a extensão analisada | Yes |
| Caminho da nota, falhas na tela e provas | Yes | Aprovado, com cursor por documento e parada em documento que não decodifica | Yes |

## Suggested Requirements for /define

### Problem Statement (Draft)

Contador ou empresa precisa dos XML das NFS-e nacionais, emitidas e recebidas, numa pasta local, sem captcha e sem entregar o certificado a terceiros; ferramentas desse tipo podem perder notas em falhas e enviar dados a servidores próprios.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Aluno do sdd-starter, em geral contador, baixando as notas de uma empresa com o certificado dela ou da matriz | Precisa de uma ferramenta em que confie e que consiga construir e conferir, em vez de só acreditar numa tela de sucesso |

### Success Criteria (Draft)

- [ ] Download incremental: a segunda execução continua do cursor e não repete o que já foi concluído.
- [ ] Com falha simulada ao gravar um documento, o cursor fica no anterior, a tela mostra "Falhou" com o NSU e o motivo, e a execução seguinte baixa o documento de novo.
- [ ] Ao clicar em Parar, o cursor fica no último documento gravado e a tela mostra "Interrompido".
- [ ] Falha transitória esgotada, timeout, `E2245`, `E2214`, certificado não apresentado e resposta desconhecida mostram falha com motivo, nunca "Em dia".
- [ ] 404 com `E2220`, `NENHUM_DOCUMENTO_LOCALIZADO` ou lote vazio mostram "Em dia".
- [ ] O manifesto tem exatamente um domínio em `host_permissions`, e nenhuma chamada sai para fora de `adn.nfse.gov.br`.
- [ ] O XML gravado é byte a byte igual ao decodificado.
- [ ] O texto vindo do XML aparece na tela só como texto (`textContent`), nunca como HTML.
- [ ] TBD: metas de tempo e volume não foram definidas nesta sessão.

### Constraints Identified

- HTML/JS puro, sem Node, npm, bundler ou TypeScript, e zero biblioteca externa.
- Chrome MV3, versão 120 ou superior (`DecompressionStream` e File System Access).
- Sem backend; o certificado nunca é lido nem guardado.
- Permissões mínimas, com um único domínio em `host_permissions`.
- Nomes de arquivo seguros. Refinado no Define: o nome é só CNPJ e NSU, o que já evita caracteres inválidos.
- Nenhum dado real de nota, CNPJ de cliente ou certificado no kit.
- Dependência: certificado instalado no Chrome e ADN disponível.
- Lacuna: os fatos da API foram lidos de código, não de respostas reais; a confirmação depende do teste manual com certificado.
- Lacuna: o funcionamento do seletor de pasta no painel lateral ainda precisa ser confirmado.

### Out of Scope (Confirmed)

- Página didática da plataforma: faz parte do mesmo trabalho, mas tem especificação própria fora deste kit, e o `/build` do aluno não a constrói.
- Consulta por CPF.
- Lista de empresas, procuração em lote e pasta por empresa.
- Excel, DANFSe/PDF e relatório HTML.
- Modo portal (`www.nfse.gov.br`) e consulta de razão social.
- Backup e importação de NSU.
- Janela anônima e certificado A3 com SafeSign.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 3 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 13 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
