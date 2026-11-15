# DESIGN: F22 — Aviso de versão e upgrade

> O pacote passa a saber a própria versão (carimbo do `git archive`, `git describe` no clone); o `init` grava no projeto
> a versão e a impressão de cada arquivo instalado; um script do projeto confere, com teto e sem token, se há tag maior;
> o `doctor`, a abertura da frente e a release repassam o aviso; o verbo `upgrade` classifica e copia o que é do pacote
> e lista o que a pessoa editou.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F22_AVISO_VERSAO |
| **Date** | 2026-11-14 (v1.0) · 2026-11-15 (v1.1, reconferido sobre `v2.16.1`) |
| **Author** | design-agent (worktree `sdd-open-f22-aviso-versao`, branch `feat/f22-aviso-versao`, hoje em `c2690d5` = `v2.16.1`) |
| **DEFINE** | [DEFINE_F22_AVISO_VERSAO.md](DEFINE_F22_AVISO_VERSAO.md) |
| **UX REVIEW** | [UX_REVIEW_F22_AVISO_VERSAO.md](../reviews/UX_REVIEW_F22_AVISO_VERSAO.md) |
| **Status** | Ready for Build (F16W2 publicada como `v2.16.1`; reconferência da Decision 10 no Revision History) |

---

## Architecture Overview

```text
 PACOTE (clone ~/sdd-open, ou git archive/tarball de uma tag)            PROJETO DO ALUNO
 ─────────────────────────────────────────────────────────────         ─────────────────────────────────────
 VERSION  ($Format:%(describe…)$ → "v2.17.0" no archive)                 sdd/open-instalado.txt
 bin/lib/versao.sh                                                         # comentário: o que é, quem grava
   versao_do_pacote  carimbo → git describe (só se PKG é a raiz           versao: v2.17.0
                     de um clone) → pasta sdd-open-vX.Y.Z → desconhecida   <sha256>  .agents/skills/…
   instalaveis       MANIFEST.txt → .agents/skills/<do pacote>/** +        <sha256>  sdd/bin/…
                     sdd/{templates,bin,hooks,review,patterns}/** +           (impressão do conteúdo DO PACOTE)
                     sdd/{playbook.md,invariants.md,WORKFLOW_CONTRACTS.yaml}
   impressoes        sha256sum | shasum -a 256 | python3 hashlib         sdd/bin/versao-nova.sh  (cópia do init)
                                                                           └─ a sdd-new-session e a FASE 0 da
 bin/sdd-open.sh                                                               sdd-release rodam este
   init ───────── 1ª instalação (sem sdd/) ──────────────────────────▶  grava o registro
   doctor ─ linha de versão (projeto · pacote) ─────────────────────────────────────────────┐
          └ bash $PKG/sdd/bin/versao-nova.sh --raiz ROOT --atual <v> ───▶ git ls-remote --tags --refs (5 s) ─▶ GitHub (público)
   upgrade [--de <pasta|tag>] [--dry-run] [--yes] [--verbose]                                 SDD_OPEN_REMOTO (só testes)
      1. versão do pacote; registro (ou --de) → impressões antigas
      2. classifica cada instalável do MANIFEST novo: igual · novo · intacto · editado · saiu
      3. plano por classe → [y/N]
      4. copia novo + intacto; editado → sdd/upgrade/<vN>/<caminho>.novo + .diff; nunca apaga
      5. regrava o registro (tmp + mv, por último) → sync --yes → doctor; nunca git add/commit
   hooks_estado: core.hooksPath absoluto de outra worktree do MESMO repositório = LIGADO
```

---

## Key Decisions

### Decision 1: a versão do pacote vem de um arquivo carimbado pelo `git archive`, com reservas

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** o pacote não tem arquivo de versão; a Release de patch é calculada no CI e a tag é criada pelo
`gh release create` **depois** do `git archive` (`release.yml`, job `release`). O aluno instala por `git clone`
(`README.pt-BR.md:26`, guia do aluno: `git pull` em `~/sdd-open`); o mantenedor roda o pacote por `git archive` da tag.

**Choice:** `VERSION` na raiz com `$Format:%(describe:tags=true,match=v[0-9]*)$` e `VERSION export-subst` no
`.gitattributes`. `versao_do_pacote` aceita, nesta ordem: (1) o conteúdo do `VERSION` quando casa
`^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+-g[0-9a-f]+)?$`; (2) `git -C "$PKG" describe --tags --match 'v[0-9]*'`, só quando
`git -C "$PKG" rev-parse --show-toplevel` é a mesma pasta que `$PKG` (`-ef`, não a grafia: `/c/…` × `C:/…`, `/var` × `/private/var`; um pacote extraído dentro de outro repositório não
herda a versão dele); (3) o nome da pasta `sdd-open-vX.Y.Z`; (4) `desconhecida`. No `release.yml`, antes do
`git archive`: `git rev-parse -q --verify "refs/tags/$TAG" >/dev/null || git tag "$TAG" "$GITHUB_SHA"` (tag
**local**; quem publica continua sendo o `gh release create`) e, depois, a conferência
`tar -xzOf dist/… sdd-open-$TAG/VERSION` = `$TAG`, que derruba o job se não bater.

**Rationale:** funciona nos 3 modos de obter o pacote sem ninguém editar versão à mão; o carimbo é do git, não do
autor.

**Alternatives Rejected:** 1. `VERSION` editado a cada release — rejeitada: a Release de patch é automática e o
arquivo esqueceria. · 2. só o nome da pasta — rejeitada: o clone do aluno se chama `sdd-open`, sem versão. · 3. ler
a versão das skills — rejeitada: cada skill tem numeração própria.

**Consequences:** um `git archive` feito com git anterior ao 2.35 (as opções `tags=` de `%(describe:…)` entraram ali;
a tag da Release é leve, então sem `tags=true` o describe não a vê) deixa o `$Format:…$` literal e cai na reserva; o
runner do GitHub e o git do mantenedor (2.54) passam disso; um clone entre a
release e a criação da tag diz `vX.Y.Z-N-g<sha>` (a versão base mais "um pouco"), o que basta para comparar.

