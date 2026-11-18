# DEFINE: F26 Documentos na main e marca do SDD Starter

> Bloco A: os documentos das frentes (DEFINE, DESIGN, relatórios, fichas, ledgers, fila da curadoria) passam a viver
> na `main`, no PR do código, com duas travas que os mantêm fora do pacote do aluno, uma varredura própria e a
> evidência bruta fora do git; a branch `docs/incorporar-starter` vira uma tag de arquivo. Bloco B: as skills
> geradas para o starter dizem "SDD Starter" na descrição e na linha de identificação.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F26_DOCS_NA_MAIN |
| **Date** | 2026-11-17 |
| **Author** | define-agent (sessão do Roberto), a partir de `sdd/handoffs/SESSION_PROMPT_F26_DOCS_NA_MAIN.md` (branch de documentos) e das decisões desta sessão |
| **Status** | Ready for Design |
| **Clarity Score** | 15/15 |

---

## Problem Statement

Os documentos das frentes do Open moram numa branch separada de longa duração (`docs/incorporar-starter`), nascida
na `v2.2.3` e com uma cópia velha do código ao lado: código e documento da mesma frente ficam em dois lugares, o
plano é editado numa worktree própria, a fila da curadoria fica numa branch e o playbook na outra (pendência da F24),
e os documentos não passam por nenhuma varredura automática (a de dado privado foi feita à mão na B2). Pôr os
documentos na `main` sem travas levaria 3.286 arquivos de documento ao CI, que hoje confere a PASTA do checkout
contra o pacote (o G3 reprova todo arquivo fora do `MANIFEST.txt`) e barraria 136 documentos por número longo, 50 por
e-mail e 439 por caminho `/Users/<nome>/`.

Bloco B (decisão do Roberto em 2026-11-17, mesma sessão): a mesma skill tem o mesmo nome e quase o mesmo texto no Open
e no starter; a descrição do starter diz "Fase 0 do SDD Open" e a única pista da origem é o endereço no fim da linha
de identificação. Quem instalou as duas não distingue qual está rodando.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Roberto (mantenedor do Open) | abre, especifica, publica e cura as frentes | dois checkouts por frente, plano que só se edita numa worktree, fila da curadoria e playbook em branches diferentes, nenhuma varredura nos documentos que já são públicos |
| Aluno que instala o Open (tarball, clone, `npx`) | recebe o pacote | não pode receber nenhum documento de frente (pasta pessoal, ids de run, evidência de 15 MB) |
| Aluno do starter (claude.ai, ChatGPT, `npx`) | usa as skills geradas | não sabe se a skill que roda é a do starter ou a do Open quando tem as duas |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Trava 1: nenhum arquivo das pastas de documento entra no pacote montado pelo `git archive` (tarball da Release, gerador do starter, cópia do Verify Gate) |
| **MUST** | Trava 2: os passos do CI que leem a árvore (publish-gate G1–G5; sintaxe de shell, sem zsh, sem symlink) passam a ler o pacote montado; documento que escapar reprova; os padrões do G2 e o G3 não são afrouxados |
| **MUST** | Varredura própria dos documentos no CI: segredo (gitleaks) e e-mail real fora dos domínios de exemplo reprovam; número longo e caminho `/Users/<nome>/` não; arquivo de evidência acima de 256 KB reprova |
| **MUST** | Migração: os documentos da branch de documentos entram na `main` num commit só (o estado, sem o histórico), depois de o lote da curadoria julgar a fila; a evidência bruta e o que passa do teto ficam só na tag `arquivo/docs-incorporar-starter`; uma conferência prova arquivo a arquivo |
| **MUST** | A branch e a worktree de documentos só saem com a tag no último commit dela, a conferência verde na `main` e o OK explícito do Roberto |
| **MUST** | Marca: a descrição e a linha de identificação de cada skill gerada no starter dizem "SDD Starter"; as do Open não mudam de texto |
| **SHOULD** | A regra da evidência daqui em diante: o que um lint ou uma pessoa lê vai para o git; o bruto (transcrição de modelo, gabarito copiado, log de série) fica fora dele e vai, varrido, como anexo da Release da frente |
| **SHOULD** | O texto do pacote que cita a branch de documentos (`sdd-engenharia-reversa-saas/manifest.json`) e as fichas e prompts de sessão do Open param de mandar documento para outra branch |
| **COULD** | — |

