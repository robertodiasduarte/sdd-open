# Compatibilidade por capacidades

## Necessário

- **Terminal com bash, git e awk**, aberto na pasta do projeto: macOS, Linux, ou Git Bash no Windows
  (vem com o Git for Windows). O alarme não usa Python nem Node.
- **Escrita em `.git/hooks/`** do projeto, só no passo `instalar` e só com o OK da pessoa.

## Onde funciona

- **Claude Code e Codex** no terminal: a skill roda `alarme.sh` e repassa a saída.
- **Terminal da pessoa**, sem agente: os mesmos comandos do Quick start.

## Onde não funciona

- **claude.ai e ChatGPT na web** (skill enviada como .zip): não há terminal nem acesso à pasta do
  projeto. A skill diz isso e indica rodar no Claude Code ou no Codex. Não entrega o alarme para colar
  à mão.

## Limitações

- Projetos com `core.hooksPath` (husky, lefthook) ou com `pre-commit` próprio: a skill não instala e
  explica como acrescentar a verificação ao alarme existente.
- `git commit --no-verify` e ferramentas que fazem commit sem rodar hooks passam sem alarme.
- Instruções de portabilidade não provam comportamento idêntico em todos os agentes; os cenários de
  `evals/cases.json` precisam ser rodados em cada um.
