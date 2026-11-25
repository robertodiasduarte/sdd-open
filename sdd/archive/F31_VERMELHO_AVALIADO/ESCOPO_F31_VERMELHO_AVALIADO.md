# ESCOPO — F31 Vermelho avaliado

> Frente aberta em 2026-11-25. Nada construído. Próxima fase: `sdd-define`.

## Problema

O `report-lint.py` (F30 S2, v2.27.0) exige `AT-nnn.antes.log` com exit fora de 0, 126 e 127. Ele olha só o exit do
comando: não sabe se **aquele** AT avaliou algum caso. Num gate composto (um comando para vários ATs), um AT sem teste
nenhum herda o exit vermelho dos outros e passa. Caso observado num projeto, com o AT em `PASS 0 · FAIL 0`.

## Já coberto (não refazer)

- Antes obrigatório por AT, com o mesmo comando do depois: `problema_antes` em `sdd/bin/report-lint.py`.
- Antes que sai 0 é recusado; `shall continue to` exige antes verde.
- Gate inteiro vermelho sem sinal de asserção: `sdd/bin/gate-baseline.sh` sai 3.
- A regra "falhou avaliando" está em prosa em `disciplina-de-teste.md`, §1; nenhuma máquina a confere por AT.

## O que falta

1. **Principal:** no `AT-nnn.antes.log`, acusar AT cuja própria linha diz zero casos avaliados.
2. **Brecha a medir:** tabela sem a coluna `Antes` só gera aviso. Decidir se relatório novo deve ser recusado
   (relatórios antigos continuam só com aviso).

## A decidir no Define

- D1. Formato que a máquina lê (ex.: `AT-nnn … (PASS n · FAIL n)`) e o que fazer com log sem contagem: recomendado, aviso.
- D2. Aviso primeiro, bloqueio depois de N relatórios sem alarme falso: recomendado.
- D3. O módulo novo que ainda não existe conta como vermelho válido (hoje conta): manter, e separar de zero casos.
- D4. Item 2 entra nesta frente ou fica para outra.

## Critério mínimo

- Caso que falha antes: relatório com `antes.log` em `[exit=2]` e a linha do próprio AT em `PASS 0 · FAIL 0`, hoje aceito.
- Controles que seguem aceitos: AT com `FAIL 1`; `shall continue to` verde; `N.A.` de gate fora de `test`/`cmd`; log
  sem contagem; relatório anterior à v2.27.0.
- Windows e Python stdlib, como o resto do `sdd/bin`.

## Origem

Landmine semente LM-002 ("asserção que não avalia nada sai `exit 0`"), com reincidência num projeto que a usa.
A promoção lá (`promovido_para=sdd/bin/report-lint.py`) só entra depois que esta frente publicar **e** o projeto
atualizar a cópia do Open.
