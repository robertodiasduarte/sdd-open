# Como funciona

Quem trabalha com dado de cliente no mesmo computador em que programa corre um risco simples: um
`git add .` leva junto a planilha de clientes, o `.env` com senhas ou o certificado A1, e o próximo
`git push` publica tudo. Apagar depois não desfaz — o histórico e as cópias continuam.

Esta skill instala um alarme no próprio git do projeto (o `pre-commit`). A cada commit, ele olha só o
que está indo naquele commit e recusa quando encontra:

- CPF ou CNPJ com dígito verificador válido, com ou sem pontuação, nas linhas novas de arquivos de texto
  (inclusive CSV exportado do Excel em Latin-1);
- arquivo de senhas: `.env` e `.env.*` (o `.env.example` e o `.env.sample` passam);
- certificado com chave privada: `.pfx`, `.p12` e `.pem` que contém `PRIVATE KEY`;
- planilha nova, de qualquer tamanho: `.xlsx`, `.xls`, `.ods`, `.csv`.

A recusa explica o que achou (com o número mascarado), por que importa e como corrigir. Quando a pessoa
conferiu e o dado é fictício ou autorizado, `git commit --no-verify` grava aquele commit mesmo assim.

A instalação só acontece com o OK de quem usa o computador e nunca por cima de outro alarme. O alarme
fica em `.git/hooks/pre-commit`: vale para todas as frentes (worktrees) do projeto, não vai para o
GitHub e sai com um comando.

É um alarme, não uma garantia: não lê o conteúdo de `.xlsx`, `.xls` e `.ods` (por isso recusa qualquer
planilha nova), não reconhece CNPJ alfanumérico e não olha commits antigos. Para saber se algo já foi
salvo no git, use a `sdd-checar-ambiente`.