### Decision 2: o registro é um arquivo próprio, gravado pelo `init` só na 1ª instalação e pelo `upgrade`

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** o `upgrade` precisa saber, sem rede, se um arquivo do projeto é cópia intacta do que o pacote entregou
ou foi editado. O `sdd/config.yaml` é editado pela pessoa; o `sync` não instala nada do pacote.

**Choice:** `sdd/open-instalado.txt`: 2 linhas de comentário (o que é; "gravado pelo `init` e pelo `upgrade` — não
edite; apagar faz o próximo upgrade pedir `--de`"), `versao: <v>` e uma linha `<sha256>  <caminho>` por arquivo
instalável, em ordem, no formato do `sha256sum` (a pessoa confere com `sha256sum -c` depois de tirar as 3 primeiras
linhas). A impressão é do **conteúdo do pacote** naquele caminho, não do arquivo do projeto: o que o projeto já tinha
diferente do pacote aparece como "editado" no próximo upgrade, que é o lado seguro. O `init` grava o registro só
quando `sdd/` não existia antes dele (1ª instalação) e a versão do pacote não é `desconhecida`; em projeto que já tem
`sdd/`, o registro fica como está, ausente inclusive (um registro com as impressões do pacote novo sobre arquivos
velhos faria o upgrade tomá-los por edição). O `sync` não grava nada. Sem ferramenta de sha256
(`sha256sum`, `shasum`, `python3`), o `init` não grava e o `doctor` diz por quê.

**Rationale:** registro legível, que viaja com o projeto (commitado) e dispensa rede; um único escritor por momento.

**Alternatives Rejected:** 1. `open.version` + impressões no `sdd/config.yaml` — rejeitada: 600 linhas no arquivo que
a pessoa edita. · 2. impressão SHA-1 do `git hash-object` — rejeitada: o pedido fala em sha256 e o formato
`sha256sum` é conferível à mão; o custo é escolher entre 3 ferramentas. · 3. `init` sempre regravando — rejeitada
pelo motivo acima.

**Consequences:** projeto instalado antes da F22 fica sem registro até o 1º `upgrade --de` (Decision 5).

### Decision 3: a checagem mora num script do projeto (`sdd/bin/versao-nova.sh`), com teto que não depende de sinal

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** a `sdd-new-session` e a `sdd-release` rodam dentro do projeto e não sabem onde está o pacote; o `doctor`
roda do pacote. O teto de tempo por sinal a grupo não corta nada no Git Bash (LM-016).

**Choice:** um script só, copiado pelo `init` como todo `sdd/bin/`: `bash sdd/bin/versao-nova.sh [--raiz <dir>]
[--atual <vX.Y.Z…>]`. A versão atual vem de `--atual` ou da linha `versao:` do registro de `<raiz>`; sem nenhuma das
duas (projeto anterior à F22 que recebeu o script pelo `init`, sem registro) ⇒ `20` "não conferida — este projeto
ainda não tem o registro de versão (o doctor diz como fazer o 1º upgrade)", sem consultar a rede: as skills calam, e o
`doctor`, que passa `--atual` com a versão do pacote, avisa. Desligado se
`SDD_OPEN_CHECK_UPDATES=0` ou se `open:`→`check_updates: false` no `sdd/config.yaml` de `<raiz>`. A consulta:
`GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -c credential.helper= ls-remote --tags --refs "$REMOTO"` com
`stdin` de `/dev/null` e **stdout e stderr para um arquivo temporário** numa pasta própria (`mktemp -d`); o subshell
de segundo plano inteiro também sai com `>/dev/null 2>&1 </dev/null`, senão ele (e um neto que sobreviva ao corte no
Windows) segura o pipe de quem chamou e o teto deixa de valer para quem lê a saída (o mesmo motivo do arquivo de saída
no vigia do `checar.sh` da F16W2). Sem pasta temporária (TMPDIR sem escrita) ⇒ `20` "não conferida — sem pasta
temporária". O subshell de segundo plano liga `set -m`, põe o `git` em segundo plano **dentro dele** (o `git` vira
líder do próprio grupo, como no `checar.sh`), grava o pid do `git` em `<pasta>/pid` e espera por ele. O pai espera em
passos de 0,2 s até 5 s; passou do teto ⇒ corta o `git` pelo pid gravado (o grupo dele fora do Windows; `taskkill /F /T`
pelo `/proc/<pid>/winpid` no Git Bash, como o `checar.sh`) e o subshell, e responde "sem resposta em 5 s" **sem
esperar o corte**.
`REMOTO` = `SDD_OPEN_REMOTO` ou `https://github.com/robertodiasduarte/sdd-open.git`. Do que voltou, só linhas
`refs/tags/vX.Y.Z` exatas contam; a maior sai por comparação numérica campo a campo (awk). Saídas (uma linha, com
símbolo e palavra, textos do UX U1 a U3): `0` em dia · `10` versão nova · `20` não conferida · `30` desligada ·
`64` uso. Nunca escreve nada.

**Rationale:** um teto que vale no Windows porque o retorno não depende de o filho morrer; um lugar só para o teto,
o opt-out e o "sem rede".

**Alternatives Rejected:** 1. a checagem dentro do `sdd-open.sh` — rejeitada: as skills não acham o pacote. · 2. API
do GitHub (`/releases/latest`) — rejeitada: cota, JSON, e não diz mais que o `ls-remote` para "há versão maior". ·
3. `http.lowSpeedTime` como teto — rejeitada: não cobre DNS nem conexão pendurada.

**Consequences:** projeto sem o script (instalado antes da F22) não tem o aviso na frente nem na release até o
upgrade; o `doctor` do pacote novo avisa assim mesmo (usa a cópia do pacote).

### Decision 4: `doctor` com 2 linhas de versão; o exit não muda

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** UX U1 a U3: uma linha de estado, a 2ª só quando há o que dizer; nunca ⚠️ por falta de rede.

