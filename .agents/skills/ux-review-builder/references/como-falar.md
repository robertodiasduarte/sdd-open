# Como falar com o aluno — ux-review-builder

Quem monta um padrão de UX sabe o que gosta de ver na tela e não conhece o vocabulário de design. A
seção "Como falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo.

## Glossário (explique na primeira vez em que o termo aparecer)

- padrão de UX / `UX_STANDARD.md` — "o documento com as regras de como as telas do seu projeto devem ser;
  é a fonte canônica: a única versão que vale";
- regra verificável — "uma regra que dá para conferir olhando a tela (ex.: 'todo botão tem pelo menos 44
  pixels de altura'), com um código fixo (ID) para ser citada";
- MUST / SHOULD / COULD — "obrigatória (bloqueia), recomendada, opcional";
- referência de look and feel — "um produto conhecido cuja aparência serve de inspiração — princípio, não
  cópia";
- lente cognitiva — "um ângulo de análise (ex.: quantas escolhas por passo); a lente recomenda ou alerta,
  nunca bloqueia";
- governança — "quem aprova mudanças no padrão e como o padrão evolui com versão";
- skill filha (`ux-review`) — "a skill gerada por esta, que revisa cada feature contra o padrão";
- modo Criação / Evolução — "criar o padrão do zero, ou mudar um que já existe, mostrando a diferença
  antes de gravar".

Não fale em heurística, affordance, design token ou wireframe sem traduzir: "regra de bolso", "o que a
tela sugere que dá para fazer", "os valores fixos de cor e tamanho", "o esboço da tela".

## Status desta skill, preenchido

`UX: ✅ 1 Modo · ✅ 2 Público · ✅ 3 Referências · ▶️ 4 Regras · ⬜ 5 Governança · ⬜ 6 Gerar e entregar`

## Exemplo de resposta completa

Situação: modo Criação; o aluno disse que o público é "contadores do escritório, o dia inteiro na tela"
e escolheu uma referência sóbria; as preferências viraram regras e precisam ser confirmadas.

**Status** — `UX: ✅ 1 Modo · ✅ 2 Público · ✅ 3 Referências · ▶️ 4 Regras · ⬜ 5 Governança · ⬜ 6 Gerar e entregar`
(no Status: "Modo" é criar o padrão do zero ou evoluir um que já existe; "Referências" são produtos
conhecidos que servem de inspiração; "Governança" é quem aprova mudanças no padrão e como ele ganha
versão.)

**O que foi feito** — Você descreveu o público (contadores, uso diário, telas densas) e escolheu uma
referência sóbria e compacta. Transformei o que você disse em 8 regras verificáveis — regras que dão para
conferir olhando a tela, cada uma com um código fixo para ser citada depois. Nada foi gravado.

**Agora: etapa 4 — Regras** — Antes de gerar o padrão, você confirma as regras: as obrigatórias (MUST)
bloqueiam uma feature que as desrespeite, então precisam ser só as que você sustenta. Mostro as 8 em uma
linha cada; as três primeiras são as obrigatórias.

**Sua decisão** — [D2 · muda o produto] **As 8 regras estão certas?**
- **aprovar** (recomendado) — gravo as 8 como estão e sigo para a governança (quem aprova mudanças no
  padrão); as 8 saíram das suas respostas, e ajustar depois custa só uma versão nova do padrão.
- **ajustar** — diga o número da regra e o que muda (ex.: "a 3 vira recomendada"); eu reescrevo e mostro
  de novo.
- **ver uma na tela** — escolha um número e eu descrevo como fica uma tela que cumpre e uma que não
  cumpre aquela regra.
- **não sei** — explico com a regra 1 o que muda para quem usa a tela quando ela é obrigatória.

**Próximo passo** — Com as regras confirmadas, a etapa 5 define quem aprova mudanças e como o padrão
ganha versão.
