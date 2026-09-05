# Fragmento — Verify Gate (taxonomia dos gates executáveis)

> Reusável. Anexado conceitualmente ao DEFINE (bloco `## Verify Gate`) e lido por
> `/build`, a fase Release e `sdd/bin/verify-gate.sh`. É o habilitador da F1 do SDD v2
> (loop engineering / Boris Cherny): **o critério de aceite vira comando, não prosa.**

## Por que existe

No SDD v1 o aceite morava em prosa (`Acceptance Tests`, `Success Criteria`) que ninguém
executava de forma determinística. Sem um gate executável, autonomia (F3 Ralph, F4 driver)
vira **lixo em escala** — "o loop roda, mas contra o quê ele para?". O Verify Gate é esse
critério de parada: um comando `pass/fail` que qualquer loop (humano ou agente) roda.

## O bloco (vai no DEFINE)

````markdown
## Verify Gate

> Gate executável de aceite (pass/fail). `/build` e a fase Release rodam isto — é **bloqueante**.

```yaml
verify_gate:
  kind: test
  cmd: "npm test -- src/x.test.ts"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```
````

Rodar: `sdd/bin/verify-gate.sh sdd/features/DEFINE_<FEATURE>.md`

## Campos

| Campo | Obrigatório | Significado |
|---|---|---|
| `kind` | sempre | categoria do gate (tabela abaixo) |
| `cmd` | exceto `manual-ux` | comando executável; em `manual-ux` use `"N/A (manual-ux)"` |
| `pass_when` | sempre | critério objetivo: `exit 0` (default) · `exit N` · `contains: TEXTO` |
| `threshold` | só `eval` | meta numérica embutida no `cmd` (ex.: `recall >= 0.80`) — informativa aqui |
| `manual_fallback` | só `manual-ux` | checklist humano a percorrer + assinar no BUILD_REPORT |

> **Sem inline comments nas linhas de valor** do bloco machine-read — o parser pega tudo
> após o primeiro `:`. Comentários ficam fora do fence.

## Taxonomia (`kind`)

| kind | Quando | `cmd` típico | `pass_when` |
|---|---|---|---|
| `test` | lógica pura testável | `npm test -- <arquivo>.test.ts` · `pytest tests/x -q` | `exit 0` |
| `smoke` | edge/HTTP responde o esperado | `curl -sS -o /dev/null -w '%{http_code}' <url>` | `contains: 401` |
| `eval` | qualidade com limiar (avaliação de saída de LLM etc.) | `scripts/eval/run.sh --threshold 0.80` | `exit 0` (limiar no cmd) |
| `typecheck` | tipos/compilação | `tsc --noEmit` · `mypy .` | `exit 0` |
| `manual-ux` | UX pura (mobile/PWA/estética) | `N/A (manual-ux)` | gate **humano** (`manual_fallback`) |

### Derivar o `kind` do padrão EARS do AT (ver `fragments/EARS.md`)

| Padrão EARS do AT | `kind` natural |
|---|---|
| **When** (event-driven) | `test` — dispara o evento, asserta a resposta |
| **If/Then** (unwanted) | `test`/`smoke` **negativo** — provoca o gatilho pelo caminho real |
| **While** (state-driven) | `test` com fixture do estado |
| **Where** (optional) | `test` em matriz (flag on/off) |
| **shall continue to** (non-regression, bugfix) | `test` — caso de regressão explícito |

### Contrato de exit do `sdd/bin/verify-gate.sh`

| exit | Significado | Efeito em `/build` e a fase Release |
|---|---|---|
| `0` | 🟢 verde (passou) | segue |
| `2` | 🔴 vermelho (falhou) | **ABORTA** |
| `3` | inconclusivo (tool ausente OU ruído 403 WAF×runner) | caller decide; não conta vermelho |
| `4` | `manual-ux`: exige assinatura humana | `/build` mostra checklist · a fase Release exige recibo |
| `5` | clarification-pending: marcador ativo de ambiguidade no DEFINE (forma canônica fora de fence — ver `fragments/CLARIFY.md`) | **PARAR e voltar ao `/define`**. NÃO é vermelho de build: `/drive` e loops **nunca** iteram DESIGN por causa dele |
| `64` | bloco ausente/malformado | DEFINE inválido (sem gate) |

## Regras de ouro

1. **`manual-ux` NÃO finge automação.** É gate humano explícito (anti "passa técnico, é lixo
   estético"). `cmd: "N/A (manual-ux)"`; o `manual_fallback` é um checklist assinado no BUILD_REPORT.
2. **Ruído de infra ≠ regressão.** Smoke que recebe 403 do WAF×IP-do-runner é inconclusivo
   (exit 3), nunca vermelho. Prefira smoke rodando **na origem via SSH** (lição do fix do changelog).
3. **Nenhum gate cruza o a fase Release.** O gate é pré-condição do deploy, não o deploy.
4. **Tool ausente = inconclusivo (3), não vermelho.** Não trava a entrega por falta de uma ferramenta.
5. **`eval` embute o limiar no `cmd`** (o runner devolve exit≠0 se ficar abaixo) — `threshold`
   no bloco é documentação para humanos.

## Exemplos prontos (1 de cada kind)

```yaml
# test — módulo com teste ao lado
verify_gate: { kind: test, cmd: "npm test -- src/pricing.test.ts", pass_when: "exit 0", threshold: "—", manual_fallback: "—" }
```
```yaml
# smoke — edge protegida devolve 401 sem JWT
verify_gate: { kind: smoke, cmd: "curl -sS -o /dev/null -w '%{http_code}' https://api.exemplo.com/v1/relatorios", pass_when: "contains: 401", threshold: "—", manual_fallback: "—" }
```
```yaml
# manual-ux — app mobile, gate humano
verify_gate: { kind: manual-ux, cmd: "N/A (manual-ux)", pass_when: "checklist assinado", threshold: "—", manual_fallback: "smoke no celular real: (1) a tela inicial abre em <2s; (2) as listas rolam; (3) ▶ Continuar funciona; (4) o card de destaque aparece; (5) ← Voltar volta." }
```

> Nota: o bloco pode ser multi-linha (legível) ou inline `{ ... }` (compacto) — o parser
> lê `kind:`/`cmd:`/`pass_when:` na 1ª ocorrência em qualquer um dos formatos multi-linha.
> Para `manual-ux` o `cmd` é ignorado na execução (sempre cai no gate humano, exit 4).
