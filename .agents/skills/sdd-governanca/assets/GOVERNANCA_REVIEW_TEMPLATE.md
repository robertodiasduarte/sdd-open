# GOVERNANÇA: {FEATURE}

| Feature | Data | Padrão do projeto | DEFINE |
|---|---|---|---|
| {FEATURE} | {AAAA-MM-DD} | uso = {…} · multi_cnpj = {…} · IA grava sozinha = {…} · guarda = {…} | {caminho do DEFINE} |

**Gatilhos encontrados:** {gatilho (linha ou AT)} · {…}

**Cobertura:** {N} itens: {a} já cobertos · {b} lacunas · {c} N.A. · {d} na 2ª camada

## Lacunas

### {Gnn} — {elemento} · severidade {alta|média|baixa}

**O que muda no app:** {uma frase}

**Por quê:** {fundamento técnico}. **Base legal:** {texto_citavel da base confirmado no catálogo | ainda não confirmada no catálogo — confira na fonte antes de citar. | o catálogo não aponta base legal para este item — o fundamento técnico vale por si.}

**Requisito (EARS):** **If** {ação proibida}, **then** the system **shall** {recusar e …}

**Como provar:** {prova_manual adaptada | prova_script adaptada, sem mexer na inversão}

**Decisão:** {aplicar | recusar — motivo: … | adiar}

## Já coberto

| Item | Onde no DEFINE (linha ou AT) |
|---|---|
| {Gnn} — {elemento} | {…} |

## N.A.

| Item | Motivo |
|---|---|
| {Gnn} — {elemento} | {…} |

## 2ª camada

| Item | Por que ficou para depois |
|---|---|
| {Gnn} — {elemento} | {não obrigatório nesta feature · adiado pelo profissional em {data}} |

## Riscos aceitos

| Item | Quem | Quando | Por quê |
|---|---|---|---|
| {Gnn} — {elemento} | {nome} | {AAAA-MM-DD} | {motivo dado na recusa} |

## Aplicado no DEFINE

| Lacuna | AT novo | AT reescrito (antes → depois) | Clarity Score antes → depois |
|---|---|---|---|
| {Gnn} | {AT-0nn} | {AT-0mm: "…" → "…" · ou —} | {x/15 → y/15} |

---

> A skill recomenda; o profissional decide e responde.
>
> No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura (`information_schema`,
> `pg_policies`, `pg_trigger`) que o SQL criou o que estes itens exigem: os itens com `prova pós-build = sim`
> no catálogo têm o que conferir no banco depois de aplicada a migration.
