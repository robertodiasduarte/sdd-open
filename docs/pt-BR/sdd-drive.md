<!-- Idioma: **Português** · [English](../sdd-drive.md) -->

# Pilotar uma feature: `sdd-drive`

A `sdd-drive` leva um DEFINE aprovado até "pronto para publicar" sozinha: desenha, constrói uma tarefa por sessão nova, roda o
teste final, corrige e repete até um limite de rodadas, e **para antes de publicar**. Você volta só para as decisões que são suas.

```text
/sdd-drive sdd/features/DEFINE_RELATORIOS.md
```

## O script decide, o agente executa

O `sdd/bin/sdd-drive.sh` guarda o estado, roda o Verify Gate, conta as rodadas e diz a próxima ação. Ele nunca chama agente,
então o mesmo mecanismo roda nos 7 agentes. Agente sem subagente para uma vez por tarefa e pede uma sessão nova: mais lento,
nunca quebrado.

Uma **rodada** é uma passada inteira: construir tudo o que falta e rodar o teste final. Teste final vermelho gasta 1 rodada, e
`drive.max_rounds` (default 3; `--max N` sobrepõe) é quantas tentativas de ficar verde você permite. Dentro da rodada não há
teto de tarefas, mas a mesma tarefa que não anda para na 3ª tentativa.

## Uma execução, do começo ao fim

```text
$ sdd-drive.sh iniciar sdd/features/DEFINE_RELATORIOS.md
ACAO: RODADA
rodada: 1/3
tarefa: 1 de 12 — src/relatorio.py
…
$ sdd-drive.sh verificar sdd/features/DEFINE_RELATORIOS.md --fundo
ACAO: ESPERAR
…
$ sdd-drive.sh proximo sdd/features/DEFINE_RELATORIOS.md
ACAO: CORRIGIR
rodada: 2/3
o teste final ficou vermelho (normal nesta etapa): restam 2 rodada(s) · log: sdd/reports/evidence/RELATORIOS/DRIVE-gate-r1.log
…
$ sdd-drive.sh concluir sdd/features/DEFINE_RELATORIOS.md
motivo: gate-verde
O teste final passou e os relatórios estão prontos. Nada foi publicado.
```

| Verbo | O que faz |
|---|---|
| `iniciar <DEFINE> [--max N]` | confere as condições, grava o estado, diz a 1ª ação |
| `--dry-run <DEFINE> [--max N]` | mostra o plano; não executa nem grava nada |
| `--resume <DEFINE> [--max N] [--aceitar-gate-novo]` | continua pelo disco, sem gastar rodada |
| `proximo <DEFINE>` | a próxima ação, recalculada do disco |
| `verificar <DEFINE> [--fundo]` | roda o teste final; `--fundo` destaca, para teste maior que o limite de um comando do agente |
| `concluir <DEFINE>` | confere o último verde e o relatório do build, e para em `gate-verde` |
| `bloqueio <DEFINE> "<motivo>"` | a construção travou e precisa de uma pessoa |
| `aguardar <DEFINE> <papel> <brief>` | sem subagente: a parada que pede uma sessão nova |
| `recibo <DEFINE> "<texto>"` | anota uma decisão de rotina no relatório |

As ações são `ESPERAR`, `DESIGN`, `REVISAO_DESIGN`, `RODADA`, `CORRIGIR`, `COMMITAR`, `VERIFICAR` e `AVALIAR_E_RELATAR`; a skill diz quem
faz cada uma.

## Motivos de parada

