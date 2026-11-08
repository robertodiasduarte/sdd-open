# Ledger da revisão adversarial real — V272_GUARDAS

Revisor claude, 2º revisor codex (acionado pelo número de arquivos), auditor `openrouter` (qwen/qwen3.7-plus). Correção
de 2 defeitos genéricos achados na instalação do Open num projeto com outro fluxo SDD e outro gerenciador de hooks
(F15, sessão 14). A 1ª chamada da rodada 1 parou com exit 65 (OPENROUTER_API_KEY fora do ambiente) e foi repetida.

| id | severidade | veredito | rodada | motivo |
|---|---|---|---|---|
| R1@claude | LOW | APLICADA | rodada=1 | husky v9: a linha vai em .husky/pre-commit e o git executa o stub .husky/_/pre-commit; ENCADEADO leva os 2 caminhos (`test_husky_v9_linha_no_script_e_bit_no_stub`) |
| R1@codex | MED | APLICADA | rodada=1 | `echo x # bash sdd/hooks/pre-commit || exit 1` contava como encadeado; caso no `test_gancho_encadeado_no_outro_gerenciador_e_reconhecido` |
| R1@claude | LOW | APLICADA | rodada=2 | a pasta `_` sozinha não prova delegação: exige o desenho do husky v9 (<hooksPath>/h e o stub que o chama) |
| R1@codex | MED | APLICADA | rodada=2 | `echo "rode: bash sdd/hooks/pre-commit || exit 1"` contava como encadeado: a linha, sem recuo, tem de começar pela chamada |
| R2@codex | MED | APLICADA | rodada=2 | o mesmo defeito do R1@claude da rodada 2 (pasta `_` sem prova de delegação) |
| R1@claude | LOW | APLICADA | rodada=3 | core.hooksPath com ~/ não era expandido (`test_hooks_path_com_til_e_expandido`) |
| R1@codex | MED | APLICADA | rodada=3 | o /h comentado no stub valia como husky; agora só em linha que não é comentário |
| R1@claude | MED | APLICADA | rodada=4 | o `git config --type=path` da rodada 3 exige git >= 2.18 e, em git antigo, o hp vazio faria o init tomar o core.hooksPath alheio como livre; a expansão de ~/ voltou a ser à mão |
| R1@codex | MED | REBATIDA_EVIDENCIA | rodada=4 | a precedência do HIGIENE sobre o ENCADEADO no hook legado é de propósito: no estado HIGIENE o init liga core.hooksPath = sdd/hooks e migra o alarme (bin/sdd-open.sh, ramo LIVRE/HIGIENE do aplicar), então as 5 regras rodam e o doctor manda rodar o init até lá; nada fica sem guarda |
| R2@codex | MED | REBATIDA_EVIDENCIA | rodada=4 | o auditor discordou (DISAGREE_CONCERN): validar o conteúdo do ajudante h seria frágil a cada versão do husky; o desenho (h presente e chamado pelo stub) é a prova estrutural escolhida, documentada em docs/hooks.md |
| R1@claude | MED | REBATIDA_EVIDENCIA | rodada=5 | linha inalcançável (depois de exit, dentro de heredoc): o doctor é diagnóstico por leitura de texto e nenhuma leitura de shell resolve isso sem executar; limite declarado em docs/hooks.md (en e pt-BR) e no comentário de chama_o_nosso; a guarda de verdade é o hook rodar |
| R1@codex | MED | APLICADA | rodada=5 | `echo "/h"` no stub valia como husky: exige a linha que carrega o h (começa por `. `), como o husky v9 gera |
| R1@claude | LOW | REBATIDA_EVIDENCIA | rodada=6 | `[[:space:]]` em awk já é usado em 12 lugares do pacote (inclusive sdd/bin/verify-gate.sh); o CI roda nos awks do Ubuntu e do macOS, que aceitam a classe; trocar só aqui não muda o piso do pacote |
| R1@codex | MED | APLICADA | rodada=6 | `. ./helper.sh` valia como o ajudante h: a linha do stub tem de terminar em `/h` (com ou sem aspas) |