**Choice:** logo depois da linha `bash · git · python3`: `✅ versão: projeto <vP> · pacote <vK>` (ou
`ℹ️ versão: projeto sem registro (instalado antes da v2.17.0) · pacote <vK> — o 1º upgrade pede --de <a versão que o
projeto tem>`); depois, a linha do `versao-nova.sh` do **pacote** com `--raiz ROOT --atual <vP ou vK>`: exit 0 ⇒ o
✅ dele; 10 ⇒ o ⚠️ dele e uma linha `→ <como atualizar>`: com o pacote num clone, `git -C <PKG> pull` e
`bash <PKG>/bin/sdd-open.sh upgrade --dry-run` (U13); sem clone (tarball, `git archive`), a URL da Release da versão
nova e `bash <pasta do pacote novo>/bin/sdd-open.sh upgrade --dry-run` (o comando que o AT-003 pede, com a pasta por
preencher); 20 e 30 ⇒ o ℹ️ dele. O
`doctor` segue saindo 0. Os 3 avisos atuais de "apague e rode init" (skill mais velha, skill faltando, `sdd/bin`
diferente) passam a dizer "rode o upgrade (ele copia o que é do pacote e não toca no que você editou)".

**Rationale:** o mesmo `doctor` de hoje com uma informação a mais; o caminho de atualização aponta para o verbo novo.

**Alternatives Rejected:** 1. ⚠️ sem rede — rejeitada (U2). · 2. exit 1 com versão nova — rejeitada (nunca bloqueia).

**Consequences:** todo `doctor` (e todo `init`, que termina nele) faz uma consulta de ~1 s; a suíte desliga (Decision 8).

### Decision 5: `upgrade` classifica pelo `MANIFEST.txt` novo e pelas impressões antigas; editado nunca é tocado

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** o caso real: 157 iguais, 46 novos, 43 intactos, 3 editados; o `init` não completa arquivo novo dentro de
skill existente; a pessoa decide e commita.

**Choice:** `bash <pacote novo>/bin/sdd-open.sh upgrade [--de <pasta|tag>] [--dry-run] [--yes] [--verbose]`, de dentro
do projeto:
1. Pré-condições: `sdd/` e `.agents/skills/` existem (senão 🛑 "rode init"); versão do pacote conhecida (senão 🛑).
2. Impressões antigas: do registro; ou, com `--de`, calculadas do pacote antigo: uma pasta com `MANIFEST.txt`, ou
   uma tag que exista no clone do pacote (`git -C "$PKG" archive <tag>` para uma pasta temporária). A versão do pacote
   antigo: na forma tag, o próprio nome da tag (`vX.Y.Z` exato); na forma pasta, `versao_do_pacote` daquela pasta
   (pacotes anteriores à F22 não têm `VERSION`: valem o clone e o nome `sdd-open-vX.Y.Z`, e por isso os comandos do
   U6 montam a pasta com `git -C ~/sdd-open archive --prefix=sdd-open-vX.Y.Z/ vX.Y.Z | tar -x -C <tmp>` ou mandam
   usar a forma tag). Sem registro e sem `--de` ⇒ 🛑 com os comandos (U6), nada escrito. `--de` que não é pacote
   (sem `MANIFEST.txt`, ou versão `desconhecida`, com o `→` dizendo para usar a forma tag ou o `--prefix`) ⇒ 64. Versão
   do pacote menor que a do projeto ⇒ 64 (sem rebaixar).
3. Instalável = linha do `MANIFEST.txt` que é arquivo de uma skill do pacote (`.agents/skills/<skill de
   skills_da_fonte>/…`) ou de `sdd/` sob as mesmas entradas que o `sdd_faltantes` completa (`templates bin hooks review
   patterns playbook.md invariants.md WORKFLOW_CONTRACTS.yaml`); a lista dessas entradas vira uma variável só, lida
   pelas duas funções, para não divergirem. Para cada instalável do `MANIFEST.txt` novo, com `p` = arquivo do projeto,
   `n` = impressão nova, `a` = antiga:
   ausente ⇒ **novo** · `sha(p) = n` ⇒ **igual** · `sha(p) = a` ⇒ **intacto** · senão ⇒ **editado**. Caminho que
   está no registro antigo e saiu do `MANIFEST.txt` novo ⇒ **saiu** (lista, nunca apaga). Sem `--de` e com
   registro, um arquivo sem linha no registro e diferente do novo é **editado** (lado seguro).
4. `--de` com menos da metade dos instaláveis presentes iguais ao pacote antigo ⇒ ⚠️ do U9 antes do `[y/N]`.
5. Plano por classe (U4), `[y/N]` pelo `confirmar` de hoje; `--dry-run` para aqui com `RESULTADO: DRY-RUN`; nada a
   copiar e nada editado ⇒ `RESULTADO: EM DIA`.
6. Copia **novo** e **intacto** (`mkdir -p`; `cp` para `<destino>.sddtmp` e `mv`; bit de execução igual ao do pacote);
   cada **editado** ganha `sdd/upgrade/<vN>/<caminho>.novo` (a versão nova) e `<caminho>.diff` (`diff -u` do arquivo
   do projeto para a versão nova; com o pacote antigo à mão, também `<caminho>.pacote.diff`, antigo → novo).
7. Por último, regrava o registro (`.sddtmp` + `mv`) com a versão nova e as impressões novas; falha no meio ⇒ 🛑
   sem tocar no registro (rodar de novo retoma: o que já foi copiado vira **igual**).
8. Roda `bash "$0" sync --yes` (AGENTS.md e adaptadores, com os vendors do config) e o `doctor`; fecho do U5. Nunca
   `git add`, `git commit`, `git stash`.

**Rationale:** é a classificação que o upgrade à mão fez, pelas impressões em vez de 2 `git archive`; a pasta
`sdd/upgrade/<vN>/` sobrevive até a pessoa mesclar e o `→` diz que ela não precisa ir para o git.

**Alternatives Rejected:** 1. sem registro, listar tudo que difere — rejeitada (listaria os 43 intactos). · 2. `.novo`
numa pasta temporária — rejeitada: some num reboot antes da mescla. · 3. rodar `init` no fim — rejeitada: o `init`
exige `--vendors` e não acrescenta nada depois da cópia; o `sync` faz o AGENTS.md e os adaptadores.

