# Playbook (fixture colapso)

## Sempre

- [LM-001] ajudou=3 mordeu=0 · conf=2026-09-01 · sup: `termo_fixture` `config.yaml` :: Slot vazio no config significa pular o passo, nunca adivinhar comando. **Do instead:** deixar vazio e reportar "pulado". · promovido_para: —

## Backend

- [LM-003] ajudou=0 mordeu=1 · conf=2026-09-01 · sup: `.in(` `414` :: TEXTO REESCRITO UM. **Do instead:** outra coisa. · promovido_para: —
- [LM-004] ajudou=2 mordeu=0 · conf=2026-09-01 · sup: `criado_em` :: TEXTO REESCRITO DOIS. **Do instead:** outra coisa. · promovido_para: —
- [LM-005] ajudou=0 mordeu=0 · conf=2026-09-01 · sup: `status` `arquivado` :: Pedido arquivado ainda aparece em relatório se o filtro olha só `ativo`.
  **Do instead:** rejeitar `arquivado` explicitamente no filtro do relatório. · promovido_para: —

## Infra / deploy

## Tombstones

- [LM-006] ☠ 2026-09-01 :: promovido a check automático no CI
