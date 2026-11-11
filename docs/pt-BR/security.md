<!-- Idioma: **Português** · [English](../security.md) -->

# Segurança embutida no fluxo: `sdd-seguranca`

A IA constrói o caminho feliz e esquece a tranca. O SDD Open pede a tranca na fase em que ela custa menos, a partir de
um catálogo das 22 falhas de segurança mais comuns em app feito com IA (tabela sem segurança por linha, chave secreta
no código, registro de outra pessoa pelo id, CORS aberto, HTML do usuário exibido sem escapar, cabeçalhos de segurança
ausentes, instrução escondida num documento, agente com poder demais e outras). Cada item do catálogo traz, num lugar só:

| Campo | Quem usa |
|---|---|
| `frase` — a regra que previne | o bloco do `AGENTS.md` (os 5 itens de maior risco da sua stack) e a `sdd-build` |
| `at` — o teste de aceitação, com o lado negativo | o passo de segurança da `sdd-define` |
| `evitar` — a decisão de design que fecha a falha | a seção `## Segurança` do DESIGN |
| `padrao` — o que a varredura procura | `sdd/bin/seguranca-varredura.sh`, em toda publicação |
| `confira` — como conferir à mão | quem não tem terminal (claude.ai, ChatGPT) e a conferência antes de publicar |

O catálogo fica em `.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md`. O texto é próprio; cada item cita
uma referência pública (OWASP, CWE).

## A sua stack decide o que vale

Um item só dispara quando a stack dele está no projeto. A varredura detecta a stack (`supabase/` ou `@supabase/` no
`package.json` ⇒ supabase; `vercel.json`, `.vercel/` ou `vercel` no `package.json` ⇒ vercel; `package.json` ou um
`.html` ⇒ web); o slot `security.stack` do `sdd/config.yaml` passa por cima (`nenhuma` = só os itens de toda stack).
Projeto sem Supabase nunca recebe regra de Supabase.

## Fase a fase

| Fase | O que acontece |
|---|---|
| Sempre | o `init` e o `sync` escrevem no `AGENTS.md` as 5 regras de maior risco da sua stack e uma linha que aponta para a `sdd-seguranca` |
| Brainstorm | três perguntas — quem pode ver, quem pode mudar, quanto alguém pode pedir — viram um perfil de risco de três linhas |
| Define, passo 12 | a `sdd-seguranca` no modo Define: sem login, rota pública, dado de terceiros, envio de arquivo, banco nem IA paga, responde N.A. em uma linha; senão, propõe até 5 itens por rodada, uma decisão por item (aplicar · recusar com motivo · adiar). O aplicado vira teste de aceitação no Verify Gate. Avisa, não trava |
| Design | a seção `## Segurança`: onde mora cada segredo, quem vê e quem muda cada tabela, a credencial de cada agente, cabeçalhos e CORS do host, e o "como evitar" de cada item aplicado como decisão. O `design-lint.py` avisa (exit 0) se ela faltar |
| Build | `seguranca-varredura.sh --regras` antes da 1ª tarefa; o BUILD_REPORT lista uma vez os itens recusados e adiados |
| Release | a varredura em toda publicação (item 10 da 0a) e a passada 0c do modelo contra a lista fixa |
| A qualquer hora | o modo incidente: "vazou a chave", "a tabela ficou aberta" — primeiro fechar a porta, depois preservar a evidência, dimensionar, corrigir, comunicar e registrar |

## A varredura

```text
bash sdd/bin/seguranca-varredura.sh [--base REF] [--saida ARQUIVO]
```

Só lê, sem rede, bash 3.2 + Python stdlib. Bloqueia só duas coisas, e só quando **esta publicação as acrescenta**
(diff da árvore de trabalho contra `origin/<branch padrão>`; sem essa ref, tudo conta como novo):

- **S11** segredo literal (cabeçalho de chave privada, prefixos conhecidos de chave com o corpo da chave, chave de
  serviço atribuída com valor); variável lida pelo nome não é segredo, e a varredura nunca imprime o valor;
- **S01** tabela criada em migração sem `enable row level security` em nenhuma migração (só com Supabase).

O resto é aviso, com o id do item, `arquivo:linha` e a conferência à mão. O mesmo achado numa linha que já existia é
aviso marcado `(já existia)`. A tela mostra os `security.max_warnings` mais graves (padrão 5); o arquivo de `--saida`
guarda a lista inteira.

| Exit | Significado |
|---|---|
| `0` | `RESULTADO: NADA ACHADO` |
| `1` | `RESULTADO: AVISOS` — CONCERNS na publicação |
| `2` | `RESULTADO: BLOQUEADO` — NON_WAIVABLE na publicação |
| `64` | `RESULTADO: ERRO DE USO` — opção, slot, catálogo ilegível, ou fora de um repositório git |

Falso positivo se dispensa na própria linha, com motivo: `sdd-seguranca: aceito S16 — <motivo>` num comentário da
linha ou da de cima. Sem motivo não vale, e a varredura diz isso. Chave real nunca se dispensa: ela já vazou, e o modo
incidente começa por trocá-la.

Os outros modos leem o mesmo catálogo: `--stack`, `--regras`, `--checklist`, `--agents`.
