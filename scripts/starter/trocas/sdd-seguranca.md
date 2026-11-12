# Trocas da sdd-seguranca para o starter: sem o seguranca-varredura.sh; cada item já tem a conferência à mão.

## SKILL.md
<<<< antes
compatibility: "Funciona em qualquer agente, inclusive na web sem terminal: cada item tem a conferência à mão. Com bash e Python 3.9, sdd/bin/seguranca-varredura.sh lê o mesmo catálogo e varre o repositório (só leitura, sem rede)."
====
compatibility: "Funciona em qualquer agente, inclusive na web sem terminal: cada item tem a conferência à mão. No SDD Open, um script lê o mesmo catálogo e varre o repositório a cada publicação."
>>>> depois

## SKILL.md
<<<< antes
**A stack.** Com terminal: `bash sdd/bin/seguranca-varredura.sh --stack` (o slot `security.stack` do
`sdd/config.yaml` passa por cima da detecção). Sem terminal: pergunte em que o app é feito e anote. Item com
====
**A stack.** Pela pasta do projeto (`package.json`, `supabase/`, `vercel.json`) ou, sem acesso a ela, pergunte
em que o app é feito e anote. Item com
>>>> depois

## SKILL.md
<<<< antes
1. Com terminal: `bash sdd/bin/seguranca-varredura.sh --checklist` lista os itens da stack, os de maior risco
   primeiro, cada um com o "confira". Sem terminal: leia o catálogo, filtre pela stack e pela fase (sem
====
1. Leia o catálogo, filtre pela stack e pela fase (sem
>>>> depois

## manifest.json
<<<< antes
    "varredura determinística da publicação (sdd/bin/seguranca-varredura.sh), para os itens com padrão",
====
    "varredura determinística da publicação, no SDD Open, para os itens com padrão",
>>>> depois

## references/CATALOGO_SEGURANCA.md
<<<< antes
> para quem não roda script. Quem lê este arquivo por máquina é só `sdd/bin/seguranca-varredura.sh`.
====
> para quem não roda script. No SDD Open, um script lê este arquivo por máquina: não mude a forma dos campos.
>>>> depois

## references/INCIDENTE.md
<<<< antes
prove pelo "confira" e pelo teste do item. Rode `bash sdd/bin/seguranca-varredura.sh` antes de publicar a correção.
====
prove pelo "confira" e pelo teste do item antes de publicar a correção.
>>>> depois
