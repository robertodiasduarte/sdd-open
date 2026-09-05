# Fragment: WORKER BRIEF — despacho stateless de item do manifest (`/build --mode briefs`)

> **Uso:** no `--mode briefs` (EXPERIMENTO R3 do benchmark LLM×SDD), o orquestrador (Opus 1M)
> compila **1 brief por item do file manifest** e despacha workers baratos (Haiku) em paralelo
> por wave de dependência. O worker vê **APENAS este brief** — nada de DESIGN/DEFINE inteiros.
> A qualidade do build depende da curadoria dos INPUTS: brief incompleto = worker confiante e
> errado. As 4 seções são obrigatórias.

---

## Template (compilado pelo orquestrador, 1 por item)

```markdown
## SUBTASK
{1 linha: ação + arquivo, copiada da linha do manifest}

## INPUTS (completos e INLINE — você NÃO tem acesso ao DESIGN/DEFINE)
- {trecho do DESIGN relevante a ESTE arquivo: code patterns, contratos, assinaturas}
- {conteúdo atual do arquivo, se Action=Modify; ou dos arquivos que ele importa}
- {convenções aplicáveis — ex.: bloco relevante do AGENTS.md}
- DECISÕES FECHADAS (não reabrir): {provider, modelo, nomes, rotas — o que o DESIGN já decidiu}

## ACCEPTANCE CRITERIA (numerados, pass/fail — serão verificados pelo orquestrador)
1. {critério funcional extraído do DESIGN para este arquivo}
2. Comando de verificação passa: `{tsc --noEmit … / php -l … / node --check …}`
3. Nenhum arquivo além de {path} foi tocado.

## OUTPUT FORMAT
- Write em {path exato}. Sem comentários explicativos. Sem TODO.
- Se um INPUT estiver faltando ou for contraditório: prefixe seu retorno com
  `INPUT GAP: {1 linha}` e prossiga com o que há — NUNCA invente contrato/assinatura.
- Retorne só o essencial (status + INPUT GAP se houver) — sem preâmbulo, sem
  "melhorias" fora do escopo do SUBTASK.

## GUIDELINES (não-negociáveis)
- Cirúrgico: só as linhas do SUBTASK; não refatorar nem "melhorar" código adjacente.
- Simples: nada não pedido (sem abstração/configurabilidade especulativa).
- Evidência: rode o comando de verificação e cole o output — nunca declare sem rodar.
```

---

## Regras de despacho (orquestrador)

1. **Waves por dependência E por arquivo disjunto** — itens sem dependência mútua e com paths
   distintos vão na mesma wave (paralelo, mesma mensagem, sem isolation extra). Colisão de
   path → waves separadas.
2. **Drift detection roda ANTES do despacho**, sobre o manifest, no orquestrador — nunca no worker.
3. **Exclusões duras (NUNCA vão pro worker barato):**
   - itens do inventário **LLM Prompts** → orquestrador + gate `prompt-builder` (qualidade>custo);
   - itens de **superfície de segurança** (RLS, gates de edge auth, migrations com lógica) →
     orquestrador; migration com lógica mantém a exigência de smoke real.
4. **Verificação por wave, no orquestrador:** comando incremental + resultado × acceptance
   criteria → **PASS / FIX / ESCALATE**. FIX segue a escada de retry do `build.md`
   (FIX-brief fresco, critério + erro verbatim). Só então libera a próxima wave.
5. **`INPUT GAP` no retorno** = defeito de compilação do brief, não do worker: o orquestrador
   completa o INPUT e redespacha (não conta como FAIL da escada).
6. **Steps 5–6 do `/build` intocados:** `sdd/bin/verify-gate.sh` continua o gate autoritativo e
   BLOQUEANTE; BUILD_REPORT ganha a tabela "briefs despachados × modelo × resultado × retries".