---

## Success Criteria

- [ ] O tarball montado como no `release.yml` a partir do commit da F26 tem 0 arquivos sob `sdd/features`, `sdd/handoffs`, `sdd/reviews`, `sdd/releases`, `sdd/archive`, `sdd/curadoria` e `sdd/reports`, e as 743 linhas do `MANIFEST.txt` (mais as que a F26 acrescentar) presentes, nos 2 sentidos.
- [ ] O starter gerado pela tag da F26 tem 0 arquivos dessas pastas e as 18 skills com "SDD Starter" nos 60 primeiros caracteres da descrição e na linha de identificação; 0 descrições acima de 1.024 caracteres.
- [ ] Na `main` depois da migração: 100% dos arquivos de documento da tag de arquivo estão na `main` com o mesmo blob ou na lista de fora com o motivo; 0 arquivos do código velho da branch de documentos entram; a fila da curadoria tem 0 entradas pendentes.
- [ ] A varredura dos documentos sai 0 na `main` migrada e sai 1 nas 3 sondas (segredo de teste montado em tempo de execução, e-mail real, evidência de 257 KB).
- [ ] CI do PR verde nos 3 sistemas (Linux, macOS no piso, Windows nas 16 fatias), com os documentos da própria F26 no checkout.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** o pacote é montado por `git archive` (o mesmo comando do `release.yml`) a partir de um commit com arquivos em `sdd/features`, `sdd/handoffs`, `sdd/reviews`, `sdd/releases`, `sdd/archive`, `sdd/curadoria` e `sdd/reports`, the pacote **shall** ter 0 arquivos dessas pastas e todas as linhas do `MANIFEST.txt`, e a árvore que o `extrair_tag` do `gerar-starter.py` extrai desse commit **shall** ter 0 arquivos dessas pastas (sem a linha `sdd/** export-ignore`, o mesmo teste falha: o baseline) | test |
| AT-002 | Unwanted | **If** um arquivo fora do `MANIFEST.txt` chega ao pacote montado (pasta de documento nova não coberta pela trava 1, ou a linha da trava 1 removida), **then** o passo do publish-gate do CI (`publish-gate.yml` e os jobs `testes` e `testes-windows` do `release.yml`; o `testes-macos` não lê a árvore) **shall** sair ≠ 0 nomeando o arquivo, e o job `release` não roda; um teste abre o tarball montado como no `release.yml` e falha com qualquer arquivo daquelas pastas | test (negativo) |
| AT-003 | Event-driven | **When** o CI roda num checkout com documentos que têm número de 11+ dígitos, caminho `/Users/<nome>/`, e-mail de domínio de exemplo e `.sh` dentro de `sdd/reports/evidence`, the passos que leem a árvore (publish-gate G1–G5; sintaxe de shell, sem zsh, sem symlink — o `run:` do workflow executado como está) **shall** ler o pacote montado e sair 0; um `.sh` inválido em `scripts/` **shall** fazer o passo de shell sair ≠ 0; com o mesmo número longo posto num arquivo do pacote, o G2 **shall continue to** sair ≠ 0 | test |
| AT-004 | Unwanted | **If** uma pasta de documento traz um segredo que o gitleaks acha, um e-mail fora dos domínios de exemplo, um arquivo de certificado com chave privada (`.pfx`, `.p12`, ou `.pem`/`.key` com cabeçalho `PRIVATE KEY`), um CPF ou CNPJ com dígito verificador válido (com ou sem pontuação) sem o comentário `docs-varredura: aceito — <motivo>` (motivo com ao menos uma letra ou dígito antes do fim da linha ou de `-->`) na linha ou na de cima, ou um arquivo de evidência versionado com mais de 256 KB (262.144 bytes; não vale para o bruto no `--pasta`), **then** a varredura dos documentos (`sdd/bin/docs-varredura.sh`, no CI a cada PR e push na `main`) **shall** sair 1 nomeando só o arquivo, a linha e a regra, nunca o conteúdo achado (um documento com caractere de controle ou com `RESULTADO: VERDE` no texto não muda a saída); com número longo sem dígito verificador válido, com o comentário de aceite e com caminho `/Users/<nome>/` ela **shall** sair 0; sem o gitleaks instalado **shall** sair ≠ 0, nunca verde; no modo repositório, o documento ainda não commitado (fora do `.gitignore`) **shall** entrar na varredura, e a `sdd-release` **shall** rodá-la antes do push | test (negativo) |
| AT-005 | Event-driven | **When** o commit da migração está na `main`, the conferência (`scripts/docs-migracao.py --conferir arquivo/docs-incorporar-starter`) **shall** sair 0 só se cada arquivo das pastas de documento da tag estiver na `main` com o mesmo blob ou na lista de fora com o motivo (classe de bruto ou acima de 256 KB), nenhum arquivo de fora das pastas de documento tiver vindo da tag, e a fila `sdd/curadoria/fila/` não tiver entrada pendente; cada desvio **shall** sair 1 com o caminho | test |
| AT-006 | State-driven | **While** a tag `arquivo/docs-incorporar-starter` não aponta para o último commit da branch `docs/incorporar-starter` do remoto, ou a conferência do AT-005 não sai 0, the `docs-migracao.py --pode-aposentar` **shall** sair 1 com o motivo, e a branch e a worktree de documentos não são apagadas (apagar pede, além disso, o OK do Roberto) | test |
| AT-007 | Non-regression | The sistema **shall continue to**: o `init` e o `upgrade` (tarball e clone) instalam só o que o `MANIFEST.txt` e o `SDD_ENTRADAS_PACOTE` listam; um push só com arquivos das pastas de documento não roda o `release.yml` (`push-de-papel.py` diz NAO_PUBLICA) e com `sdd/playbook.md` roda (PUBLICA); a suíte inteira passa no piso (`/usr/bin/python3`, `/bin/bash` 3.2) e no CI do PR em Linux, macOS e Windows | test |
| AT-008 | Event-driven + Optional feature | **When** o `gerar-starter.py` gera o starter, cada uma das 18 `SKILL.md` (e, **where** a skill tem arquivo de modo em `scripts/starter/modos.tsv`, o arquivo de modo) **shall** ter a descrição com "SDD Starter" nos 60 primeiros caracteres e sem "SDD Open", e a linha de identificação `` `<skill> vX.Y.Z · SDD Starter · <mês>/<ano> · versão atual: https://github.com/robertodiasduarte/sdd-starter/releases/latest` ``; o `check-versions.py` do starter **shall** aceitar essa forma e recusar a antiga | test |
| AT-009 | Unwanted | **If** a descrição com a marca passa de 1.024 caracteres, **then** o `gerar-starter.py` **shall** sair 65 nomeando a skill e o tamanho, sem gravar nada no destino | test (negativo) |
| AT-011 | Event-driven + Unwanted + Optional feature | **When** a `sdd-release` publica uma frente que tem `sdd/reports/evidence/<F>/bruto/` e, **where** o projeto publica Release no GitHub (a Release da tag existe), the passo do bruto **shall** anexar `evidencia-bruta-<F>.tar.gz` com exatamente os arquivos da pasta (conferido pelo anexo baixado: a lista e os bytes; um download com outro conteúdo ⇒ `ANEXO DIFERENTE`, exit 1); **if** a varredura dos documentos sai ≠ 0 sobre o bruto, ou a Release da tag não existe, **then** ele **shall** não anexar nada e dizer o motivo em 1 linha; o `bruto/` **shall** estar no `.gitignore` | test |
| AT-012 | Ubiquitous | The `CONTRIBUTING.md` **shall** ter a seção "Pedido de remoção de dado pessoal" com os 3 lugares onde o dado pode estar (a `main`, a tag `arquivo/docs-incorporar-starter`, os anexos `evidencia-bruta-<F>.tar.gz` das Releases), o passo de cada um (commit que tira da `main`; tag regravada sem o arquivo; anexo trocado por um sem o arquivo, varrido de novo) e o prazo de resposta de 30 dias; e o `sdd/bin/docs-varredura.sh` **shall** aceitar `--padrao <regex>` (só essa regra; com `--ref`, todos os arquivos da ref) para provar, nos 3 lugares, que o dado pedido sumiu (sai 1 enquanto achar) | test |
| AT-010 | Non-regression | The sistema **shall continue to**: as skills do Open sem "SDD Starter" na descrição e na linha de identificação (a linha do Open muda só pela versão); o `checar.sh` da F25 classificando a cópia gerada como `starter` e a do Open como `open`; o gerador recusando cópia gerada que mudou sem versão maior que a do starter (por isso as 18 skills sobem de versão no Open) | test |

