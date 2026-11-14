# DEFINE: F22 — Aviso de versão e upgrade

> Quem instalou o Open pelo `init` passa a saber, sem procurar, que saiu versão nova, e atualiza com um comando que
> copia o que é do pacote e lista, sem tocar, o que foi editado no projeto. Nada é atualizado nem commitado sozinho.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F22_AVISO_VERSAO |
| **Date** | 2026-11-14 (v1.0) |
| **Author** | define-agent (worktree `sdd-open-f22-aviso-versao`; branch `feat/f22-aviso-versao`, de `origin/main` `ad32fe1` = `v2.16.0`) |
| **Status** | Ready for UX Review |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F22_AVISO_VERSAO.md` (abordagem A) |

---

## Problem Statement

O `init` não grava no projeto qual versão do Open instalou, e o `doctor` compara o projeto só com o pacote que rodou,
nunca com a última versão publicada: o único sinal de versão nova é o link `…/releases/latest` na 1ª linha das skills,
que ninguém clica. Atualizar é trabalho à mão que o aluno não sabe fazer: o `init` nunca toca arquivo que existe e só
copia skill cujo diretório inteiro falta. No 1º projeto que subiu 3 versões de uma vez (`v2.12.1` → `v2.15.0`) foi
preciso classificar à mão cada arquivo do `MANIFEST.txt` entre as duas tags: 157 iguais, 46 novos (27 dentro de skills
que já existiam), 43 cópias intactas da tag velha (copiar) e 3 editados no projeto (não tocar). O próprio pacote não
sabe a sua versão: ela só existe na tag. Do mesmo upgrade vieram 2 defeitos: o `doctor` acusa "hooks do open não
ligados" quando o `core.hooksPath` aponta, por caminho absoluto, para o `sdd/hooks` de outra worktree do mesmo
repositório; e 3 textos de skill do pacote citam `LM-004` no sentido da semente, um número que num projeto com
playbook próprio aponta para outra regra.

## Target Users

| User | Pain Point |
|---|---|
| Aluno que usa o Open com terminal (Claude Code, Codex, Cursor…), em macOS, Linux ou Windows (Git Bash) | não fica sabendo de versão nova; não sabe o que copiar sem perder o que editou |
| Roberto, mantenedor e usuário | atualizar o próprio projeto custa uma tarde de classificação à mão |
| Quem abre uma frente ou publica | descobre tarde que está numa versão velha, com defeito já consertado |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | o pacote diz a própria versão (Release, `git archive` de tag, clone) |
| **MUST** | o `init` grava no projeto a versão instalada e a impressão (sha256) de cada arquivo do pacote que instala |
| **MUST** | o `doctor` mostra a versão do projeto e a do pacote e confere, sem token e com teto curto, se há tag maior no repositório público; nunca bloqueia nem muda o exit |
| **MUST** | a `sdd-new-session` e a FASE 0 da `sdd-release` repassam o aviso de versão nova como informação |
| **MUST** | verbo `upgrade`: copia o que é igual/novo/intacto, lista sem tocar o que foi editado, roda `sync` e `doctor`, nunca commita |
| **MUST** | nenhuma consulta de rede na suíte de testes |
| **MUST** | (a) `doctor`/`init` reconhecem o `sdd/hooks` de outra worktree do mesmo repositório como o gancho do Open |
| **MUST** | (b) nenhum texto de skill do pacote cita um ID `LM-nnn` como referência à semente |
| **SHOULD** | o diff entre as versões de cada arquivo editado, gravado para a mescla à mão |
| **COULD** | candidatos ao playbook do que morder |

---

## Success Criteria

- [ ] O tarball da Release, um `git archive vX.Y.Z` e um clone na tag dizem `vX.Y.Z`; um commit depois da tag diz `vX.Y.Z-N-g<sha>`; sem nenhuma fonte, `desconhecida`.
- [ ] `init` numa pasta sem `sdd/` grava `sdd/open-instalado.txt` com a versão e uma impressão por arquivo instalável do `MANIFEST.txt`; um 2º `init` deixa o arquivo byte a byte igual.
- [ ] `doctor` com remoto local que tem tag maior ⇒ ⚠️ com a versão nova, a do projeto e o comando; sem tag maior ⇒ ✅; remoto pendurado ⇒ "não conferido" em ≤ 7 s; o exit é o mesmo nos três casos.
- [ ] `upgrade --de <pacote v2.12.1>` numa instalação `v2.12.1` com 3 arquivos editados, a partir do pacote desta frente: os 3 não mudam e aparecem listados com o diff; todo o resto instalável fica igual ao pacote novo; `git log` e o índice do git não mudam; o `doctor` de depois não acusa "difere do pacote" para nenhum arquivo copiado.
- [ ] Os 2 defeitos do mesmo upgrade não se repetem: (a) "hooks ligados" com o `core.hooksPath` absoluto de outra worktree; (b) 0 citação `LM-nnn` de referência nos textos de skill.
- [ ] Verify Gate verde no Mac; Ubuntu e piso do macOS verdes no CI do PR, dentro dos tetos.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Ubiquitous | O pacote **shall** determinar a própria versão nesta ordem: o arquivo de versão da raiz carimbado pelo `git archive` (`export-subst`), quando carimbado com uma forma `vX.Y.Z` ou `vX.Y.Z-N-g<sha>`; senão `git describe --tags` do próprio pacote, quando ele é um clone; senão o nome da pasta `sdd-open-vX.Y.Z`; senão `desconhecida`. O job `release` do `release.yml` **shall** criar a tag localmente antes do `git archive`, para o tarball da Release sair carimbado com a tag exata | test |
| AT-002 | Event-driven | **When** o `init` roda num projeto sem `sdd/`, ele **shall** gravar `sdd/open-instalado.txt` com a versão do pacote e uma linha `<sha256>  <caminho>` por arquivo instalável do `MANIFEST.txt` (as skills do pacote em `.agents/skills/` e os arquivos de `sdd/` que o `init` completa, sem `sdd/config.yaml` nem `sdd/fixtures/`), com a impressão do conteúdo que o pacote entrega; **when** o `init` roda num projeto que já tem `sdd/`, ele **shall** deixar o registro como está (ausente continua ausente) | test |
| AT-003 | Event-driven | **When** o `doctor` roda, ele **shall** imprimir uma linha com a versão do projeto (a do registro, ou `sem registro`) e a do pacote; e, com a checagem ligada, **shall** consultar `git ls-remote --tags --refs` do repositório público (sem token, sem enviar dado do projeto) e: havendo tag `vX.Y.Z` maior que a do projeto (ou que a do pacote, sem registro), imprimir ⚠️ com a versão nova, a atual e o comando do upgrade; senão, ✅ com a última versão publicada. O exit do `doctor` **shall** ser o mesmo com e sem versão nova | test |
| AT-004 | Unwanted | **If** o remoto não responde, recusa, ou devolve lista sem nenhuma tag `vX.Y.Z`, **then** o `doctor` **shall** imprimir "não conferido" com o motivo em palavras, em até 5 s de consulta (≤ 7 s no total da checagem), e seguir com o mesmo exit; **where** a checagem está desligada (slot `open.check_updates: false` em `sdd/config.yaml`, ou a variável `SDD_OPEN_CHECK_UPDATES=0`), ele **shall** não consultar nada e dizer que está desligada e onde; **while** a suíte de testes roda, nenhuma consulta **shall** sair para a rede (a suíte desliga a checagem e aponta o remoto para um repositório local) | test |
| AT-005 | Event-driven | **When** a `sdd-new-session` abre uma frente, ou a FASE 0 da `sdd-release` começa, num projeto com o script de versão do `init`, a skill **shall** rodar a checagem e repassar ao aluno a linha de versão nova como informação, sem parar nem pedir decisão; sem o script (projeto sem `init`, starter), **shall** pular sem mensagem. A `sdd-new-session` e a `sdd-release` geradas no starter **shall** sair sem esse passo (o lint do `init` do gerador continua verde) | test |
| AT-006 | Event-driven | **When** `sdd-open.sh upgrade` roda, do pacote novo, num projeto com registro de versão menor, ele **shall** mostrar o plano e, com o OK (ou `--yes`), classificar cada arquivo instalável do `MANIFEST.txt` novo: igual ao pacote novo ⇒ nada; ausente ⇒ copiar; igual à impressão do registro (intacto) ⇒ copiar a versão nova; diferente das duas (editado) ⇒ **não tocar** e listar, gravando o diff "seu arquivo → versão nova" (e, com `--de`, "versão antiga → nova") numa pasta que ele nomeia; arquivo do registro que saiu do pacote ⇒ listar, nunca apagar; depois **shall** regravar o registro com a versão nova, rodar o `sync` e o `doctor`, e **shall** terminar sem `git add` nem `git commit`; `--dry-run` **shall** mostrar o plano sem escrever | test |
| AT-007 | Unwanted | **If** o projeto não tem registro e o `upgrade` veio sem `--de`, **then** ele **shall** parar antes de escrever, com os comandos que montam a pasta do pacote antigo; **if** `--de` não aponta para um pacote do sdd-open (sem `MANIFEST.txt` ou sem versão), ou a versão do pacote é menor que a do projeto, **then** **shall** sair 64 sem escrever; **if** a versão do pacote é igual à do projeto e nada difere, **then** **shall** dizer "em dia" e sair 0; **if** uma escrita falha no meio, **then** **shall** sair ≠ 0 sem regravar o registro, e rodar de novo **shall** retomar | test |
| AT-008 | Event-driven | **When** o `core.hooksPath` é um caminho absoluto que resolve para `<worktree>/sdd/hooks` de qualquer worktree do mesmo repositório (o `git worktree list` dele), o `doctor` **shall** dizer "hooks ligados" (citando a worktree quando não é a atual) e o `init` **shall** tratá-lo como já ligado, sem o aviso de "husky, lefthook ou outro gerenciador"; um caminho absoluto de **outro** repositório **shall continue to** ser OUTRO | test |
| AT-009 | Ubiquitous | Nenhum `SKILL.md` nem arquivo de `references/` das skills do pacote **shall** citar um ID `LM-nnn` como referência a uma regra do playbook; os exemplos de sintaxe da `sdd-playbook` e de `docs/playbook-curation.md` (formato de linha, delta do curador) **shall** ficar, numa lista de aceites com motivo | test |
| AT-010 | Non-regression | O `init`, o `sync`, o `sync --check` e o `doctor` **shall continue to** passar nos testes de hoje (o `doctor` sai 0); o `gerar-starter.py` **shall continue to** gerar o starter com o lint do `init` verde; as contagens fixadas (22 skills, versões de skill) **shall** ser atualizadas só pelos bumps desta frente; a suíte **shall continue to** passar no Ubuntu e no piso do macOS (bash 3.2, Python 3.9) | test |

While: no AT-004 (enquanto a suíte roda). Where: no AT-004 (checagem desligada). If/Then: AT-004, AT-007.

---

## Clarifications

### Session 2026-11-14

- [x] (escopo) As 4 peças entram (Roberto): versão registrada, checagem no `doctor`, aviso na frente e na release, verbo `upgrade`.
- [x] (escopo) Starter: nada além da 1ª linha da skill, que já diz a versão e o link das versões do sdd-starter (Roberto). O gerador não leva ao starter o passo do aviso.
- [x] (escopo) Os candidatos (a) hooks em outra worktree e (b) `LM-004` nos textos entram (Roberto).
- [x] (dados) O registro mora num arquivo próprio (`sdd/open-instalado.txt`), não no `sdd/config.yaml`; quem grava é o `init` (1ª instalação) e o `upgrade`; o `sync` não grava (não instala nada do pacote). Rotina, registrada no BRAINSTORM.
- [x] (edge case) Projeto sem registro (instalado antes da F22): o `upgrade` exige `--de <pasta do pacote antigo>`; sem ele, para antes de escrever com os comandos. Rotina, registrada no BRAINSTORM.
- [x] (restrições) Build só depois de a F16W2 publicar (Roberto): rebase sobre a tag nova e DESIGN reconferido antes do build.
- [x] (NFR) Teto da consulta: 5 s (medido 0,7 a 2,6 s); a checagem nunca bloqueia nem muda o exit.
- [x] (UX) Há interface de linha de comando (as mensagens do `doctor` e do `upgrade`, as linhas das skills): UX review antes do Design.
- [x] (dados) Amostras: as tags públicas deste repositório e os números do upgrade medido. Nada do projeto privado.

### Session 2026-11-14 (governança)

- [x] (governança) N.A. — revisor em contexto novo (passo 11, fronteira conferida, bloco válido), 2026-11-14: ver a linha Governança do Technical Context.

### Segurança

- [x] N.A. para a feature: sem login, rota pública, dado de terceiros, envio de arquivo, IA nem banco. Nota de construção (não é item do catálogo): o nome das tags vem do remoto e é dado não confiável — aceito só na forma `vX.Y.Z` (AT-004), nunca executado nem interpolado em comando; o `upgrade` só copia do pacote que a própria pessoa rodou e só escreve nas pastas do Constraints.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 a AT-008 num módulo novo de testes da frente (repositório git temporário com tags; remoto local por
variável de ambiente; pacote antigo montado por `git archive` de uma tag em tempo de teste) e nos módulos de hoje
(`test_sdd_open.py`, `test_release_workflow.py`, `test_matriz_new_session.py`, `test_gerar_starter.py`); AT-009 num
teste de texto sobre `.agents/skills/`; AT-010 na suíte inteira. O gate roda de um `git archive HEAD`: a pasta não é
clone, e a versão do pacote nos testes vem do repositório temporário de cada teste, nunca deste clone.

---

## Out of Scope

- Atualização automática de qualquer coisa (cron, hook que atualiza); mescla automática de arquivo editado.
- Aviso automático no starter além da 1ª linha da skill (decisão do Roberto).
- Notas da Release ou API do GitHub; cache da checagem.
- O repositório privado (o upgrade de lá é numa frente de lá, já pelo verbo novo, e é a prova de uso).
- Projetar o registro para versões anteriores sem `--de` (tabela de impressões de todas as versões no pacote).

## Constraints

- bash 3.2 e Python 3.9 stdlib; `sdd/bin/*.sh` sempre por `bash`; sem `declare -A`; exit medido sem pipe (LM-018 no zsh do agente).
- A suíte nunca vai à rede; `git ls-remote` só com `GIT_TERMINAL_PROMPT=0` e teto.
- `MANIFEST.txt` a cada arquivo novo; sem número de 11 dígitos no pacote (LM-012: montado em tempo de execução nos testes).
- O `upgrade` e o `init` nunca escrevem fora de `.agents/skills/`, `sdd/` e dos adaptadores; nunca apagam; nunca commitam.
- Build depois da F16W2 (mexe em `sdd/bin`, no `checar`, na `sdd-new-session` e no adaptador do Claude Code).
- Teto do método: 3 rodadas de revisão, 2 ciclos do avaliador; acima disso, pergunta ao Roberto.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `bin/sdd-open.sh` (init, doctor, verbo `upgrade`, hooks), arquivo de versão da raiz + `.gitattributes`, `sdd/bin/` (o script de versão que o projeto recebe), `.github/workflows/release.yml` (tag local antes do `archive`), `.agents/skills/sdd-new-session`, `.agents/skills/sdd-release`, `.agents/skills/sdd-build` (texto do LM-004), `scripts/gerar-starter.py` ou seus dados (se o passo do aviso precisar sair do starter), `MANIFEST.txt`, `tests/`, README/docs do `doctor` | `scripts/` é do mantenedor |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | só o `release.yml` |
| **LLM Prompts** | false | nenhum prompt de produção; as skills são instruções de agente, não runtime |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | — |
| **Governança** | N.A. — o DEFINE trata versão, impressões sha256 e upgrade de arquivos do pacote, sem dinheiro, lançamento, nota fiscal, tributo, folha ou dado pessoal | revisor fresco, 2026-11-14 |
| **Segurança** | N.A. — sem login, rota pública, dado de terceiros, envio de arquivo, IA nem banco (ver Clarifications) | 2026-11-14 |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | `export-subst` com `%(describe:tags=true)` carimba a tag no `git archive` (git ≥ 2.32 de quem gera o pacote) | reserva pelo nome da pasta e pelo `git describe`; medido aqui com git 2.54 | [x] medido no brainstorm |
| A-002 | O `git ls-remote` responde em < 5 s na rede comum | "não conferido" com mais frequência; medido 0,7 a 2,6 s | [x] |
| A-003 | No Git Bash, o teto da consulta funciona com o vigia que o `checar.sh` já usa no Windows (`taskkill` pelo `winpid`) | a consulta pendurada passaria do teto no Windows (o job do Windows é informativo) | [ ] |
| A-004 | O `MANIFEST.txt` da tag lista todo arquivo instalável | arquivo fora do manifesto não é atualizado; teste confere manifesto × árvore | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | medido num upgrade real |
| Users | 3 | 3 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | números e exits |
| Scope | 2 | o encaixe com a F16W2 só fecha depois que ela publicar |
| **Total** | **14/15** | |

## Open Questions

- nenhuma

## Revision History

| Versão | Data | Mudança |
|---|---|---|
| 1.0 | 2026-11-14 | primeira versão, do brainstorm |

## Next Step

**sdd-ux-review** (há interface de linha de comando), depois **sdd-design**.
