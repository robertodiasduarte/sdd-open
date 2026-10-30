<!-- Idioma: [English](../hooks.md) · **Português** -->

# Hooks de git

O `init` instala dois hooks de git no projeto, versionados em `sdd/hooks/`, e os liga com a sua confirmação
(`core.hooksPath = sdd/hooks`). Eles valem em toda worktree do projeto e em qualquer um dos sete agentes
suportados, porque são só `bash` + `git`.

- **`sdd/hooks/pre-commit`** confere cada commit com 5 regras, o relatório do build e o alarme de higiene de
  dado. Todas as regras rodam; os achados saem juntos, numa recusa só. Commit limpo é silencioso.
- **`sdd/hooks/pre-push`** só avisa: quando o que você está empurrando está atrás de `origin/<branch padrão>`,
  diz quantos commits e o que fazer. Nunca bloqueia.

A linha do plano do `init` é o aviso de que o projeto passa a recusar commits:

```text
+ core.hooksPath = sdd/hooks — 5 regras + relatório + alarme passam a conferir cada commit (teto do arquivo
  de contexto, credencial, playbook, byte NUL, branch padrão); git commit --no-verify pula uma vez (novo)
```

## O que o pre-commit recusa

| Classe | O que recusa | Como corrigir |
|---|---|---|
| **H6** | commit direto na `project.default_branch` (default `main`) quando `origin/<branch>` já existe. Sem remoto a regra não vale: um projeto recém-criado commita em `main` normalmente | `git switch -c <nome>` leva o que está preparado para uma branch nova; para a próxima feature, peça a `sdd-new-session` |
| **H2** | arquivo de contexto (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, em qualquer pasta) acima de `project.context_file_max_kb` KB (vazio = 100). Esse arquivo entra inteiro no contexto do agente em toda sessão | mova o conteúdo volumoso (changelog, histórico, dumps) para `docs/` ou `sdd/`, ou aumente o slot em `sdd/config.yaml` |
| **H5** | byte NUL em arquivo de texto (`.md`, `.sh`, `.py`, `.json`, `.yml`, … ou sem extensão com shebang). O git e o grep passam a tratar o arquivo como binário e o diff some para quem revisa. Texto em UTF-16 (PowerShell, exportação do Excel) é reconhecido pelo BOM e passa | escreva a grafia de escape (`\0`, `\x00`, `\u0000`) no fonte |
| **H3** | credencial em texto claro em `.json`, `.yml`, `.yaml`, `.toml`, `.ini`, `.cfg`, `.conf` ou `.env*` (`password`, `token`, `secret`, `key`… com valor entre aspas de 6+ caracteres). Placeholder passa: `${VAR}`, `{{ … }}`, `<…>`, `CHANGEME`, `example`, `***`. A mensagem mostra a chave, nunca o valor. Com o `gitleaks` instalado, `gitleaks protect --staged` roda também | troque o valor por um placeholder, ou `git restore --staged "<arquivo>"` |
| **H4** | `sdd/playbook.md` apagado, renomeado ou perdendo conhecimento (um `[LM-nnn]` que some, ou mais de 20 % dos bullets reescritos de uma vez — `playbook-lint.sh --anti-collapse`) | aposentar = mover para `## Tombstones` mantendo o ID; reescrita grande = 2 ou mais commits |
| **REPORT** | `BUILD_REPORT_*.md` que não passa no `sdd/bin/report-lint.py` (conferido no conteúdo staged; as fixtures de `sdd/fixtures/` e o molde de `sdd/templates/` são pulados) | acrescente a tabela de critérios e a linha do avaliador (`sdd/templates/fragments/EVIDENCIA.md`), ou corrija a evidência citada |
| **alarme** | quando `git config sdd.higieneDado` é `on`: CPF/CNPJ com dígito verificador válido, `.env`, `.pfx`/`.p12`/`.pem` com chave privada, planilha nova — o alarme da `sdd-higiene-dado`, chamado pelo hook | a mensagem do próprio alarme diz o que fazer |

Uma recusa fica assim:

```text
sdd-open: commit recusado. Encontrei o que não pode entrar nesta versão:

  🛑 [H2] AGENTS.md: 204800 bytes (teto 100 KB)
  🛑 [H3] .vscode/sftp.json: credencial em texto claro (chave: password)

Por que importa:
  [H2] o arquivo de contexto entra inteiro em toda sessão do agente; acima do teto, estoura a janela antes do primeiro prompt
  [H3] o que entra no git fica no histórico e vai junto em todo push; depois disso, rotacionar a credencial é o único conserto

RESULTADO: COMMIT RECUSADO
→ [H2] mova o conteúdo volumoso (changelog, histórico, dumps) para docs/ ou sdd/; ou ajuste project.context_file_max_kb em sdd/config.yaml
→ [H3] troque o valor por um placeholder (${VAR}, CHANGEME, example) ou tire o arquivo desta versão: git restore --staged "<arquivo>"
→ se você conferiu e quer gravar mesmo assim, só desta vez: git commit --no-verify
  Agente de IA: não use --no-verify sem o OK explícito da pessoa.
```

