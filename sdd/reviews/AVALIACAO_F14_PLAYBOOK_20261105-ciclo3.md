# AVALIACAO: F14_PLAYBOOK — ciclo 3 (focado, decisão D4 do Roberto)

- **Modo:** veredito · **Base:** HEAD `17dc00c`, foco `git diff 9b3dad1 HEAD` · **Data:** 2026-11-05
- **Quem avaliou:** agente de contexto fresco; não viu a conversa do build
- **Evidência:** `sdd/reports/evidence/F14_PLAYBOOK/AVAL3-01` a `AVAL3-13`
- **Limites da prova:** bloco do curador gerado por script; G3 rodada isolada; mutantes contra 4 módulos

<<<AVALIACAO
VEREDITO: NEEDS_WORK

## Estado dos achados do ciclo 2

FECHADOS: N-H1 (o conserto criou N3-H1), N-M1, N-M2, N-L1, N-L1b, N-L2, N-L3, N-L4, N-L5, N-L7, N-L8. ABERTO: N-M3 (fechou sem conflito; dobra no conflito, N3-M3; sem versionamento não tem teste, N3-M2). REGREDIU: N-L6 (cegou caminho legítimo, N3-M1).

## AT do foco

PASS: 001 nos dados reais (11 DESIGN, 44 linhas, 0 diferenças contra um oráculo pelo cabeçalho), 021, 024 no caminho sem conflito, 026, 040, 041, 043, 044. REPROVA: 001 nas linhas de ataque (N3-H1), 014, 015 e 018 (N3-M1). PARCIAL: 024 (N3-M2, N3-M3). NAO_VERIFICADO: 038 e o Verify Gate (log ausente ao final).

## Mutantes (`AVAL3-12`)

8 plantados, 3 mortos, 5 vivos: conjunto ignora PERGUNTA OBRIGATÓRIA · `arquivo_do_projeto` sem a saída da raiz · `check` aceita `../fora` · mkdir do item 3 sem `sdd/releases` · troca do `check=` vira no-op.

## ACHADOS novos

### Grave

- **N3-H1.** Regressão do conserto N-H1: a nota ou o resumo dá a contagem à lição errada. A regra pega o ID da 1ª célula que cita alguma lição, sem exigir que seja a coluna da fonte; o molde permite `Fonte` = ficha. O conferidor imprime AUTO, e `--aplicar`, lint, anti-collapse e trava saem 0. Nos dados reais de hoje, nenhuma linha dispara.

### Médios

- **N3-M1.** Regressão do N-L6: `check=` com caminho que começa por ponto (`.github/…`, `.agents/…`) é recusado, e o `--cruzar` propõe o que a trava recusa.
- **N3-M2.** O item 8 não diz como saber se o projeto versiona `sdd/releases/`; no sdd-open, o registro entra no commit e deixa a regra G3 vermelha.
- **N3-M3.** No conflito do item 9, o registro não é reaplicado, e a contagem dobra numa frente nova.

### Leves

- **N3-L1.** `ACEITAR` com evidência em arquivo com espaço no nome reprova.
- **N3-L2.** Frase de regra antes do ID, sem veredito depois, conta. **N3-L3.** `N. A.` com espaço não é N.A.
- **N3-L4.** Item 6 "nada aplicado": o registro fica fora do git, e uma frente nova rejulga. Sem dado errado.
- **N3-L5.** O `grep -n -A3` do curador corta bullet com mais de 4 linhas.
- **N3-L6.** Contagem + aposentadoria da mesma lição gasta o único redespacho; o brief não avisa.
- **N3-L7.** O DESIGN ainda lista a fonte antiga do registro; 5 mutantes vivos.

## Limites, não defeitos

Existiam antes do diff: `| LM-x | N/A | ✔ tratado |` perde a contagem; barra escapada parte a célula; linha sem barra final não é lida; `check=` em link que sai da raiz passa.
>>>
