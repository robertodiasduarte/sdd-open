# Patterns do projeto — como a casa constrói

O `sdd/playbook.md` guarda o que **morde** (landmines). Esta pasta guarda como o projeto **constrói**: o
esqueleto que se copia para uma operação nova, uma tela nova, uma migration nova. O `sdd-design` cita
um pattern no lugar de reinventar o código, e o `sdd/bin/patterns-lint.sh` prova que o pattern citado
não apodreceu.

A pasta nasce só com este README. Escreva um pattern quando a mesma forma de construir aparecer pela
2ª vez, a partir de um arquivo real do projeto.

## Formato de um pattern (`sdd/patterns/<nome>.md`)

Título `# Pattern: <nome>` e 6 seções, nesta ordem (o lint recusa fora dela):

| Seção | O que vai nela |
|---|---|
| `## Quando se aplica` | o gatilho objetivo. Ex.: "toda operação nova que grava um pedido" |
| `## Esqueleto` | o código copiável, com a âncora `← arquivo:linha` em cada bloco |
| `## Checklist de conformidade` | itens verificáveis, um por linha |
| `## Exemplos canônicos` | os arquivos de referência e **por que** são referência |
| `## Landmines` | só os `LM-nnn` do playbook que se aplicam; nunca copie o texto deles |
| `## Validado em` | `AAAA-MM-DD · <sha> · <feature>` — a data em que o esqueleto foi conferido contra o código |

Toda âncora `arquivo:linha` precisa existir (o arquivo e a linha); um nome de arquivo sem pasta só vale
se for único entre os arquivos versionados.

## Como citar no DESIGN (seção Code Patterns)

```markdown
**Pattern:** `patterns/pedidos.md §Esqueleto` (validado_em 2026-11-03) — adaptações: nenhuma.
```

Só a linha que começa com `**Pattern:**` conta como citação; um caminho mencionado em prosa ou no File
Manifest não conta.

## Quem valida e o limite de idade

`bash sdd/bin/patterns-lint.sh sdd/patterns` confere a pasta: seções, âncoras, landmines e a data
(sai 0 ou 2). O `sdd-design` roda `bash sdd/bin/patterns-lint.sh --design sdd/features/DESIGN_<F>.md`:

- pattern **citado** com âncora morta ou validado há **mais de 90 dias** reprova (exit 2);
- pattern **não citado** com o mesmo defeito só avisa.

Ao mudar um esqueleto, confira de novo as âncoras (as linhas mudam) e atualize `## Validado em`.
Antes de confiar no lint, rode `bash sdd/bin/patterns-lint.sh --self-test`.

## O mapa de domínios (`sdd/patterns/dominio.md`)

É um pattern como os outros (as mesmas 6 seções) que o passo 1.5 do `sdd-define` lê para saber que
domínio uma feature toca. Dentro de `## Esqueleto`, um bloco por domínio:

```markdown
### ctx:pedidos

**Faz:** o pedido do cliente, do carrinho à entrega.
**Âncoras:** `pedido` · `pedido_item` · `app/pedidos.py` · `/pedidos`
sup: `pedido_item` `checkout`
```

- `### ctx:<slug>` — o nome do domínio; o CONTEXTO dele fica em `sdd/contexto/<slug>.md`.
- `**Âncoras:**` — termos entre crases que identificam o domínio num pedido: tabelas, módulos, rotas,
  comandos. Termos curtos e comuns (menos de 6 letras, sem `_ - . /`) não contam.
- `sup:` — os termos que o cartógrafo procura no playbook (`playbook-lint.sh --grep`).

Com 2 ou mais termos de um bloco no pedido, o `bash sdd/bin/contexto-lint.sh --sugerir <pedido>` recomenda
gerar ou reusar o CONTEXTO daquele domínio (no máximo 2 domínios por feature). Sem `dominio.md`, o
passo 1.5 diz "pulado" e o Define segue normalmente.
