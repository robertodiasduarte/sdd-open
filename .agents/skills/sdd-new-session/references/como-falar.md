# Como falar com o aluno — sdd-new-session

Quem pede uma frente nova quer começar a trabalhar e, em geral, não sabe o que é uma branch. A seção
"Como falar com o aluno" do `SKILL.md` dá o formato, e a tabela "Como traduzir cada achado" dá a frase
de cada problema do pré-voo; este arquivo dá as palavras e dois exemplos inteiros.

## Glossário (explique na primeira vez em que o termo aparecer)

- frente — "uma pasta separada para esta tarefa, ao lado do projeto, onde o trabalho não esbarra em outro";
- worktree — o nome técnico da frente; diga "a pasta da frente";
- branch — "a linha de versões desta tarefa; ela nasce da versão mais nova do projeto no GitHub";
- branch padrão — "a linha principal do projeto (em geral `main`), de onde as frentes nascem";
- pré-voo — "a conferência rápida antes de criar a frente: git, projeto e acesso ao GitHub";
- remoto — "a cópia do projeto guardada no GitHub (ou em outro serviço)";
- slot — "um campo do arquivo de configuração do projeto; slot vazio quer dizer 'pule e diga que pulou'";
- editor — "o programa onde você abre os arquivos do projeto".

Não fale em `HEAD`, fetch, origin ou upstream sem traduzir: diga o efeito ("a versão mais nova do
GitHub", "a cópia do GitHub").

## Status desta skill, preenchido

`Nova sessão: ✅ 1 Pré-voo · ▶️ 2 Conhecer o repositório · ⬜ 3 Criar a frente · ⬜ 4 Abrir no editor`

## Exemplo 1 — resposta completa, com decisão (etapa 1 — Pré-voo)

Situação: o pré-voo achou "Este projeto ainda não usa git", e a skill `sdd-iniciar-repo` está instalada.

**Status** — `Nova sessão: ⏸️ 1 Pré-voo · ⬜ 2 Conhecer o repositório · ⬜ 3 Criar a frente · ⬜ 4 Abrir no editor`
(no Status: "Pré-voo" é a conferência antes de criar a pasta da frente; ⏸️ quer dizer parada.)

**O que foi feito** — Conferi a pasta: há 23 arquivos do projeto e nenhum histórico de versões (git).
Nenhuma frente foi criada.

**Agora: etapa 1 — Pré-voo** — A frente nasce do histórico de versões no GitHub, e este projeto ainda não
tem um. Dá para resolver agora, conferindo antes o que não pode sair do computador.

**Sua decisão** — [D1 · não se desfaz] **Posso pôr este projeto no git e num GitHub privado, conferindo antes o que não pode ir?**
- **sim** (recomendado) — sigo pela `sdd-iniciar-repo`, uma etapa por vez, com o seu OK em cada uma;
  depois volto e crio a frente.
- **não** — paro aqui; nada é criado.
- **não sei** — explico o que é o git e o que vai e o que não vai para o GitHub.

**Próximo passo** — Com o seu sim, começo pela lista do que entraria no git.

## Exemplo 2 — parada (etapa 1 — Pré-voo, pasta sincronizada)

**Status** — `Nova sessão: ⏸️ 1 Pré-voo · ⬜ 2 Conhecer o repositório · ⬜ 3 Criar a frente · ⬜ 4 Abrir no editor`

**Por que parei:** esta pasta é sincronizada pelo iCloud, e ali o histórico do projeto se corrompe.

**Onde:** no Finder, e depois no terminal.

**Passos:**
1. Mova a pasta do projeto para fora da nuvem, por exemplo para `~/Projetos` → a pasta some do iCloud.
2. Abra o terminal e o agente na pasta nova → o agente mostra o nome da pasta nova.

**O que não foi feito:** nenhuma frente foi criada.

Quando terminar, me peça de novo, eu continuo daqui.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
