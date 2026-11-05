# BUILD REPORT: FIXTURE — sintético (self-test do playbook-curator.sh)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FIXTURE |
| **Date** | 2026-09-02 |

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `termo_candidato_a` `outro_termo`
regra: Regra sintética com evidência. **Do instead:** ação sintética.
evidencia: AVAL-AT-002.log:3
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Domínio
sup: `termo_candidato_b`
regra: Candidato sem a linha de evidência: deve sair REJEITADO. **Do instead:** nada.
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Backend
sup: `termo_candidato_c` `chave_propria`
regra: Regra em duas linhas, com continuação
  indentada.
evidencia: AVAL-AT-002.log:3
  (continuação da evidência)
Do instead: ação em chave própria,
  também em duas linhas.
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Domínio
sup: `termo_candidato_d`
regra: Candidato sem a ação em lugar nenhum (nem na regra, nem em chave própria): deve sair REJEITADO.
evidencia: AVAL-AT-002.log:3
ficha: —
mordeu_antes: —
>>>
```
