# DESIGN: FIXTURE — sintético (self-test do playbook-curator.sh)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FIXTURE |
| **Date** | 2026-09-02 |

## Landmines aplicáveis

> Varredura rodada em 2026-09-02 (fixture). Só linha desta seção com `LM-nnn` e veredito ✔ vira `ajudou+1`.

| Landmine | Fonte | Veredito | Como |
|----------|-------|----------|------|
| Agendador sem o segredo | `LM-020` | ✔ tratado | fixture: cabeçalho literal na chamada |
| Preflight que cai com login | `LM-016` | N.A. | fixture: a rota não é chamada pelo navegador; N.A. não conta |
| Nota sem ID | `nota_sem_lm` | ✔ tratado | fonte sem LM-nnn: não gera delta |

## Outra seção (fora da de landmines: não conta)

| x | `LM-021` | ✔ tratado | linha fora da seção: a colheita ignora |
