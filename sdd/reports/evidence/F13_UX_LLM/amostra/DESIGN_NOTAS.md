# DESIGN: Notas de versão

> Technical design for implementing Notas de versão

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | NOTAS |
| **DEFINE** | `sdd/features/DEFINE_NOTAS.md` |
| **LLM Prompts** | true |
| **Status** | Ready for Build |

## Key Decisions

### Decision 1: Conferência por código

**Choice:** o redator é um modelo e quem confere a citação é código.

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `src/notas/LOOP_SPEC.md` | Create | o processo em laço e os prompts dos estágios (linha 1 do inventário) | (general) | None |

**Total Files:** 1

## LLM Prompts

### Inventário

| # | Nome | Tipo | Arquivo de destino | Versão | Provedor/Modelo | Origem da entrada | Consumidor da saída | Material de referência | Completeness | Refator de? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | notas_de_versao | loop | `src/notas/LOOP_SPEC.md` | v1 | provedor-exemplo / modelo-exemplo-1 | lista de commits entre 2 tags, gerada por código | NOTAS.md, lido por pessoas | formato do item, abaixo | um item por commit visível | novo |

### Contrato por prompt

#### Prompt 1: notas_de_versao

| Atributo | Valor |
|---|---|
| **Tom/audiência** | direto, para quem atualiza o software |
| **Tipo de saída** | Markdown, uma linha por item |
| **Fallback aprovado** | commit sem descrição legível fica de fora, com o motivo |
| **Autônomo?** | sim, não pode pedir nada de volta |
| **Verification interna** | sim, todo item cita um hash da lista |
| **Eval mínimo pré-ship** | sem ground truth: definir antes da release |
| **Intenção** | gerar NOTAS.md com um item por commit visível, para quem atualiza o software; pronto quando a conferência por código aprova todo item |
| **Perfil de risco dos efeitos** | locais e reversíveis: grava um arquivo |
| **Ground truth disponível** | nenhum |

**Material de referência a injetar:**
- Formato do item: `- <descrição> (<hash>)`.
- Commit visível: assunto começando por `feat:` ou `fix:`. Os outros ficam de fora, sem item.
- Quando a conferência reprova um item, o modelo reescreve só esse item, a partir do próprio texto anterior.

**Decisões já fechadas:**
- Pasta do processo: `src/notas/`. Prompts em arquivos `.txt`.
- Provedor `provedor-exemplo`, modelo `modelo-exemplo-1`: nomes fictícios desta amostra, já decididos. Nenhuma chamada real ao modelo nesta tarefa.
- Orçamento: até 4 ciclos.

## Next Step

Execute o **SDD Build by RDD**.
