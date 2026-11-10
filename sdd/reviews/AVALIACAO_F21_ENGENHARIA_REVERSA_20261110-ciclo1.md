# Avaliação de contexto fresco — F21_ENGENHARIA_REVERSA, ciclo 1 (2026-11-10)

Avisos do avaliador antes do bloco: a árvore de trabalho mudou durante a avaliação (4 arquivos com os consertos da revisão adversarial, ainda sem commit); o veredito vale para `2af3d6c`. Sem contaminação: não abriu o BUILD_REPORT nem o diff do build. Gravou só 7 arquivos `AVAL-*.log` na evidência.

<<<AVALIACAO
FEATURE: F21_ENGENHARIA_REVERSA
MODO: veredito · ciclo: 1
ALVO: commit 2af3d6c, em cópia de `git archive HEAD` sem `.git`; base v2.8.0 = 45e27a9
AMBIENTE: /usr/bin/python3 3.9.6 · python3 3.15.0 · /bin/bash 3.2.57 · sem rede · sem credenciais
CONTAMINAÇÃO: nenhuma

VEREDITO: NEEDS_WORK

| AT | Sonda (executada) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | listagem da pasta da skill; busca por `LICENSE.txt`, `VALIDACAO.md`, `tests/`; leitura do frontmatter, `manifest.json` e `evals/cases.json`; `git ls-files` contra `MANIFEST.txt`; classe `Pacote` de `test_f21_textos.py` | 13 arquivos, nenhum proibido, versão 1.1.0 nos três lugares, cada arquivo no MANIFEST | 13 arquivos; nenhum proibido; `name` igual à pasta; descrição com 748 caracteres; `compatibility`, `license: MIT`, `author`, `version "1.1.0"`, `updated "2026-11"`; MANIFEST idêntico à árvore, com 15 linhas novas | PASS |
| AT-002 | `skill-lint.py --conversa .agents/skills/*/SKILL.md`; `sdd-decisoes-lint.sh --sites .agents/skills`; sabotagem em cópia (tirar "não sei"); `test_skill_lint.py`, `test_conversa.py`, `test_decisoes_lint.py` | exit 0 nas 20 skills; a sabotagem reprova | 20 linhas verdes, exit 0; decisões: 27 perguntas em 22 arquivos, exit 0; sabotagem deu VERMELHO em `como-falar.md:68`; testes 29, 19 e 11 OK | PASS |
| AT-003 | CLI sobre levantamento válido, com 3.9.6 e 3.15, cwd `/`, caminho relativo em pasta com espaço, script da fonte e das cópias `.claude` e `.cursor`; SHA-256 do arquivo antes e depois | JSON `"ok": true`, exit 0, arquivo intacto | exit 0 em todos os casos; arquivo intacto; variante com CRLF também aprovada | PASS |
| AT-004 | 10 malformações do DEFINE mais arquivo ausente, diretório, sem argumento, vazio, BOM, não UTF-8 e mais de 2 MB, nas duas versões de Python; 18 testes de `test_validate_reverse.py` | exit diferente de 0 com o código do erro; arquivo ausente sem traceback | todas saem com exit 2 e o código certo (`OBSERVADO_SEM_SESSAO`, `REFERENCIA_INEXISTENTE`, `SUPORTE_INDISPONIVEL`, `ACHADO_SEM_EVIDENCIA`, `ID_*_DUPLICADO`, `DIMENSOES_COBERTURA`, `CONCLUSAO_COM_LACUNAS_OU_ESCOPO_VAZIO`, `PLACEHOLDER_NAO_PREENCHIDO`, `LINHA_ACHADOS`, `SECAO_AUSENTE_OU_DUPLICADA`); ausente dá exit 2 com JSON, sem traceback; 18 de 18 nas duas versões. Ressalva em A4 | PASS |
| AT-005 | grep da regra de pasta e da frase antiga; sabotagem em cópia (trocar a regra no `SKILL.md`) | mesma frase canônica nos dois arquivos; sem a frase antiga; a sabotagem derruba teste nomeado | frase idêntica em `SKILL.md:43` e `ORQUESTRACAO_SDD.md:55`; frase antiga ausente; sabotagem derruba `test_regra_da_pasta_igual_nos_dois_arquivos` e `test_sem_a_regra_antiga_da_pasta`. `ESCOPO_CONFIRMADO.md:50` mantém o critério da 1.0.0 com a nota de revisão (Decision 2) | PASS |
| AT-006 | grep de produto real, vitrine e sequência de 11 dígitos; inserção em cópia do nome do produto, da vitrine e de um termo da lista do `test_agnostico.py`; grep de "SDD Brainstorm" e "SDD Define" | a suíte falha nomeando arquivo e linha; exemplo neutro; dependências citadas como `sdd-brainstorm` e `sdd-define` | zero ocorrências dos termos proibidos; as inserções derrubam `test_sem_produto_real_vitrine_ou_ferramenta_de_um_agente` e `test_agnostico`, com arquivo e linha; exemplo neutro presente. **Dependências fora do nome técnico em `COMO_FUNCIONA.md:19` e `cases.json:57`, com a suíte verde (A2)** | FAIL parcial |
| AT-007 | `git diff 45e27a9 HEAD` de `AGENTS.md.tmpl`, dos dois README, do guia do aluno e de `cli-conventions.md`; grep de "19 skills"; `test_docs.py` | linha `ER` entre `KB` e `0`; célula Create/Criar; linha de conceito; 20 skills; ficha no guia; linha e exceção no cli-conventions | tudo presente; nenhum "19 skills" restante; 23 testes OK | PASS |
| AT-008 | `git init` e `init --vendors claude --yes` em projeto novo; de novo com `claude,codex,gemini,cursor,kimi` e Python 3.9 no PATH; `diff -r` contra o pacote; lint das cópias geradas; `sync --check`; editar a fonte e rodar `sync --yes`; apagar a cópia gerada e rodar `sync --yes` | pasta inteira nas duas localizações; lint da cópia sai 0; `sync --check` sai 0 | init exit 0 com 20 skills; `.agents` igual ao pacote; cópias `.claude` e `.cursor` com cabeçalho e lint exit 0; JSON das cópias válido; `sync --check` 0; após edição 1, depois 0; cópia apagada é recriada; molde da cópia gerada reprova com `TITULO` e o da fonte não. Sem `git init`, o init recusa com mensagem clara | PASS |
| AT-009 | `git diff --quiet v2.8.0 HEAD` das pastas `sdd-brainstorm` e `sdd-define`; diff da tabela de fases; `test_docs`, `test_conversa`, `test_agnostico`, `test_decisoes_lint`, `test_sdd_open` e outros 8 arquivos, no 3.9.6 com bash 3.2 | 19 skills verdes; linhas da tabela iguais; arquivos verdes; âncoras presentes | diff quiet exit 0; a tabela só ganhou a linha `ER`; `test_sdd_open` 41 OK em 482 s; os demais OK; `check-versions.py --base v2.8.0` VERDE com 20 skills | PASS |
| AT-010 | leitura por JSON de `manifest.json` e `cases.json`; classe `Manifesto`; grep da frase canônica nos logs de ER-09 | 17 cenários; contagem de executados declarada; sem verificação que não rodou aqui; `testes_escritos` aponta o teste | 17 casos; 3 executados e 14 `escrito_nao_executado`; verificações da 1.0.0 isoladas em `historico_1_0_0`; as duas verificações declaradas (18 testes nas duas versões, lints com exit 0) foram reproduzidas por mim; logs batem com o manifesto (série 1: 1 de 3; série 2: 3 de 3) | PASS |

