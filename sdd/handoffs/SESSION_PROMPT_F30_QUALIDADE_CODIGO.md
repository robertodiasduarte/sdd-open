# Prompt de sessão — F30 Qualidade do código gerado

Cole o bloco abaixo numa sessão nova do agente, aberta **dentro** de
`/Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob` (branch `f30-sdd-open-uncle-bob`, nascida de
`origin/main` `4aa0cce`).

---

Frente F30 do sdd-open: fazer o código gerado pelo método seguir as boas práticas consagradas (Clean Code, TDD),
com os **itens 1 a 8** escolhidos pelo Roberto em 23/11, em **3 fatias publicáveis**:
- **S1 Qualidade por stack** (itens 1, 3, 4): lint e tipos de verdade no Build, regras de qualidade no AGENTS.md, linter proposto quando falta;
- **S2 Disciplina de teste** (itens 2, 6, 7): vermelho antes do verde, sabotagem do gate, refatorar depois do verde;
- **S3 Métricas no diff, só aviso** (itens 5, 8): duplicação e complexidade.

Um ciclo por fatia: DEFINE → DESIGN → BUILD → RELEASE, sem brainstorm (o ESCOPO já faz esse papel).
- Governança: N.A.
- UX: N.A., porque não há tela. O texto ao aluno segue as `references/como-falar.md` das skills tocadas.
- Segurança: só o item S2-b (a sabotagem nunca toca a árvore de trabalho).

1. Leia, nesta ordem:
   - `sdd/features/AVALIACAO_F30_UNCLE_BOB.md`: o porquê (práticas de Uncle Bob, o que o Open já cobre, as 15 propostas com benefício × custo, a nota estimada e as decisões de 23/11);
   - `sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md`: o que já existe, os achados com linha, os 8 itens, as decisões D1–D7 com a recomendação, o que fica fora e a proposta de Verify Gate;
   - a seção `## Sempre` de `sdd/playbook.md`;
   - `bash sdd/bin/playbook-lint.sh --grep <termo> sdd/playbook.md` para `report-lint`, `AGENTS.md.tmpl`, `seguranca-varredura`, `gerar-starter`, `checar.sh` e `SKILL.md`.
2. `sdd-define` da **S1**: `sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md`, com as fatias como seções e os ATs da S1 primeiro.
   - Pergunte **D1 a D7 juntas**, numa mensagem, com as recomendações do ESCOPO. As da S2 e da S3 também, para o desenho não mudar no meio.
   - O Verify Gate precisa sair 0 antes do build.
3. `sdd-design` da S1. O manifest não pode esquecer:
   - `.agents/skills/sdd-build/SKILL.md` (passo 4, linha ~188) e as `references/`;
   - `AGENTS.md.tmpl` (`{{QUALIDADE}}`) e `bin/sdd-open.sh` (`init`/`sync`, molde das linhas 446–457);
   - o catálogo novo (D6);
   - `sdd/bin/report-lint.py` (o `LINT.log`);
   - `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` e a tabela de tradução da `sdd-new-session` (há um teste que confere que toda mensagem do script tem linha na tabela);
   - `sdd/config.example.yaml`;
   - `scripts/gerar-starter.py` (as regras precisam chegar ao Starter **pelo texto da skill**, porque o Starter não tem AGENTS.md);
   - os testes `tests/test_f30_*.py`.
4. `sdd-build` da S1. Rode a suíte inteira (`python3 -m unittest discover -s tests`). Gere o starter numa pasta temporária e rode os `grep` da F29 (nenhum padrão que o Snyk marca) mais o S1-d.
5. `sdd-release` da S1, com 1 OK. Depois, a geração seguinte do starter em `~/rdd-public/sdd-starter`.
6. Repita os passos 2 a 5 para a S2 e depois para a S3: o DEFINE ganha as seções, com `sdd-iterate`, não com um arquivo novo.
7. No fim de cada fatia, atualize a linha da F30 no "Estado das frentes" de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` e a ficha `sdd/handoffs/HANDOFF_F30_QUALIDADE_CODIGO.md`.

Restrições:
- Só **bloqueia** o que é objetivo: teste e erro de lint ou de tipos com o slot cheio. Métrica (S3) **só avisa**; ferramenta ausente é "não medido", nunca "0 achados".
- Nada instala ferramenta no projeto do aluno sem o sim dele (D2).
- Texto novo de skill em frase positiva, sem banner e sem "não cite" (lição da F29).
- A sabotagem (item 6) roda numa cópia descartável; a árvore de trabalho tem de ficar idêntica, com hash conferido no teste.
- Medir o custo extra em tokens dos itens 2, 6 e 7 e registrar no BUILD_REPORT.
