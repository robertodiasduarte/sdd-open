# DESIGN: F26 Documentos na main e marca do SDD Starter

> Como os documentos das frentes passam a viver na `main` sem chegar ao pacote, como a branch de documentos vira
> uma tag de arquivo, e como o gerador do starter põe "SDD Starter" nas skills geradas.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F26_DOCS_NA_MAIN |
| **Date** | 2026-11-17 |
| **Author** | design-agent (sessão do Roberto) |
| **DEFINE** | [DEFINE_F26_DOCS_NA_MAIN.md](./DEFINE_F26_DOCS_NA_MAIN.md) (revisão 1.3, corrigida por este DESIGN: Decision 3) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                       repositório sdd-open (main)
   ┌──────────────────────────────────────────────────────────────────────┐
   │ pacote (MANIFEST.txt)                  documentos (todo sdd/ fora do  │
   │ .agents/ bin/ scripts/ tests/ docs/    pacote: features handoffs      │
   │ sdd/{bin,templates,hooks,review,       reviews releases archive       │
   │      patterns,fixtures,playbook.md,    curadoria reports              │
   │      invariants.md,WORKFLOW_CONTRACTS, GOVERNANCA_PADRAO.md …)        │
   │      config.example.yaml}                                             │
   └───────────┬───────────────────────────────────────┬──────────────────┘
               │ .gitattributes: sdd/** export-ignore   │
               │ + "-export-ignore" (pasta E conteúdo)  │ sdd/bin/docs-varredura.sh
               │   de cada entrada do pacote            │ (gitleaks · e-mail real · certificado
               ▼  ── TRAVA 1 ──                         │  · CPF/CNPJ válido · evidência >256 KB;
   git archive HEAD ─┬─► tarball da Release            │  saída sem conteúdo) ── CI, a cada PR
                     ├─► gerar-starter.py ─► starter   │
                     └─► scripts/montar-pacote.sh ─► pasta do pacote
                                    │
                                    ▼  ── TRAVA 2 ──
                     publish-gate.sh (G1–G5) e "shell syntax"
                     sobre a PASTA DO PACOTE, nos 2 workflows
                     (gate, testes, testes-windows fatia 1)

   docs/incorporar-starter ──(lote da curadoria julga a fila)──► tag arquivo/docs-incorporar-starter
                │                                                      │
                └── scripts/docs-migracao.py --copiar ──► commit de migração na main
                    (igual · ajustado · fora, em sdd/reports/MIGRACAO_DOCS_F26.tsv)
                    --conferir (AT-005) · --pode-aposentar (AT-006)

   sdd-release (depois do push e da Release conferida)
     sdd/reports/evidence/<F>/bruto/ (fora do git) ── docs-varredura --pasta ──► gh release upload
                                                         evidencia-bruta-<F>.tar.gz

   gerar-starter.py: descrição "SDD Open"→"SDD Starter" (ou prefixo "SDD Starter — "),
                     linha `<skill> vX · SDD Starter · mês/ano · versão atual: <starter>`, teto 1.024
```

---

## Components

| Componente | Papel | Onde |
|---|---|---|
| Trava 1 | o pacote é uma lista de permissão dentro de `sdd/`: tudo fora, menos as entradas do pacote | `.gitattributes` |
| Montador do pacote | `git archive HEAD` extraído numa pasta; imprime o caminho | `scripts/montar-pacote.sh` (novo) |
| Trava 2 | os passos que leem a árvore leem a pasta do pacote | `.github/workflows/publish-gate.yml`, `release.yml` |
| Varredura dos documentos | regras do AT-004, modos repositório, `--pasta`, `--ref`, `--padrao` | `sdd/bin/docs-varredura.sh` + `sdd/bin/docs-varredura.py` (novos, no pacote) |
| Migração | copia, confere e diz se pode aposentar | `scripts/docs-migracao.py` (novo) |
| Passo do bruto | junta, varre, anexa e confere o anexo | `.agents/skills/sdd-release/scripts/anexar-bruto.sh` (novo) + `references/bruto.md` (novo) |
| Marca | descrição e linha de identificação das cópias geradas | `scripts/gerar-starter.py`, `scripts/starter/raiz/scripts/check-versions.py`, `scripts/starter/raiz/README.md` |
| Remoção a pedido | procedimento escrito | `CONTRIBUTING.md` |

---

## Key Decisions

### Decision 1: Trava 1 como lista de permissão dentro de `sdd/`

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** O prompt de abertura recomendava listar as pastas de documento no `.gitattributes`. As skills criam
mais pastas de documento do que as 7 de hoje (`sdd/contexto/`, `sdd/tests/governanca/`, `sdd/upgrade/`,
`sdd/kb/`), e esta frente já criou um arquivo solto (`sdd/GOVERNANCA_PADRAO.md`).

**Choice:** `sdd/** export-ignore` e, para cada entrada do pacote dentro de `sdd/` (as do `MANIFEST.txt`:
`bin`, `templates`, `hooks`, `review`, `patterns`, `fixtures`, `playbook.md`, `invariants.md`,
`WORKFLOW_CONTRACTS.yaml`, `config.example.yaml`), a linha `-export-ignore` da pasta **e** a do conteúdo
(`sdd/bin -export-ignore` e `sdd/bin/** -export-ignore`).

**Rationale:** documento novo fica fora do pacote sem ninguém lembrar dele. O erro oposto, uma entrada nova do
pacote sem a linha, reprova no G3 ("declared but missing"), e o teste do AT-002 cobre os dois.

**Alternatives Rejected:** 1. Lista das pastas de documento — rejeitada porque cada pasta nova de documento
derrubaria o CI até alguém acrescentar a linha. · 2. `export-ignore` só no conteúdo (`sdd/bin/**`) — **medido em
2026-11-17 (git 2.50.1): sem a linha da pasta, o `git archive` tira a pasta inteira, calado**; por isso as 2
linhas.

**Consequences:** o `.gitattributes` passa a ter 21 linhas a mais · o pacote fica fechado por padrão em `sdd/`.

### Decision 2: Trava 2 por um montador único, chamado pelos workflows

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** O publish-gate do CI roda sobre a pasta do checkout (`publish-gate.yml:35`, `release.yml:70`,
`:238`); com documentos na `main`, o G3 reprovaria cada um e o G2 reprovaria 136 deles. O passo "Shell syntax"
faz `find . -name '*.sh'` e acharia os 87 `.sh` de evidência.

**Choice:** `scripts/montar-pacote.sh [destino]` faz `git archive --format=tar HEAD | tar -x -C <destino>` (pasta
temporária quando sem destino) com `pipefail`, confere que o `MANIFEST.txt` chegou e só então imprime o caminho;
qualquer falha sai ≠ 0 sem imprimir caminho, e o workflow chama em 2 linhas (`P="$(…)"` e depois o gate), para o
exit do montador derrubar o passo (revisão D1, R10). Os passos que leem a árvore são exatamente 6, conferidos nos
workflows: `publish-gate.yml` gate (publish-gate e shell) e testes-windows (publish-gate); `release.yml` testes
(publish-gate e shell) e testes-windows (publish-gate); o testes-macos só roda os testes unitários (revisão D1, R5). Os 4 passos de publish-gate (`publish-gate.yml` gate e
testes-windows; `release.yml` testes e testes-windows) e os 2 passos "Shell syntax" passam a rodar sobre essa pasta.
O `publish-gate.sh` não muda. O passo "Skill integrity" lê `.agents/skills`, que é pacote: não muda.

**Rationale:** o Verify Gate local já faz isso (`git archive HEAD | tar -x`); o CI passa a conferir o mesmo objeto
que a Release publica. Um script só evita 4 cópias da mesma linha divergindo.

**Alternatives Rejected:** 1. Um modo `--pacote` dentro do `publish-gate.sh` — rejeitada porque o modo `port` da
`sdd-release` já roda sobre uma cópia, e o gate continuaria com 2 contratos de entrada. · 2. Afrouxar G2/G3 para
as pastas de documento — proibido pelo pedido de abertura.

**Consequences:** o publish-gate do CI deixa de ver documento, então a varredura própria (Decision 3) passa a ser a
única barreira deles · o CI ganha 1 `git archive` por job (segundos).

### Decision 3: A varredura dos documentos mora no pacote (`sdd/bin/`), não em `scripts/`

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** O DEFINE 1.2 pôs a varredura em `scripts/docs-varredura.sh` (só do mantenedor) e, no Out of Scope,
"varredura de documentos no projeto do aluno". Mas o passo do bruto (AT-011) é da `sdd-release`, que roda em
qualquer projeto, e precisa varrer o bruto antes de anexar; um script do pacote não pode chamar `scripts/`, que o
`init` não copia.

**Choice:** `sdd/bin/docs-varredura.sh` (entrada, gitleaks, uso) e `sdd/bin/docs-varredura.py` (regras e
saída). Modos: `[raiz]` (documentos do repositório: arquivos versionados sob `sdd/` que a trava 1 tira do pacote,
pelo `git check-attr export-ignore`), `--pasta <dir>` (todo arquivo da pasta: bruto antes do anexo, anexo baixado),
`--ref <ref>` (documentos de um commit ou tag, lidos por `git cat-file`), `--padrao <regex>` (regra extra: sai 1
enquanto achar). O DEFINE passa a 1.3: AT-004, AT-012, o `cmd` do Verify Gate e o Technical Context com o caminho
novo; o Out of Scope passa a dizer "o CI do projeto do aluno não ganha a varredura; o passo do bruto da
`sdd-release` a usa".

**Rationale:** uma implementação só das regras para o CI do Open, o bruto de qualquer projeto e a prova da remoção
(LM-005: dois leitores da mesma regra usam a mesma função).

**Alternatives Rejected:** 1. Duas varreduras (uma em `scripts/`, outra embutida no passo do bruto) — rejeitada
pela LM-005. · 2. O passo do bruto só no Open — rejeitada: o DEFINE o pôs na `sdd-release` para todo projeto.

**Consequences:** o script entra no `MANIFEST.txt` e é instalado pelo `init` (`bin` está em `SDD_ENTRADAS_PACOTE`) ·
sem gitleaks, a varredura sai 2 ("não conferido") e o bruto não é anexado.

### Decision 4: Regras da varredura e saída sem conteúdo

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** AT-004 (gitleaks, e-mail real, certificado, CPF/CNPJ válido, evidência > 256 KB; S17: nunca o
conteúdo). Medido nos 3.286 documentos: e-mails só de `example.*`, `example.invalid`, `exemplo.com`,
`exemplo.invalid`, o endereço SSH do git no GitHub, um endereço de teste no domínio `e.com` e 1 real; 1 CPF com
dígito válido.

**Choice:**
- gitleaks: `gitleaks detect --source <cópia> --no-git --redact --report-format json --report-path <tmp>`; a
  saída é lida do JSON (`File`, `StartLine`, `RuleID`), nunca do texto do gitleaks.
- e-mail: reprova fora de `example.com|org|net`, `*.example`, `*.invalid`, `*.test`, `*.localhost`, `exemplo.com`
  (exato, nunca `exemplo.*`: revisão D1, R9),
  `*.noreply.github.com`, `noreply@anthropic.com` e do endereço SSH `git@github.com`.
- certificado: `.pfx` e `.p12` por extensão; qualquer arquivo com `-----BEGIN [A-Z ]*PRIVATE KEY-----`.
- CPF/CNPJ: 11 ou 14 dígitos, com ou sem a pontuação canônica, com dígito verificador válido, sem dígitos todos
  iguais; dispensado pelo comentário `docs-varredura: aceito — <motivo>` (motivo não vazio) na linha ou na de cima;
  o aceite cobre só aquela linha (LM-023).
- tamanho: arquivo versionado sob `sdd/reports/evidence/` com mais de 262.144 bytes; **não** no modo `--pasta`
  (o bruto é grande por natureza e vai para o anexo: revisão D1, R1).
- `--padrao`: modo próprio, só a regra pedida e sem gitleaks; com `--ref`, varre **todos** os arquivos da ref, não
  só os documentos (a tag de arquivo guarda também o código velho: revisão D1, R4). O `--ref` usa o
  `.gitattributes` da árvore atual (o `git check-attr` sem `--source`), não o da ref.
- saída: `🔴 <caminho>:<linha> · <regra>` (uma por achado, até 50, com "e mais N"), `RESULTADO: VERDE|VERMELHO|
  NÃO CONFERIDO`, exit 0 · 1 · 2 (gitleaks ausente ou falhou) · 64 (uso). Nunca o trecho achado; o caminho sai com
  todo caractere não imprimível trocado por `?` (revisão D1, R11).

**Rationale:** o que a governança e a segurança aplicaram, com os casos medidos fora da regra; a saída sem conteúdo
não repete o dado no log público do CI e não deixa um documento forjar a linha de resultado.

**Alternatives Rejected:** 1. Aceitar `e.com` — rejeitada: é domínio real; o único arquivo fica fora da migração.
· 2. Aceite de CPF por arquivo de exceções — rejeitada: o comentário na linha mostra o motivo onde o número está.

**Consequences:** o arquivo com o endereço de teste (`F14_DRIVE/AVAL2-21-agents-tmpl-e-gh-ausente.log`) fica só na tag · a
ficha `HANDOFF_INCORPORAR_STARTER.md` ganha 1 comentário de aceite (categoria "ajustado").

### Decision 5: Migração por lista, em 3 categorias, com conferência arquivo a arquivo

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** Decisões 1 e 2 do Roberto: estado atual, num commit, depois do lote; bruto e > 256 KB só na tag.
Medido: 5 classes de bruto em `sdd/reports/evidence` (392 arquivos, 5,1 MB de 14,9 MB) e 1 arquivo > 256 KB fora
delas.

**Choice:** `scripts/docs-migracao.py`:
- `--copiar <tag>`: lê os documentos da tag (caminho sob `sdd/` que a trava 1 tira do pacote) por `git ls-tree` e
  `git cat-file`, grava na árvore os de categoria **igual**, e escreve `sdd/reports/MIGRACAO_DOCS_F26.tsv`
  (`caminho<TAB>categoria<TAB>motivo`) com uma linha por documento da tag. **fora**: classe de bruto
  (`/(codex|claude|gemini|kimi|openrouter|deepseek|qwen)[-_][^/]*\.log$`, `/gabarito[^/]*/`, `seri(e|es)` no nome,
  `/ensaio[^/]*$`, `/INICIANTE-[^/]*$`), acima de 262.144 bytes, ou que a varredura reprova sem ajuste possível
  (log com e-mail de teste, sonda com chave falsa por extenso). **ajustado**: Markdown cujos únicos achados são
  números que fecham a conta de CPF/CNPJ entra com o comentário de aceite antes de cada um, o motivo na lista.
  Documento que já existe na `HEAD` com outro conteúdo: o `--copiar` recusa e não grava nada (revisão D1, R7).
- `--conferir <tag>`: lê o **commit da migração** (o que criou a lista, `git log --diff-filter=A`), não a `HEAD`:
  depois dele a release atualiza a ficha e o plano e a colheita põe entrada na fila, e isso não desfaz a prova
  (build, DESIGN 1.3). 0 só se (a) cada documento da tag está na lista uma vez; (b) igual ⇒ mesmo blob no commit da
  migração; ajustado ⇒ existe nele, blob diferente, motivo não vazio; fora ⇒ ausente dele **e** recalculado como
  bruto, acima do teto ou reprovado pela varredura (revisão D1, N1); (c) o commit que criou a
  lista (`git log --diff-filter=A`) só toca documentos e a lista (`--no-renames`, LM-007); (d) a fila
  `sdd/curadoria/fila/` não tem entrada no commit da migração. Cada desvio: `🔴 <caminho> · <motivo>`, exit 1.
- `--pode-aposentar <tag>`: 0 só se a tag aponta para `git ls-remote origin refs/heads/docs/incorporar-starter` e o
  `--conferir` sai 0.

**Rationale:** a lista é a fonte estruturada que a conferência lê (LM-005), e quem revisar vê o porquê de cada
arquivo de fora.

**Alternatives Rejected:** 1. Copiar à mão com `git checkout <tag> -- <pastas>` — rejeitada: traria o bruto e não
deixa prova. · 2. Classificar bruto só por tamanho — rejeitada pela medição (baseline vermelho de 533 KB é prova;
transcrição de 70 KB é bruto).

**Consequences:** a `main` ganha ~2.890 arquivos de documento num commit · a lista fica como registro permanente ·
a evidência guarda os bytes (`sdd/reports/evidence/** -text` no `.gitattributes`): 40 logs do Windows vêm com CRLF,
e normalizar o fim de linha mudaria a prova e o blob (medido no clone de teste do Build).

### Decision 6: O lote da curadoria roda dentro da F26, antes da migração

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** A fila tem 2 entradas (F23B2, F25) que o lote prova pelo histórico da branch de documentos. A F24 julgou
o 1º lote numa worktree da `main` e registrou na branch de documentos.

**Choice:** passo 0 do Build: o lote (`sdd-playbook`, `references/lote.md`) julga as 2 entradas com o playbook desta
worktree (nascida da `main` atualizada, sem mudança no playbook), registra e tira da fila na branch de documentos
(commit lá); o playbook muda nesta branch, num commit próprio. Só depois a tag e a migração.

**Rationale:** uma publicação só (a da F26) em vez de duas; a ordem garante a fila vazia que o AT-005 exige.

**Alternatives Rejected:** 1. Lote numa frente e numa Release próprias antes da F26 — rejeitada: mais uma
publicação sem ganho. · 2. Migrar com a fila cheia — rejeitada: as 2 entradas seriam recusadas depois.

**Consequences:** o PR da F26 leva também o commit do lote · o push da branch de documentos (registro do lote) e o
da tag pedem o OK do Roberto na Release.

### Decision 7: Marca no gerador, depois da troca de modo, com o teto antes de gravar

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** Decisão 4 do Roberto. Medido: 8 descrições com "SDD Open" (posição 10 a 67), 10 sem; 3 estilos de
YAML (aspas, simples, `>-`); `sdd-checar-ambiente` com 1.014 caracteres; 4 arquivos de modo.

**Choice:** `marcar(texto, skill)` no `gerar-starter.py`, aplicada à `SKILL.md` e ao arquivo de modo já montados:
na descrição, se "SDD Starter" **cabe** nos 60 primeiros caracteres no lugar do 1º "SDD Open" (posição + 11 ≤ 60;
revisão D1, R8), troca toda ocorrência por "SDD Starter"; senão,
põe "SDD Starter — " no começo (depois da aspa, ou no início da 1ª linha do `>-`) e troca as outras; conta a
descrição como o `check-versions.py` do starter conta e sai 65 acima de 1.024, antes de gravar. A linha de
identificação ganha ` · SDD Starter` depois da versão. O `check-versions.py` do starter espera a linha nova e
recusa a antiga. No Open, as 18 skills sobem patch (a cópia gerada muda e o gerador exige versão maior, LM-022); a
`sdd-checar-ambiente` perde ≥ 4 caracteres na descrição; a `sdd-release` sobe minor (passo novo); a
`sdd-engenharia-reversa-saas` troca a frase da "branch de documentos" no `manifest.json`.

**Rationale:** a marca nasce onde a cópia nasce; o Open não muda de texto (AT-010).

**Alternatives Rejected:** 1. Marca por troca em `scripts/starter/trocas/` — rejeitada: 22 trocas manuais que
quebram a cada descrição nova. · 2. Versão do starter com sufixo (`2.5.0-s`) — rejeitada: o version gate compara
semver e o `checar.sh` da F25 compara as versões das duas origens.

**Consequences:** 18 versões novas no Open sem mudança de comportamento · 1 linha de exemplo nos 2 READMEs do starter.

### Decision 8: O bruto vira anexo pela `sdd-release`, num script e numa referência

| **Status** | Accepted | · | **Date** | 2026-11-17 |

**Context:** Decisão 5 do Roberto (AT-011). A `sdd-release` tem 448 linhas (teto 500, LM-038).

**Choice:** `anexar-bruto.sh <FEATURE> <tag>`: sem `sdd/reports/evidence/<F>/bruto/` ⇒ `sem bruto` e exit 0;
`gh release view <tag>` falha ⇒ 1 linha e exit 1, nada enviado; `bash sdd/bin/docs-varredura.sh --pasta <bruto>` ≠
0 ⇒ 1 linha e exit 1; senão `tar -czf evidencia-bruta-<F>.tar.gz -C <bruto> .`, `gh release upload <tag> <arq>
--clobber`, baixa de volta (`gh release download -p`) e compara a lista do tarball com a da pasta: igual ⇒ exit 0;
diferente ⇒ exit 1. Na `SKILL.md`, 1 linha no passo depois da Release conferida, apontando para
`references/bruto.md`. O `.gitignore` ganha `sdd/reports/evidence/*/bruto/`.

**Rationale:** prova pelo que foi publicado, não pelo exit do upload (LM-004, por analogia).

**Alternatives Rejected:** 1. Enviar sem baixar de volta — rejeitada: o exit do `gh` não prova o conteúdo.

**Consequences:** depende do `gh` logado; sem ele, a `sdd-release` diz o motivo e o bruto fica na pasta.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `.gitattributes` | Modify | Trava 1 (Decision 1) | (general) | None |
| 2 | `scripts/montar-pacote.sh` | Create | Montador do pacote (Decision 2) | (general) | 1 |
| 3 | `.github/workflows/publish-gate.yml` | Modify | Trava 2 nos passos gate/shell/windows; passo da varredura dos documentos | (general) | 2, 5 |
| 4 | `.github/workflows/release.yml` | Modify | Trava 2 nos jobs testes e testes-windows | (general) | 2 |
| 5 | `sdd/bin/docs-varredura.py` | Create | Regras e saída da varredura (Decision 4) | (general) | 1 |
| 6 | `sdd/bin/docs-varredura.sh` | Create | Entrada, gitleaks, modos (Decision 3) | (general) | 5 |
| 7 | `scripts/docs-migracao.py` | Create | `--copiar`, `--conferir`, `--pode-aposentar` (Decision 5) | (general) | 1, 5 |
| 8 | `.agents/skills/sdd-release/scripts/anexar-bruto.sh` | Create | Passo do bruto (Decision 8) | (general) | 6 |
| 9 | `.agents/skills/sdd-release/references/bruto.md` | Create | Texto do passo do bruto para quem conduz a release | (general) | 8 |
| 10 | `.agents/skills/sdd-release/SKILL.md` | Modify | 1 linha do passo do bruto; versão minor | (general) | 9 |
| 11 | `.gitignore` | Modify | `sdd/reports/evidence/*/bruto/` | (general) | None |
| 12 | `CONTRIBUTING.md` | Modify | Seção de remoção a pedido (AT-012) | (general) | 6 |
| 13 | `scripts/gerar-starter.py` | Modify | `marcar()` e linha de identificação (Decision 7) | (general) | None |
| 14 | `scripts/starter/raiz/scripts/check-versions.py` | Modify | Linha de identificação com a marca | (general) | 13 |
| 15 | `scripts/starter/raiz/README.md` | Modify | Exemplo da linha de identificação (pt-BR e EN) | (general) | 13 |
| 16 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Modify | Descrição ≥ 4 caracteres menor; versão | (general) | 13 |
| 17 | `.agents/skills/sdd-engenharia-reversa-saas/manifest.json` | Modify | Tirar a "branch de documentos"; versão | (general) | None |
| 18 | `.agents/skills/*/SKILL.md` e arquivos de modo (as outras 15 da lista do starter) | Modify | Versão patch e linha de identificação (Decision 7) | (general) | 13 |
| 19 | `MANIFEST.txt` | Modify | Arquivos novos do pacote (LM-037), inclusive os de `scripts/` | (general) | 2, 5, 6, 7, 8, 9, 20, 21 |
| 20 | `tests/test_f26_docs_na_main.py` | Create | AT-001 a AT-007, AT-011, AT-012 | (general) | 1–12 |
| 21 | `tests/test_f26_marca_starter.py` | Create | AT-008 a AT-010 | (general) | 13–18 |
| 22 | `tests/test_gerar_starter.py`, `tests/test_f17c_gerador.py`, `tests/test_f25_skills_duplicadas.py` | Modify | Linha de identificação do starter com a marca | (general) | 13, 14 |
| 23 | `sdd/features/DEFINE_F26_DOCS_NA_MAIN.md` | Modify | Revisão 1.3 (Decision 3) | (general) | None |
| 24 | `sdd/playbook.md` | Modify | Lote da curadoria (Decision 6), commit próprio | (general) | None |
| 25 | `sdd/reports/MIGRACAO_DOCS_F26.tsv` e os documentos da tag | Create | Migração (Decision 5), commit próprio | (general) | 7, 24 |

**Total Files:** 25

---

## Landmines aplicáveis

Varredura rodada em 2026-11-17 pelas superfícies do manifest (`MANIFEST.txt`, `publish-gate`, `git archive`,
`gerar-starter`, `starter`, `sha256`, `[0-9]{11,}`, `verify-gate`, `baseline`, `Windows`, `subprocess`, `text=True`,
`SKILL.md`, `sdd-release`, `check-versions`, `--no-renames`, `regex`, `aceite`, `evidência`, `chave falsa`, `zsh`,
`git grep`); entradas inteiras lidas.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Gate que confere fiação | LM-001 | ✔ tratado | os testes executam montador, gate, varredura e gerador sobre repositórios de teste, com o lado que reprova |
| Asserção sem baseline vermelho | LM-002 | ✔ tratado | o Verify Gate sai vermelho hoje (conferência e varredura inexistentes); cada teste tem o caso negativo |
| Script que só roda com `.git` | LM-006 | ✔ tratado | a conferência e a varredura da `main` rodam na árvore real, antes da cópia; os testes montam o próprio repositório |
| `git diff --name-only` sem `--no-renames` | LM-007 | ✔ tratado | `--conferir` usa `--no-renames` ao ler o commit da migração |
| Número longo no pacote | LM-012 | ✔ tratado | o G2 continua sobre o pacote; os testes montam números em tempo de execução |
| Edição de teste por corte | LM-013 | ✔ tratado | os 3 testes existentes mudam por troca exata da linha do starter; contagem de `def test_` antes e depois |
| `subprocess` sem `encoding` / saída em cp1252 | LM-014, LM-015, LM-030 | ✔ tratado | `docs-varredura.py` e `docs-migracao.py` trocam a própria saída no início; testes com `encoding="utf-8"` |
| Fallback calado | LM-017 | ✔ tratado | sem gitleaks a varredura sai 2, nunca 0; teste com `path_restrito` |
| `PIPESTATUS` no zsh | LM-018 | ✔ tratado | logs de evidência por script bash com `rc=$?` |
| Chave falsa por extenso na evidência | LM-020 | ✔ tratado | o segredo de teste é montado em tempo de execução; a varredura roda sobre a evidência antes do commit |
| Lista de exceções que cala a linha | LM-023 | ✔ tratado | o aceite cobre só a linha dele e a de baixo, e só com motivo; teste com aceite na linha N e CPF na N+2, e com aceite sem motivo |
| Teste de texto por regex | LM-026 | ✔ tratado | o teste dos workflows confere que o passo chama o montador **e** que nenhum passo de gate ou shell roda sobre o checkout |
| `bash` sem caminho no Windows | LM-029 | ✔ tratado | os testes chamam pela constante `BASH` de `tests/apoio.py` |
| PATH restrito por link no Windows | LM-034 | ✔ tratado | `path_restrito` de `tests/apoio.py` para tirar o gitleaks |
| Texto de skill gerada que cita `sdd/bin/` | LM-035 | ✔ tratado | a `sdd-release` do starter sai só de `references/MODO_INICIANTE.md` (`modos.tsv`), e o gerador copia só os arquivos que o modo cita (`CITA`, `gerar-starter.py:324`); o modo não cita nenhum: a `SKILL.md`, o `bruto.md` e o `anexar-bruto.sh` do Open não vão ao starter (revisão D1, R6); `test_gerar_starter` antes do gate |
| Arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | item 19 do manifest; publish-gate numa cópia antes do gate inteiro |
| Teto de 500 linhas | LM-038 | ✔ tratado | 1 linha na `sdd-release` (448 → 449); o resto em `references/bruto.md` |
| Gerador que muda todo arquivo / version gate do destino | LM-022 | ✔ tratado | as 18 skills sobem versão no Open (Decision 7) |
| Heurística sobre texto livre | LM-005 | ✔ tratado | a migração lê a lista estruturada; documento = `git check-attr export-ignore`, função única importada pela migração |
| Mutante com `git checkout` | LM-009 | N.A. | sem script de sabotagem nesta frente |
| Medidas pelo `usage` | LM-036 | N.A. | sem custo de sessão |

Landmine nova medida neste Design (candidata para a colheita): `export-ignore` com "-export-ignore" só no conteúdo
(`sdd/bin/**`) tira a pasta inteira do `git archive`, calado.

---

## Contrato de aceite

**negociado em 2026-11-17** · 5 propostas · 5 aceitas (o avaliador de contexto fresco, modo `contrato`; evidência
`sdd/reports/evidence/F26_DOCS_NA_MAIN/AVAL-01..09.log`). Aceitas por quem conduz o build, sob o pedido do Roberto de
executar o pipeline até a release; nenhuma muda o escopo decidido, só o que prova cada AT.

| # | Alvo | Classe | Proposta (resumo) | Decisão | Aplicado em |
|---|------|--------|-------------------|---------|-------------|
| 1 | AT-004 | estado-sem-criterio | aceite só com motivo (letra ou dígito antes do fim ou de `-->`); vale para a linha e a de baixo | ACEITA | DEFINE › AT-004 · `docs-varredura.py` `aceito_em()` |
| 2 | AT-001 | aceite-circular | provar a trava pela árvore que o `extrair_tag` do gerador extrai, com o baseline sem a trava | ACEITA | DEFINE › AT-001 · `test_f26_docs_na_main` |
| 3 | AT-003 | aceite-circular | executar o `run:` do passo "Shell syntax" dos 2 workflows num repositório de teste, nos 2 sentidos | ACEITA | DEFINE › AT-003 · `test_f26_docs_na_main` |
| 4 | AT-011 | efeito-nao-observavel | conferir o anexo baixado byte a byte, não só a lista; `gh` falso que devolve outro conteúdo | ACEITA | DEFINE › AT-011 · `anexar-bruto.sh` |
| 5 | AT-004 | gate-nao-cobre-at | o modo repositório inclui o documento ainda não commitado; a `sdd-release` roda a varredura antes do push | ACEITA | DEFINE › AT-004 · `docs-varredura.py` · `sdd-release` item 10 |

Fora das 5, aplicado: a varredura tinha 2 e-mails por extenso e reprovava o G2 do pacote (montados em execução); o
passo do gate ganhou `|| exit 1` explícito.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1–25 | o repositório não define agentes especialistas |

**Agent Discovery:**
- Scanned: `.claude/agents/`, `.codex/agents/` (não existem neste repositório)
- Matched by: nenhum

---

## Code Patterns

Sem `sdd/patterns/` neste repositório. Candidato a pattern: `ci-pacote-montado`.

### Pattern 1: Trava 1 (trecho do `.gitattributes`)

```gitattributes
# F26: documento das frentes vive na main e nunca entra no pacote. Lista de PERMISSÃO dentro de sdd/: tudo fora,
# menos as entradas do pacote. Cada entrada precisa das 2 linhas (a pasta e o conteúdo): só com "/**", o git
# archive tira a pasta inteira, calado (medido no Design da F26). O G3 reprova a entrada que faltar.
sdd/** export-ignore
sdd/bin -export-ignore
sdd/bin/** -export-ignore
sdd/playbook.md -export-ignore
```

### Pattern 2: Passo do CI sobre o pacote

```yaml
      - name: Run publish gate (on the package assembled by git archive)
        env:
          PUBLISH_GATE_MODE: ci
        run: |
          P="$(bash scripts/montar-pacote.sh)" || exit 1
          bash scripts/publish-gate.sh "$P"
```

### Pattern 3: Saída da varredura (nunca o conteúdo)

```python
def achado(caminho, linha, regra):
    # S17: o trecho achado nunca é impresso — nem no log público do CI, nem para quem lê a saída
    print("🔴 %s:%d · %s" % (caminho, linha, regra))
```

---

## Data Flow

1. Push ou PR → `publish-gate.yml`: monta o pacote, publish-gate e shell sobre ele; varredura dos documentos sobre o
   checkout; testes no checkout.
2. Push na `main` com código → `release.yml`: os mesmos passos sobre o pacote; tarball pelo `git archive` (sem
   documento); Release.
3. Release de frente → `sdd-release`: commit de papel na `main` (não publica); Release conferida; `anexar-bruto.sh`.
4. Migração (uma vez): lote → tag → `--copiar` → commit → `--conferir` → PR → `--pode-aposentar` → OK do Roberto.

---

## Integration Points

| Sistema | Uso | Falha |
|---|---|---|
| gitleaks 8.30.1 | varredura (JSON) | ausente ⇒ exit 2 |
| `gh` | anexo do bruto, Release | sem login ou sem Release ⇒ nada enviado, 1 linha |
| GitHub Actions | travas no CI | passo vermelho segura o job `release` |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit + integração | AT-001 a AT-007, AT-011, AT-012 | `tests/test_f26_docs_na_main.py` | `unittest`, repositórios git temporários, `gh` falso | todo AT com o lado que reprova |
| Unit | AT-008 a AT-010 | `tests/test_f26_marca_starter.py` + os 3 testes do starter | `unittest`, gerador sobre tag de teste | 18 skills, 4 modos, teto, as duas origens no `checar.sh` |
| Regressão | AT-007 | suíte inteira | `/usr/bin/python3`, `/bin/bash` 3.2; CI do PR (Linux, macOS, Windows) | 0 falha |
| Real | AT-005, varredura da `main` | `docs-migracao.py --conferir`, `docs-varredura.sh .` | árvore real, depois da migração | exit 0 |

Blocos do teste por AT:
- AT-001: repositório com documentos em 7 pastas + `sdd/GOVERNANCA_PADRAO.md` + pasta nova `sdd/estudos/`; `git archive` como o `release.yml`; 0 documentos e o `MANIFEST` nos 2 sentidos; gerador sobre a tag.
- AT-002: o mesmo repositório com a linha `sdd/bin -export-ignore` removida (G3 "declared but missing") e com um documento numa entrada do pacote fora do `MANIFEST` (G3 "undeclared"): publish-gate ≠ 0 com o nome; texto dos 2 workflows: todo passo `publish-gate.sh` e "Shell syntax" usa `montar-pacote.sh`.
- AT-003: checkout com número longo, `/Users/x/`, `.sh` em evidência: montador + gate saem 0; número longo num arquivo do pacote: G2 ≠ 0.
- AT-004: cada regra com um caso que reprova e um vizinho que passa; segredo e certificado montados em execução; documento com `RESULTADO: VERDE` e `\x1b`: a saída não muda; gitleaks fora do PATH ⇒ 2.
- AT-005/006: repositório com branch de documentos, tag, lista e fila; um desvio por vez (blob diferente, arquivo fora presente, código vindo da tag, fila com entrada, tag atrás do remoto).
- AT-007: `push-de-papel.py` com as pastas e com `sdd/playbook.md`; `init` de um tarball com documentos: 0 documentos no projeto.
- AT-011: `gh` falso que guarda o anexo; sem pasta; Release ausente; varredura vermelha; lista do tarball baixado.
- AT-012: texto do `CONTRIBUTING.md`; `--padrao` em `--ref` e `--pasta`.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| gitleaks ausente ou com erro | `NÃO CONFERIDO`, exit 2; o bruto não é anexado | No |
| tag de arquivo ausente ou fora do lugar | `--conferir`/`--pode-aposentar` saem 1 com o motivo | No |
| descrição marcada acima de 1.024 | gerador sai 65, nada gravado | No |
| `gh release upload` falha ou anexo diferente | exit 1, 1 linha; a pasta fica | Yes (a pessoa roda de novo; `--clobber`) |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `SDD_DOCS_TETO` | int | `262144` | teto de bytes por arquivo de evidência (só para teste; o CI usa o padrão) |

---

## Segurança

1. **Onde mora cada segredo:** nenhum segredo novo; o `gh` usa o login de quem roda a release; o CI usa o
   `GITHUB_TOKEN` só leitura nos jobs de teste (sem mudança).
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** o anexo usa o `gh` de quem publica, depois do OK da release;
   nenhum agente novo.
4. **Cabeçalhos e CORS do host:** N.A. — sem host web.
5. **Itens aplicados no Define:** S17 Log que aceita linha forjada → a varredura imprime só caminho, linha e regra,
   nunca o trecho; a linha de resultado vem do exit, e um documento com `RESULTADO: VERDE` ou caractere de controle
   não muda a saída (teste no AT-004).

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | saída do CI: 1 linha por achado (caminho, linha, regra) |
| Metrics | contagem de documentos migrados por categoria na lista |
| Tracing | N.A. |

---

## Advisor Ledger

Rodada D1 (`EXTERNAL_REVIEW_20261117-215809`, sobre `7146c84`): `claude` (claude-opus-5-5) revisa, `codex`
(gpt-6.1-sol) audita; diversidade de vendor; US$ 0,93. Ledger: `sdd/reviews/LEDGER_REVISAO_F26_DOCS_NA_MAIN.md`.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| R1 | teto de 256 KB no `--pasta` impede o anexo do bruto | MED | APLICADA | Decision 4: o teto vale só para evidência versionada; `docs-varredura.py` (`regras_do_arquivo(…, versionado)`) |
| R2 | DEFINE manda o lote em frente própria; Decision 6 o põe na F26 | MED | APLICADA | DEFINE 1.4, Constraints |
| R3 | `scripts/docs-migracao.py` fora das dependências do `MANIFEST.txt` | MED | APLICADA | File Manifest, item 19 |
| R4 | `--ref --padrao` não varre o código velho da tag | MED | APLICADA | Decision 4: `--padrao` com `--ref` varre todos os arquivos; attrs da árvore atual |
| R5 | trava 2 pode deixar passo ou job lendo a árvore | MED | REBATIDA_EVIDENCIA | `release.yml:145-187` (testes-macos só roda unittest); os 6 passos listados na Decision 2; DEFINE 1.4 troca "3 jobs" por testes e testes-windows |
| R6 | starter receberia a linha e os arquivos do bruto da `sdd-release` | MED | REBATIDA_EVIDENCIA | `scripts/starter/modos.tsv` (sdd-release → `references/MODO_INICIANTE.md`); `gerar-starter.py:324` copia só o que o modo cita; o modo não cita nenhum arquivo |
| R7 | migração sem categoria para documento já na `main` com outro conteúdo | LOW | APLICADA | Decision 5: o `--copiar` recusa e não grava |
| R8 | "SDD Open" nos 60 primeiros não garante "SDD Starter" nos 60 | LOW | APLICADA | `gerar-starter.py` `marcar()`: posição + 11 ≤ 60, e confere depois da troca |
| R9 | `exemplo.*` aceita domínio real | LOW | APLICADA | Decision 4: só `exemplo.com` exato |
| R10 | exit do montador perdido na substituição de comando | LOW | APLICADA | Decision 2: `pipefail`, confere o `MANIFEST.txt`, chamada em 2 linhas |
| R11 | caminho impresso sem neutralizar controle | LOW | APLICADA | Decision 4: `limpo()` troca não imprimível por `?` |
| N1 | `fora` aceito sem provar o motivo | MED | APLICADA | Decision 5: `--conferir` recalcula a classe de cada `fora` |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-17 | design-agent | Versão inicial |
| 1.2 | 2026-11-17 | build | Contrato de aceite: 5 propostas aceitas; Pattern 2 em 2 linhas |
| 1.3 | 2026-11-18 | build | `--conferir` lê o commit da migração, não a `HEAD` (o papel da release e a fila nova reprovariam o `--pode-aposentar` à toa) |
| 1.1 | 2026-11-17 | design-agent | Revisão D1: 10 notas aplicadas, 2 rebatidas com evidência; evidência com `-text` (CRLF medido) |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F26_DOCS_NA_MAIN.md`
