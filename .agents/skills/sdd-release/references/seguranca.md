# Segurança na publicação — varredura (0a, item 10), passada 0c e fecho

Lido pelos itens da `sdd-release` que citam este arquivo. A fonte dos itens é o catálogo da skill `sdd-seguranca`
(`.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md`); o único leitor dele é `sdd/bin/seguranca-varredura.sh`.

## 0a, item 10 — varredura (em toda publicação)

`bash sdd/bin/seguranca-varredura.sh --saida sdd/reports/evidence/{F}/SEGURANCA.log` — só lê, sem rede; compara com
`origin/{default_branch}`.

| Exit | Ação |
|---|---|
| `2` | **abortar** (NON_WAIVABLE), citando cada `🛑 Snn arquivo:linha` e o "confira à mão" que o script imprimiu: segredo literal (S11) ou tabela sem RLS (S01) acrescentados nesta publicação. Segredo real que chegou ao repositório **já vazou**: diga isso e aponte o modo incidente da `sdd-seguranca` (trocar a chave antes de qualquer outra coisa) |
| `1` | CONCERNS: os avisos que o script mostrou (até `security.max_warnings`, os mais graves) vão para a linha **Segurança:** do bloco do OK e para a ficha |
| `0` | siga |
| `64` ou `127` | **abortar** com a causa e a frase de atualizar `sdd/bin/` do item 5 (catálogo ausente: o `init` instala a `sdd-seguranca`) |

Falso positivo sai pela dispensa na linha do código (`sdd-seguranca: aceito Snn — <motivo>`), que o script lista como
`✔ aceito`; nunca por dispensa no OK. Chave real nunca se dispensa.

## 0c — passada do modelo (em toda publicação, com a lista fixa)

`bash sdd/bin/seguranca-varredura.sh --checklist` dá a lista do catálogo para a stack do projeto, os de maior risco
primeiro (sem terminal: o modo checklist da `sdd-seguranca`). Confira o diff contra cada item, na ordem, e marque
**cumprido**, **não cumprido** (com `arquivo:linha`) ou **não se aplica a este diff**. Além da lista: credencial no
código, permissão afrouxada, dado pessoal em log ou resposta, proteção de acesso removida (o que o diff tira conta
tanto quanto o que ele põe). Não cumprido que expõe dado ou credencial é **segurança crítica** (NON_WAIVABLE na 0d); o
resto é aviso. Os itens recusados ou adiados no Define (sessão `### Segurança` das Clarifications do DEFINE) não são
achado: vão para a linha **Segurança:** do bloco do OK.

## Fecho (ficha, item 17)

Os avisos da varredura e os itens recusados ou adiados no Define entram como pendências. A ficha termina com a linha:
"Confira no app publicado (cabeçalhos, CORS, cadastro, limites): `/sdd-seguranca app <URL>`. Se algo vazar: modo
incidente da `sdd-seguranca`."
