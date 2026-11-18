# BRAINSTORM: F16W2 Windows, porte das quebras

> Sessão exploratória para clarear intenção e abordagem antes dos requisitos.

## Metadata

| Atributo | Valor |
|-----------|-------|
| **Feature** | F16W2_WINDOWS |
| **Data** | 2026-11-14 |
| **Autor** | brainstorm-agent (sessão com o Roberto) |
| **Status** | Ready for Define |
| **Base** | `feat/f16w2-windows`, nascida de `origin/main` `ad32fe1` (`v2.16.0`); passo 0 em `10dc298` |

---

## Ideia inicial

A F16W pôs a suíte inteira no `windows-latest` (16 fatias, informativo) e mediu: **1.324 de 2.076 testes passam (~64%)**,
38 de 82 módulos inteiros verdes, 5 unidades no teto de 600 s. As quedas vêm de poucas causas, guardadas em
`sdd/reports/evidence/F16W_WINDOWS/windows/` (`MEDICAO-1-491efa6.md`, `MEDICAO-1-causas.txt`, `logs-quebrados/`). A F16W2
conserta por causa, em ordem de peso, cada uma com teste:

1. os scripts Python do `sdd/bin` (e os das skills) imprimem ✅ e "ç" num stdout cp1252: no Windows o aluno que roda
   `python3 sdd/bin/design-lint.py` no Git Bash vê `UnicodeEncodeError`; o `sdd-drive` cai em cascata (o design-lint sai 1);
2. o `.claude/settings.json` que o `init` do adaptador do Claude Code gera leva caminho do Windows sem escape (JSON inválido);
3. caminhos `C:\` × `/c/` (governança-fronteira, slot);
4. o `gh` falso dos testes (script com shebang, que o Python do Windows não executa) e o resolvedor de Python nos testes;
5. `git commit` pendurado 120 s com os hooks (`test_sdd_open.Hooks`);
6. o vigia do `checar` no Windows: askpass do editor e `gh` pendurados ainda passam do teto (AT-004 da F16W);
7. os 4 achados guardados (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`; AT-005 da F16W);
8. as 5 unidades no teto (`test_sdd_open.Projeto`, `test_claude_adapter.Projeto`).

Depois: decidir com o Roberto o piso (o job do Windows no `needs:` da release) e as 4 frases de Windows do README e do
quickstart (hoje "cerca de 64% dos testes passam").

### Contexto coletado

| Aspecto | Observação | Implicação |
|--------|-------------|-------------|
| Onde mora | `sdd/bin/*.py`, `sdd/bin/*.sh`, `sdd/bin/adapters/`, `bin/sdd-open.sh`, `.agents/skills/*/scripts/`, `tests/` | produto e testes; workflows só no piso |
| Releitura da medição | 738 blocos de queda nos 169 logs: 238 com `UnicodeEncodeError`/`charmap`; outros ~250 são a mesma causa de forma indireta (a mensagem sai em stderr com `\U0001f6d1` e o "ã" como byte cp1252, que o teste decodifica como `\ufffd`) | a causa (1) passa de metade das quedas |
| Causas novas na releitura | `adversarial-review.sh:37` faz `cd "$(dirname "$0")"`, e o teste roda com PATH sem `dirname` ⇒ `cd: null directory` (~70 quedas de `test_revisao*`); o `grep` chamado direto do Python passa pelo runtime do MSYS, que expande `{11,}` do padrão (`test_publish_gate_patterns`, 14) | entram no porte, junto das causas da lista |
| Emulação local | no Mac, `PYTHONUTF8=0 LC_ALL=en_US.ISO8859-1` faz o Python escrever em Latin-1 e recusar o ✅: `test_design_lint`, `test_kb_dominios`, `test_handoff_lint` e `test_skill_lint` dão 114 quedas, como no Windows | dá para provar a causa (1) sem Windows, antes do PR |
| Domínios da KB | N.A. | — |

---

## Perguntas e respostas

| # | Pergunta | Resposta | Impacto |
|---|----------|----------|---------|
| 1 | O que entra? (do prompt da sessão) | As 8 causas, em ordem de peso, cada uma com teste; depois o piso e as 4 frases | escopo fechado pelo Roberto ao abrir a frente |
| 2 | Medir no meio do build? | **Não:** o Roberto escolheu medir só no PR do fim (2026-11-14), como na F16W | o build se guia pela emulação local e pelos logs da 1ª medição |
| 3 | Se o PR ainda tiver quebras? | **Consertar e medir de novo no PR, até 2 vezes** (cada push com a frase); o job só entra no `needs:` se ficar 100% verde; senão segue informativo com o número novo | define o fim da frente e o piso |
| 4 | O starter entra? | **Sim, se uma skill do starter mudar** (provável: `sdd-checar-ambiente`, causa 6): gerar pela tag num clone limpo, com o OK próprio do Roberto lá | passo extra na release |

## Perfil de risco

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | N.A.: pacote de scripts e testes; nenhum dado de terceiros, nenhum login, nenhuma rota pública |
| Quem pode mudar? | quem tem push no repositório (o Roberto); o CI só lê |
| Quanto alguém pode pedir? | N.A.: nenhuma chamada paga no produto; a revisão adversarial paga (OpenRouter) é do processo, com o saldo lido antes de cada rodada |

