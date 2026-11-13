# Compatibilidade por capacidades

## Núcleo portátil

O fluxo depende de diálogo, leitura e escrita de texto. Não depende de um único fornecedor.

## Capacidades opcionais

- **Navegação:** permite analisar URLs de referência. Sem ela, usar capturas de tela ou descrição.
- **Acesso aos arquivos do projeto:** permite ler o `UX_STANDARD.md` e o DEFINE e gravar os artefatos na pasta do SDD.
- **Execução local:** permite rodar o validador estrutural incluído.

## Chat e agente

- No chat (ChatGPT, Claude), os três artefatos saem para download.
- No agente com acesso ao projeto (Claude Code, Codex), os documentos vão para a pasta do SDD e a `ux-review/` fica pronta para ser instalada como skill.

A regra da pasta do SDD está em `references/GOVERNANCE.md`.

## Limitações

Instruções de portabilidade não provam comportamento idêntico em todos os agentes. Validar a skill no ambiente de destino. Acesso à internet, persistência e escrita variam por produto e configuração.