| `motivo:` | Exit | O que a pessoa lê |
|---|---|---|
| `gate-verde` | 0 | O teste final passou e os relatórios estão prontos. Nada foi publicado. |
| `simulacao` | 0 | Simulação: nada foi executado nem gravado. |
| `orcamento-rodadas` | 20 | O teste final continuou vermelho nas rodadas permitidas. Nada foi publicado. |
| `manual-ux` | 20 | O teste final precisa da conferência de uma pessoa. Nada foi publicado. |
| `clarificacao-pendente` | 20 | O DEFINE ainda tem dúvida aberta ou a revisão de governança pendente. |
| `define-invalido` | 20 | O DEFINE não tem um teste final válido. |
| `gate-inconclusivo` | 20 | O teste final não chegou ao fim: isso não é vermelho e não gastou rodada. |
| `gate-alterado` | 20 | O comando do teste final mudou desde o início desta execução. |
| `bloqueio-humano` | 20 | A construção parou e precisa de você. Nada foi publicado. |
| `aguardando-sessao` | 40 | Esta etapa precisa de uma sessão nova do agente. Nada foi publicado. |
| `estado-invalido` | 20 | Não consegui ler onde a execução parou, e não vou adivinhar. |
| `branch-padrao` | 20 | O piloto não roda na branch principal: ele precisa de uma frente de trabalho própria. |

Exit 10 é "continue" (com uma linha `ACAO:`), exit 2 é falha do próprio script (não conseguiu gravar, ou `sdd/bin/` desatualizado),
exit 64 é chamada errada.

## O que protege você

- **A barreira dura.** Nenhum verbo publica. Verde não é "no ar": publicar é a `sdd-release`, com o seu OK.
- **Só o script roda o teste que decide.** O agente que construiu não informa o próprio verde.
- **A impressão digital do Verify Gate.** Se o comando do teste final muda no meio, a execução para com `gate-alterado`, e você
  decide. Verde do comando antigo nunca vale depois de aceitar um novo. Isso não protege de teste enfraquecido por dentro do comando:
  esse é o papel do avaliador de contexto fresco e da revisão.
- **Commit ou nada.** Mudança fora das pastas de documento (`sdd/features/`, `sdd/reports/`, `sdd/reviews/`, `sdd/handoffs/`,
  `sdd/traces/`), ou arquivo lá com extensão que não é de documento, como `.sh`, segura o teste final com `ACAO: COMMITAR`, para o verde ser de um commit.
- **As decisões continuam suas.** Chamar o drive liga o encadeamento só naquela execução: `[auto · de rotina]` segue a recomendada e vai
  para a seção `Decidi sozinho` do relatório; D1 a D5 são sempre perguntadas.

O que fica: `sdd/reports/DRIVE_REPORT_<F>.md`, `sdd/reports/progress/DRIVE_<F>.json` e
`sdd/reports/evidence/<F>/DRIVE-gate-r<k>.log`. Para recomeçar, apague o arquivo de estado.

## Limites conhecidos

- **Estado editado à mão.** Uma linha de gate sem o log dela não vale, mas uma forja deliberada do estado e do log não é algo que um script no seu próprio repositório consiga barrar: a prova contra isso é o avaliador e a revisão.
- **Arquivo ignorado e `skip-worktree`.** A conferência vê o que o git vê: arquivo no `.gitignore`, ou marcado `skip-worktree`/`assume-unchanged`, fica de fora. Um gate que roda sobre `git archive HEAD` não depende deles.
- **O teste dentro do comando.** A impressão digital protege o comando, e não o teste que ele roda.
- **Processo do gate morto.** Se o agente matar o script, a trava se libera, e um gate órfão pode seguir rodando enquanto o próximo começa.
- **`DRIVE_REPORT` e `BUILD_REPORT` são lidos, não refeitos.** Depois de um verde novo, um `BUILD_REPORT` antigo que passa no lint continua passando.

## Também nesta entrega

- **`sdd/bin/deploy-do-sha.sh`** responde "este commit está no ar?" para a `sdd-release`: o run do workflow que publica, na branch
  padrão, ou um run mais novo, verde, que contém o commit. Falha num passo de `deploy.transient_steps` repete 1 vez, na ponta da branch, e só
  se o commit ainda é a ponta; nunca usa `gh run rerun`. Saídas: `0` no ar · `2` fora do ar · `3` sem `gh` ou `git`, ou sem login ·
  `4` ainda não sei, que não é falha · `64` uso.
- **`sdd/bin/sdd-archive.py`** faz a faxina dos documentos de features fechadas: simulação por padrão, `git mv` de 1 lote por commit
  (`--lote com-ledger|sem-ledger|soltos --aplicar`), nada apagado, e feature com a ficha `HANDOFF_<F>.md` aberta fica onde está.
