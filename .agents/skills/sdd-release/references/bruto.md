# Evidência bruta — o anexo da Release

> Lido no item 10 da `sdd-release`, depois de a Release desta publicação existir e o smoke depois do deploy ter
> rodado. Não é parada: o passo roda sem pergunta e diz o resultado em 1 linha.

## O que é bruto

Durante a frente, o que serve de prova mas ninguém lê inteiro fica em `sdd/reports/evidence/{F}/bruto/`: a transcrição
de uma conversa com um modelo, a cópia de um gabarito, o log de uma série de execuções. Essa pasta está no `.gitignore`:
o bruto é grande, e o que um lint ou uma pessoa lê (o log de cada AT, o do Verify Gate, os vereditos, os resumos) já
está nos documentos da frente, no git.

## O passo

Na raiz do projeto, com a tag da Release desta publicação (no Open, a `vX.Y.Z` que o CI criou):

```bash
bash .agents/skills/sdd-release/scripts/anexar-bruto.sh {F} <tag>
```

| Saída | O que dizer ao aluno (1 linha) |
|---|---|
| `SEM BRUTO` (0) | nada: a frente não tem bruto |
| `ANEXADO` (0) | "A evidência bruta foi anexada à Release `<tag>` como `evidencia-bruta-{F}.tar.gz`." |
| `NADA ANEXADO` (1) | o motivo que o script imprimiu, e que o bruto continua na pasta da frente; vira pendência 🐛 na ficha |
| `NÃO CONFERIDO` ou `ANEXO DIFERENTE` (1) | o motivo; pendência 🐛 na ficha, com o comando para rodar de novo |

## Por que cada regra existe

- **A varredura vem antes do envio:** o anexo é público e permanente. Uma transcrição pode trazer um e-mail, uma chave
  falsa escrita por extenso numa sonda ou um CPF de exemplo que fecha a conta; a `docs-varredura.sh --pasta` barra e o
  script não envia nada.
- **A prova é o anexo baixado, não o exit do envio:** o script baixa o arquivo publicado e compara a lista de arquivos com
  a da pasta.
- **Sem Release, nada é enviado:** num projeto que não publica Release no GitHub, o bruto fica na pasta da frente; diga
  isso em 1 linha. Ele se perde quando a worktree da frente é removida, então guarde-o antes, se ele for necessário.
- **Pedido de remoção de um dado que estava no bruto:** troque o anexo por um sem o arquivo (`--clobber`) e prove com
  `bash sdd/bin/docs-varredura.sh --pasta <anexo extraído> --padrao '<o dado>'` (o `CONTRIBUTING.md` do Open tem o
  procedimento inteiro).
