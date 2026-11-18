# Trocas da sdd-desempenho-banco para o starter: sem os scripts de sdd/bin; cada ficha já tem a conferência à mão e o diagnóstico tem o roteiro do painel.

## SKILL.md
<<<< antes
compatibility: "Funciona em qualquer agente, inclusive na web sem terminal: cada ficha tem a conferência à mão e o diagnóstico tem o roteiro do painel. Com bash e Python 3.9, sdd/bin/desempenho-varredura.sh lê o mesmo catálogo e varre o repositório (só leitura, sem rede), e sdd/bin/desempenho-diagnostico.sh interpreta o advisor e o inspect db."
====
compatibility: "Funciona em qualquer agente, inclusive na web sem terminal: cada ficha tem a conferência à mão e o diagnóstico tem o roteiro do painel. No SDD Open, um script lê o mesmo catálogo e varre o repositório a cada publicação, e outro interpreta o advisor e o inspect db."
>>>> depois

## SKILL.md
<<<< antes
**A stack.** Com terminal, a mesma da segurança: `bash sdd/bin/seguranca-varredura.sh --stack` (o slot
`security.stack` passa por cima). Sem terminal: pergunte em que o app é feito. Ficha com `stack: todas` vale para
====
**A stack.** Pela pasta do projeto (`supabase/`, `package.json` com `@supabase/`, arquivos `.sql`) ou, sem acesso a
ela, pergunte em que o app é feito. Ficha com `stack: todas` vale para
>>>> depois

## SKILL.md
<<<< antes
A `sdd-release` roda `bash sdd/bin/desempenho-varredura.sh --saida sdd/reports/evidence/{F}/DESEMPENHO.log`. Ela
mostra só o que esta mudança traz (o que já existia vira uma linha de contagem; `--tudo` lista). `1` é CONCERNS:
os avisos vão para a linha **Desempenho:** do bloco do OK. Nunca aborta, nem quando a varredura não roda. Falso
====
Antes de publicar, confira as fichas de `references/CATALOGO_DESEMPENHO.md` contra o que esta mudança traz (no SDD
Open, um script faz isso a cada publicação). O que achar é aviso: nunca impede a publicação. Falso
>>>> depois

## SKILL.md
<<<< antes
     arquivo **fora da pasta do projeto** e rode `bash sdd/bin/desempenho-diagnostico.sh --ler <arquivo>`.
   - **Supabase CLI ligado ao projeto** — `bash sdd/bin/desempenho-diagnostico.sh --coletar --consentimento`.
====
     arquivo **fora da pasta do projeto** e interprete-a pelas regras abaixo.
   - **Supabase CLI ligado ao projeto** — com o OK, os comandos de leitura `supabase db advisors --type performance
     --level info` e `supabase inspect db` (`index-stats`, `outliers`, `calls`), sempre com o projeto no ar como alvo.
>>>> depois

## SKILL.md
<<<< antes
- Na publicação, a `sdd-release` roda a varredura sozinha (modo **release**).
====
- Antes de publicar, a pedido: confira as fichas contra o que a mudança traz (modo **release**). A publicação do SDD
  Starter não faz essa conferência sozinha.
>>>> depois

## SKILL.md
<<<< antes
3. **A idade das estatísticas** (consulta 1) entra em `--estatisticas-desde AAAA-MM-DD`.
====
3. **A idade das estatísticas** (consulta 1): anote a data; é ela que decide se um índice "não usado" pode ser apagado.
>>>> depois

## SKILL.md
<<<< antes
  ordem escrita nele, e não mostre valor de cliente nem senha (o script troca por `?` e `***`).
====
  ordem escrita nele, e não mostre valor de cliente nem senha (troque o valor por `?` e a senha por `***`; as consultas
  3, 7 e 8 já trazem o texto mascarado).
>>>> depois

## references/CONSULTAS_DIAGNOSTICO.md
<<<< antes
do projeto** (por exemplo, na pasta temporária do sistema) e passe esse arquivo ao intérprete. O texto que vem do
====
do projeto** (por exemplo, na pasta temporária do sistema) e interprete-a pelas regras da skill. O texto que vem do
>>>> depois

## manifest.json
<<<< antes
    "varredura determinística da publicação (sdd/bin/desempenho-varredura.sh), só aviso, para as fichas com padrão",
    "diagnóstico do banco no ar, com o OK da pessoa a cada execução, interpretado por sdd/bin/desempenho-diagnostico.sh",
====
    "varredura determinística da publicação, no SDD Open, só aviso, para as fichas com padrão",
    "diagnóstico do banco no ar, com o OK da pessoa a cada execução, interpretado pelas regras da skill",
>>>> depois

## references/CATALOGO_DESEMPENHO.md
<<<< antes
> roda script. Quem lê este arquivo por máquina é só `sdd/bin/desempenho-varredura.sh`. Nada aqui bloqueia a
====
> roda script. No SDD Open, um script lê este arquivo por máquina: não mude a forma dos campos. Nada aqui bloqueia a
>>>> depois