São 12 ATs, acima dos ~10: 2 blocos numa frente (decisão do Roberto) e o AT-012 da governança; cortar juntaria regras de natureza diferente num AT só.

Padrões considerados: **While** no AT-006 (estado da tag e da conferência); **If/Then** nos AT-002, AT-004, AT-009 e AT-011;
**Where** no AT-008 (skill com arquivo de modo × sem). Não é bugfix, mas os AT-007 e AT-010 registram a
não-regressão do empacotamento, da Release e do `checar.sh` da F25.

### O que é documento, bruto e pacote (regras do corpo)

- **Pastas de documento:** (mais o `sdd/GOVERNANCA_PADRAO.md`, criado nesta frente, que também não vai ao pacote) `sdd/features`, `sdd/handoffs`, `sdd/reviews`, `sdd/releases`, `sdd/archive`,
  `sdd/curadoria` e `sdd/reports`. `sdd/traces/` e `sdd/reports/reviews/` continuam no `.gitignore`. Se a trava 1
  vira lista de pastas (denylist) ou "todo `sdd/` menos o pacote" (allowlist), quem decide é o Design, com o
  porquê; o AT-002 vale nos dois casos.
- **Migração (decisão 1 do Roberto, 2026-11-17):** o estado atual das pastas de documento, num commit só, sem o
  histórico; antes dela, o lote da curadoria julga as 2 entradas da fila (F23B2, F25) como a F24 fez em
  2026-11-17, porque o lote prova cada entrada pelo histórico do git e, depois da migração sem histórico, as 2
  seriam recusadas. O código velho da branch de documentos (`.agents`, `bin`, `scripts`, `tests`, `docs`,
  `sdd/bin`, `sdd/templates` e o resto fora das pastas de documento) não migra.
