# Fragmento — Clarify (protocolo do token de ambiguidade)

> Reusável. Lido pelo `/define` (Step 5.4). **Regra de honestidade:** diante de ambiguidade,
> o agente **marca, nunca chuta** — suposição silenciosa é a classe de erro mais cara do
> funil (só aparece no smoke ou em prod).

## O token

Forma ativa canônica (a ÚNICA que o `verify-gate.sh` detecta, e só fora de code fences):

```
[NEEDS CLARIFICATION: <pergunta específica>]
```

- Vai **no lugar exato da ambiguidade** (Problem, ATs, Constraints — qualquer seção).
- Enquanto houver token ativo, `sdd/bin/verify-gate.sh` devolve **exit 5**
  (`clarification-pending`): `/build`, a fase Release e `/drive` **param e voltam ao `/define`**.
  Não é gate vermelho de build — **nunca** aciona iteração de DESIGN.
- `--print` é isento (uso de autoria durante a redação do DEFINE).

### Convenção de menção (anti-falso-positivo)

Toda referência **documental** ao token — em template, fragmento, exemplo ou histórico —
vai **dentro de code fence** (como acima) ou **sem os colchetes** (ex.: "o protocolo NEEDS
CLARIFICATION…"). A forma canônica em prosa aberta = marcador ativo, e bloqueia.

## As 9 categorias (varrer TODAS antes de declarar o DEFINE pronto)

| # | Categoria | Pergunta-guia |
|---|---|---|
| 1 | Escopo | O que está dentro/fora? Qual slice é este? |
| 2 | Modelo de dados | Que entidades/colunas/estados? Quem é o dono da tabela? |
| 3 | Fluxo UX | O que o usuário vê em cada estado (vazio, erro, sucesso)? |
| 4 | NFRs | Latência, volume, custo de token, janela de cron? |
| 5 | Integrações | provedor de mensagens, videoconferência, e-mail, servidores MCP — qual contrato/limite? |
| 6 | Edge cases | Gatilho indesejado, linha ausente, permissão negada, fila cheia? |
| 7 | Restrições | O que não pode mudar? Precedente/landmine aplicável? |
| 8 | Terminologia | Termo do domínio com 2 leituras (cliente×conta, pedido×ordem)? |
| 9 | Sinal de conclusão | Como sabemos que acabou? Qual o comando pass/fail? |

Para cada categoria: **Clear / Partial / Missing**. Partial e Missing geram token.

## Protocolo de resolução

1. **≤5 perguntas por rodada**, via `AskUserQuestion` — múltipla escolha (2–4 opções),
   **opção recomendada primeiro** com "(Recomendado)". Mais de 5 pendências? Prioridade:
   o que muda arquitetura > escopo > o resto; nova rodada depois.
2. **Resposta integra NO CORPO da spec**: substituir o texto ambíguo (e o token) pela decisão —
   nunca deixar a resposta só em apêndice com o texto contraditório intacto.
3. **Registrar no log** `## Clarifications` do DEFINE:
   ```markdown
   ## Clarifications
   ### Session 2026-08-15
   - [x] (6-edge cases) Fila cheia descarta ou enfileira? → enfileira com TTL 24h; integrado em ATs (AT-004)
   ```
   (Formato: `- [x] (categoria) pergunta → resposta; integrado em <seção>`. Sem a forma
   canônica do token — convenção de menção.)
4. **Gate mecânico:** DEFINE pronto = **zero tokens ativos**. Conferir: o bloco de gate roda
   `verify-gate.sh` (exit 5 enquanto restar token).
