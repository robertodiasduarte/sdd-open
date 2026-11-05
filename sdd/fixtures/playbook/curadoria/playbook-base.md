# Playbook sintético — base do --aplicar e do próximo ID (self-test do playbook-curator.sh)

## Sempre

- [LM-001] ajudou=0 mordeu=0 · conf=2026-09-01 · sup: `termo_base` :: regra base. **Do instead:** ação. · promovido_para: —

## Dados

## Backend

- [LM-016] ajudou=0 mordeu=0 · conf=2026-09-01 · sup: `preflight` `OPTIONS` :: o preflight cai quando a rota exige login (fixture). **Do instead:** liberar o OPTIONS. · promovido_para: —
- [LM-020] ajudou=0 mordeu=0 · conf=2026-09-01 · sup: `agendador` `fila_de_envio` :: o agendador chama a rota sem o segredo (fixture). **Do instead:** mandar o cabeçalho literal. · promovido_para: —
  continuação de teste do LM-020 (deve ser preservada pelo --aplicar).

## Frontend

## Infra / deploy

- [LM-004] ajudou=2 mordeu=2 · conf=2026-09-01 · sup: `dois_ambientes` :: dois ambientes com o mesmo nome (fixture). **Do instead:** conferir o destino. · promovido_para: —

## Reviews / harness

## Domínio

- [LM-021] ajudou=0 mordeu=0 · conf=2026-09-01 · sup: `dominio_fixture` :: d. **Do instead:** e. · promovido_para: —

## Tombstones

- [LM-022] ☠ 2026-09-01 :: aposentado — o maior ID é tombstone: o próximo livre tem de ser LM-023 (nunca reusar)
