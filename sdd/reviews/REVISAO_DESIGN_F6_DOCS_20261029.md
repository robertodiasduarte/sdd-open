# REVISÃO DO DESIGN F6_DOCS — contexto fresco (modo contrato, antes do build)

> Bloco devolvido pelo revisor em contexto fresco (subagente sem a conversa do design), sobre
> `DESIGN_F6_DOCS.md` v1.0 e `DEFINE_F6_DOCS.md` v1.0, com a branch em `7e19462` (= `v2.2.6`).
> Logs das sondas em `sdd/reports/evidence/F6_DOCS/AVAL-DESIGN-*.log`. As decisões sobre cada ajuste
> estão no Advisor Ledger do DESIGN (v1.1).

VEREDITO: NEEDS_WORK — 3 HIGH, 4 MEDIUM, 3 LOW.

- **H1** — classe `Comparison`: "a linha de deltas não contém ✅" reprova o `comparison.md` de hoje (a
  coluna OpenSpec tem ✅); o gate nunca sairia 0. Conferir só a célula do SDD Open
  (`AVAL-DESIGN-comparison-deltas.log`).
- **H2** — "atualizar = `git pull` no clone + `sync`" é falso: o `init` nunca sobrescreve skill instalada
  (`bin/sdd-open.sh:603-604`), o `sync` diz "EM DIA" e a skill fica velha; o `doctor` manda apagar a pasta
  e rodar `init`. O §5 dos 2 quickstarts afirma o mesmo hoje (`AVAL-DESIGN-atualizar-pull-sync.log`).
- **H3** — `sdd-release`: "base conferida antes e integrada depois do OK" é regra do starter; no open a
  integração (landar) é a FASE 1, item 5, antes do OK, e depois só há a reconferência; falta o ledger
  (`AVAL-DESIGN-regras-skills.log`). Menor: a entrevista da ux-review também roda quando o aluno pede.
- **M1** — `comandos-intactos.py` é cego a regra em prosa, título sem número e linha de bloco sem comando
  (3 regras mudadas, "idêntico" nas 7: `AVAL-DESIGN-comandos-intactos-cego.log`). Exigir igualdade do
  texto inteiro normalizado.
- **M2** — AT-003 pede os 7 agentes na tabela "onde roda", e a classe não confere; no arquivo inteiro seria
  circular (a tabela do topo já cita os 7). Conferir dentro de `## 4.`…`## 5.`
  (`AVAL-DESIGN-quickstart-7-agentes.log`).
- **M3** — faltam python3 ≥ 3.9 e bash ≥ 3.2 nos requisitos do guia (os lints das fases precisam), e o
  `--yes`: o `init` rodado pelo agente sem terminal sai CANCELADO; `git init -b main` como na
  `sdd-iniciar-repo` (`AVAL-DESIGN-python3-requisito.log`, `AVAL-DESIGN-init-sem-tty.log`).
- **M4** — o DEFINE pede regra nova no `AGENTS.md.tmpl`; o DESIGN a rejeita sem iterar o DEFINE.
- **L1** — `ancora()` com `\w` descarta marcas Unicode (⏸️ com U+FE0F, NFD) que o GitHub mantém; usar
  `unicodedata.category` (L*, M*, Nd, Pc) e NFC (`AVAL-DESIGN-ancora.log`).
- **L2** — o literal proibido "não vai para o GitHub" é largo (o guia dirá isso de `.env` e planilha);
  prender a `sdd/` e incluir "fora do git"; palavras-chave do roadmap só em linhas de tabela.
- **L3** — frase de cobertura do Verify Gate (AT-010 e AT-013 dependem de logs); o
  `test_correcoes_w0.PROMESSA_VAZIA` varre os docs do `MANIFEST.txt` (`/drive`, `slice 2`…); "branch
  `docs/`" é convenção deste repositório, não do guia.

Sondas que confirmaram o resto do desenho: 52 links relativos hoje e exatamente os 2 quebrados do
`adaptation-guide`; com os 7 bumps e as 7 seções simuladas, só os 3 testes de versão do manifest falham;
o `AGENTS.md.tmpl` da Decision 4 deixa `test_sdd_open`, `test_agnostico` e `test_release_workflow` verdes;
`check-versions` VERDE na árvore simulada; `init` sem git sai 64 e, depois do `git init`, cai no caso
"git sem commit" da `iniciar-repo`; publish-gate ci verde em HEAD; G2 nas fontes do starter só em
`voce@exemplo.com`, fora do que se porta; regras previstas de brainstorm, define, governanca, design e
build existem no texto; números de linha do DEFINE conferem.
