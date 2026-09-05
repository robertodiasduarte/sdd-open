# Playbook (fixture delta ok)

## Sempre

- [LM-001] ajudou=4 mordeu=0 · conf=2026-09-05 · sup: `termo_fixture` `config.yaml` :: Slot vazio no config significa pular o passo, nunca adivinhar comando. **Do instead:** deixar vazio e reportar "pulado". · promovido_para: —

## Backend

- [LM-003] ajudou=0 mordeu=2 · conf=2026-09-05 · sup: `.in(` `414` :: Lista grande no filtro vira URL longa e o servidor responde 414 sem o cliente lançar erro. **Do instead:** lotear em ≤150 itens e checar `error`. · promovido_para: —
- [LM-004] ajudou=2 mordeu=0 · conf=2026-09-01 · sup: `criado_em` `enviado_em` :: Convenção de timestamp não é universal no schema. **Do instead:** conferir a coluna antes de escrever a query. · promovido_para: —
- [LM-008] ajudou=0 mordeu=0 · conf=2026-09-05 · sup: `select(` `error` :: Destructure só de `data` esconde erro 400 do embed. **Do instead:** sempre `{ data, error }` e logar `error`. · promovido_para: —

## Frontend

- [LM-009] ajudou=0 mordeu=0 · conf=2026-09-05 · sup: `localStorage` `session` :: Dois clientes com o mesmo storageKey disputam o refresh token. **Do instead:** singleton do cliente. · promovido_para: —

## Infra / deploy

- [LM-002] ajudou=2 mordeu=0 · conf=2026-09-05 · sup: `deploy.yml` :: Deploy só em push para main. **Do instead:** trabalhar em branch off origin/main. · promovido_para: —
- [LM-007] ajudou=0 mordeu=0 · conf=2026-09-05 · sup: `rsync` :: Deploy com --delete apaga arquivos de runtime do servidor. **Do instead:** nunca --delete; inventariar runtime antes. · promovido_para: —

## Tombstones

- [LM-005] ☠ 2026-09-05 :: promovido a filtro no relatório
- [LM-006] ☠ 2026-09-01 :: promovido a check automático no CI