Conferências extras:
- `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh` na cópia sem `.git` — GREEN.
- Linha de base vermelha — os testes novos e os de contagem falham numa cópia de 45e27a9.
- Sabotagem do lint (remover `OBSERVADO_SEM_SESSAO`) — derruba `test_observed_requires_session_evidence`.
- Layout do starter (teste dentro da pasta da skill) — 18 de 18 no 3.9.6.
- Links relativos e caminhos em crase da skill — todos existem.

ACHADOS

A1 · MÉDIO · Decision 4 do DESIGN ausente no commit: rodar o teste sem `-B` grava `__pycache__` na pasta da skill, e o `init` leva junto.
  Reprodução, em cópia de `git archive HEAD`:
  1. `grep -n dont_write_bytecode tests/test_validate_reverse.py` — nada, exit 1.
  2. `python3 -m unittest discover -s tests -p test_validate_reverse.py` (3.15, sem `-B`) — OK, e aparece `.agents/skills/sdd-engenharia-reversa-saas/scripts/__pycache__/validate_reverse.cpython-315.pyc`.
  3. `git init` e `bash bin/sdd-open.sh init --vendors claude --yes` em projeto novo — o `.pyc` chega em `.agents/skills/...` e em `.claude/skills/...`.
  4. Na mesma cópia, a rodada seguinte falha em `test_f21_textos.Pacote.test_arquivos_presentes_e_ausentes`, dá ERROR em `test_matriz_new_session.Portadas.test_sem_referencia_ao_starter`, e o `publish-gate.sh` bloqueia com "undeclared file".
  O Verify Gate usa `-B` e não vê isso. Com o 3.9.6 da Apple o `.pyc` não foi gravado. Log: `AVAL-pycache-na-pasta-da-skill.log`.
  Conserto esperado: `sys.dont_write_bytecode = True` antes de carregar o script, como o DESIGN manda.