**Consequences:** `sdd/upgrade/` aparece no `git status` até a pessoa apagar (o fecho diz).

### Decision 6: hooks de outra worktree do mesmo repositório contam como ligados

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** as worktrees dividem o `.git/config`; um `core.hooksPath` absoluto para `<worktree A>/sdd/hooks` vale
para todas, e hoje `hooks_path_e_nosso` (`bin/sdd-open.sh:542`) só aceita a pasta da raiz atual.

**Choice:** `hooks_path_e_nosso` também aceita o caminho absoluto (`/…` ou `C:\…`/`C:/…`, como a F16W2 deixou) que é a
mesma pasta (`-ef`, o critério da F16W2: link, `/tmp` do macOS, `/c/…` × `C:/…`) que `<w>/sdd/hooks` de algum `w` de
`git worktree list --porcelain` (linhas `worktree <caminho>`); guarda esse `w` em `HOOKS_OUTRA_WT` quando não é a raiz
atual. `doctor` ⇒ `✅ hooks ligados (pelo sdd/hooks de outra worktree deste repositório: <w>)` (U11), com a conferência
do bit de execução feita na pasta de `w`. O `init` vê LIGADO e não mexe. Caminho absoluto de outro repositório segue
OUTRO.

**Rationale:** o falso alarme some sem mudar o `.git/config` de ninguém.

**Alternatives Rejected:** 1. o `init` reescrever para `sdd/hooks` relativo — rejeitada: muda a config de todas as
worktrees sem perguntar.

**Consequences:** os hooks que rodam são os da outra worktree (versão dela); a linha do `doctor` diz de onde.

### Decision 7: textos de skill citam a regra pelo texto, não pelo `LM-nnn`

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** `sdd-build/SKILL.md:189` e `:299` e `sdd-release/references/como-falar.md:119` citam `LM-004` como a
semente "exit 0 não prova a migration"; o playbook do projeto pode ter outra regra nesse número.

**Choice:** trocar a citação por "(a armadilha da migration que sai `exit 0` sem estar no banco)" ou equivalente curto;
um teste varre `.agents/skills/**/*.md` por `\bLM-[0-9]{3}\b` com uma lista de aceites com motivo (os exemplos de
sintaxe da `sdd-playbook`: `SKILL.md` e `references/`, que mostram o formato da linha e do delta).

**Rationale:** o texto da skill vale em qualquer projeto; o número só vale no playbook que o nomeou.

**Alternatives Rejected:** 1. o `init` avisar da correspondência — rejeitada: o aviso não conserta o texto.

**Consequences:** bump patch da `sdd-build` (2.10.0 → 2.10.1); a `sdd-release` já sobe minor pela Decision 9.

### Decision 8: a suíte não vai à rede por construção

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** o `doctor` roda no fim de todo `init`, e dezenas de testes rodam `init`.

**Choice:** `tests/apoio.py`, na importação, põe em `os.environ` (sem sobrescrever o que já veio)
`SDD_OPEN_CHECK_UPDATES=0` e `SDD_OPEN_REMOTO=<pasta inexistente sob o tmp>`; o `Teste.env` herda. Os testes da
checagem ligam a checagem e apontam `SDD_OPEN_REMOTO` para um repositório local com tags (ou um `git` falso que
pendura). `tests/test_alarme.py` já importa o `apoio` desde a F16W2 (`SO_NO_WINDOWS`), então herda. Um teste de
guarda reprova módulo de teste que cite `sdd-open.sh` sem importar o `apoio`. Os jobs de teste dos 2 workflows e o
`cmd` do Verify Gate não precisam de variável própria (o `apoio` cobre), mas o `env:` dos jobs ganha
`SDD_OPEN_CHECK_UPDATES: '0'` como segunda trava.

**Rationale:** a guarda está onde todo teste passa; o remoto inválido garante que, mesmo ligada por engano, a
consulta falha local, sem rede.

**Alternatives Rejected:** 1. só o env dos workflows — rejeitada: o gate do Mac roda fora deles.

**Consequences:** um teste novo que monte o ambiente do zero sem o `apoio` escapa da guarda; o teste de guarda pega o
caso que cita `sdd-open.sh`.

### Decision 9: o aviso nas skills é 1 frase, sem decisão; o starter não o recebe

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** UX U7; decisão do Roberto: o starter fica só com a 1ª linha da skill.

**Choice:** `sdd-new-session` (1.6.1 → 1.7.0), no Passo 3 — Responda: se a frente tem `sdd/bin/versao-nova.sh`, rode
`bash sdd/bin/versao-nova.sh` de dentro dela; exit 10 ⇒ acrescente a frase do U7 com as 2 versões da linha; qualquer
outro exit ou script ausente ⇒ nada. `sdd-release` (2.12.1 → 2.13.0; a F16W2 publicou a 2.12.1), FASE 0, antes da
0a: o mesmo, como informação no relatório da fase e no bloco do OK, sem abortar nada. No starter: um bloco novo em
`scripts/starter/trocas/sdd-new-session.md` tira o parágrafo (a troca casa 1 vez, senão o gerador sai 65); a
`sdd-release` do starter sai do `MODO_INICIANTE.md`, cujo texto não muda; só a 1ª linha acompanha a versão (2.13.0),
como a F16W2 fez com a 2.12.1.

**Rationale:** o aluno fica sabendo sem ter de decidir; o lint do `init` do gerador continua verde.

**Alternatives Rejected:** 1. perguntar se quer atualizar agora — rejeitada (U7, nunca para).

**Consequences:** o starter precisa ser gerado de novo pela tag (a versão da `sdd-new-session` muda), com o OK próprio
do Roberto para push, PR e merge lá.

### Decision 10: o que fica para depois da F16W2

| **Status** | Accepted | · | **Date** | 2026-11-14 |
|---|---|---|---|---|

**Context:** a F16W2 mexe em `sdd/bin` (stdout UTF-8 dos scripts Python), no vigia do `checar.sh` (askpass, `gh`),
na `sdd-new-session` e no adaptador do Claude Code; já trouxe ao playbook LM-029 a LM-031 e promoveu a LM-012.

