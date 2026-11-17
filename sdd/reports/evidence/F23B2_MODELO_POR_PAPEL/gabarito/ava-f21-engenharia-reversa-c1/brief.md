modo: veredito · ciclo: 1 · FEATURE: F21_ENGENHARIA_REVERSA · DEFINE: sdd/features/DEFINE_F21_ENGENHARIA_REVERSA.md ·
DESIGN: sdd/features/DESIGN_F21_ENGENHARIA_REVERSA.md · projeto: @COPIA@ · URL base: — ·
credenciais: "não autorizadas"

Você não viu a conversa do build. Leia o DEFINE como contrato. Para cada AT, PROVE por
execução (comando, chamada, clique) — nunca lendo diff. Superfície visual: derive um roteiro
clicável dos ATs e do manual_fallback e execute-o; sem browser/sessão, devolva o roteiro em
NAO_VERIFICADO, nunca PASS. Só leitura em produção (GET, consultas SELECT, rotas idempotentes);
nada que grave ou envie. Devolva <<<AVALIACAO … >>> com: veredito PASS | NEEDS_WORK |
PASS_PENDENTE_RECIBO, tabela por AT (sonda · esperado · observado · resultado) e ACHADOS
(cada um com reprodução exata). Não edite código nem documento do projeto: o único arquivo
que você grava de propósito, pelo shell, é `sdd/reports/evidence/F21_ENGENHARIA_REVERSA/AVAL-*.log` (1ª linha
`$ comando`, saída verbatim).

Devolva o bloco <<<AVALIACAO … >>> com a linha `VEREDITO: …` e uma tabela com uma linha por AT, `| AT-nnn | sonda | esperado | observado | resultado |`, com o resultado PASS, FAIL ou NAO_VERIFICADO.
