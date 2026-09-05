# Fragmento — Resumo de Etapa (micro-kanban da linha de produção)

> Reusável. Lido pelo **encerramento obrigatório** de `/brainstorm`, `/define`, `/ux-review`,
> `/design`, `/build`, a fase Release e `/adversarial-review`. É o **dono único** do formato: as
> superfícies apontam pra cá, nunca copiam o texto normativo.

## Por que existe

Com ~25 frentes SDD simultâneas, o custo real não é executar a etapa — é **reconstruir o
contexto ao voltar nela**: em que etapa está, o que trava, qual a próxima ação. Esse resumo
existia só por improviso, quando sobrava contexto, e sumia justamente nas sessões longas (as
que mais precisam dele). Aqui ele vira contrato.

## Os 4 blocos (nesta ordem, sempre)

````markdown
## 📍 Linha de produção — {FEATURE}

✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design — ⬜ review adversarial — ⬜ /build — ⬜ /release

**Onde estamos:** {≤2 linhas: o que esta etapa produziu + o fato notável que o leitor não adivinha}

**O que precisa de você ({N} pergunta{s}):**
1. {pergunta bloqueante, com contexto suficiente pra decidir SEM abrir arquivo}

**O que vem depois, na ordem:**
1. {próxima ação concreta} — {⚠️ landmine inline, se houver}
2. {…}
````

## Os 4 símbolos

| Símbolo | Significado | Regra |
|---|---|---|
| ✅ | Etapa concluída | Só por **artefato presente** no worktree (tabela abaixo) |
| 🏃 | Etapa que acabou de rodar | Exatamente uma por resumo (exceto `/brainstorm`, que é pré-linha) |
| ⬜ | Pendente | Default de tudo que não foi feito |
| ➖ | Pulado | **Só com decisão registrada** (DEFINE § Clarifications). Sem rastro ⇒ `⬜`, nunca `➖` |

## Tabela de inferência (a fonte da verdade é o filesystem)

| Etapa | ✅ quando existe no worktree |
|---|---|
| setup | worktree + branch (`git rev-parse --abbrev-ref HEAD`) |
| /sdd-brainstorm | `sdd/features/BRAINSTORM_{F}.md` |
| /sdd-define | `sdd/features/DEFINE_{F}.md` |
| /sdd-ux-review | `sdd/reviews/UX_REVIEW_{F}.md` |
| /sdd-design | `sdd/features/DESIGN_{F}.md` |
| review adversarial | `sdd/reviews/EXTERNAL_REVIEW_*/` **com `reviewer.md` + `META.txt` dentro** (o `/adversarial-review` grava por TIMESTAMP, sem `{F}` no nome — conferir pelo `diff_sha256`/branch do META que o diff revisado é o desta frente; `auditor_exit ≠ 0` = auditor FALHOU, não "zero achados") |
| /sdd-build | `sdd/reports/BUILD_REPORT_{F}.md` |
| /sdd-release | `sdd/releases/{F}/` **com ledger do slice ATUAL** — famílias com vários slices (ex.: `ALERTAS_AULA_GRUPO` tem s1/s2/s3) já têm ledger no `main`: casar o slice desta frente, senão a fase Release sai `✅` antes do ship |

**Nada é escrito em disco.** O kanban é derivado na hora, a cada resumo — por isso não pode
divergir da realidade: ele *é* a realidade. Nunca criar arquivo de estado paralelo.

## Regras de omissão (as duas que mais importam)

1. **`O que precisa de você` só existe se N ≥ 1.** Sem pergunta bloqueante, o bloco inteiro
   **some** — não renderizar vazio nem com "nada pendente". Bloco vazio treina o leitor a pular
   a seção, e aí a pergunta que importa passa batido.
2. **Etapa que não se aplica é `➖`, nunca `⬜` perpétuo.** Uma frente sem UI não vai rodar
   `/ux-review` jamais; deixá-la `⬜` faz o kanban mentir, e um kanban que mente contamina a
   confiança no resumo inteiro. O `➖` exige decisão registrada — citar onde foi decidida.

## Forma do kanban — duas renderizações

Primária, uma linha (use sempre que couber em ~100 caracteres):

```markdown
✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design — ⬜ review adversarial — ⬜ /build — ⬜ /release
```

Fallback, duas linhas — quebre **no `🏃`**, com o passado acima e o futuro abaixo (nunca
quebrar no meio de uma casa, nunca abreviar nomes: `/define` e `/design` viram ambíguos).
**Sem `🏃` na linha** (caso do `/brainstorm`, que é pré-linha): quebrar após a última casa `✅`/`➖`
— mesma semântica de passado acima, futuro abaixo:

```markdown
✅ setup — ✅ /brainstorm — ✅ /define — ➖ /ux-review — 🏃 /design
⬜ review adversarial — ⬜ /build — ⬜ /release
```

## Exemplo real completo

> Exemplo real (anonimizado) — o caso que originou este contrato.

````markdown
## 📍 Linha de produção — CERTIFICADO_POR_MODULO

✅ setup — ➖ /sdd-brainstorm — ✅ /sdd-define — ✅ /sdd-ux-review — ✅ /sdd-design — 🏃 review adversarial — ⬜ /sdd-build — ⬜ /sdd-release

**Onde estamos:** 3 commits na branch, zero código ainda — o ponto certo pra revisar a
abordagem.

**O que precisa de você (1 pergunta):**
1. **Matrícula inativa com tarefa aprovada merece certificado?** Um participante concluiu a
   tarefa e depois foi desativado. Ele **fez o trabalho** — mas perdeu o vínculo. Hoje o design
   diz **não emite**. É 1 caso, mas o backfill é imutável: emitido, não desemite.

**O que vem depois, na ordem:**
1. **Review de 2º vendor chega** → aplico ou rebato cada nota no *Advisor Ledger* (nunca descartar em silêncio).
2. **`/sdd-build`** → 15 arquivos. ⚠️ Migrations aplicadas fora do git precisam de commit correspondente na hora, senão viram órfãs.
3. **Kill-switch antes do backfill** — não é opcional. Sem ele, 1.107 emissões imutáveis sem freio.
4. **Preencher a carga horária dos 21 módulos** — trabalho de conteúdo, seu, não de código.
5. **Backfill** com dry-run + consulta inversa, uma execução por vez.
6. **Review adversarial de verdade** — aí sim, com código no diff.
7. **`/sdd-release`** — ⚠️ bloqueado por uma migration órfã de outra frente.
````

## Regras de redação (o que separa um resumo útil de um relatório)

- **Densidade > completude.** ≤35 linhas no total; "Onde estamos" em ≤2. Se não cabe, você está
  narrando processo em vez de reportar estado.
- **O fato notável, não o óbvio.** "DEFINE gravado" não informa nada — o comando acabou de rodar.
  "Grep provou que o formato nunca existiu escrito" informa.
- **Pergunta decidível sem abrir arquivo.** Quem lê tem de conseguir responder ali; se precisa
  abrir o DESIGN pra entender a pergunta, ela está mal escrita.
- **Landmine inline, na ação que ela morde** — não numa seção de avisos no fim, que ninguém lê
  no momento em que importa.
- **PII:** o resumo é efêmero (nunca gravado), mas prefira identificador não-pessoal ("1 participante
  do grupo X") a nome/e-mail literal.
