# Changelog

## 1.2.0 - 2026-10

- Modo "hooks do projeto": quando o sdd-open instalou os hooks dele (`core.hooksPath = sdd/hooks`, com o
  dispatcher), `alarme.sh instalar` liga o alarme por `git config sdd.higieneDado on` (nada é gravado em
  `.git/`) e `desinstalar` desliga; o dispatcher chama `pre-commit.sh` no fim de cada commit. Qualquer outro
  `core.hooksPath` ou pre-commit alheio continua recusado (exit 2). O `init` do sdd-open migra um alarme já
  instalado em `.git/hooks` para este modo.
- O arquivo do alarme é sempre `<git-common-dir>/hooks/pre-commit`: `git rev-parse --git-path` seguia o
  `core.hooksPath` e apontaria para o dispatcher. A última linha da recusa, com `core.hooksPath` definido,
  passa a indicar `alarme.sh desinstalar` em vez de `rm`.
- Detecções, mensagens de recusa e códigos de saída do alarme não mudam.

## 1.1.1 - 2026-10

- Passa a ser mantida no sdd-open (`.agents/skills/sdd-higiene-dado/`); os testes ficam em `tests/` na
  raiz do repositório e não vão mais para o projeto de quem instala; sai `agents/openai.yaml`.
- `alarme.sh instalar` tira as linhas `sdd-open:generated` da cópia gerada pelo `sync` antes de gravar
  o hook: instalar da fonte ou da cópia produz o mesmo `.git/hooks/pre-commit`.
- Identificação e rodapé apontam para o sdd-open. Detecções, mensagens e códigos de saída não mudam.

## 1.1.0 - 2026-10

- Seção "Como falar com o aluno": 3 etapas com nome fixo (Verificar · Explicar o alarme · Instalar) e os
  atendimentos Commit recusado e Desinstalar; toda resposta com status, o que foi feito, agora, decisão
  com opções e próximo passo; glossário na primeira vez; sem saída crua de comando; sem citar as
  próprias instruções.
- A pergunta de instalação vem com três opções (sim / não / ver o que ele recusa); o commit recusado
  pergunta "O que fazemos com este arquivo?" com corrigir / dado fictício / gravar mesmo assim.
  `--no-verify` continua só com a escolha explícita da pessoa, para aquele commit.
- Comandos, conferências e ordem dos passos não mudam.

## 1.0.0 - 2026-10

- Criada a skill `sdd-higiene-dado`: alarme de commit (pre-commit) instalado com OK explícito.
- Recusa CPF/CNPJ com dígito verificador válido (com e sem máscara, inclusive em CSV Latin-1),
  `.env`/`.env.*` (exceto `.env.example` e `.env.sample`), `.pfx`, `.p12`, `.pem` com chave privada e
  planilha nova de qualquer tamanho; número mascarado na mensagem.
- Mensagem ensina a corrigir, cita `git commit --no-verify` e diz como desinstalar.
- Não instala por cima de outro alarme (husky, `core.hooksPath`, pre-commit próprio); desinstalar
  remove só o alarme desta skill.
