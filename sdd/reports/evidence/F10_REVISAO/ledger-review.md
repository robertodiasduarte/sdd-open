# Ledger da revisão adversarial do build — F10_REVISAO

Rodada 3 (teto): `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-012417` (diff de `248301d`; `loop` PRONTO, 0 HIGH; os 4 MED e 3 LOW não bloqueiam e ficam para a F11 — ver BUILD_REPORT, Advisor Ledger).
Rodada 2: `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-010707` (mesmas engines; diff de `55a866d`; convergência `sim`).
Rodada 1: `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-004259` (revisor claude, 2º revisor codex, auditor
openrouter:qwen/qwen3.7-plus; diff de `486ed2e`). Lido por `sdd/bin/sdd-fluxo.sh loop` por célula.

| achado | sev | veredito | rodada | evidência / motivo |
|---|---|---|---|---|
| R1@codex | HIGH | APLICADA | rodada=1 | auditor sem veredito para algum achado recebido → 68 (plano 8.1, R2: "exit 68 se faltar veredito"); `test_revisao.RevisaoFinal` |
| R2@codex | HIGH | APLICADA | rodada=1 | `--revisor2` igual ao revisor ou ao auditor (mesmo adapter e modelo) → 64 antes de chamar; em execução, sem candidato → indisponível |
| R1@claude | MED | APLICADA | rodada=1 | identidade de engine = adapter + modelo na exclusão (67) e na diversidade |
| R2@claude | LOW | APLICADA | rodada=1 | candidatos do 2º revisor e do desempate filtrados sem `uso()`: adapter ausente não derruba depois do revisor pago |
| R3@claude | LOW | APLICADA em parte | rodada=1 | `--indent-heuristic`, `diff.suppressBlankEmpty=false`, `core.attributesFile=/dev/null` e `GIT_ATTR_NOSYSTEM`; `core.autocrlf` REBATIDA_ESCOPO: é do checkout (estável na mesma máquina) e forçá-lo faria um checkout com CRLF virar um diff inteiro |
| R4@claude | LOW | APLICADA | rodada=1 | auditor 68 não grava `auditor.verdicts.jsonl` |
| R5@claude | LOW | APLICADA | rodada=1 | aviso de `--um-engine` impresso antes das linhas ▶ |
| R3@codex | MED | APLICADA | rodada=1 | mesmo conserto do R3@claude |
| R4@codex | MED | APLICADA | rodada=1 | preço pelo modelo reportado e depois pelo pedido |
| R5@codex | MED | APLICADA | rodada=1 | papel chamado que falhou sem custo reportado = `$?` (pode ter cobrado), nunca n/d |
| N1 | MED | APLICADA | rodada=1 | NOVO do auditor exige `arquivo`, `linha` e `resumo` |
| N2 | MED | REBATIDA_EVIDENCIA | rodada=1 | `gatilho_estatico` acrescenta `layers.sql` aos globs quando o slot tem valor (`sdd/bin/adversarial-review.sh`, linha `if camadas.get("sql"): globs.append(...)`); com o slot vazio não há glob a casar — igual ao `review-design` |
| R1@codex | HIGH | APLICADA | rodada=2 | dentro do bloco, só a linha que é só cerca (```` ``` ````, ```` ```json ````) é ignorada; linha que começa com crases e traz conteúdo → 68 |
| R1@claude | MED | APLICADA | rodada=2 | `sinal_auth` sem `\b401\b` solto: `claude` por `authentication_error`/`api_error_status: 401`; `codex` por `401 Unauthorized`; `gemini` por `"code": 40[13]` |
| R2@claude | MED | APLICADA | rodada=2 | `git add --intent-to-add` que falha → 64 nomeando o lote, nunca diff parcial; a sonda achou de quebra um nome que começa com `:` (pathspec mágico) e o add passa a usar `--literal-pathspecs` |
| R3@claude | LOW | APLICADA | rodada=2 | sem `os.killpg` (Python nativo do Windows), mata só o processo; nunca traceback. Sem teste: o piso do pacote (macOS e Ubuntu) sempre tem `killpg` |
| R2@codex | MED | APLICADA | rodada=2 | 2º revisor automático exclui também por adapter + modelo do revisor e do auditor |
| R3@codex | MED | APLICADA | rodada=2 | `openrouter.sh` grava `HTTP <código>` na 1ª linha da saída de erro; o registry casa `^HTTP 40[13]`, `^HTTP 429`, `^HTTP 402` |
| R4@codex | MED | APLICADA | rodada=2 | custo reportado de toda tentativa com resposta é somado ao papel |
