# AVALIAÇÃO F6_DOCS — ciclo 1 (contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), sobre o commit
> `963c47e` numa worktree destacada (`/Users/robertoduarte/rdd-worktrees/sdd-open-f6-aval`), contra
> `DEFINE_F6_DOCS.md` v1.1 e `DESIGN_F6_DOCS.md` v1.1, base `v2.2.6`. Logs em
> `sdd/reports/evidence/F6_DOCS/AVAL-*.log`. As decisões sobre cada achado estão no Advisor Ledger do
> `BUILD_REPORT_F6_DOCS.md`.

<<<AVALIACAO
VEREDITO: NEEDS_WORK — 3 HIGH, 3 MEDIUM, 6 LOW

14 ATs provados por execução no piso (Python 3.9.6, bash 3.2.57): 13 PASS e o AT-002 PARCIAL. Os HIGH são
afirmações falsas que o contrato não pega (2 no guia, 1 na seção nova de uma skill).

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | `unittest -v test_docs` (AVAL-testes-tocados.log); sabotagem AT-001a (ficha da sdd-kb renomeada) | guia com 10 blocos, 17 fichas, 7 agentes, init/--yes/python3/doctor/apague+init, releases/latest | 5 testes de Guia ok; sem a ficha, `test_uma_ficha_por_skill` vermelho | PASS |
| AT-002 | sabotagens AT-002a–f num clone de 963c47e (AVAL-sabotagens.log) | falha com cada texto proibido | `npx skills`, `sdd/DEFINE_`, `/drive` (W0) vermelhos; a frase do starter (linha 144), a do glossário dele (459) e "A pasta `sdd/` não entra no git" ficam verdes | PARCIAL (M2) |
| AT-003 | classe Quickstart; sabotagens Lovable e passo 5 PT da v2.2.6 | regra, ≥4 validações, tabela e 7 agentes no passo 4, doctor+init no passo 5, sem Lovable | verde; as 2 sabotagens vermelhas | PASS |
| AT-004 | classe Roadmap; ano 2027 no EN | 5 temas planejados, deltas em avaliação, sem ano, cabeçalho | verde; ano deixa vermelho | PASS |
| AT-005 | classe Comparison; ✅ na célula do open (AT-014c, AT-005e) | ❌ e em avaliação só na última célula | vermelhas | PASS |
| AT-006 | classe ReadmeEAgents; kb-dominios.py tirado do README PT | 17 skills, kb-dominios.py, OK único, guia, roadmap, link do outro README | verde; sabotagem vermelha | PASS |
| AT-007 | `test_agents_tmpl` + `test_agnostico`; sem "um OK só" | 5 skills, kb-dominios.py, "um OK só", VENDORS; agnóstico verde | verde; sabotagem vermelha | PASS |
| AT-008 | classe Links; sabotagens AT-008a/b/c | arquivo/âncora inexistente reprova com `arquivo:linha → alvo` | vermelhos com a linha; `docs/ROADMAP.md` (caixa) passa no macOS | PASS (L1) |
| AT-009 | seção apagada nas 9; 2 itens; título duplicado | falha nomeando a skill | 13/13 vermelhos; clone limpo verde | PASS |
| AT-010 | AVAL-versoes-secao-lint.log | seção antes de Encerramento; patch no frontmatter e na identificação; skill-lint 0 | as 7 em patch, 1 identificação cada, Encerramento em seguida; lint 0 nas 17 | PASS |
| AT-011 | script próprio, texto normalizado v2.2.6 × HEAD | igual nas 7 | igual; fora da seção só `version:` e identificação | PASS |
| AT-012 | `check-versions --base v2.2.6 --base-obrigatoria` | exit 0 | VERDE | PASS |
| AT-013 | `cmd` do gate; diff dos caminhos intocados; MANIFEST | publish-gate ci verde; >499 OK; diff vazio; ≤500 linhas | GREEN; 513 OK; 0 linhas; maior SKILL.md 376; MANIFEST = ls-files em ordem C | PASS |
| AT-014 | sabotagens AT-014a/b/c + baseline v2.2.6 | 3 vermelhos nomeados; limpo verde | vermelhos; limpo 0; baseline vermelho | PASS |

Outras provas verdes: "Skill integrity" do CI verbatim, 0 achados em 94 arquivos, e 0 em docs/, READMEs e
AGENTS.md.tmpl; instalação do guia (sem git → 64; `--dry-run` não escreve; sem `--yes` e sem terminal →
CANCELADO; com `--yes` instala); atualização do guia (`sync` sozinho deixa 2.2.0; doctor aponta as 7; apagar
+ `init --yes` → 2.2.1 e `sync --check` EM DIA).

ACHADOS:
- H1 · guia-do-aluno.md:581 · "é dado fictício (ela registra e libera)": a sdd-higiene-dado troca o número por um inválido e salva (SKILL.md:145); veio do starter (413). Correção: "(ela troca o número por um inválido e salva)"; "registra e libera" em PROIBIDO_NO_GUIA.
- H2 · guia-do-aluno.md:365 · a ficha da sdd-design diz que ela devolve o Define com dúvidas; a skill não tem essa regra (quem segura é o Verify Gate, exit 5); veio do starter (250).
- H3 · sdd-brainstorm/SKILL.md:160-162 · "e nenhum corte é inventado" descreve regra que a skill não tem; quebra o Goal ("regra que a skill já tem"). Correção: tirar a 2ª metade.
- M1 · guia-do-aluno.md:681-683 · "o doctor avisa se encontrar os dois": o starter se instala globalmente e o doctor só olha o projeto (bin/sdd-open.sh:600; AVAL-guia-starter-global.log).
- M2 · tests/test_docs.py:38 · SDD_FORA_DO_GIT só pega 2 frases, caixa exata, até 80 caracteres depois de sdd/; passam as 2 linhas do starter e "não entra no git". Correção: regex sem caixa por parágrafo/linha de tabela que cita sdd/, com autoteste das 2 linhas do starter.
- M3 · guia-do-aluno.md:89-97, :583 · o caminho de atualização só apaga skills; o doctor também aponta sdd/bin/* e o init não o atualiza sem apagar (AVAL-guia-sdd-bin.log).
- L1 · tests/test_docs.py:127 · `exists()` em disco sem caixa (macOS) aceita `docs/ROADMAP.md`. Correção: conferir cada parte do caminho com `os.listdir`, caixa exata.
- L2 · guia :95, quickstarts :185 · `sync` sem `--yes` sai CANCELADO pelo agente; a seção 8 só explica o do init.
- L3 · guia :403 · "não encerra sem mudar nada": a release já commitou e landou antes do OK (FASE 1, 3–5); a skill diz "encerra sem publicar".
- L4 · sdd-design/SKILL.md:173-174 · "quebra quem lê, sem erro visível": o design-lint da própria skill reprova o título (AVAL-design-lint-titulo.log).
- L5 · sdd-release/SKILL.md:283 · o item põe em negrito o rótulo do bloco do OK com `?`, contra a Decision 5.
- L6 · guia :75-76, :679; README.md:66, README.pt-BR.md:66 · o `=` do plano só sai com `--verbose`; o doctor compara com o clone baixado, não com a release publicada; "prepare once … sdd-new-session" contradiz "a cada frente".
>>>
