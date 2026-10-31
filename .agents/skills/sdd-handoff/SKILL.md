---
name: sdd-handoff
description: Passa o bastão para uma sessão nova e mantém a FICHA DA FEATURE do SDD Open — um arquivo por feature em sdd/handoffs/HANDOFF_{FEATURE}.md, com estado agregado, pendências, alertas e um prompt de retomada autossuficiente (IDs, caminhos e comandos colados). Use quando o usuário disser "estou no limite de contexto", "documenta pra continuar depois", "passa o bastão", /sdd-handoff, quando a fase Release rodar, ou quando o agente perceber que o contexto está acabando no meio de um trabalho longo.
compatibility: Requer bash >= 3.2 e git >= 2.20. Não depende de memória proprietária de nenhum agente — a ficha vive no repositório.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.1.1"
  updated: "2026-10"
  fase: "transversal"
---

# sdd-handoff — ficha da feature + passar o bastão

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-handoff v2.1.1 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Duas responsabilidades, sempre nesta ordem:

1. **Manter a ficha da feature** — `sdd/handoffs/HANDOFF_{FEATURE}.md`, **um arquivo por
   feature** (nunca por slice), com o estado agregado no topo.
2. **Gerar o prompt da próxima sessão** (opcional quando não há continuação).

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Família | 0 |
| 2 | Estado | 1 |
| 3 | Ficha | 2 |
| 4 | Prompt de retomada | 3 e 3b |
| 5 | Limpeza | 4 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Handoff: ✅ 1 Família · ✅ 2 Estado · ▶️ 3 Ficha · ⬜ 4 Prompt de retomada · ⬜ 5 Limpeza`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.

## Princípio

A próxima sessão começa com **zero memória** desta conversa — em qualquer agente, em qualquer
máquina. Ela só lê o repositório e o prompt que você der. Então o handoff é **autossuficiente,
concreto e acionável**: IDs reais, caminhos, comandos exatos, sem "como discutimos".

A ficha é projeção narrativa; a fonte determinística do que foi publicado é o ledger
(`sdd/releases/{F}/*.yaml`). O que só a ficha guarda é a narrativa: casos, alertas, próximos
passos — então é isso que ela carrega bem.

## Processo

### 0. Resolver a família (antes de criar arquivo)

Slug drift é a doença que este passo mata: a mesma feature não pode gerar
`HANDOFF_PAGAMENTO_PIX.md` e `HANDOFF_PIX_CHECKOUT_S2.md`. Procure por domínio:
`ls sdd/handoffs/`, `ls sdd/releases/`, o `{F}` dos artefatos em `sdd/features/`. Achou ficha
→ **atualize-a**. Ambíguo → proponha o match e confirme dentro de uma pergunta que já vai
acontecer. Só crie arquivo novo para família genuinamente nova; o slug escolhido é o
`feature_id` canônico em ledger, ficha e artefatos.

### 1. Capturar o estado (varrer a conversa)

- **Feito** — o que foi construído/decidido/publicado, com versões, SHAs, arquivos.
- **Casos e testes em aberto** — entidades reais com **IDs concretos** (id, e-mail, caminho).
- **Falta** — o que resta, o que está bloqueado e por quê.
- **Próximos passos** — lista **ordenada**, cada item com comando ou arquivo.
- **Alertas** — o que pode quebrar, invariantes, o que **não** mexer.
- **Git** — branch, pasta, se já está na branch padrão, comando de limpeza.

Se falta um ID que você sabe que existe, **rode o comando agora** para pegá-lo — a próxima
sessão não terá como.

### 2. Persistir a ficha

Use `sdd/templates/HANDOFF_TEMPLATE.md`. Regras:

- **Slice novo = subseção nova no topo** do histórico; a ficha do cabeçalho reflete o agregado.
- **Sem total autoritativo de slices** ("s2 de s3" ❌): escopo muda. Mudança de escopo ou
  pausa é **linha nova** em um bloco `## Eventos`, nunca sobrescrita silenciosa.
- **DoD manda no ✅**: só marcar completa quando o Definition of Done estiver objetivamente
  satisfeito.
- **Cap ~10 KB**: ao passar, comprimir slices antigos fechados em 1 linha cada (o detalhe está
  no git e no ledger).
- **Veredito da release** (PASS / CONCERNS / WAIVED) vai na ficha; WAIVED exige o registro
  completo (`classe= · finding= · motivo= · por= · data=`).
- Datas absolutas. Nada que o git ou o ledger já registrem.

### 3. Gerar o prompt da nova sessão

Bloco de código pronto para colar, seguindo o **Prompt de retomada** do template:

- manda ler `sdd/handoffs/HANDOFF_{F}.md` primeiro, depois DEFINE e DESIGN;
- resume em 2–3 linhas onde paramos;
- setup antes de código (branch, pasta, `git fetch`/rebase se atrasada);
- **tarefas numeradas** com IDs e comandos **colados**, não referenciados;
- alertas (o que não quebrar) e fora de escopo;
- estado do Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>` saiu N em <data>);
- fluxo de publicação (`/sdd-release` no fim).

Regra de ouro: sem `«placeholder»` sobrando. Linha sem valor concreto: ou você busca o valor
agora, ou apaga a linha. O prompt tem de funcionar **sozinho**, mesmo se a ficha sumir.

### 3b. Conferir a ficha

`python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_{FEATURE}.md` sobre o arquivo gravado: ficha
com Objetivo, Status e Verify Gate, prompt de retomada em bloco de código (só a ficha ✅ sem
continuação o dispensa), slice datado no histórico, nenhum placeholder, nenhum "como discutimos". Vermelho ⇒ corrija a ficha e rode de novo antes de
entregar.

### 4. Oferecer limpeza

Feature já publicada e sessão dentro de branch/worktree descartável → oferecer o comando de
remoção (rodado fora dele). Ficha ✅ completa → oferecer arquivar os artefatos em
`sdd/archive/{F}/` com 1 OK. Nunca apagar sem confirmação.

## Checklist

```text
[ ] Família resolvida: ficha existente atualizada OU família nova justificada
[ ] Cabeçalho: Objetivo · Status · Feito (com SHAs) · Falta · DoD · Verify Gate · veredito da release
[ ] WAIVED com registro completo (se houver)
[ ] Sem "s<n> de s<m>"; mudança de escopo em ## Eventos
[ ] Todo caso tem ID concreto, não nome solto
[ ] Prompt autossuficiente, sem placeholders, com comandos colados
[ ] Comando de limpeza incluído (se aplicável)
```

## Anti-padrões

- ❌ `HANDOFF_{F}_s3.md` — slice nunca vira arquivo novo.
- ❌ "Continue de onde paramos" sem dizer onde foi.
- ❌ Entidade por nome sem ID.
- ❌ Comando ou caminho que a próxima sessão vai "descobrir".
- ❌ Documentar só o sucesso e omitir o que ficou quebrado.
- ❌ Sobrescrever "Falta" sem linha em ## Eventos.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
