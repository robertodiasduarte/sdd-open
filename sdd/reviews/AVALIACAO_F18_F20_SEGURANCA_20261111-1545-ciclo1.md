# Avaliação em contexto fresco — F18_F20_SEGURANCA, ciclo 1

Bloco devolvido pelo avaliador (subagente sem a conversa do build), verbatim:

<<<AVALIACAO
feature: F18_F20_SEGURANCA · ciclo 1 · HEAD 433785c (feat/f18-f20-seguranca) · modo veredito
veredito: NEEDS_WORK
VEREDITO: NEEDS_WORK

8 dos 10 ATs passaram. Dois ATs falham em parte, por uma lacuna cada, com reprodução exata (A1 e A2 abaixo). Tudo foi provado executando os comandos em repositórios temporários (mktemp -d), com o pacote instalado pelo `bin/sdd-open.sh init` e um remoto bare como origin. Não editei nenhum código nem documento do projeto: gravei só `sdd/reports/evidence/F18_F20_SEGURANCA/AVAL-*.log`. Não rodei a suíte inteira.

| AT | sonda | resultado |
|---|---|---|
| AT-001 | AVAL-AT001.log, AVAL-AT001-b.log: 7 segredos em 6 formatos, 3 leituras por nome, já existia, base ausente, `--base`; (h) segredo acrescentado em `sdd/reports/evidence/…log`, `sdd/handoffs/…md` e `.claude/settings.json` sai 0 | FAIL parcial (A1) |
| AT-002 | AVAL-AT002.log, AVAL-AT002-b.log: sem RLS, RLS noutra migração, comentário, disable, drop+recriação, sem Supabase, `layers.sql`, linha antiga, outro esquema | PASS |
| AT-003 | AVAL-AT003.log, AVAL-AT003-b.log: 7 padrões com par; S14 não acusa `headers['Access-Control-Allow-Origin'] = '*'` (JS) nem `response.headers["Access-Control-Allow-Origin"] = "*"` (Python) | FAIL parcial (A2) |
| AT-004 | AVAL-AT004.log: teto, ordem, bloqueio fora do teto, `--saida` | PASS |
| AT-005 | AVAL-AT005.log: dispensa na linha e na de cima, sem motivo, de outro id, duas acima, motivo com segredo | PASS |
| AT-006 | AVAL-AT006.log: 9 detecções, slot, `nenhuma`, inválido | PASS |
| AT-007 | AVAL-AT007.log: init com e sem Supabase, acréscimo de 1548 B e 867 B, sync --check e sync, pacote sem catálogo | PASS |
| AT-008 | AVAL-AT008.log: parser independente e 10 testes | PASS |
| AT-009 | AVAL-AT009.log, AVAL-AT009-b.log: design-lint, skill-lint nas 6 skills, textos, `--checklist` | PASS |
| AT-010 | AVAL-AT010.log, AVAL-AT010-b.log: checar --segredo e doctor iguais à v2.11.0, só a Governança trava, 214 testes com /bin/bash, check-versions | PASS |

ACHADOS
A1 — média-alta, AT-001: segredo acrescentado em `sdd/` ou `.claude/` passa calado (a exclusão de pastas da Decision 4 vale também para o S11, cujo padrão exige o corpo da chave). Reprodução: `sk_live_…` num log de `sdd/reports/evidence/`, `ghp_…` em `sdd/handoffs/HANDOFF_X.md`, `sk-proj-…` em `.claude/settings.json`, commitados; varredura sai NADA ACHADO, exit 0. Esperado: exit 2.
A2 — média, AT-003/S14: `headers['Access-Control-Allow-Origin'] = '*'` e `response.headers["Access-Control-Allow-Origin"] = "*"` não acusam (o `]` entre o nome e o `=`). Sugestão: aceitar `\]?` antes de `\s*[:,=]`.
A3 — baixa: `el.innerHTML += t` não acusa (S12 casa só `=`); `create table app.w` com `alter table public.w enable row level security` sai 0 (tabela fora do esquema public, que a API não expõe por padrão).
A4 — cosmética: a linha do bloqueio traz a gravidade (`🛑 S11 alta app.js:1`), o AT-001 diz `🛑 S11 <arquivo>:<linha>`.
>>>
