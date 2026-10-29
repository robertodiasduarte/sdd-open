# HANDOFF: CONTADOR_LINHAS

> Fixture do `sdd/bin/handoff-lint.py`: ficha preenchida a partir de `sdd/templates/HANDOFF_TEMPLATE.md`,
> que passa. Não tem a seção de eventos (é opcional) e o prompt traz comandos reais com chaves. Os testes
> trocam um trecho por vez para provar cada regra.

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
