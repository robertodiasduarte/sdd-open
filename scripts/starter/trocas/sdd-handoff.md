# Trocas da sdd-handoff para o starter: sem o verify-gate.sh e o handoff-lint.py do sdd-open, a conferência é a
# leitura descrita em "Sem terminal".

## SKILL.md
<<<< antes
- estado do Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>` saiu N em <data>);
====
- estado do Verify Gate (o comando do projeto e o que ele saiu em <data>, ou `sem gate por comando`);
>>>> depois

## SKILL.md
<<<< antes
`python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_{FEATURE}.md` sobre o arquivo gravado: ficha
com Objetivo, Status e Verify Gate, prompt de retomada em bloco de código (só a ficha ✅ sem
continuação o dispensa), slice datado no histórico, nenhum placeholder, nenhum "como discutimos". Vermelho ⇒ corrija a ficha e rode de novo antes de
entregar.
Sem terminal, ou sem esse script no projeto: a conferência é a releitura do checklist de **Sem terminal**.
====
Releia a ficha antes de entregar: Objetivo, Status e Verify Gate preenchidos, prompt de retomada em bloco
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
