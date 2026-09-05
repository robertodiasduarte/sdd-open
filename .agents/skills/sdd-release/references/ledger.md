# Ledger de release — `sdd/releases/{FEATURE}/{slice}_{versão-ou-data}.yaml`

O ledger é o **registro determinístico** do que foi publicado: vive no git, dentro do commit
atômico da release, um arquivo novo a cada release (append-only por construção — zero conflito
entre sessões paralelas). A ficha (`sdd/handoffs/HANDOFF_{F}.md`) é projeção narrativa disto;
se a ficha se perder, o ledger a reconstrói.

## Esquema

```yaml
feature_id: PAGAMENTO_PIX          # igual ao {F} dos artefatos e da ficha — nunca drifta
slice_id: s1                       # s1, s2, fix-1… (sem "s2 de s3": escopo muda)
versao: 1.4.0                      # se o projeto versiona; senão omitir
data: 2026-09-05
estado: shipado                    # shipado | parcial | pausa
veredito: PASS                     # PASS | CONCERNS | WAIVED (com o registro abaixo)
waived: null                       # ou: "classe=… · finding=… · motivo=… · por=… · data=…"
dod: "PIX aparece como opção no checkout e o webhook confirma em <10 s"
descricao: "Botão PIX no checkout + webhook de confirmação + reconciliação noturna"
deploy: no-op                      # no-op | real (o que subiu para produção)
avisos:                            # da Fase 0 que não abortaram — não podem evaporar
  - "teste de reconciliação vermelho pré-existente na baseline (waivable, não dispensado)"
```

**Sem SHA dentro do arquivo**: o SHA é do próprio commit que contém o ledger (`git log --
sdd/releases/{F}/`).

## Por que não um `SHIPPED_{DATA}.md`

Já existem três camadas: o ledger (determinístico, git), a ficha (narrativa, git) e o
changelog (comunicação). Um quarto artefato narrativo é duplicação — foi exatamente o que
aposentou a fase "ship" separada no projeto de origem.

## Convenções

- `feature_id` em CAIXA_ALTA_COM_UNDERSCORE, o mesmo do DEFINE/DESIGN/BUILD_REPORT/HANDOFF.
- Um arquivo por release; nunca editar ledger antigo (o passado não muda).
- `estado: pausa` também é ledger: registra que a frente parou e por quê (`descricao`).