## Inventário de amostras

| Tipo | Onde | Qtd | Notas |
|------|------|-----|-------|
| Entrada real | `sdd/reports/evidence/F16W_WINDOWS/windows/logs-quebrados/` | 169 logs | a saída de cada unidade que quebrou no `windows-latest` |
| Verdade medida | `MEDICAO-1-491efa6.md` e `resumo-testes-windows-fatia-*.tsv` | 460 unidades | estado por unidade; a régua do "antes" |
| Agrupamento | `MEDICAO-1-causas.txt` | 515 quedas | por causa, 4 exemplos cada |
| Código a reusar | `sdd/bin/sdd-archive.py` (`reconfigure` de stdout/stderr), `sdd/bin/lib/python.sh` (`PYTHONIOENCODING`), `tests/apoio.py` (`caminho_bash`, `caminho_nativo`, `BASH`) | — | os padrões que já valem no Windows |

## Abordagens exploradas

### Abordagem A: Por causa, provando cada uma no Mac quando der, medindo no PR ⭐ Recomendada

**Por quê:** a medição já separou as causas; cada uma tem um conserto pequeno e um teste. A causa (1), que é metade das
quedas, reproduz no Mac com o locale Latin-1; as outras se provam pelo log da 1ª medição e por teste que simula o Windows
onde der (caminho `C:\`, `cmd` sem `dirname`). **Prós:** conserta o produto onde o aluno vê; cada causa vira commit e teste
próprios. **Contras:** sem medir no meio, causas que só o Windows mostra podem sobrar para as 2 rodadas do PR.

### Abordagem B: Pular no Windows o que quebra (`skipIf`)

**Por que não recomendada:** deixa o job verde sem consertar nada; a causa (1) é defeito do produto que o aluno vê.

### Abordagem C: Trocar o CI para WSL

**Por que não recomendada:** o aluno usa Git Bash com Python nativo; o WSL mediria outro ambiente (decisão da F16W).

## Abordagem escolhida

| Atributo | Valor |
|-----------|-------|
| **Escolhida** | Abordagem A |
| **Confirmação** | 2026-11-14, escopo fixado pelo Roberto no prompt da frente e nas 2 respostas desta sessão |
| **Razão** | consertar por causa é o que a medição permite; a emulação cobre a maior causa sem push |

## Decisões

| # | Decisão | Razão | Alternativa recusada |
|---|---------|-------|----------------------|
| 1 | Todo script Python do pacote que imprime fora do ASCII reconfigura stdout e stderr para UTF-8 no início (como o `sdd-archive.py`) | vale quando o aluno chama o `.py` direto, sem bash no meio | só `PYTHONIOENCODING` no `python.sh`: não cobre a chamada direta |
| 2 | Guarda por teste: todo `.py` do `MANIFEST.txt` que escreve fora do ASCII tem o `reconfigure` | a próxima frente que criar script não reabre a causa | lista fixa de arquivos |
| 3 | A emulação Latin-1 vira uma linha de base local, rodada antes e depois (HEAD × build) | mede o efeito da causa (1) sem Windows | confiar só no log antigo |
| 4 | Medir no PR, até 2 rodadas de conserto; piso só com 100% verde | decisão do Roberto (pergunta 3) | piso parcial |

## Removidas (YAGNI)

| Sugerida | Por que saiu | Volta? |
|-------------------|----------------|----------------|
| Rodar a suíte no Windows de outra forma (WSL, MSYS2 puro) | o aluno usa Git Bash + Python nativo | Não |
| Paralelismo maior no job do Windows para ganhar tempo | as fatias já cabem no teto de 30 min | Sim, se o teto apertar |
| `workflow_dispatch` só do Windows | o Roberto escolheu medir só no PR | Sim |

## Validações incrementais

| Seção | Apresentada | Retorno | Ajustou? |
|---------|-----------|---------------|-----------|
| Escopo (as 8 causas + piso e frases) | ✅ prompt da frente | fixado pelo Roberto | Não |
| Medição e fim da frente | ✅ perguntas 2 e 3 | medir só no PR; até 2 rodadas; piso só 100% verde | Sim (meta) |
| Starter | ✅ pergunta 4 | entra se a skill mudar | Não |

## Requisitos sugeridos para o Define

- **Problema:** no Windows (Git Bash + Python nativo), ~36% dos testes quebram; parte é defeito que o aluno vê (os lints em
  Python e o `settings.json` do Claude Code).
- **Usuário:** o aluno no Windows; e quem mantém o pacote, que precisa de um job do Windows que diga algo.
- **Sucesso mensurável:** (a) nenhum script Python do pacote quebra ao imprimir num stdout cp1252 (teste com Latin-1 e
  guarda no `MANIFEST.txt`); (b) o `settings.json` gerado é JSON válido com caminho do Windows; (c) cada uma das causas
  3 a 8 com teste ou com o motivo de ficar de fora; (d) no CI do PR, a proporção de testes que passam no Windows sobe de
  ~64% (meta: 100%, piso no `needs:` só então); (e) README e quickstart com o número medido no PR.
- **Fora de escopo:** WSL; o caminho do aluno em PowerShell sem Git Bash; o repositório privado.

## Próximo passo

`/sdd-define sdd/features/BRAINSTORM_F16W2_WINDOWS.md`