**Choice:** antes do build: rebase de `feat/f22-aviso-versao` sobre a tag da F16W2; reconferir (a) o corte do vigia
que a F16W2 deixar no `checar.sh` (a Decision 3 copia o padrão dele), (b) a versão da `sdd-new-session` e da
`sdd-release` (os bumps partem do que ela publicou), (c) os testes que fixam versões e contagens, (d) a varredura do
playbook com as LM novas, (e) `tests/apoio.py` (ela mexe nele); registrar o resultado no Revision History.

**Rationale:** decisão do Roberto (build depois da F16W2); o que este DESIGN copia do vigia pode mudar.

**Consequences:** o build só começa depois da publicação da F16W2.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `VERSION` | Create | o carimbo `$Format:%(describe:tags=true,match=v[0-9]*)$` (Decision 1) | (general) | None |
| 2 | `.gitattributes` | Modify | `VERSION export-subst` | (general) | 1 |
| 3 | `bin/lib/versao.sh` | Create | `versao_do_pacote`, `versao_valida`, `versao_menor` (com sufixo `-N-g`), `instalaveis`, `impressoes` (sha256 por 3 ferramentas) | (general) | 1 |
| 4 | `sdd/bin/versao-nova.sh` | Create | a checagem com teto e opt-out, exits 0/10/20/30/64 (Decision 3) | (general) | None |
| 5 | `bin/sdd-open.sh` | Modify | carrega `versao.sh`; `init` grava o registro (Decision 2); `doctor` com as linhas de versão e os avisos que apontam o upgrade (Decision 4); verbo `upgrade` (Decision 5); hooks de outra worktree (Decision 6); ajuda e lista de verbos | (general) | 3, 4 |
| 6 | `sdd/config.example.yaml` | Modify | bloco `open:` com `check_updates: true` comentado (o que faz `false`) | (general) | 4 |
| 7 | `.github/workflows/release.yml` | Modify | tag local antes do `git archive` e a conferência do `VERSION` no tarball; `SDD_OPEN_CHECK_UPDATES: '0'` nos jobs de teste | (general) | 1 |
| 8 | `.github/workflows/publish-gate.yml` | Modify | `SDD_OPEN_CHECK_UPDATES: '0'` nos jobs de teste | (general) | None |
| 9 | `tests/apoio.py` | Modify | defaults de ambiente sem rede (Decision 8) | (general) | None |
| 10 | `.agents/skills/sdd-release/references/MODO_INICIANTE.md` | Modify | só a 1ª linha: `sdd-release v2.13.0` (o `test_alarme.py` da v1.0 saiu daqui: já importa o `apoio` desde a F16W2) | (general) | 14 |
| 11 | `tests/test_f22_versao.py` | Create | AT-001 a AT-005, AT-008, AT-009 e a guarda de rede | (general) | 1–9 |
| 12 | `tests/test_f22_upgrade.py` | Create | AT-006 e AT-007 sobre um pacote falso montado no teste (roda sempre, inclusive no gate); e um teste próprio com o pacote real `git archive v2.12.1` deste clone, que roda onde há tags (CI, `fetch-depth: 0`; máquina do mantenedor) e, sem a tag (gate de `git archive`), é **pulado com o motivo**, nunca troca de pacote em silêncio | (general) | 5 |
| 13 | `.agents/skills/sdd-new-session/SKILL.md` | Modify | o aviso no Passo 3; 1.7.0 | (general) | 4 |
| 14 | `.agents/skills/sdd-release/SKILL.md` | Modify | o aviso na FASE 0; 2.13.0 | (general) | 4 |
| 15 | `.agents/skills/sdd-release/references/como-falar.md` | Modify | sem `LM-004` (Decision 7) | (general) | None |
| 16 | `.agents/skills/sdd-build/SKILL.md` | Modify | sem `LM-004` (2 lugares); 2.10.1 | (general) | None |
| 17 | `scripts/starter/trocas/sdd-new-session.md` | Modify | tira do starter o parágrafo do aviso | (general) | 13 |
| 18 | `docs/upgrade.md` | Create | como atualizar (EN): quando, os comandos, as classes do plano, o caso sem registro, como mesclar | (general) | 5 |
| 19 | `docs/pt-BR/upgrade.md` | Create | o mesmo em PT | (general) | 5 |
| 20 | `docs/pt-BR/guia-do-aluno.md` | Modify | "Quando sair versão nova" pelo `upgrade`; a linha da tabela de problemas | (general) | 5 |
| 21 | `docs/cli-conventions.md` | Modify | palavras `ATUALIZADO`, `ATUALIZADO, N PARA MESCLAR`; exits do `upgrade` e do `versao-nova.sh` | (general) | 4, 5 |
| 22 | `README.md`, `README.pt-BR.md`, `docs/quickstart.md`, `docs/pt-BR/quickstart.md` | Modify | o verbo `upgrade` onde os verbos são listados; o link para `upgrade.md` | (general) | 18, 19 |
| 23 | `MANIFEST.txt` | Modify | `VERSION`, `bin/lib/versao.sh`, `sdd/bin/versao-nova.sh`, os 2 `upgrade.md`, os 2 testes | (general) | 1–19 |
| 24 | testes que fixam versão (medido sobre `v2.16.1`): `test_contrato_build_release`, `test_correcoes_w0`, `test_f14_drive_textos`, `test_f14_textos`, `test_f15_slots_textos`, `test_f16_textos`, `test_f17b_textos`, `test_f18_f20_textos`, `test_f19_textos`, `test_matriz_new_session` (e contagem que a suíte acusar) | Modify | as versões novas das 3 skills | (general) | 13, 14, 16 |

**Total Files:** 24 linhas (a 22 com 4 arquivos; a 24 com 10)

---

## Landmines aplicáveis

