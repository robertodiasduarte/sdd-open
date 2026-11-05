# Playbook sintético — cruzamento com invariantes (self-test do playbook-curator.sh)

## Sempre

- [LM-030] ajudou=0 mordeu=1 · conf=2026-09-24 · sup: `inv_um` :: origem única promovida. **Do instead:** x. · promovido_para: sdd/bin/playbook-curator.sh
- [LM-031] ajudou=0 mordeu=1 · conf=2026-09-24 · sup: `inv_dois` :: 1ª de 2 origens. **Do instead:** x. · promovido_para: —
- [LM-032] ajudou=0 mordeu=1 · conf=2026-09-24 · sup: `inv_dois` :: 2ª de 2 origens. **Do instead:** x. · promovido_para: —
- [LM-033] ajudou=0 mordeu=1 · conf=2026-09-24 · sup: `inv_tres` :: origem única com check curado. **Do instead:** x. · promovido_para: —
- [LM-035] ajudou=0 mordeu=1 · conf=2026-09-24 · sup: `inv_desc` :: descartado. **Do instead:** x. · promovido_para: —
- [LM-036] ajudou=0 mordeu=0 · conf=2026-09-24 · sup: `inv_fora` :: fora do universo. **Do instead:** x. · promovido_para: —
- [LM-037] ajudou=0 mordeu=0 · conf=2026-09-24 · sup: `inv_fora2` :: fora do universo. **Do instead:** x. · promovido_para: —

## Tombstones

- [LM-034] ☠ 2026-09-01 :: aposentado
