# Invariantes — regras que nunca podem ser quebradas

Invariante não é landmine: a landmine do `sdd/playbook.md` diz "isto me mordeu"; a invariante diz "isto
nunca pode ser violado, e aqui está o que vigia". Quem escreve neste arquivo é a curadoria da fase Release
(passo 17b da `sdd-release`), com o seu OK por item; a trava é
`bash sdd/bin/playbook-curator.sh --validar-inv sdd/playbook.md sdd/invariants.md`. Explicação longa:
`docs/playbook-curation.md` do pacote.

Toda landmine ativa com `mordeu` de 1 para cima, ou com `promovido_para` preenchido, precisa estar
classificada aqui: como origem de uma invariante, ou em `## Descartados` com o motivo.

Gramática (1 linha por invariante; abaixo da primeira, linha fora dela é erro):

    - [INV-NNN] estado=ok|auto|humano origem=seed|LM-nnn[,LM-mmm] [check=<caminho>] :: <regra> · por quê: <texto> [· tarefa: <…> | · motivo: <…>]

- `ok`: o check roda sem alguém lembrar (hook, CI ou passo obrigatório com script). Com origem numa
  landmine promovida, o check é o `promovido_para` dela; senão, `check=` aponta um arquivo que existe.
- `auto`: dá para automatizar e ainda não foi; exige `· tarefa:` com o comando ou o alvo.
- `humano`: exige julgamento; exige `· motivo:` dizendo por que máquina não pega.
- `origem=seed`: regra que não veio de uma landmine.
- IDs estáveis: nunca renumerar nem reusar.
- `## Descartados`: landmine que não é regra do sistema (defeito de ferramenta, por exemplo):
  `- [LM-nnn] descartado :: <motivo>`.

## Invariantes

- [INV-001] estado=ok origem=LM-004 :: Migration só conta como aplicada com prova por leitura registrada em `## Migrations aplicadas` do BUILD_REPORT · por quê: o comando de aplicar pode sair 0 com a migration fora do banco (outro projeto ligado, recusa do servidor, SQL sem efeito), e o código vai para produção chamando o que não existe

## Descartados