- **Evidência antiga (decisão 2):** a tag `arquivo/docs-incorporar-starter` no último commit da branch guarda
  tudo; na `main` entram os documentos escritos e os logs que um lint ou uma pessoa lê (por AT, do gate,
  vereditos, resumos). Ficam só na tag: a classe de bruto (transcrição de modelo como `codex-*.log`, gabarito
  copiado como `gabarito*/`, log de série; a lista exata é do Design, medida sobre os 2.875 arquivos de
  `sdd/reports/evidence`) e todo arquivo acima de 256 KB (hoje 2: 533 KB e 256 KB).
- **Evidência bruta das próximas frentes (decisão 5 do Roberto, 2026-11-17):** durante a frente, o bruto fica em
  `sdd/reports/evidence/<F>/bruto/`, ignorado pelo git; na publicação, a `sdd-release` o junta num
  `evidencia-bruta-<F>.tar.gz` e o anexa à Release da versão que ele prova, depois do push, e só depois de a
  varredura dos documentos sair 0 sobre ele (o anexo é público). Num projeto que não publica Release no GitHub, o
  passo diz isso em 1 linha e não faz nada; o bruto continua na pasta da frente. A `sdd-release` está no teto de
  500 linhas (LM-038): o passo mora em `references/` e num script, com 1 linha na `SKILL.md`.
- **Varredura dos documentos (decisão 3):** gitleaks e e-mail real fora dos domínios de exemplo reprovam; número
  longo e `/Users/<nome>/` não (a LM-012 manda o id de run ficar no documento; o caminho das worktrees está em 439
  documentos e o nome de usuário já é público). A lista dos domínios de exemplo é do Design (hoje aparecem
  `example.com`, `example.invalid`, `exemplo.invalid`, `exemplo.com`, `e.com`, `github.com`); o 1 e-mail real
  medido sai na migração.
