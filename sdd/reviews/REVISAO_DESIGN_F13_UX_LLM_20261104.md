# Revisão de contexto fresco do DESIGN — F13_UX_LLM (modo contrato)

- **Data:** 2026-11-04
- **Revisor:** agente fresco (subagente em contexto limpo), brief do modo `contrato` de `sdd-build/references/contexto-fresco.md`, ampliado com o ataque ao DESIGN contra o repositório real
- **Sobre:** DEFINE v1.1 e DESIGN v1.0
- **Evidência:** `sdd/reports/evidence/F13_UX_LLM/AVAL-DESIGN-01-*.log`
- **Veredito:** NEEDS_WORK — 3 HIGH, 7 MEDIUM, 6 LOW, 5 propostas

## O que o revisor mediu e está correto

- Os 7 oráculos do `contraste.sh` batem em Python e em `awk` BWK; o `+1e-9` não alcança 4,4999996, que dá 449.
- A premissa A-002 vale no BSD grep: expressão inválida sai 2.
- Nenhum teste fora do manifest quebrou na simulação: 767 testes em 30 módulos; as falhas caíram em arquivos do manifest.
- `design-lint.py` passa hoje em DESIGN_F10, F12 e F13.

## Limites declarados

- Sem GNU grep nem mawk na máquina: o lado Ubuntu não foi medido.
- A simulação usou stubs e rodou só os módulos `test_[acdfprs]*`.
- Os 2 scripts não existiam: as medições são de protótipos das regras escritas, não do código final.
- Desvios: a sonda `grep-a002` gravou `/tmp/null_grep_$$`, apagado no mesmo comando; os testes da simulação criaram pastas por `tempfile.mkdtemp`; leitura das fontes privadas citadas no BRAINSTORM.

## Propostas

| # | Alvo | Classe | Problema |
|---|---|---|---|
| P1 | Verify Gate + AT-017, AT-033, AT-034 | gate não cobre AT | O `cmd` roda em `git archive`, sem `.git` nem `sdd/features/`; AT-033 e AT-034 têm `kind: test` e nenhum comando do gate os executa; AT-017 cita arquivo não versionado (`AVAL-DESIGN-01-gate-archive.log`) |
| P2 | AT-021 + Decision 12 | aceite circular | "O scan aparece e 3 arquivos existem" passa com stubs; os estágios nascem da LOOP_SPEC gerada; o exemplo precisa de DEFINE e `sdd/config.yaml` |
| P3 | AT-019, AT-020, AT-024 | aceite circular | `kind: test` sobre texto prova a frase, não o comportamento; bloqueio e triagem nunca rodam num agente |
| P4 | AT-006 | não-verificável | Só tem dentes onde o locale existe; num locale inexistente passa com ou sem a guarda (`AVAL-DESIGN-01-locale-awk.log`) |
| P5 | AT-013 + Error Handling | estado sem critério | Arquivo ilegível conclui `LIMPO`; `grep` de conteúdo com saída 2 também (`AVAL-DESIGN-01-prototipo-grep-falha.log`) |

## Defeitos

| # | Sev. | Defeito | Evidência |
|---|---|---|---|
| D1 | HIGH | A entrada do roteador exige o texto que o roteador deveria produzir: o scan vem antes da skill; prompt novo não tem conteúdo, e entrada vazia sai 64; item do inventário que sai 0 pula a skill; o texto gerado sai 2 sem regra | leitura de DESIGN, AT-013, UX e `build.md` privado |
| D2 | HIGH | Caminho absoluto por symlink vira falso `LIMPO`: raiz `/private/var/...`, caminho `/var/...`, sinal de pasta perdido; `apoio.Sandbox` resolve o caminho e o teste não veria; absoluto fora da raiz contradiz "at any depth" | `AVAL-DESIGN-01-prototipo-caminho-absoluto.log` |
| D3 | HIGH | O AT-030 pede que o `sync` instale, e o `sync` não toca `sdd/`; `test_sdd_open.py` na Traceability e fora do manifest | `AVAL-DESIGN-01-sync-nao-instala.log` |
| D4 | MEDIUM | `Tipo=loop` não fecha: destino pasta × saída 64 para pasta; sem nome para a LOOP_SPEC e para os estágios; `sdd-integration.md` exige contrato por prompt | `AVAL-DESIGN-01-citacoes-fora-do-manifest.log` |
| D5 | MEDIUM | `system:` sem âncora à esquerda casa `package-ecosystem: "npm"`, `filesystem:`, `operating_system:` | `AVAL-DESIGN-01-prototipo-system-substring.log` |
| D6 | MEDIUM | `lint_prompts` não enxerga o formato antigo real (`### Inventory`, DESIGN_F10) e não diz o que faz sem o título | `AVAL-DESIGN-01-lint-formato-antigo.log` |
| D7 | MEDIUM | Fim do valor entre aspas indefinido: comentário gruda no slot, que nunca casa; CRLF gruda `\r` | `AVAL-DESIGN-01-prototipo-slot-yaml.log` |
| D8 | MEDIUM | Self-test quebra com caminho relativo depois do `cd` (`rc=127`) | `AVAL-DESIGN-01-prototipo-selftest-cwd.log` |
| D9 | MEDIUM | `WORKER_BRIEF.md`, a descrição da `sdd-prompt-builder` e `sdd-integration.md` contradizem o roteador e o AT-018 | `AVAL-DESIGN-01-citacoes-fora-do-manifest.log` |
| D10 | MEDIUM | As 11 colunas não são nomeadas; o racional do validador não vale no Open; o teste de nomes não tem o que comparar | `AVAL-DESIGN-01-citacoes-fora-do-manifest.log` |
| D11 | LOW | Casos de borda do `contraste.sh`: piso com 3 casas, zero, base 8 no bash, `--piso` último, array vazio, 1 ou 4 posicionais | `AVAL-DESIGN-01-prototipo-bash32.log` |
| D12 | LOW | `contraste.sh #777 #fff` sem aspas chega sem argumento | `AVAL-DESIGN-01-prototipo-bash32.log` |
| D13 | LOW | O nome e o conteúdo do próprio scan caem nos sinais; o Build da F13 não prevê isso | leitura |
| D14 | LOW | Modo de execução indefinido: 20 de 25 em `sdd/bin` são 100644, e os textos chamam sem `bash` | `AVAL-DESIGN-01-citacoes-fora-do-manifest.log` |
| D15 | LOW | "1 pergunta a mais": a skill nova sozinha já dá 19 em 19 | `AVAL-DESIGN-01-sim-testes-fora-do-manifest.log` |
| D16 | LOW | A validação do slot testa a expressão pura e pode divergir entre BSD e GNU; `(` e `[` são os casos seguros | `AVAL-DESIGN-01-grep-a002.log` |