Varredura rodada em 2026-11-14 sobre `ad32fe1` (o playbook da F16W2, com LM-029 a LM-031, entra na reconferência da
Decision 10). Termos: doctor, init, sync, MANIFEST, hooksPath, worktree, git archive, sha256, ls-remote, teto, timeout,
Windows, PIPESTATUS, 11 dígitos, winpid, taskkill, export-subst, tag, rede, starter, contagem, text=True.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| script que só roda dentro de git passa local e falha no gate (cópia sem `.git`) | LM-006 | ✔ tratado | o gate roda de `git archive HEAD`: `versao_do_pacote` não pode exigir `.git` (reserva até `desconhecida`); os testes montam o próprio repositório temporário e nunca dependem da versão deste clone; os testes de upgrade conferem exit exato |
| sabotagem com `git checkout --` apaga conserto não commitado | LM-009 | ✔ tratado | sabotagens só numa cópia de `git archive`, depois do commit |
| engine da OpenRouter que passa do teto é cobrada | LM-010 | ✔ tratado | revisão com o modelo já medido (qwen como auditor); `/credits` antes e depois de cada rodada |
| 11 dígitos seguidos no pacote barram o publish-gate; SHA-256 inteiro arrisca | LM-012 | ✔ tratado | nenhum sha256 inteiro em arquivo do pacote (os testes calculam em tempo de execução); o registro só existe no projeto do aluno; docs citam prefixo de 12 |
| `text=True` sem `encoding` no Windows | LM-014 | ✔ tratado | os testes novos usam o `roda` do `apoio` (UTF-8); o `upgrade` não usa Python para texto |
| teto por sinal a grupo não corta no Git Bash | LM-016 | ✔ tratado | Decision 3: o retorno não depende de o filho morrer (saída em arquivo, pai com relógio próprio); o corte é melhor-esforço, com `taskkill` no Windows |
| fallback silencioso esconde o caminho errado | LM-017 | ✔ tratado | cada reserva de `versao_do_pacote` tem teste que prova qual fonte respondeu (carimbo, describe, pasta, desconhecida) |
| `${PIPESTATUS[0]}` vazio no zsh | LM-018 | ✔ tratado | logs de evidência por script bash com `rc=$?` |
| gerador que escreve tag em cada arquivo muda tudo | LM-022 | N.A. | o `VERSION` é um arquivo só, na raiz, e não vai para o starter (o gerador não o copia) |
| `ls a b` sai ≠ 0 quando um falta | LM-025 | ✔ tratado | o `doctor` testa existência com `[ -f ]` num laço (registro, script do projeto) |
| `subprocess.run(["bash", …])` acha o bash do WSL no Windows | LM-029 | ✔ tratado | os testes novos chamam o bash pelo `BASH`/`roda` do `apoio`, nunca pelo nome |
| executor que põe `PYTHONIOENCODING` mascara o cp1252 do aluno | LM-030 | ✔ tratado | os testes novos não põem `PYTHONIOENCODING` no ambiente; o `versao-nova.sh` e o `upgrade` são bash e não imprimem por Python |
| teste de tempo cai sob carga | LM-031 | ✔ tratado | o teste do teto mede só o limite de cima (≤ 7 s para um teto de 5 s) e usa um `git` falso que pendura, não a rede |
| no Git Bash cada processo custa 10–20 ms (F16W2, `extensao_de`) | F16W2 | ✔ tratado | impressões em lote (`xargs sha256sum` uma vez para o pacote e uma para o projeto), nunca um `sha256sum` por arquivo no laço do `upgrade` |

---

## Contrato de aceite

**N.A. (1 camada)** — o manifest toca só o pacote de linha de comando (shell, testes, textos de skill e docs); sem
segunda camada (banco, edge, UI web).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1–24 | o repositório não tem agentes especializados; o Build faz direto |

---

## Code Patterns

### Pattern 1: consulta com teto que não depende de sinal (`sdd/bin/versao-nova.sh`)

```bash
s="$(mktemp -d 2>/dev/null)" || {
  printf 'ℹ️  versão nova: não conferida — sem pasta temporária para a consulta (o resto do diagnóstico vale)\n'; exit 20; }
( set -m                             # o git, posto em 2º plano AQUI, vira líder do próprio grupo
  GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -c credential.helper= ls-remote --tags --refs "${REMOTO}" \
    </dev/null >"${s}/out" 2>"${s}/err" &
  echo "$!" >"${s}/pid"
  wait "$!"; echo "$?" >"${s}/rc" ) </dev/null >/dev/null 2>&1 &   # o subshell também solta o pipe de quem chamou
sub=$!
i=0
while [ ! -s "${s}/rc" ] && [ "${i}" -lt 25 ]; do sleep 0.2; i=$((i + 1)); done
if [ ! -s "${s}/rc" ]; then
  corta "$(cat "${s}/pid" 2>/dev/null)" "${sub}"   # grupo do git fora do Windows; taskkill /F /T pelo winpid no Git Bash
  rm -rf "${s}" 2>/dev/null          # o filho, se sobreviver, escreve num arquivo apagado: ninguém espera por ele
  printf 'ℹ️  versão nova: não conferida — sem resposta em 5 s (o resto do diagnóstico vale)\n'; exit 20
fi
```

### Pattern 2: a maior tag `vX.Y.Z` e a comparação com sufixo

```bash
maior="$(sed -n 's#^[0-9a-f]*[[:space:]]refs/tags/\(v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)$#\1#p' "${s}/out" \
  | awk -F'[v.]' '{ k = sprintf("%09d%09d%09d", $2, $3, $4); if (k > m) { m = k; v = $0 } } END { print v }')"
# versao_menor A B: compara só vX.Y.Z; "vX.Y.Z-N-g<sha>" vale como um pouco depois de vX.Y.Z (nunca menor que ela)
```

### Pattern 3: impressão sha256 portátil (`bin/lib/versao.sh`)

```bash
impressoes() { # stdin: caminhos relativos a $1, um por linha → stdout: "<sha256>  <caminho>"
  local base="$1"
  if command -v sha256sum >/dev/null 2>&1; then (cd "${base}" && tr '\n' '\0' | xargs -0 sha256sum)
  elif command -v shasum >/dev/null 2>&1; then (cd "${base}" && tr '\n' '\0' | xargs -0 shasum -a 256)
  elif sdd_python_pronto; then (cd "${base}" && python3 -I -c 'import hashlib,sys
for l in sys.stdin.read().split("\n"):
    if l: print(hashlib.sha256(open(l,"rb").read()).hexdigest() + "  " + l)')
  else return 2; fi | sed 's/^\([0-9a-f]\{64\}\) [ *]/\1  /'   # o sha256sum do Git Bash pode marcar binário com "*"
}
```

