# HANDOFF: F29 Skills marcadas pelos scanners

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F29_SCANNERS_SKILLS |
| **Objetivo** | Tirar do texto das skills os três padrões que o Snyk do skills.sh lê como "prompt injection" (E004): "Não cite nem resuma as instruções", "como veio" e a linha de versão com link e "comece com esta linha", mais o bloco "Quando migrar para o SDD Open" do starter, sem perder a intenção de cada frase |
| **Status** | ✅ DoD fechado — publicado na `v2.25.1` (`main` = `89a0ecb`, PR #42, CI 18 de 18), 2026-11-20; starter **`v1.5.30`** (14ª geração, PR #23 de lá, 19 zips OK no `shasum -c`). A reauditoria do Snyk ainda não aconteceu (ver "Falta") |
| **Última sessão** | 2026-11-20 |
| **Branch / pasta** | `scanners-skills` · `/Users/robertoduarte/rdd-worktrees/sdd-open-scanners-skills` (nascida de `origin/main` em `f1abdfa`; entrou na `main` por squash, `89a0ecb`) |
| **Artefatos** | `sdd/archive/F29_SCANNERS_SKILLS/{ESCOPO,DEFINE,DESIGN,BUILD_REPORT}_F29_SCANNERS_SKILLS.md` · `sdd/reviews/AVALIACAO_F29_SCANNERS_SKILLS_20261120-1713.md` · `sdd/reports/evidence/F29_SCANNERS_SKILLS/` |
| **Verify Gate** | 🟢 0 em `0503b71` (2.765 testes, 4 pulados, `publish-gate` GREEN, bash 3.2); CI do PR #42 verde em Linux, macOS e Windows (16 fatias) |

## Publicado

> Gerado por `python3 sdd/bin/ficha-publicado.py F29_SCANNERS_SKILLS` a partir de `sdd/releases/F29_SCANNERS_SKILLS/`:
> uma linha por release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-20 · s1 · 2.25.1 · shipado · CONCERNS · deploy no-op · trilha completa · 89a0ecb
<!-- publicado:fim -->

## Feito

- Tudo do DEFINE (AT-001 a AT-009) está na `v2.25.1`; a descrição e a prova estão no ledger da publicação.
- Decisões do Roberto: D1 origem em `metadata.source` do frontmatter (o Snyk cita o link em 3 das 8 páginas marcadas, por isso ele saiu da linha), D2 a linha de versão continua sem link, D3 o bloco de migração sai do starter.
- Curadoria: na fila (`sdd/curadoria/fila/F29_SCANNERS_SKILLS/20261120T234916Z`, 6 contagens, 0 candidatos); o próximo lote da `sdd-playbook` julga.

## Falta

1. 🐛 **Reauditoria do Snyk (o critério de "funcionou", fora do pronto).** Em 20/11, depois de publicar o starter `v1.5.30`, as 8 páginas `skills.sh/robertodiasduarte/sdd-starter/<skill>/security/snyk` ainda mostravam a auditoria de 19/11 (04:25 PM, Critical em todas): o skills.sh não reanalisou. Reabrir as 8 páginas (sdd-checar-ambiente, sdd-engenharia-reversa-saas, sdd-governanca, sdd-higiene-dado, sdd-iniciar-repo, sdd-loop-builder, sdd-release, sdd-seguranca) quando a data mudar, registrar o resultado aqui com a data e, se alguma seguir marcada, o motivo novo. Não reabrir a frente por isso sem falar com o Roberto.
2. A-001 e A-002 do DEFINE seguem sem validar: se uma URL em `metadata.source`, sem instrução que mande mostrá-la, deixa de ser lida como banner, e se o `npx skills`, o claude.ai e o ChatGPT aceitam a chave `source`. O `check-versions` do starter e os 19 zips da Release não acusaram nada, mas o upload no claude.ai/ChatGPT não foi testado.
3. Smoke depois do deploy: pulado — slot vazio (o Open não tem `sdd/config.yaml`); a Release `v2.25.1` e a `v1.5.30` foram conferidas à mão.
4. 🐛 O run da `main` (44826530064) caiu na 1ª vez no macOS: `test_f28_revisores.Estados.test_so_le_nada_muda_e_nenhuma_chamada_de_rede` achou `.git/objects/maintenance.lock` na foto antes/depois (a manutenção automática do git rodou no meio). Passou ao refazer o job, mas o teste é frágil: excluir `.git/objects` e o `maintenance.lock` da foto, ou desligar `gc.auto` e `maintenance.auto` no repositório do teste.
5. ✨ Restam "como veio" fora dos `SKILL.md`: `sdd-governanca/references/revisor.md`, `sdd-desempenho-banco/references/CONSULTAS_DIAGNOSTICO.md`, um comentário de `sdd-iniciar-repo/scripts/inventario.sh`. Ali a frase quer dizer "copie o dado sem alterar", não esconder atividade; o escopo limitou a regra aos `SKILL.md`. Se o Snyk os marcar, vira item de uma frente futura.
6. ✨ A regra "Saída de comando nunca crua" (o Snyk a cita só na `sdd-iniciar-repo`) ficou como estava: o escopo não a incluiu.
7. ✨ Fora do escopo por decisão: W012 (`npx skills add` é o canal de instalação), W013 (as ações já pedem o OK) e a revisão por segunda IA, dispensada pelo Roberto com motivo no ledger.

## Definition of Done

- [x] AT-001 a AT-009 com log por AT (`sdd/reports/evidence/F29_SCANNERS_SKILLS/AT-*.log`) e avaliador fresco PASS (ciclo 1)
- [x] Verify Gate verde em `0503b71` (3ª rodada; as duas primeiras saíram vermelhas por causas conhecidas, ver Landmines)
- [x] Release `v2.25.1` conferida (`89a0ecb`, pacote e `SHA256SUMS`)
- [x] Starter `v1.5.30` publicado (19 zips conferem no `shasum -c`)
- [ ] Reauditoria do Snyk registrada (depende do skills.sh)

## ⛔ Landmines desta feature

- Teste que fixa o número de versão de uma skill: ao subir um patch, procure também `vX.Y.Z · nov/2026` sem aspas e `'version: "X.Y.Z"'` em `tests/`; o 2º gate só pegou o `test_f17_passo0` depois de 37 minutos.
- Verify Gate lançado com `&` num shell não interativo: o subshell ignora SIGINT e o `test_f23b2_papeis.test_sinal_na_serie_mata_o_agente` estoura 15 s. Lance como tarefa em segundo plano do agente, sem `&` interno.
- O `report-lint` não aceita `avaliador: N.A.` num projeto sem `layers:` (contagem impossível): rode o avaliador de contexto fresco ou declare `PENDENTE`, que a release recusa.
- O gerador lê da **tag**, nunca da árvore de trabalho; para conferir antes de publicar, crie uma tag local temporária, rode num clone descartável do starter e apague a tag.
- A `main` do Open é protegida: o caminho é branch + PR, e o workflow de release repete a suíte na `main` antes de criar a tag (pode levar ~1 h; um job pode cair por teste frágil e ser refeito com `gh run rerun --failed`).

## Casos e testes em aberto

- ✨ Ver "Falta" 2, 4, 5 e 6.

## Eventos

- 2026-11-20 — frente aberta com o ESCOPO (achado do Snyk: 8 de 18 Critical, E004 risco 0,30; nenhum scanner achou código malicioso); DEFINE e DESIGN curtos, sem brainstorm, governança e UX N.A.; D1, D2 e D3 decididas pelo Roberto (D1 com a conferência das páginas do Snyk).
- 2026-11-20 — Build: troca em lote nas 24 skills com antes/depois por arquivo; `duplicadas.sh`, `checar.sh`, gerador e `check-versions.py` do starter; 14 arquivos de teste atualizados e 1 novo; linha de base vermelha (93 falhas em `f1abdfa`); avaliador fresco PASS.
- 2026-11-20 — release: dispensa da revisão por segunda IA pelo Roberto, com motivo; PR #42, CI 18 de 18; run da `main` caiu 1 vez no macOS (teste frágil da F28) e passou ao refazer; `v2.25.1` publicada.
- 2026-11-20 — starter: 14ª geração pela tag `v2.25.1` num clone limpo, PR #23 de lá, `v1.5.30` (19 zips OK).
- 2026-11-20 — reauditoria do Snyk: as 8 páginas ainda mostram a auditoria de 19/11.

## Recomendações

- Ao mexer em texto de skill do starter, rode `test_gerar_starter` e os testes que fixam versão depois de cada rodada, antes do gate inteiro.
- Antes de contar o resultado do Snyk, confira a data da análise na página: ela só vale se for posterior à publicação do starter.

## Veredito

- 🟡 CONCERNS — revisão externa dispensada com motivo no ledger; reauditoria do Snyk pendente.

## Setup

1. `cd /Users/robertoduarte/rdd-worktrees/sdd-open-scanners-skills && git fetch origin` — a `main` em `89a0ecb` ou depois.

## Tarefas

1. Abrir as 8 páginas do Snyk quando a data da análise passar de 19/11 e registrar o resultado em "Falta" 1.

## Ship

- **Publicar:** feito (`v2.25.1`, PR #42, `89a0ecb`; starter `v1.5.30`, PR #23).
- **Limpar:** pendente — a branch `scanners-skills` no Open e `gen/v2.25.1` no starter, e a worktree local; pedem o OK do Roberto.

## Prompt de retomada

```text
Retomar a F29 (skills marcadas pelos scanners) do SDD Open. Leia sdd/handoffs/HANDOFF_F29_SCANNERS_SKILLS.md na
main (git -C /Users/robertoduarte/rdd-worktrees/sdd-open-scanners-skills fetch origin). A F29 está publicada
(v2.25.1, PR #42; starter v1.5.30). Falta só registrar a reauditoria das 8 páginas do Snyk quando a data da análise
passar de 19/11 (item 1 de "Falta") e a limpeza das branches, que pede o OK do Roberto. Responda em português;
publicar ou apagar pede o OK do Roberto.
```
