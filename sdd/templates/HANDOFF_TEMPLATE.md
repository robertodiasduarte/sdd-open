# HANDOFF: {Feature Name}

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | {FEATURE_NAME} |
| **Objetivo** | {1 frase: o que muda para quem usa} |
| **Status** | {🔨 em andamento · 🚢 publicado · ✅ DoD fechado · ⏸ pausado} |
| **Última sessão** | {YYYY-MM-DD} |
| **Branch / pasta** | `{branch}` · `{caminho}` |
| **Artefatos** | `sdd/features/DEFINE_{F}.md` · `sdd/features/DESIGN_{F}.md` · `sdd/reports/BUILD_REPORT_{F}.md` |
| **Verify Gate** | {🟢 0 · 🔴 2 · inconclusivo 3 · assinatura 4 · clarificar 5} — `sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md` |

## Feito

- {o que está pronto, com o comando ou arquivo que PROVA — nunca "acho que funciona"}

## Falta

- {o que falta, em ordem, cada item começando por verbo}

## Definition of Done

- [ ] {critério verificável 1}
- [ ] {critério verificável 2}

## ⛔ Landmines desta feature

- {armadilha que mordeu ou quase mordeu, com o "faça isto em vez disso"; candidata ao `sdd/playbook.md`}

## Casos e testes em aberto

- {caso não coberto · teste que falha · smoke pendente}

---

## Prompt de retomada

> Cole este bloco inteiro numa sessão nova do seu agente. Ele tem de ser autossuficiente:
> caminhos absolutos, IDs, comandos exatos. Quem lê não viu a sessão anterior.

```text
Retomar a feature {FEATURE_NAME}.

Contexto: {2-3 frases — o que é, por que existe, em que fase está}.
Pasta: {caminho absoluto} · branch {branch}.
Leia primeiro: sdd/handoffs/HANDOFF_{F}.md, depois sdd/features/DEFINE_{F}.md e DESIGN_{F}.md.
Estado do gate: `sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md` saiu {N} em {data}.

Próxima ação: {1 ação concreta, com o comando}.
Não faça: {o que NÃO mexer e por quê}.
Landmines: {1 linha por armadilha}.
```

---

## Histórico de slices

### {slice/sessão mais recente} — {YYYY-MM-DD}

- {o que aconteceu nesta sessão, em 3-6 linhas}

### {slice anterior} — {YYYY-MM-DD}

- {…}
