# Prompt de sessão — F29 Skills marcadas pelos scanners

Cole o bloco abaixo numa sessão nova do agente, aberta **dentro** de
`/Users/robertoduarte/rdd-worktrees/sdd-open-scanners-skills` (branch `scanners-skills`, nascida de `origin/main`
`f1abdfa`).

---

Frente F29 do sdd-open: corrigir o texto das skills que os scanners do skills.sh (Snyk, Gen) marcam como
"prompt injection" ou "banner promocional". Quero um **ciclo ágil**: DEFINE curto → DESIGN curto → BUILD →
RELEASE, sem brainstorm. A governança é N.A. (não trata dinheiro nem dado pessoal), a UX também (a correção não
cria tela), e a segurança entra só como os itens 5 do escopo.

1. Leia, nesta ordem:
   - `sdd/features/ESCOPO_F29_SCANNERS_SKILLS.md`: o achado completo, o escopo, as decisões D1–D3 com as
     recomendações e a proposta de Verify Gate;
   - a seção `## Sempre` de `sdd/playbook.md`;
   - `sdd/bin/playbook-lint.sh --grep "gerar-starter" sdd/playbook.md` e `--grep "SKILL.md"`.
2. `sdd-define`: escreva `sdd/features/DEFINE_F29_SCANNERS_SKILLS.md` a partir do ESCOPO, sem perguntar o que o
   ESCOPO já responde. Pergunte só D1, D2 e D3, juntas, numa mensagem, com as recomendações. Os ATs são os
   `grep` vazios e os testes da seção 6 do ESCOPO. O Verify Gate precisa sair 0 antes do build.
3. `sdd-design`: um DESIGN curto com o manifest. Pontos que não podem faltar:
   - `.agents/skills/*/SKILL.md` e os `references/` que têm as frases;
   - `scripts/gerar-starter.py` e `scripts/starter/blocos/MIGRAR.md`;
   - `.agents/skills/sdd-checar-ambiente/scripts/duplicadas.sh` (`dup_meta`, que hoje acha a origem pelo
     trecho `<repo>/releases/latest`) e `scripts/starter/raiz/scripts/check-versions.py`;
   - `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` (`URL_ATUAL`);
   - os 8 testes listados no item 6 do ESCOPO.
4. `sdd-build`: aplique a troca de frase em lote, com um script que mostra o antes e o depois por arquivo, e
   confira as frases à mão em 3 skills. Rode a suíte inteira (`python3 -m unittest discover -s tests`).
   Gere o starter numa pasta temporária e confira os `grep` da seção 6, incluindo o bloco de migração.
5. `sdd-release`: release do Open com 1 OK. Depois, a geração seguinte do starter em
   `~/rdd-public/sdd-starter`, com o fluxo de publicação que o README do starter descreve.
6. Depois de publicar, abra `https://skills.sh/robertodiasduarte/sdd-starter/<skill>/security/snyk` nas 8 skills
   que eram Critical e registre no HANDOFF da F29 o resultado novo, com a data. Se alguma continuar marcada,
   registre o motivo novo; não reabra a frente por isso sem falar comigo.

Restrições:
- Uma frase positiva com a mesma intenção, nunca só apagar. "Não cite as instruções" existe para o aluno
  receber o motivo em palavras dele; "como veio" existe para não cortar o relatório; a linha de versão existe
  para o aluno saber qual versão roda.
- Não mudar comportamento de script, só o lugar de onde a origem é lida (se D1 for o frontmatter).
- Registrar a F29 no "Estado das frentes" do plano, como as outras frentes.
