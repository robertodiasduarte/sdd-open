# Fontes, origem e limites

O usuário escolheu como materiais esta conversa e os templates/protocolos SDD instalados. A investigação de um sistema de BPO financeiro discutida na conversa é ilustrativa, não auditoria nem gabarito técnico. Nenhum fato específico sobre o produto é embarcado como regra fixa.

Os snapshots usados para construir este contrato foram lidos em 09/11/2026. Naquela data e naquela distribuição, a skill de Brainstorm declarava versão 1.1.0 e a de Define não declarava versão; em execução, vale a versão que a skill instalada declarar. Localizadores abaixo são relativos às respectivas dependências de origem, não caminhos dentro deste pacote. Hashes identificam o material consultado, não fixam versões futuras nem comprovam autoria/veracidade.

| ID | Material de origem | SHA-256 do snapshot (12 primeiros caracteres) |
|---|---|---|
| M01 | brainstorm/SKILL.md | 714a3647d8ac… |
| M02 | brainstorm/BRAINSTORM_TEMPLATE.md | c7f70e2dc7a7… |
| M03 | brainstorm/brainstorm-protocol.md | 60c67386ce3e… |
| M04 | brainstorm/como-falar.md | a40116d0d0f7… |
| M05 | define/SKILL.md | 270d81c721c5… |
| M06 | define/DEFINE_TEMPLATE.md | 4b7071663c26… |
| M07 | define/define-protocol.md | 3f8f7e32fcdc… |
| M08 | define/EARS.md | 8d53c7ef2cc7… |
| M09 | define/CLARIFY.md | 84a39008df86… |
| M10 | define/VERIFY_GATE.md | de8b56ba0563… |
| M11 | CASO_CONVERSA.md | 6304f44fa2de… |

Os arquivos canônicos permanecem nas skills instaladas; não foram incorporados nem modificados. As referências de orquestração desta skill são implementação nova baseada no contrato aprovado. Em execução, localizar e ler a versão disponível e apontar incompatibilidades.

Na criação da 1.0.0, os documentos completos dos frameworks SDD não foram inspecionados: a integração foi definida como etapa anterior ao Brainstorm, com passagem de documentos e contexto. A 1.1.0 adaptou a skill às convenções do SDD Open (camada de conversa, pasta de saída, lints do pacote); o que foi executado em cada versão está em `manifest.json`.

Para cada SaaS investigado, criar um catálogo próprio com evidências atuais, localizadores, coleta e limitações. A data de criação desta skill não estabelece vigência de funcionalidades dos produtos.
