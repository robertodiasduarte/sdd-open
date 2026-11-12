# Trocas do molde PERGUNTA_DECISAO.md para o starter: no starter não há encadeamento de fases nem os lints do pacote.

## sdd/templates/fragments/PERGUNTA_DECISAO.md
<<<< antes
> próprios exemplos. O `sdd/bin/skill-lint.py --conversa` confere as perguntas desses exemplos.
====
> próprios exemplos.
>>>> depois

## sdd/templates/fragments/PERGUNTA_DECISAO.md
<<<< antes
   da decisão em palavras e se ela continua sendo perguntada com o encadeamento ligado
   (`flow.autonomous: true`; ver `sdd/templates/fragments/FLUXO_ENCADEADO.md`).
====
   da decisão em palavras. A coluna da direita vale só no SDD Open, com o encadeamento de fases ligado;
   aqui toda pergunta é feita.
>>>> depois

## sdd/templates/fragments/PERGUNTA_DECISAO.md
<<<< antes
   Antes da primeira pergunta `[auto · de rotina]` da sessão, rode `bash sdd/bin/sdd-fluxo.sh estado`:
   0 ligado · 1 desligado · 64 valor inválido (avise com a linha que ele imprimiu e trate como
   desligado). A pergunta do OK da `sdd-release` ("Posso finalizar…?") é D1 por construção e não leva
   marca: o texto dela é contrato. `sdd/bin/sdd-decisoes-lint.sh --sites` confere a marca e o rótulo.
====
   A pergunta do OK da `sdd-release` ("Posso finalizar…?") é D1 por construção e não leva marca: o texto
   dela é contrato.
>>>> depois