A2 · MÉDIO-BAIXO · AT-006: dependência citada fora do nome técnico, sem teste que acuse.
  Reprodução: `grep -rnE "SDD Brainstorm|SDD Define" .agents/skills/sdd-engenharia-reversa-saas`
  - `references/COMO_FUNCIONA.md:19` — "As skills SDD Brainstorm e SDD Define precisam estar disponíveis no ambiente."
  - `evals/cases.json:57` (ER-04) — "Não há skill SDD Brainstorm instalada…"
  - `references/ESCOPO_CONFIRMADO.md` linhas 16, 34, 39, 40 e 69 — registro histórico da 1.0.0; aceitável se declarado.
  `test_f21_textos.py` segue verde com essas ocorrências. Log: `AVAL-dependencias-pelo-nome.log`.
  Conserto esperado: trocar por `sdd-brainstorm` e `sdd-define` nos dois primeiros arquivos e pôr um teste que acuse a forma antiga fora do `ESCOPO_CONFIRMADO.md`.

A3 · BAIXO · `references/como-falar.md:84`: instrução ao agente dentro do exemplo de resposta ao aluno.
  O exemplo "pedido fora do limite" traz, no corpo da resposta, "Diga a frase de recusa inteira, como está no `SKILL.md`:". Quem copiar o exemplo fala isso ao aluno e contraria a regra da própria skill de não citar as instruções dela.
  Reprodução: `sed -n 82,87p .agents/skills/sdd-engenharia-reversa-saas/references/como-falar.md`.

A4 · BAIXO · O lint dá traceback e exit 1 quando o stdout é ASCII e o erro tem acento.
  Reprodução: levantamento válido com `## Lacunas e contradições` renomeada; `PYTHONIOENCODING=ascii /usr/bin/python3 -B .agents/skills/sdd-engenharia-reversa-saas/scripts/validate_reverse.py arquivo.md` — `UnicodeEncodeError`, exit 1. O mesmo ocorre com `LC_ALL=C PYTHONCOERCECLOCALE=0 PYTHONUTF8=0`. Sem a variável: JSON e exit 2. Com `LC_ALL=C` puro funciona.
  Não quebra o AT-004 (o exit é diferente de 0, e o caso do arquivo ausente só tem ASCII), mas contradiz `docs/cli-conventions.md` ("sai `2` na falha"). O script é byte a byte o da 1.0.0 por decisão; cabe corrigir numa versão nova ou declarar o limite. Log: `AVAL-lint-traceback-stdout-ascii.log`.

A5 · INFO · O comando do Success Criteria não roda como escrito.
  `python3 sdd/bin/skill-lint.py --conversa` sem caminhos sai 64 (uso). A forma que funciona é `python3 sdd/bin/skill-lint.py --conversa .agents/skills/*/SKILL.md`, exit 0 com 20 linhas. Ajuste de redação no DEFINE.

A6 · INFO · Folgas do lint, sem AT violado (o script está congelado).
  O lint aprova marcador em minúsculas (`{saas}`), marcador com hífen (`{DATA-ISO}`) e linha separadora com menos colunas que o cabeçalho (`|---|` numa tabela de 8). Os marcadores do molde são todos maiúsculos com sublinhado, então o AT-004 está coberto. Log: `AVAL-lint-levantamentos-malformados.log`, linhas com `XX`.

A7 · INFO · Árvore de trabalho divergiu do commit durante a avaliação.
  `git status --short` mostra os 4 arquivos modificados citados no início. Numa cópia dos arquivos rastreados da árvore de trabalho: `test_validate_reverse.py`, `test_f21_textos.py` e `test_matriz_new_session.py` OK no 3.9.6; `skill-lint --conversa` da skill OK; A1 e A2 não se reproduzem. Não vale como avaliação completa dessa versão: o conserto precisa ser commitado e reavaliado no ciclo 2, e ainda falta o teste de A2.

EVIDÊNCIA (em `sdd/reports/evidence/F21_ENGENHARIA_REVERSA/`):
AVAL-testes-f21-duas-versoes.log · AVAL-testes-nao-regressao.log · AVAL-lint-levantamentos-malformados.log · AVAL-lint-traceback-stdout-ascii.log · AVAL-init-sync-projeto-novo.log · AVAL-pycache-na-pasta-da-skill.log · AVAL-dependencias-pelo-nome.log

CONTAGEM: 7 achados (2 que pedem conserto: A1 e A2; 2 baixos: A3 e A4; 3 informativos)
>>>
