# Playbook sintético — escada de promoção (self-test do playbook-curator.sh)

## Sempre

- [LM-001] ajudou=1 mordeu=2 · conf=2026-09-02 · sup: `termo_promovido` :: Já promovido a mecanismo: não deve perguntar. **Do instead:** nada. · promovido_para: sdd/hooks/pre-commit
- [LM-004] ajudou=1 mordeu=2 · conf=2026-09-02 · sup: `termo_candidato` :: Mordeu duas vezes sem mecanismo: deve perguntar. **Do instead:** promover. · promovido_para: —

## Infra / deploy

- [LM-002] ajudou=0 mordeu=1 · conf=2026-09-02 · sup: `termo_um` :: Mordeu uma vez só: não pergunta. **Do instead:** x. · promovido_para: —

## Tombstones

- [LM-003] ☠ 2026-09-02 :: fixture
