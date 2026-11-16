# Fixtures do custo-feature.sh (F23)

Dados inventados para `tests/test_f23_custo.py`. Nenhum é sessão real: os textos com `segredo-ficticio-123` e
`/pasta-secreta/segredo.txt` existem para provar que nada do texto das sessões sai dos leitores.

- `claude/`: sessão principal com a mesma mensagem repetida em 3 linhas, um resultado de
  ferramenta (não é turno), uma linha `isMeta` (não é turno), um modelo com `|` e quebra de linha (sai `?`) e um subagente.
- `codex/`: a sessão do projeto (`__RAIZ__` é trocado pela pasta do teste), com `token_count` repetido, e uma
  sessão de outra pasta de trabalho (a da revisão), que nunca entra.
- `traces/`: marcas de `define` (par) e `build` (sem fim), 2 voltas do gate e uma marca de outra feature.
- `reviews/`: 3 revisões — uma do DEFINE da feature, uma de outra feature, uma só citada pelo ledger.
- `precos/`: tarifas inventadas; o `modelo-c` não tem preço de cache.