- **Marca (decisão 4):** na descrição, "SDD Open" vira "SDD Starter"; sem "SDD Open", ela começa com
  "SDD Starter — ". A descrição da `sdd-checar-ambiente` tem 1.014 caracteres e passaria do teto: ela perde ao
  menos 4 no Open. A linha de identificação ganha `· SDD Starter ·` depois da versão. Como as 18 cópias geradas
  mudam, as 18 skills sobem a versão (patch) no Open, que é o que o gerador e o version gate do starter exigem.

---

## Clarifications

### Session 2026-11-17 (decisões do Roberto, nesta sessão)

- [x] (escopo) A marca do starter entra na F26 como bloco separado (ATs e commits próprios), em vez de frente à parte; se a parte dos documentos emperrar, o bloco sai sozinho num PR pequeno. Integrado no resumo, em Goals e nos AT-008 a AT-010.
- [x] (dados) Migração → só o estado atual, num commit, depois de o lote da curadoria julgar a fila. Integrado em "O que é documento, bruto e pacote" e no AT-005.
- [x] (dados) Evidência bruta antiga → tag de arquivo no último commit da branch de documentos, e a branch sai; na `main`, documentos escritos e logs leves. Integrado no AT-005 e no AT-006.
- [x] (NFRs) Varredura dos documentos → gitleaks e e-mail real; sem número longo nem `/Users/`. Integrado no AT-004.
- [x] (terminologia) Marca → "SDD Starter" por extenso na descrição e na linha de identificação, não "(s)". Integrado no AT-008.
- [x] (dados) Bruto das próximas frentes → anexo `evidencia-bruta-<F>.tar.gz` na Release da frente, pela `sdd-release`, depois do push e da varredura; a pasta `bruto/` fica fora do git. Integrado em "O que é documento, bruto e pacote" e no AT-011.

### Session 2026-11-17 (governança)

- [x] (governança) Revisor fresco, 2ª tentativa (a 1ª devolveu PADRAO_AUSENTE: o padrão do projeto foi respondido pelo Roberto e gravado em `sdd/GOVERNANCA_PADRAO.md`, com `uso: clientes também`). Resultado REVISADO, 0 lacunas, 18 N.A., 2 na 2ª camada (G14, G16): `sdd/reviews/GOVERNANCA_REVIEW_F26_DOCS_NA_MAIN.md`.
- [x] (governança) G16, 2ª camada → aplicado (Roberto): certificado com chave privada nas pastas de documento e no bruto reprova a varredura. Integrado no AT-004.
- [x] (governança) G14, 2ª camada → aplicado (Roberto): CPF ou CNPJ com dígito verificador válido reprova, com dispensa por comentário com motivo (medido: 1 caso nos 3.286 documentos, em `sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md`, provavelmente um id de run); e o procedimento de remoção a pedido nos 3 lugares. Integrado no AT-004 e no AT-012.

### Segurança

- [x] (segurança) Gatilho: dado de terceiros (documentos e bruto públicos e permanentes). S10 já atendido pelo AT-004 e pelo AT-011 (gitleaks nas pastas de documento e no bruto antes do anexo).
- [x] (segurança) S17 Log que aceita linha forjada → aplicado (Roberto): a saída da varredura diz arquivo, linha e regra, sem o conteúdo achado. Integrado no AT-004.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "python3 -B scripts/docs-migracao.py --conferir arquivo/docs-incorporar-starter && bash sdd/bin/docs-varredura.sh . && T=$(mktemp -d) && git archive HEAD | tar -x -C $T && cd $T/tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest test_f26_docs_na_main test_f26_marca_starter test_gerar_starter test_f17c_gerador test_f25_skills_duplicadas && cd $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura:
- AT-005 e a varredura da `main` rodam na árvore real, antes da cópia: a conferência precisa do git (tag e
  blobs) e os documentos não existem na cópia do `git archive` (é a trava 1). Antes da migração, as duas saem ≠ 0:
  é o baseline vermelho.
- AT-011: no mesmo módulo, com um `gh` falso (como o do `test_checar.py`) que guarda o anexo enviado e responde
  "Release não existe" num 2º cenário; o envio real fica para a publicação da própria F26 (recibo no ledger).
