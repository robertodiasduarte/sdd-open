# Playbook (fixture válida)

## Sempre

- [LM-001] ajudou=3 mordeu=0 · conf=2026-09-01 · sup: `termo_fixture` `config.yaml` :: Slot vazio no config significa pular o passo, nunca adivinhar comando. **Do instead:** deixar vazio e reportar "pulado". · promovido_para: —

## Backend

- [LM-003] ajudou=0 mordeu=1 · conf=2026-09-01 · sup: `.in(` `414` :: Lista grande no filtro vira URL longa e o servidor responde 414 sem o cliente lançar erro. **Do instead:** lotear em ≤150 itens e checar `error`. · promovido_para: —
- [LM-004] ajudou=2 mordeu=0 · conf=2026-09-01 · sup: `criado_em` `enviado_em` :: Convenção de timestamp não é universal no schema. **Do instead:** conferir a coluna antes de escrever a query. · promovido_para: —

## Infra / deploy

- [LM-002] ajudou=1 mordeu=0 · conf=2026-09-01 · sup: `deploy.yml` :: Deploy só em push para main. **Do instead:** trabalhar em branch off origin/main. · promovido_para: —

## Domínio

- [LM-005] ajudou=0 mordeu=0 · conf=2026-09-01 · sup: `status` `arquivado` :: Pedido arquivado ainda aparece em relatório se o filtro olha só `ativo`.
  **Do instead:** rejeitar `arquivado` explicitamente no filtro do relatório. · promovido_para: —

## Tombstones

- [LM-006] ☠ 2026-09-01 :: promovido a check automático no CI
