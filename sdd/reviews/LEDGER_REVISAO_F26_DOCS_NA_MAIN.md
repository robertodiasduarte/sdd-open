# Ledger da revisão — F26_DOCS_NA_MAIN

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Rodada D1 (revisão do DESIGN, antes do código): `claude` (claude-opus-5-5) revisa, `codex` (gpt-6.1-sol) audita, sobre
`sdd/features/DEFINE_F26_DOCS_NA_MAIN.md` e `sdd/features/DESIGN_F26_DOCS_NA_MAIN.md` em `7146c84`; US$ 0,93. Engines
escolhidas pelo Roberto (as da F25). Sem código revisado, `dano` é `nao` em todas.

revisor2: dispensado rodada=D1 — sem superfície de risco

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=D1 | DESIGN 1.1, Decision 4: o teto vale só para evidência versionada (`regras_do_arquivo(…, versionado)`) | nao | EXTERNAL_REVIEW_20261117-215809 |
| R2 | MED | APLICADA | rodada=D1 | DEFINE 1.4, Constraints: o lote roda dentro da F26 | nao | EXTERNAL_REVIEW_20261117-215809 |
| R3 | MED | APLICADA | rodada=D1 | DESIGN 1.1, File Manifest item 19 com a dependência 7 | nao | EXTERNAL_REVIEW_20261117-215809 |
| R4 | MED | APLICADA | rodada=D1 | DESIGN 1.1, Decision 4: `--padrao` com `--ref` varre todos os arquivos da ref | nao | EXTERNAL_REVIEW_20261117-215809 |
| R5 | MED | REBATIDA_EVIDENCIA | rodada=D1 | `.github/workflows/release.yml:145-187`: o testes-macos só roda unittest; os 6 passos que leem a árvore estão na Decision 2 | nao | EXTERNAL_REVIEW_20261117-215809 |
| R6 | MED | REBATIDA_EVIDENCIA | rodada=D1 | `scripts/starter/modos.tsv` (sdd-release → `references/MODO_INICIANTE.md`) e `scripts/gerar-starter.py:324` (copia só o que o modo cita; o modo não cita arquivo) | nao | EXTERNAL_REVIEW_20261117-215809 |
| R7 | LOW | APLICADA | rodada=D1 | DESIGN 1.1, Decision 5: o `--copiar` recusa documento da HEAD com outro conteúdo | nao | EXTERNAL_REVIEW_20261117-215809 |
| R8 | LOW | APLICADA | rodada=D1 | `scripts/gerar-starter.py` `marcar()`: posição + 11 ≤ 60 e conferência depois da troca | nao | EXTERNAL_REVIEW_20261117-215809 |
| R9 | LOW | APLICADA | rodada=D1 | DESIGN 1.1, Decision 4: só `exemplo.com` exato | nao | EXTERNAL_REVIEW_20261117-215809 |
| R10 | LOW | APLICADA | rodada=D1 | DESIGN 1.1, Decision 2: `pipefail`, `MANIFEST.txt` conferido, chamada em 2 linhas | nao | EXTERNAL_REVIEW_20261117-215809 |
| R11 | LOW | APLICADA | rodada=D1 | DESIGN 1.1, Decision 4: `limpo()` no caminho impresso | nao | EXTERNAL_REVIEW_20261117-215809 |
| N1 | MED | APLICADA | rodada=D1 | DESIGN 1.1, Decision 5: o `--conferir` recalcula a classe de cada `fora` | nao | EXTERNAL_REVIEW_20261117-215809 |

Rodada 1 (revisão do código, depois do Build): `claude` (claude-opus-5-5) revisa, `codex` (gpt-6.1-sol) audita, sobre
`304e60a..b9270a2` só nos caminhos de código (o diff com os 2.867 documentos migrados passaria do teto de 8 MB); US$ 1,77.
O 2º revisor entrou pela regra (o diff toca `.agents/skills/sdd-seguranca/SKILL.md`, só a linha da versão) e o
`gemini` falhou por credencial (exit 65): a dispensa vai para a release, com o motivo, pelo `--aceitar-sem-revisor2`.

revisor2: dispensado rodada=1 — gemini sem credencial (exit 65); a superfície de risco é só a linha da versão da sdd-seguranca, nenhuma regra de segurança mudou (Roberto, 2026-11-18)

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=1 | teste: test_at012_texto_procura_o_dado_letra_a_letra · `docs-varredura --texto` (re.escape) e o CONTRIBUTING passa a usá-lo; vermelho em REVISAO-R1-vermelho.log | sim | EXTERNAL_REVIEW_20261118-065427 |
| R2 | MED | APLICADA | rodada=1 | CONTRIBUTING: o histórico da `main` ainda guarda o commit antigo; reescrever é decisão do mantenedor, informada na resposta (só texto; o AT-012 não pede reescrita) | nao | EXTERNAL_REVIEW_20261118-065427 |
| R3 | MED | APLICADA | rodada=1 | teste: test_at005_cada_desvio_sai_1 (subteste "ajustado com outro conteúdo") · o `--conferir` recalcula a categoria e compara o ajustado com `ajustar()` da tag | nao | EXTERNAL_REVIEW_20261118-065427 |
| R4 | MED | APLICADA | rodada=1 | teste: test_at005_squash_com_o_codigo_da_frente_confere · a `main` recebe a frente por squash (F25 `304e60a`, F23B2 `2204a14`); reprova só o arquivo de código que ficou igual ao da tag | nao | EXTERNAL_REVIEW_20261118-065427 |
| R5 | MED | APLICADA | rodada=1 | teste: test_at008_descricao_entre_aspas_simples_ou_sem_aspas · a marca entra depois da aspa simples; nenhuma das 18 skills usa aspas simples hoje | nao | EXTERNAL_REVIEW_20261118-065427 |
| R6 | LOW | APLICADA | rodada=1 | teste: test_f26_copia_do_starter_diz_sdd_starter · o `checar.sh` da cópia do starter (URL trocada pelo gerador) imprime "· SDD Starter" | nao | EXTERNAL_REVIEW_20261118-065427 |
| R7 | LOW | APLICADA | rodada=1 | teste: test_at011_nome_acentuado_confere e test_at011_link_na_pasta_nada_enviado · a causa medida é o NFD do tar do macOS, não a localidade: listas em NFC pelo Python da varredura; link recusado antes do envio | nao | EXTERNAL_REVIEW_20261118-065427 |
| R8 | LOW | REBATIDA_EVIDENCIA | rodada=1 | `sdd/bin/playbook-curator.sh` `RE_ENTRADA` e `conferir_entrada`: entrada é só pasta `fila/<F>/<AAAAMMDDTHHMMSSZ>/`; no nível de `<F>` só existe a marca `.recusada`, ao lado da pasta dela | nao | EXTERNAL_REVIEW_20261118-065427 |
| N1 | MED | REBATIDA_ESCOPO | rodada=1 | a varredura dos documentos barra antes do push (`sdd-release` item 10) e no CI do PR (`publish-gate.yml`); no `release.yml` o documento já está na `main` pública, e travar a Release do pacote não o tira de lá | nao | EXTERNAL_REVIEW_20261118-065427 |
| N2 | MED | APLICADA | rodada=1 | teste: test_at004_log_em_utf16_e_varrido · `como_texto()` lê UTF-16 (com e sem BOM) antes das regras de e-mail e CPF/CNPJ; binário continua só com nome e chave | sim | EXTERNAL_REVIEW_20261118-065427 |
