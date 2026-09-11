---
name: sdd-build
description: Fase 3 do SDD Open — executa o manifest do DESIGN arquivo a arquivo com verificação incremental, trata o Verify Gate do DEFINE como bloqueante, exige evidência abrível para cada critério (nunca "deve funcionar"), recomenda review de segundo vendor e avaliação em contexto fresco, e grava sdd/reports/BUILD_REPORT_{FEATURE}.md. Use quando o DESIGN estiver pronto ou o usuário disser /sdd-build.
compatibility: Requer bash >= 3.2, git >= 2.20 e python3 (report-lint.py). Roda sdd/bin/verify-gate.sh como critério de parada.
license: MIT
metadata:
  author: RDD
  version: "2.0.0"
  fase: "3"
---

# sdd-build — Fase 3

> Abra a resposta com o banner: `🧠 BUILD (Fase 3)`.

Construir o que o DESIGN desenhou, e **provar** que atende ao que o DEFINE contratou. O
critério de parada é um comando: `sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md`. Sem
ele em `0` (ou `4` com recibo humano), o build não terminou.

## Entrada

`/sdd-build sdd/features/DESIGN_{FEATURE}.md [--mode ralph]`

## Processo

### 1. Contexto e landmines

Leia DESIGN, DEFINE, `AGENTS.md`, `sdd/config.yaml`. **Conte as camadas** do manifest usando
`layers:` do config (ex.: `api`, `ui`, `sql`): ≥2 camadas distintas ⇒ os passos 1.5 e 5d são
obrigatórios; 1 camada ⇒ registre `avaliador: N.A. (1 camada)` no relatório.

Repita a varredura de landmines por superfície (o manifest cresce no build):
`sdd/bin/playbook-lint.sh --grep "<termo>" sdd/playbook.md`. Registre **só os IDs** em
`## Landmines lidas no build` (`LM-nnn` + 1 linha + ✔ tratado / N.A.). Hit que o DESIGN não
listou vira tarefa **antes** do código.

### 1.5. Contrato de aceite negociado (≥2 camadas)

Antes de codar, alguém **que não viu esta conversa** revisa os ATs e o Verify Gate contra o
DESIGN e propõe ≤5 ajustes (classes: não-verificável · estado sem critério · gate não cobre
AT · aceite circular · efeito não observável). Ver `references/contexto-fresco.md` para o
brief. Negocie com o usuário (múltipla escolha, uma opção por proposta); toda proposta recebe
**ACEITA** (aplicada no DEFINE, `Revision History` atualizado, `verify-gate.sh --print` ainda
parseia) ou **RECUSADA (motivo)** — registradas em `## Contrato de aceite` do DESIGN. Nunca
silêncio. Se o DESIGN já tem contrato negociado após a última edição do DEFINE, pule.

### 2–3. Tarefas e ordem

Converta o manifest em lista de tarefas e ordene por dependência (imports, schemas
compartilhados). **A primeira tarefa é o gate**: se o Verify Gate aponta para um script que
ainda não existe, crie-o **já com todos os blocos, falhando** — só assim existe baseline
vermelho de verdade. Script ausente sai `3` (inconclusivo), não `2`, e um gate que nunca
ficou vermelho não prova nada.

### 3b. Modo de execução (recomendação → decisão do usuário)

| Sinal | Empurra para |
|---|---|
| poucos arquivos, acoplados (schemas/helpers compartilhados) | **default** (um autor lembra nomes e assinaturas) |
| muitos arquivos independentes, build longo, risco de perder o fio | **ralph** (contexto fresco por tarefa, commit atômico, retomável) |
| volume paralelizável fora de segurança e de prompts LLM | **briefs** (workers paralelos; experimental) |

Empate → default. Mesmo com recomendação óbvia, **pergunte**; com `--mode` explícito,
registre "modo fixado por flag". Detalhes em `references/modos-e-retry.md`.

### 4. Executar cada tarefa

Guidelines inegociáveis: suposição vira pergunta · simplicidade · mudança cirúrgica ·
critério antes do código · **evidência, não declaração**.

1. **Drift de prompt** (sempre): o arquivo cheira a prompt de produção (path `**/prompts/**`,
   parâmetro de system prompt do seu wrapper de LLM recebendo um **literal**, `messages.create`,
   `chat.completions`) e não está no inventário do DESIGN? **Pare** e pergunte: iterar o DESIGN,
   ou confirmar falso positivo e registrar em "Drift detectado". ⛔ Calibre o sinal pelo código
   real do projeto: se as chamadas passam por um wrapper próprio, procurar só pelas assinaturas
   do SDK deixa o gate **cego**. Exclua arquivos de teste, ou o gate vira lobo e é ignorado.
2. **Prompt no inventário:** compile o contrato do DESIGN (tom, saída, fallback, referências) e
   passe à skill `sdd-prompt-builder` (ou a que estiver em `prompts.builder_skill` do
   `sdd/config.yaml`); não reabra decisões de provedor/modelo. Sem skill disponível, **bloqueie
   o item** e peça decisão — nunca improvise o texto que vai para produção.
