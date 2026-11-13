# Raio de impacto — F17b (antes da última rodada de revisão)

Superfícies mudadas e quem as usa fora do diff, conferidas por execução num projeto temporário (pacote = `git archive`
da frente; projeto = repositório novo). Logs da sessão; a reprodução está em cada linha.

| Superfície mudada | Quem usa fora do diff | Conferido | Resultado |
|---|---|---|---|
| `bin/sdd-open.sh` `skills_da_fonte` passa a listar a `ux-review-builder` | `init`, `sync`, `sync --check`, `doctor` (contagem), adaptadores de vendor (`.claude/skills/`, cabeçalho `sdd-open:generated`), `orfaos_listar` | `init --vendors claude,codex --yes` num projeto novo: 22 skills em `.agents/skills/`, a builder também em `.claude/skills/` com o cabeçalho; `doctor` verde; `sync --check` EM DIA | ok |
| idem | projeto que já tinha a `ux-review-builder` do **starter** em `.claude/skills/` (com `agents/openai.yaml` e uma edição à mão) | `init --yes`: o plano lista "~ atualizar" nos arquivos dela (o mesmo contrato das `sdd-*` do starter: sem `--yes`, pede OK); o `doctor` **não avisava** a colisão, porque procurava só `sdd-*/agents/openai.yaml` | **quebra achada**: o aviso de "skills do sdd-starter no mesmo projeto" passou a incluir a builder (`1a71e1a`, teste `test_doctor_avisa_a_ux_review_builder_do_starter`); a 1ª versão do conserto usava `ls a b`, que sai ≠ 0 quando um dos caminhos falta, e derrubou o teste antigo: trocado por um laço com `[ -f ]` |
| `doctor`: mensagem "N skill(s) sdd-*" | quem lê a saída | a builder não é `sdd-*`: a linha passou a dizer "skill(s) do pacote" (nenhum teste fixava o texto antigo) | ok |
| `.github/workflows/publish-gate.yml`: lint `--conversa` com a builder | `tests/test_release_workflow.py` (a linha do passo é conferida) | teste atualizado com a linha nova | ok |
| `scripts/gerar-starter.py` `DONO_INTEIRO` com `docs/`, `exemplos/`, `tests/` | a 2ª geração sobre o clone real, com o `docs/guia-do-aluno.pt-BR.md` não rastreado (BRAINSTORM) | o gerador recusa destino com arquivo não rastreado (`--untracked-files=all`, sai 64); medido: o guia ficou | ok (a 2ª geração precisa do clone limpo: o guia não é tocado) |
| molde `RESUMO_ETAPA` do starter (trocas) | toda skill gerada que o leva | o gerador pediu versão nova em `sdd-new-session` e `sdd-seguranca` (a trava da F17); patch nas duas | ok |
| `check-gerado.py` com 3 pastas inteiras novas | CI do starter (`ci.yml`, `auto-release.yml`, `release.yml`) | geração de ensaio sobre a `v1.5.17` real + as 9 checagens do CI de lá (`ENSAIO-v1.5.17.log`) | ok |