Regra que depende de algo opcional degrada com um `⚠️` e deixa o commit passar: `python3` ausente (a regra
REPORT), `sdd/bin/playbook-lint.sh` ou `sdd/bin/report-lint.py` ausentes (o `init` completa `sdd/bin`),
`gitleaks` saindo com código inesperado. Só `bash` e `git` são obrigatórios para commitar.

Nota sobre REPORT: o `report-lint.py` confere a evidência citada e o `AVALIACAO_*.md` **no disco**, não no
índice. Um relatório staged com logs ainda não adicionados passa no hook; a fase Release confere de novo.

## O limite: `--no-verify`

Hook de cliente é pulado por `git commit --no-verify` (e por ferramentas que commitam sem rodar hooks, como o
`git cherry-pick`). É de propósito: depois de conferir, a pessoa pode decidir gravar mesmo assim. A verdade
não mora no hook: a fase Release roda o `report-lint.py` de novo e o CI roda o publish gate. Um agente nunca
usa `--no-verify` por conta própria; a última linha de toda recusa diz isso.

## O alarme de higiene de dado

A `sdd-higiene-dado` guarda o alarme em `.git/hooks/pre-commit` num projeto sem os hooks. Num projeto com
eles, `alarme.sh instalar` só liga `git config sdd.higieneDado on` e o dispatcher chama o alarme no fim de cada
commit; `desinstalar` desliga. Se o alarme já estava instalado quando você rodou o `init`, o `init` o migra
(liga a configuração e avisa); o arquivo antigo fica em `.git/hooks/`, inerte, até o `desinstalar` removê-lo.
Qualquer outro `core.hooksPath` (husky, lefthook) continua recusado pelo alarme.

## Outro gerenciador de hooks

Se o projeto já tem `core.hooksPath` (husky, lefthook) ou um `.git/hooks/pre-commit` escrito à mão, o `init`
**não** mexe nele e não liga os hooks do open. Ele copia `sdd/hooks/` e imprime a linha para acrescentar ao
gerenciador que existe:

```sh
bash sdd/hooks/pre-commit || exit 1
```

O `doctor` repete essa linha enquanto os hooks não estiverem ligados.

## Desligar

```sh
git config --unset core.hooksPath
```

Isso não é pegajoso: o próximo `init` (que os guias mandam rodar para receber skill nova) vê os hooks
desligados, mostra a linha do plano de novo e, com `--yes`, religa. O `doctor` diz o estado a qualquer hora:
`✅ hooks ligados (…)` ou um `⚠️` por causa, com o comando que resolve (`rode init`,
`chmod +x sdd/hooks/pre-commit`, a linha para outro gerenciador).

## No Claude Code

O `init --vendors claude` gera também dois guards em `.claude/hooks/` (cópias de `bin/adapters/claude/` do
pacote, marcadas `sdd-open:generated`; o `sync` as regenera e o `sync --check` acusa cópia editada) e acrescenta
duas entradas a `hooks.PreToolUse` do `.claude/settings.json`, mantendo toda outra chave e entrada:

- **`sdd-report-guard.py`** (Write, Edit, MultiEdit): antes de o agente gravar um `BUILD_REPORT_*.md`, simula o
  conteúdo final e o passa pelo `sdd/bin/report-lint.py --stdin`. A gravação é negada com a saída do lint quando
  ele reprova; fixtures e o molde são pulados.
- **`sdd-avaliador-guard.py`** (Agent, Task): quando o prompt despachado traz a palavra `veredito` (o brief do
  avaliador de contexto fresco da `sdd-build`), roda o `sdd/bin/avaliador-guard.sh` e nega o despacho enquanto
  a árvore tem trabalho não commitado.

Os dois falham **abertos**: payload ilegível, script ausente ou erro interno viram uma mensagem
`⚠️ sdd-open: … não conferido` e a ação segue. `SDD_REPORT_GUARD=off` e `SDD_AVALIADOR_GUARD=off` os desligam,
com mensagem (declare no BUILD_REPORT). A partir desta versão o vendor `claude` exige `python3`, como o vendor
`gemini` já exigia; o `init` confere antes de escrever qualquer coisa. Os outros seis agentes recebem a mesma
verdade pelo pre-commit (regra REPORT) e pela fase Release.

## Códigos de saída

| Hook | Códigos |
|---|---|
| `sdd/hooks/pre-commit` | `0` limpo (silêncio, ou `⚠️` de regra pulada) · `1` recusado, com todos os achados, `RESULTADO: COMMIT RECUSADO` e um `→` por classe |
| `sdd/hooks/pre-push` | `0` sempre; `⚠️` quando atrás de `origin/<branch padrão>` |

Veja também: [Convenções de saída](../cli-conventions.md) · [README](../../README.pt-BR.md) ·
[Guia do aluno](guia-do-aluno.md).