- AT-012: no mesmo módulo — teste de texto do `CONTRIBUTING.md` e o `--padrao` sobre um repositório de teste com a tag e um tarball de anexo.
- AT-001 a AT-004, AT-006 e AT-007: módulo novo `tests/test_f26_docs_na_main.py`, com repositórios de teste em
  pasta temporária (commit com documentos, `git archive`, tarball como no `release.yml`, pasta de documento
  nova, linha da trava removida, tag fora do lugar, fila com entrada), o segredo montado em tempo de execução
  (LM-020) e o gitleaks ausente por PATH restrito (`path_restrito` de `tests/apoio.py`). Os passos do CI são
  conferidos pelo texto dos workflows e executados pelo mesmo script que eles chamam.
- AT-008 a AT-010: módulo novo `tests/test_f26_marca_starter.py`, mais `test_gerar_starter`, `test_f17c_gerador`
  e `test_f25_skills_duplicadas` chamados pelo nome (os 3 conferem a linha de identificação do starter hoje).
- AT-007: a suíte inteira no piso (o `discover` do fim) e o CI do PR nos 3 sistemas (recibo no BUILD_REPORT).

---

## Out of Scope

- Ligar a varredura dos documentos no CI do projeto do aluno: ela mora no pacote (`sdd/bin/docs-varredura.sh`) porque o passo do bruto da `sdd-release` (AT-011) a usa em qualquer projeto, mas só o CI do Open a chama sobre os documentos (DESIGN, Decision 3).
- Reescrever os documentos antigos para tirar caminho `/Users/<nome>/`, número longo ou id de run.
- Mudar o nome das skills do starter (DC4 da F25 continua valendo).
- A F27 (`feat/f27-db-performance`): já nasce com os documentos na própria branch; o rebase dela é da sessão dela.
- Publicar o bruto antigo em qualquer lugar além da tag de arquivo.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | O pacote é o `git archive` (tarball da Release, `gerar-starter.py`, cópia do Verify Gate); o `init`/`upgrade` instalam por lista | a trava 1 é `export-ignore` no `.gitattributes`, que vale nos 3 usos |
| Technical | G2 e G3 não são afrouxados para o pacote (pedido de abertura) | o CI muda o QUE confere (o pacote montado), não as regras |
| Technical | LM-037 (arquivo novo no `MANIFEST.txt`), LM-035 (texto de skill gerada que cita `sdd/bin/`), LM-038 (teto de 500 linhas), LM-012 (número longo) | rodar `test_gerar_starter` e o publish-gate numa cópia de `git archive` antes do gate inteiro |
| Technical | Suíte verde no Windows (job no `needs:` da release); teste que pergunta a plataforma usa `tests/apoio.py`; Bash do agente é zsh | testes com as constantes do `apoio.py`; scripts chamados por `bash` |
| Process | Apagar a branch e a worktree de documentos e publicar (push, PR, merge, tag, Release) pedem o OK do Roberto | AT-006 e a fase Release |
| Process | O lote da curadoria escreve no `playbook.md` da `main`, e isso publica uma Release | roda antes da migração, dentro da F26, num commit próprio; publica junto com a F26 (DESIGN, Decision 6) |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.gitattributes`, `.gitignore`, `.github/workflows/publish-gate.yml`, `.github/workflows/release.yml`, `scripts/montar-pacote.sh`, `sdd/bin/docs-varredura.sh` e `.py`, e `scripts/docs-migracao.py` (novos), `scripts/gerar-starter.py`, `scripts/starter/raiz/scripts/check-versions.py`, `scripts/starter/raiz/README.md`, `.agents/skills/sdd-release/` (1 linha na `SKILL.md`, o passo do bruto em `references/` e um script em `scripts/`), `.agents/skills/*/SKILL.md` (18, versão) e os arquivos de modo, `.agents/skills/sdd-checar-ambiente/SKILL.md` (descrição), `.agents/skills/sdd-engenharia-reversa-saas/manifest.json`, `tests/test_f26_docs_na_main.py`, `tests/test_f26_marca_starter.py`, os testes que conferem a linha do starter, `MANIFEST.txt`, e as pastas de documento migradas | `docs-migracao.py` e `montar-pacote.sh` ficam em `scripts/` (do mantenedor); a varredura fica em `sdd/bin/` (do pacote), porque o passo do bruto da `sdd-release` a usa (DESIGN, Decision 3) |
| **KB Domains** | nenhum | o repositório não tem `sdd/kb/` |
| **IaC Impact** | Modify existing | os 2 workflows do GitHub Actions; nenhum recurso de infraestrutura |
| **LLM Prompts** | false | nenhum prompt de runtime; o texto das skills muda só na descrição gerada e na versão |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | GOVERNANCA_REVIEW_F26_DOCS_NA_MAIN.md · 0 aplicadas · 0 recusadas · 0 adiadas (2ª camada: G14 e G16 aplicados, AT-004 e AT-012) | 2026-11-17 |
| **Segurança** | 1 aplicados (S17) · 0 recusados · 0 adiados | 2026-11-17 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O `export-ignore` vale no tarball, no `gerar-starter.py` e na cópia do Verify Gate, porque os 3 usam `git archive` | um documento chegaria ao pacote por um caminho que não usa `git archive` | [x] `release.yml:288`, `gerar-starter.py:91`; o Verify Gate do DEFINE usa `git archive HEAD` |
| A-002 | O `init` e o `upgrade` copiam por lista, de tarball ou de clone | um clone levaria os documentos ao projeto | [x] `bin/lib/versao.sh:8` e `:59-75`, `bin/sdd-open.sh:667` |
| A-003 | Um push só de documentos não publica | cada commit de papel abriria uma Release | [x] `push-de-papel.py` → NAO_PUBLICA com as 7 pastas; PUBLICA com `sdd/playbook.md` (2026-11-17) |
| A-004 | Nenhum teste lê os documentos do próprio repositório | um teste quebraria com a migração | [x] `grep` em `tests/`: só caminhos em pastas temporárias e listas via `MANIFEST.txt` |
| A-005 | Uma tag fora do padrão `v*` (`arquivo/…`) não dispara o `release.yml` nem muda o `next-version.sh` | a tag de arquivo viraria Release | [ ] conferir no Design (`release.yml:42` só casa `v[0-9]+.[0-9]+.[0-9]+`) |
| A-006 | O lote da curadoria das 2 entradas da fila cabe antes da migração, como na F24 | a migração esperaria o lote | [ ] depende da sessão do lote |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | medido: 3.286 documentos, G2/G3 do CI, fila × histórico, descrições do starter |
| Users | 3 | mantenedor, aluno do Open, aluno do starter |
| Goals | 3 | 6 MUST com as decisões da sessão |
| Success | 3 | contagens e exits verificáveis |
| Scope | 3 | o destino do bruto das próximas frentes decidido (decisão 5) |
| **Total** | **15/15** | |

---

## Open Questions

Nenhuma — pronto para o Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-17 | define-agent | Versão inicial, blocos A e B |
| 1.1 | 2026-11-17 | define-agent | Decisão 5 (bruto das próximas frentes como anexo da Release): AT-011 |
| 1.2 | 2026-11-17 | define-agent | Governança (0 lacunas; G14 e G16 da 2ª camada aplicados) e segurança (S17): AT-004 ampliado, AT-012 |
| 1.5 | 2026-11-17 | build | Contrato de aceite (5 aceitas): AT-001 pelo `extrair_tag`, AT-003 executando o passo de shell, AT-004 com aceite só com motivo e documento não commitado, AT-011 byte a byte |
| 1.4 | 2026-11-17 | design-agent | Revisão D1 do DESIGN: lote dentro da F26 (Constraints), jobs da trava 2 nomeados (AT-002), teto só para evidência versionada (AT-004), `--padrao` em todos os arquivos da ref (AT-012) |
| 1.3 | 2026-11-17 | design-agent | A varredura dos documentos vai para `sdd/bin/` (pacote), porque o passo do bruto da `sdd-release` a usa em qualquer projeto: AT-004, AT-012, `cmd` do Verify Gate, Out of Scope e Technical Context (DESIGN, Decision 3) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F26_DOCS_NA_MAIN.md` (sem UX review: não há interface; o texto que o
aluno lê muda só na descrição e na linha de identificação do starter, conferidas por teste).