3. **Escrever** seguindo os Code Patterns. 4. **Verificar** (lint, tipos, teste do arquivo).
5. **Marcar** concluído.

**Escada de retry — correção é redispatch fresco, nunca reply:** 1ª falha → corrigir no
contexto (erro trivial). 2ª falha → **reexecutar do zero** a partir de um brief que leva SÓ o
critério que falhou (verbatim), o erro (verbatim) e a instrução "trate como tarefa nova; não
assuma que a tentativa anterior estava quase certa". 3ª falha → **parar** e reportar; nunca
contornar o critério.

### 5. Validação

**5a. Verify Gate (bloqueante):** `sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md`

| exit | Ação |
|---|---|
| `0` | verde — seguir |
| `2` | vermelho — **abortar**; corrigir código (ou iterar DESIGN/DEFINE se a premissa está errada) e rodar de novo |
| `3` | inconclusivo — **não** é verde: instale a ferramenta ou rode onde ela exista; registre |
| `4` | manual-ux — mostre o `manual_fallback` ao humano e **pare** até o recibo (quem, data, resultado) |
| `5` | clarificação pendente — **pare** e volte ao Define; não é vermelho de build |
| `64` | DEFINE sem gate válido — volte ao Define |

**5b. Checks do projeto:** `{{TEST_CMD}}`, `{{TYPECHECK_CMD}}`, `{{LINT_CMD}}` do config,
quando preenchidos. Slot vazio = pular **e dizer que pulou**.

**5c. Review adversarial pós-build (recomende; o usuário decide).** Sim quando o diff toca
segurança, rota pública, lógica sutil entre arquivos, ou o build rodou em ralph/briefs. Não em
fix trivial. **Commite antes** (trabalho commitado com arquivos untracked ao lado faz um
review de "não commitado" revisar o vazio). Contrato de resposta em
`sdd/templates/fragments/ADVISOR_CONSULT.md`; cada nota → APLICADA · REBATIDA_EVIDENCIA ·
REBATIDA_ESCOPO no Advisor Ledger do relatório. Vendor que não seguiu o formato **falhou**:
nunca leia como "zero achados". Review nunca substitui smoke real.

**5d. Avaliador de contexto fresco (bloqueante em ≥2 camadas).** Quem julga não é quem
constrói. Alguém sem esta conversa (agente novo, sessão nova, ou subagente onde o vendor
tiver) lê o DEFINE como contrato e **prova cada AT executando** — comando, chamada, clique
— nunca lendo o diff. O brief leva só: modo `veredito`, feature, caminhos do DEFINE e do
DESIGN, pasta do projeto, URL base e se há credenciais autorizadas. Persista o bloco
`<<<AVALIACAO … >>>` em `sdd/reviews/AVALIACAO_{F}_{YYYYMMDD-HHMM}.md`. `PASS` → seguir.
`NEEDS_WORK` → os achados são o brief do ciclo seguinte (fresco); máximo 2 ciclos, depois
`Status: Blocked`. Sem browser/sessão para superfície visual → `NAO_VERIFICADO`, nunca PASS.
Detalhes em `references/contexto-fresco.md`.

### 6. BUILD_REPORT

`sdd/reports/BUILD_REPORT_{FEATURE}.md`, do template. **Default-FAIL:** a tabela de ATs nasce
com todo AT `false`. `true` exige evidência abrível — `sdd/reports/evidence/{F}/AT-nnn.log`
(1ª linha `$ comando`, saída verbatim), `AVALIACAO_{F}_*.md`, ou `recibo: nome YYYY-MM-DD`
(só gate manual-ux). "Por raciocínio" e "deve funcionar" são negados. Valide:

```bash
python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_{FEATURE}.md   # exit 0 obrigatório
```

Seções obrigatórias: Seleção de modo · Contrato de aceite · Landmines lidas no build ·
Candidatos ao playbook (bloco literal `<<<CANDIDATO_PLAYBOOK … >>>` com `evidencia:`, ou
"nenhum candidato") · Verify Gate (exit + recibo se manual-ux) · Veredito do avaliador ·
Advisor Ledger (se houve review) · Drift detectado (mesmo que "nenhum").

## Quality Gate

```text
[ ] Camadas contadas; ≥2 ⇒ 1.5 e 5d rodaram · 1 ⇒ "avaliador: N.A." no relatório
[ ] Contrato de aceite: toda proposta ACEITA|RECUSADA (ou "já negociado" / N.A.)
[ ] Verify Gate exit 0 (ou 4 com recibo) — nunca 2, nem 3 sem resolução
[ ] Todos os arquivos do manifest criados; verificações passam; sem TODO no código
[ ] Todo AT `true` cita evidência válida; report-lint.py exit 0; sem bypass silencioso
[ ] Seleção de modo e reviews decididas com registro (SIM com ledger ou NÃO com motivo)
[ ] Drift registrado (mesmo zero) · candidatos ao playbook com evidência (ou "nenhum")
[ ] Resposta fechada com o resumo de etapa (fragments/RESUMO_ETAPA.md)
```

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-build`.

**Próximo passo:** `/sdd-release <o que liberar>` — a fase Release roda o Verify Gate de novo
antes de qualquer publicação.
