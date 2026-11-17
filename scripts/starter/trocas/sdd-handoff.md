# Trocas da sdd-handoff para o starter: sem o verify-gate.sh e o handoff-lint.py do sdd-open, a conferência é a
# leitura descrita em "Sem terminal".

## SKILL.md
<<<< antes
- estado do Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>` saiu N em <data>);
====
- estado do Verify Gate, se o projeto tiver um gate por comando (o comando e o que ele saiu em <data>);
>>>> depois

## SKILL.md
<<<< antes
`python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_{FEATURE}.md` sobre o arquivo gravado: ficha
com Objetivo, Status e Verify Gate, prompt de retomada em bloco de código (só a ficha ✅ sem
continuação o dispensa), slice datado no histórico, nenhum placeholder, nenhum "como discutimos". Vermelho ⇒ corrija a ficha e rode de novo antes de
entregar.
Sem terminal, ou sem esse script no projeto: a conferência é a releitura do checklist de **Sem terminal**.
====
Releia a ficha antes de entregar: Objetivo e Status preenchidos, prompt de retomada em bloco
de código (só a ficha ✅ sem continuação o dispensa), slice datado no histórico, nenhum placeholder, nenhum
"como discutimos". Faltou algo ⇒ corrija antes de entregar.
>>>> depois

## SKILL.md
<<<< antes
compatibility: Requer bash >= 3.2 e git >= 2.20. Não depende de memória proprietária de nenhum agente — a ficha vive no repositório.
====
compatibility: Funciona na web (claude.ai, ChatGPT), onde a ficha sai no chat, e em qualquer agente com acesso ao projeto. Não depende de memória proprietária de nenhum agente.
>>>> depois

## SKILL.md
<<<< antes
  `## Ship`: preencha a que tiver o que dizer e apague a que ficar vazia; o `handoff-lint.py` não exige
  nenhuma delas, mas reprova a que ficar com o texto do molde entre chaves.
====
  `## Ship`: preencha a que tiver o que dizer e apague a que ficar vazia; nenhuma é obrigatória, mas
  nenhuma fica com o texto do molde entre chaves.
>>>> depois

## SKILL.md
<<<< antes
[ ] Cabeçalho: Objetivo · Status · Feito (com SHAs) · Falta · DoD · Verify Gate · veredito da release
====
[ ] Cabeçalho: Objetivo · Status · Feito (com SHAs) · Falta · DoD
>>>> depois

## SKILL.md
<<<< antes
- **Veredito da release** (PASS / CONCERNS / WAIVED) vai na ficha; WAIVED exige o registro
  completo (`classe= · finding= · motivo= · por= · data=`).
====
- **O que foi publicado** (commit ou PR, e o endereço quando houver) vai na ficha.
>>>> depois

## assets/HANDOFF_EXAMPLE.md
<<<< antes
| **Verify Gate** | 🔴 2 em 2026-03-11 (o caso do pagamento no dia do vencimento) — `sdd/bin/verify-gate.sh sdd/features/DEFINE_CONTROLE_HONORARIOS.md` |
====
>>>> depois

## assets/HANDOFF_EXAMPLE.md
<<<< antes
Estado do gate: `sdd/bin/verify-gate.sh sdd/features/DEFINE_CONTROLE_HONORARIOS.md` saiu 2 em 2026-03-11.
====
>>>> depois

## SKILL.md
<<<< antes
- **O bloco `## Publicado` é gerado, nunca escrito à mão:** `python3 sdd/bin/ficha-publicado.py {FEATURE}` projeta uma
  linha por ledger de `sdd/releases/{FEATURE}/`, entre os marcadores `<!-- publicado:inicio … -->` e
  `<!-- publicado:fim -->`, e não toca o resto da ficha. Quando a `sdd-release` chama esta skill, você escreve **só**
  o que o ledger não diz: `## Falta`, os alertas, a linha `Curadoria:` e o veredito; nada do bloco Publicado se repete
  em "Feito" nem em "Histórico de slices". Ledger com `trilha: curta` ⇒ ficha curta: Ficha, Publicado e Falta, até 20
  linhas (o `handoff-lint.py` aceita o bloco Publicado como histórico).
====
- **O que foi publicado vai uma vez só,** na seção `## Publicado`: uma linha por publicação, a mais recente no topo
  (data, o que subiu, o commit ou PR). Nada dessa linha se repete em "Feito" nem em "Histórico de slices"; o resto da
  ficha diz o que a publicação não diz: o que falta e os alertas.
>>>> depois

## assets/HANDOFF_EXAMPLE.md
<<<< antes
<!-- publicado:inicio (gerado por ficha-publicado.py a partir do ledger; não edite à mão) -->
- 2026-03-04 · etapa-1 · shipado · PASS · deploy real · trilha completa · 3f9a1c2
<!-- publicado:fim -->
====
- 2026-03-04 · etapa 1 · cadastro de clientes e lançamentos mensais · commit 3f9a1c2
>>>> depois