Quem lê o registro também aceita `<sha> *<caminho>` (normaliza igual), para um registro gravado em outro sistema.

candidato a pattern: shell (consulta de rede com teto que vale no Git Bash).

---

## Data Flow

1. `init` (1ª vez) → copia → `instalaveis` do `MANIFEST.txt` do pacote → `impressoes` do pacote → `sdd/open-instalado.txt`.
2. `doctor` → lê `versao:` do registro → `versao-nova.sh` do pacote → `ls-remote` (5 s) → 1 linha.
3. `sdd-new-session` / `sdd-release` → `bash sdd/bin/versao-nova.sh` da frente → exit 10 ⇒ 1 frase ao aluno.
4. `upgrade` → registro ou `--de` → classificação → plano → cópia → registro novo → `sync` → `doctor`.

---

## Integration Points

| Sistema | Como | Falha |
|---|---|---|
| GitHub (repositório público `sdd-open`) | `git ls-remote --tags --refs` anônimo | "não conferida", sem mudar exit |
| `gerar-starter.py` | troca nova em `trocas/sdd-new-session.md` | troca que não casa ⇒ 65 no gerador (teste de hoje pega) |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| AT-001 | as 4 fontes de `versao_do_pacote` (repositório temporário com tag e `export-subst`; `git archive`; clone; pasta `sdd-open-v9.8.7` sem git; nenhuma); texto do `release.yml` (tag local antes do `archive`, conferência do `VERSION`) | unittest | cada fonte prova que respondeu |
| AT-002 | `init` sem `sdd/` grava o registro (versão + uma linha por instalável, impressão = sha256 do pacote); 2º `init` byte a byte igual; `init` com `sdd/` prévio não cria | unittest | — |
| AT-003/004 | `versao-nova.sh` e `doctor` com remoto local com tag maior (10), igual (0), sem tag `vX.Y.Z` (20), caminho inexistente (20), `git` falso que pendura com neto (20 em ≤ 7 s), desligado por slot e por env (30, nenhuma chamada ao `git` falso), tag com lixo (`v1.2.3-rc`, `v1.2`) ignorada; exit do `doctor` 0 nos casos | unittest | teto medido |
| AT-005 | texto das 2 skills (o passo, o "nada" nos outros exits, sem pergunta); `gerar-starter.py` sobre a tag de teste: a `sdd-new-session` gerada sem `versao-nova.sh` e lint do `init` verde | unittest | — |
| AT-006 | upgrade de uma instalação montada de um pacote antigo (com 3 arquivos editados, 1 arquivo que sai do pacote, 1 novo dentro de skill existente) para o pacote desta árvore: classes, `.novo`/`.diff`, registro novo, `git log`/índice iguais, `doctor` sem "difere do pacote" no que copiou; `--dry-run` não escreve | unittest | — |
| AT-007 | sem registro e sem `--de` (para, nada escrito); `--de` que não é pacote (64); pacote mais velho (64); em dia (0, `EM DIA`); escrita que falha (diretório sem permissão) ⇒ ≠0 e registro intacto; 2ª rodada retoma | unittest | — |
| AT-008 | `core.hooksPath` absoluto para o `sdd/hooks` de outra worktree (LIGADO, texto do U11) e de outro repositório (OUTRO) | unittest | — |
| AT-009 | varredura de `LM-[0-9]{3}` nas skills com a lista de aceites | unittest | — |
| AT-010 | a suíte inteira; guarda de rede (módulo que cita `sdd-open.sh` importa o `apoio`) | unittest | — |
| Sabotagens | 8 mutantes numa cópia de `git archive`: teto 25→250 passos; maior tag por ordem de texto; intacto vira copiado sem conferir; editado sobrescrito; registro regravado antes da cópia; `init` regravando com `sdd/` prévio; hooks de outro repositório aceitos; guarda de rede desligada | script bash | 8 de 8 mortos |

---

## Error Handling

| Erro | Resposta |
|---|---|
| sem rede, remoto recusa, teto | `ℹ️ … não conferida — <motivo>`; exit do `doctor` 0 |
| sem ferramenta sha256 | `init` não grava o registro; `doctor` diz "sem sha256sum, shasum nem python3: o registro de versão não foi gravado"; `upgrade` 🛑 com o que instalar |
| `upgrade` sem registro, sem `--de` | 🛑 + `RESULTADO: ERRO` + `→` os 2 comandos (U6); nada escrito |
| escrita que falha | 🛑 com o arquivo; registro intacto; "rode de novo, ele retoma" |
| versão do pacote `desconhecida` | `upgrade` 🛑 "não sei a versão deste pacote: baixe pela Release ou rode do clone"; `init` instala sem registro e o `doctor` diz |

---

## Configuration

```yaml
# sdd/config.example.yaml (bloco novo, comentado)
open:
  check_updates: true   # false: o doctor, a abertura de frente e a release não consultam se saiu versão nova
```

Variáveis: `SDD_OPEN_CHECK_UPDATES=0` (desliga), `SDD_OPEN_REMOTO` (outro endereço; usado pelos testes).

---

## Segurança

1. **Onde mora cada segredo:** N.A. — nenhum segredo; o `ls-remote` é anônimo e roda com `credential.helper` vazio e sem prompt, para não oferecer credencial do aluno ao endereço.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** N.A. — nenhuma; o nome das tags que volta é dado não confiável, aceito só na forma `vX.Y.Z` e nunca executado.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** N.A. — a linha Segurança do DEFINE é N.A.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | as linhas do `doctor` e o plano/fecho do `upgrade`; nada gravado além do registro e de `sdd/upgrade/<vN>/` |
| Metrics | N.A. |
| Tracing | N.A. |

