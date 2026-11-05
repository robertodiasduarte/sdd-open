# HANDOFF: CONTADOR_LINHAS

> Fixture do `sdd/bin/handoff-lint.py`: ficha preenchida a partir de `sdd/templates/HANDOFF_TEMPLATE.md`
> com as 6 seções opcionais (eventos, recomendações, veredito, preparo, tarefas e publicação), que passa.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | CONTADOR_LINHAS |
| **Objetivo** | Quem recebe um arquivo de texto sabe quantas linhas ele tem sem abrir o editor |
| **Status** | 🚢 publicado |
| **Última sessão** | 2026-10-29 |
| **Branch / pasta** | `feat/contador` · `/srv/projetos/contador` |
| **Artefatos** | `sdd/features/DEFINE_CONTADOR_LINHAS.md` · `sdd/features/DESIGN_CONTADOR_LINHAS.md` · `sdd/reports/BUILD_REPORT_CONTADOR_LINHAS.md` |
| **Verify Gate** | 🟢 0 — `sdd/bin/verify-gate.sh sdd/features/DEFINE_CONTADOR_LINHAS.md` |

## Feito

- Lint novo publicado na release v1.0.0; `python3 -m unittest tests/test_conta.py` dá 3 OK.

## Falta

- Aceitar mais de um arquivo por chamada.

## Definition of Done

- [x] `conta.py exemplo.txt` imprime `12 linhas`.
- [ ] Arquivo ausente sai 2 com a mensagem de erro.

## ⛔ Landmines desta feature

- Arquivo com CRLF conta igual: não troque `splitlines()` por `split("\n")`.

## Casos e testes em aberto

- `tests/test_conta.py::test_ausente` ainda não existe.

## Eventos

- 2026-10-28 — Escopo reduzido a um arquivo por chamada; a dona do projeto decidiu deixar vários arquivos para depois.
- 2026-10-29 — Publicada a v1.0.0.

## Recomendações

- Fazer o caso do arquivo ausente antes de aceitar vários arquivos: ele muda a saída que os dois usam.

## Veredito

- 🟡 CONCERNS — o teste do arquivo ausente ainda não existe; virou pendência desta ficha.

## Setup

1. `git fetch origin && git worktree add ../contador-frentes/varios-arquivos -b varios-arquivos origin/main` → a pasta nova aparece com os arquivos da `main`.
2. `python3 -m unittest discover -s tests` → 3 testes OK antes de mexer.

## Tarefas

1. **Escrever o teste do arquivo ausente** — Pronto quando: `python3 -m unittest tests/test_conta.py` mostra 4 testes e o novo falha.
2. **Fazer `conta.py` sair 2 com a mensagem** — Pronto quando: o mesmo comando dá 4 OK.

## Ship

- **Publicar:** as 2 mudanças acima, pela `sdd-release`.
- **Limpar:** `git worktree remove ../contador-frentes/varios-arquivos` e apagar a branch `varios-arquivos` depois de integrada.

---

## Prompt de retomada

```text
Retomar a feature CONTADOR_LINHAS.

Contexto: script que conta linhas de um arquivo de texto; publicado em v1.0.0, falta o caso de arquivo ausente.
Pasta: /srv/projetos/contador · branch feat/contador.
Leia primeiro: sdd/handoffs/HANDOFF_CONTADOR_LINHAS.md, depois sdd/features/DEFINE_CONTADOR_LINHAS.md e DESIGN_CONTADOR_LINHAS.md.
Estado do gate: `sdd/bin/verify-gate.sh sdd/features/DEFINE_CONTADOR_LINHAS.md` saiu 0 em 2026-10-29.

Próxima ação: rodar `ls ${HOME}/entrada | awk '{print $1}'` para listar as amostras e escrever tests/test_conta.py::test_ausente.
Não faça: mudar o formato da saída (há quem leia "N linhas" no terminal).
Landmines: CRLF conta igual; mantenha splitlines().
```

---

## Histórico de slices

### Sessão 1 — 2026-10-29

- Contador escrito, testado com a amostra de 12 linhas e publicado em v1.0.0.
