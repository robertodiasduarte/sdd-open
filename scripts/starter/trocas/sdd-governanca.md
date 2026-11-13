# Trocas da sdd-governanca para o starter: o despacho pelo passo 11 do sdd-define e a fronteira de escrita só
# existem num projeto com o init do sdd-open.

## SKILL.md
<<<< antes
Quem escreveu o Define não se revisa. Desde a v2.4.0 do pacote, o passo 11 (Governança) do `sdd-define`
despacha esta skill em todo Define, num agente fresco, com o brief `references/revisor.md`: o revisor faz
os passos 1 a 4 e devolve o bloco `<<<GOVERNANCA`; quem conduz o Define faz os passos 5 e 6, e é **dono do
`prova_script`** (grava o `.sql` e o liga ao `cmd` do Verify Gate; o Design só o lista no manifest).
Chamada avulsa desta skill continua valendo para revisar de novo um DEFINE já escrito: rode em conversa
nova, com só o DEFINE e esta skill.
====
Quem escreveu o Define não se revisa: rode esta skill numa conversa nova, com só o DEFINE e esta skill.
>>>> depois

## references/revisor.md
<<<< antes
(`sdd-fluxo.sh despachar revisor-governanca …`, exit 40). Contrato de máquina: `sdd/WORKFLOW_CONTRACTS.yaml`
› `revisor_governanca`.
====
(`sdd-fluxo.sh despachar revisor-governanca …`, exit 40), num projeto com o SDD Open.
>>>> depois

## references/revisor.md
<<<< antes
  depois (`sdd/bin/governanca-fronteira.sh`).
====
  depois.
>>>> depois

## SKILL.md
<<<< antes
**Próximo passo:** `/sdd-ux-review sdd/features/DEFINE_{FEATURE}.md` se há interface; senão
`/sdd-design sdd/features/DEFINE_{FEATURE}.md`.
====
**Próximo passo:** a `ux-review` do seu projeto (criada pela `ux-review-builder`) se há interface; senão
a skill `sdd-design`, com o DEFINE atualizado (na web, mande o documento junto com o pedido).
>>>> depois

## SKILL.md
<<<< antes
compatibility: "Requer bash >= 3.2 e git >= 2.20. Não executa nada no banco do projeto; a prova que ela recomenda vira script chamado pelo cmd do Verify Gate."
====
compatibility: "Funciona na web (claude.ai, ChatGPT), onde o relatório sai no chat, e em qualquer agente com acesso ao projeto. Não executa nada no banco do projeto."
>>>> depois
