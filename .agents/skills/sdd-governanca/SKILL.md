---
name: sdd-governanca
description: "Revisão de governança do SDD Open, depois do Define e antes da UX Review, para DEFINE que trata dinheiro, saldo, lançamento, nota fiscal, tributo, folha ou dado pessoal. Compara o DEFINE com um catálogo curado (lançamento que não se apaga, partidas dobradas, fechamento de período, trilha de auditoria, segregação de funções, aritmética exata, importação idempotente e outros) e recomenda requisitos novos em EARS com teste negativo, uma decisão por item; grava sdd/reviews/GOVERNANCA_REVIEW_{FEATURE}.md. Use quando o DEFINE tiver um desses gatilhos ou quando o usuário disser /sdd-governanca. Sem gatilho, responde N.A. em uma linha."
compatibility: "Requer bash >= 3.2 e git >= 2.20. Não executa nada no banco do projeto; a prova que ela recomenda vira script chamado pelo cmd do Verify Gate."
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.1.0"
  fase: "Gov"
---

# sdd-governanca — revisão de governança

> Abra a resposta com o banner: `⚖️ GOVERNANÇA`.

Num sistema financeiro, contábil ou fiscal, governança responde uma pergunta: **daqui a cinco anos,
um fiscal, um auditor ou um perito reconstrói o que aconteceu, quem fez e por quê — com prova de que
nada foi alterado depois?** Esta fase confere se o DEFINE exige isso **antes** que o Design e o código
endureçam — mudar um requisito aqui custa uma linha; depois do Build, custa migração.

## Entrada

`/sdd-governanca sdd/features/DEFINE_{FEATURE}.md`

## Processo

Siga `references/PROCEDIMENTO.md` à letra: triagem por gatilhos → padrão do projeto → item a item →
relatório → uma decisão por lacuna → aplicar no DEFINE. O catálogo é
`references/CATALOGO_GOVERNANCA.md`; o relatório usa `assets/GOVERNANCA_REVIEW_TEMPLATE.md` e é gravado
em **`sdd/reviews/GOVERNANCA_REVIEW_{FEATURE}.md`**; o padrão do projeto usa
`assets/GOVERNANCA_PADRAO_TEMPLATE.md` e fica em `sdd/GOVERNANCA_PADRAO.md` (raiz de `sdd/`, um por projeto —
nunca em `sdd/features/`).

**Nesta porta, a prova de cada lacuna aplicada é um script.** Para cada lacuna que o profissional
mandar aplicar e que tenha `prova_script` no catálogo:

1. adapte só os nomes de tabela e coluna aos do DEFINE e grave em `sdd/tests/governanca/{FEATURE}_<Gnn>.sql`
   — um arquivo por feature: o mesmo item adaptado a outra tabela, numa feature futura, não sobrescreve este;
2. acrescente `psql -v ON_ERROR_STOP=1 -f sdd/tests/governanca/{FEATURE}_<Gnn>.sql` ao `cmd` do bloco
   `verify_gate` **existente** do DEFINE — nunca crie um 2º bloco;
3. **não mexa na inversão nem na guarda de schema**: o script já sai `0` só quando o banco **recusa** a ação
   proibida, e falha quando a aceita ou quando o nome de tabela/coluna não confere. Não ponha `!` nem
   `|| true` na frente;
4. o `cmd` roda contra um **banco de desenvolvimento, de teste ou um branch — nunca contra produção**: mesmo
   com `rollback`, a tentativa trava a linha e dispara os triggers. Se o projeto só tem o banco de produção,
   escreva isso no DEFINE e use o `prova_manual` até existir um banco de teste.

O `prova_manual` vai para o AT como roteiro **sempre** — com ou sem script. O script prova a metade que o
banco recusa; a metade que depende da aplicação (ex.: "cada estorno gera 1 linha na trilha") só o roteiro prova.

Quem escreveu o Define não se revisa: rode em conversa nova ou despache um subagente que receba só o
DEFINE e esta skill.

## Regras que não se negociam

- **Base legal só do catálogo, e só `confirmado`.** Base `nao-confirmado` não se cita — nem artigo, nem
  número de lei, nem "aproximadamente". Use a frase padrão do procedimento e fique com o fundamento técnico.
- **Uma decisão por lacuna**: aplicar · recusar (com motivo) · adiar. Nunca "aplicar todos".
- **Sem tema financeiro, sem relatório**: N.A. em uma mensagem, sem arquivo. A triagem é pelo sentido, não só
  pela palavra — e, em dúvida, não é N.A.
- **A skill recomenda; o profissional decide e responde.** Essa linha fecha todo relatório.

## Quality Gate

```text
[ ] Triagem registrada (gatilhos com linha/AT, ou N.A. em 1 mensagem sem arquivo)
[ ] GOVERNANCA_PADRAO.md lido (confirmado em 1 linha) ou criado (5 campos, 1 mensagem)
[ ] Todo item do catálogo com exatamente 1 veredito; cobertura em 1 linha no topo
[ ] Cada lacuna: o que muda no app · por quê · EARS · como provar · severidade
[ ] Base legal só de item confirmado; senão a frase padrão
[ ] Uma decisão por lacuna; recusa com motivo vai a Riscos aceitos
[ ] Aplicados viram AT no DEFINE + script em sdd/tests/governanca/ chamado pelo cmd do gate
[ ] Clarity Score antes e depois · linha fixa de responsabilidade · resumo de etapa
```

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é `/sdd-governanca`.

**Próximo passo:** `/sdd-ux-review sdd/features/DEFINE_{FEATURE}.md` se há interface; senão
`/sdd-design sdd/features/DEFINE_{FEATURE}.md`.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