---

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| R1 | versão de um `--de` anterior à F22 (sem `VERSION`) | MED | APLICADA | Decision 5, passo 2: forma tag usa o nome da tag; forma pasta pede `--prefix=sdd-open-vX.Y.Z/` (U6) |
| R2 | o gate (`git archive`, sem tags) nunca exercita o pacote real | MED | APLICADA | manifest 12: teste com o pacote falso sempre; teste com `v2.12.1` real no CI (`fetch-depth: 0` em `publish-gate.yml:24`) e pulado com motivo no gate |
| R3 | lista fixa de instaláveis ≠ o que o `init` completa (ex.: `config.example.yaml`) | MED | REBATIDA_EVIDENCIA | `bin/sdd-open.sh:641`: o `sdd_faltantes` completa `templates bin hooks review patterns playbook.md invariants.md WORKFLOW_CONTRACTS.yaml` e o `config.yaml` (a partir do example, que não é instalado); a Decision 5 passou a ler a mesma variável |
| R4 | `sha256sum` do Git Bash com `*` antes do caminho | MED | APLICADA | Pattern 3 normaliza na escrita e na leitura |
| R5 | `mktemp -d` falho sai 20 calado | LOW | APLICADA | Pattern 1 imprime o motivo |
| R6 | `set -m` no subshell não dá grupo ao pid guardado | LOW | APLICADA | Decision 3 e Pattern 1: o `git` vai a 2º plano dentro do subshell, pid em arquivo, corte pelo pid do `git` |
| R7 | sem clone, o aviso não traz o comando do upgrade | LOW | APLICADA | Decision 4: URL + `bash <pasta do pacote novo>/bin/sdd-open.sh upgrade --dry-run` |
| R8 | `versao-nova.sh` sem `--atual` e sem registro | LOW | APLICADA | Decision 3: `20` com o motivo, sem rede; o `doctor` avisa |
| R9 | `%(describe:tags=…)` exige git 2.35, não 2.32 | LOW | APLICADA | Decision 1, Consequences |
| 2·R1 | "é a raiz do clone" por igualdade de texto falha com `/c/…` × `C:/…` e `/var` × `/private/var` | MED | APLICADA | Decision 1: a comparação é `-ef` (`bin/lib/versao.sh`, `versao_do_pacote`); teste `test_describe_pelo_caminho_de_um_link` |
| 2·R2 | ~250 sha256 inteiros no registro podem ser barrados pela trava de CPF ao commitar | MED | REBATIDA_EVIDENCIA | `.agents/skills/sdd-higiene-dado/scripts/pre-commit.sh:84-87`: o alarme só confere um token inteiro de dígitos; um sha256 é um token de 64 caracteres hexadecimais, nunca só dígitos; `sdd/hooks` e `sdd/bin` não têm regra de 11 dígitos (o publish-gate é do pacote, e o registro só existe no projeto) |
| 2·R3 | o teste do AT-009 varre só `*.md` | LOW | APLICADA | `test_skill_e_references_sem_lm_nnn` varre `SKILL.md` e todo arquivo de `references/` |
| 2·R4 | doctor sem versão do pacote e sem registro; exit 64 do script | LOW | APLICADA | Decision 4: versão `desconhecida` ⇒ 2 linhas ℹ️ sem consulta; outro exit ⇒ "não conferida — o script de versão saiu N" |
| 2·R5 | "instalado antes da v2.17.0" é falso para registro apagado | LOW | APLICADA | texto: "sem registro de versão (instalado antes da v2.17.0, ou o registro foi apagado)" |
| 2·R6 | o doctor manda rodar o upgrade para arquivo editado, que o upgrade não toca | LOW | APLICADA | Decision 4: com o registro na versão do pacote, "é edição sua, que o upgrade não toca; para voltar à do pacote, apague o arquivo e rode o upgrade"; teste `test_avisos_antigos_apontam_o_upgrade` |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-14 | design-agent | Initial version (sobre `ad32fe1`; reconferir depois da F16W2 — Decision 10) |
| 1.1 | 2026-11-15 | design-agent | Decision 10 cumprida sobre `v2.16.1` (`c2690d5`, avanço rápido da branch, sem conflito): (a) o vigia do `checar.sh` agora manda a saída para arquivo e anuncia o corte por marca; a Decision 3 já não dependia do exit, e ganhou o subshell de segundo plano sem o pipe de quem chamou e o caso TMPDIR sem escrita · (b) `sdd-release` publicada em 2.12.1 (→ 2.13.0, ainda minor), `sdd-new-session` 1.6.1 e `sdd-build` 2.10.0 sem mudança; a 1ª linha do `MODO_INICIANTE.md` acompanha (linha 10 do manifest) · (c) os 10 testes que fixam versão listados na linha 24 · (d) LM-029, 030 e 031 na varredura, e o custo por processo no Git Bash · (e) `apoio.py` ganhou `path_restrito`, `apaga`, `caminho_neutro`, `SO_NO_WINDOWS` e o `write_text` com LF, mas nenhuma variável de ambiente: a Decision 8 vale; o `test_alarme.py` já importa o `apoio` · Decision 6 pelo `-ef` e pela forma `C:/…` que a F16W2 trouxe · o job do Windows entrou no `needs:` da release (o CI da F22 precisa ficar verde lá) |
| 1.3 | 2026-11-15 | design-agent | Revisão adversarial, rodada 2 (`EXTERNAL_REVIEW_20261115-055723`; claude revisou; o auditor qwen passou do teto de 900 s, exit 67): 5 aplicadas no build, 1 rebatida com evidência (linhas 2·R1 a 2·R6 do Advisor Ledger) |
| 1.2 | 2026-11-15 | design-agent | Revisão adversarial, rodada 1 (`EXTERNAL_REVIEW_20261115-054927`; claude revisou, o auditor qwen respondeu os 9 em prosa e cortou o bloco de vereditos ⇒ REVIEW INVÁLIDA, exit 68): 8 aplicadas, 1 rebatida com evidência (Advisor Ledger) |

---

## Next Step

Revisão adversarial do DESIGN (exigida: arquivos novos); depois **sdd-build**.
