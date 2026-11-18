# ESCOPO — `sdd-checar-ambiente` 1.6.1 (sobras da F25)

- **Data:** 2026-11-18
- **Frente:** ainda não aberta. Quando abrir, nasce de `origin/main` atualizada pela `sdd-new-session`.
- **O que é este arquivo:** os 5 ajustes pequenos que as revisões da F25 (skills duplicadas, `v2.22.0`) acharam e deixaram para depois, cada um com onde está no código, quando acontece, o conserto proposto e o teste que prova. É a entrada da `sdd-define`. Não é DEFINE: nada aqui tem teste de aceitação ainda.
- **Versão:** a F26 (documentos na main e marca do SDD Starter) já publica a `sdd-checar-ambiente` como 1.6.1; esta frente, quando abrir, sobe para a **1.6.2** (o nome do arquivo fica como está).
- **Estado:** registrado; nenhum é urgente. Nenhum quebra nada hoje em macOS, Linux ou Git Bash.
- **Origem:** "Casos e testes em aberto" da ficha `sdd/handoffs/HANDOFF_F25_SKILLS_DUPLICADAS.md`; rodada 4 da revisão do código, avaliação fresca (A2) e A-001 do `sdd/archive/F25_SKILLS_DUPLICADAS/DEFINE_F25_SKILLS_DUPLICADAS.md`.
- **Linhas citadas:** `origin/main` em `304e60a` (`v2.22.0`). Confira de novo ao abrir a frente: o código pode ter andado.

## 1. Os 5 ajustes

| # | Ajuste | Onde | Tipo | Custo |
|---|---|---|---|---|
| 1 | Caminho com `\` passado ao `awk` por `-v` | `scripts/duplicadas.sh` | prevenção | pequeno |
| 2 | "Nada foi tirado" quando o npx tocou pasta fora do plano | `scripts/duplicadas.sh:564` e `:640` | texto | pequeno |
| 3 | `CDPATH` exportado muda a pasta da própria skill | `scripts/checar.sh:244` e `:261` | prevenção | mínimo |
| 4 | "Para desfazer" impresso quando nada saiu | `scripts/duplicadas.sh:642` | texto | pequeno |
| 5 | `$CLAUDE_CONFIG_DIR/skills` nunca foi medido | `scripts/duplicadas.sh:28`, `SKILL.md:255` | medição | experimento |

Os caminhos são relativos a `.agents/skills/sdd-checar-ambiente/`.

### 1.1 Caminho com barra invertida no `awk -v`

- **O que é:** o `awk` interpreta as sequências de escape (`\t`, `\n`, `\\`) do valor passado por `-v`. Um caminho com `\` chega alterado ao programa. Os pontos são as linhas 94 (`r`, a raiz do projeto), 96 e 248 (`cg` e `ga`, as pastas globais), 142, 367 (`r`, caminho de cópia) e 627 (`eu`).
- **Quando acontece:** hoje nunca, porque macOS, Linux e Git Bash entregam caminhos com `/`. Passaria a acontecer se um caminho nativo do Windows (`C:\Users\…`) chegasse ali, por exemplo se `CLAUDE_CONFIG_DIR` vier do Windows com `\`.
- **Conserto:** passar os valores pelo ambiente e ler com `ENVIRON["…"]` no `awk`, que não interpreta escape. O padrão é `R="$(dup_raiz)" awk '{ print ENVIRON["R"] "/" $0 }'`. A linha 178 (`dup_compara`, versões como `1.6.0`) não precisa mudar.
- **Teste:** com `CLAUDE_CONFIG_DIR` contendo `\t` literal no nome da pasta (só em macOS e Linux, porque no Windows o nome não é válido), o diagnóstico mostra o caminho igual ao do disco. Vermelho antes do conserto.

### 1.2 "Nada foi tirado" quando o npx mexeu fora do plano

- **O que é:** quando a primeira saída falha, a linha 640 imprime `🛑 <erro>. Nada foi tirado.`. Um dos erros possíveis (linha 564) é o npx ter mexido numa pasta que não estava no plano, detectado pelo retrato das outras pastas. Nesse caso algo foi, sim, tirado ou alterado, ainda que fora do plano. A frase do erro já nomeia a pasta, mas o fecho "Nada foi tirado" contradiz o que veio antes. O mesmo vale para o erro da linha 539 (o npx rodou e uma pasta protegida não voltou).
- **Conserto:** guardar, junto do `DUP_ERRO`, se o npx chegou a rodar. Nesse caso o fecho vira "Nada do plano foi tirado.". Os outros "Nada foi tirado" (linhas 597 a 614, e os erros antes do npx) ficam, porque ali nada rodou.
- **Teste:** com o npx de teste no modo `demais`, a saída tem "Nada do plano foi tirado" e não tem "Nada foi tirado.". Os testes que hoje exigem "Nada foi tirado." (`tests/test_f25_skills_duplicadas.py:442`, `:471`, `:524`) precisam ser conferidos um a um: ficam os casos em que o npx não rodou. A frase não aparece em `references/como-falar.md`.

### 1.3 `CDPATH` exportado

- **O que é:** as linhas 244 e 261 do `checar.sh` fazem `cd "$(dirname "$0")/.."` para achar a pasta da skill. Com `CDPATH` exportado e o script chamado por caminho relativo sem `./` (`bash .agents/skills/…/checar.sh`), o `cd` pode ir para uma pasta de mesmo nome listada no `CDPATH` e ainda imprimir o caminho na saída. O resultado é que `DIR_SKILL` e `SKILL_MD` apontam para outro lugar.
- **Quando acontece:** muito raro, porque exige `CDPATH` exportado (pouca gente usa) e esse jeito de chamar. O padrão já existia no arquivo antes da F25; a revisão o achou no raio de impacto.
- **Conserto:** `unset CDPATH` no começo do `checar.sh`, uma linha que vale para o `duplicadas.sh`, carregado por `source`. Conferir os outros scripts da pasta `scripts/` com o mesmo padrão.
- **Teste:** com `CDPATH` exportado apontando para uma pasta que tem `.agents/skills/sdd-checar-ambiente` falsa, a saída do `--duplicadas` usa a skill verdadeira. Vermelho antes.

### 1.4 "Para desfazer" quando nada saiu

- **O que é:** a linha 642 imprime `Para desfazer: bash …/desfazer.sh` sempre, mesmo quando a primeira saída falhou e `DUP_FEITO` está vazio. O aluno lê como se algo tivesse mudado. Rodar o comando não faz mal, porque não há nada para devolver.
- **Conserto:** imprimir a linha só quando há o que desfazer: `DUP_FEITO` não está vazio, ou o erro manda rodar o desfazer. A linha 539 ("o npx rodou, mas não consegui devolver uma pasta protegida; rode o desfazer") é o caso em que `DUP_FEITO` está vazio e o desfazer é necessário. Nessa situação, esconder a linha seria um defeito grave. Quando nada há para desfazer, a lixeira criada pode ser apagada se não tiver nada além do `PLANO.txt` e do `desfazer.sh`; decidir no DEFINE.
- **Teste:** com o npx de teste no modo `nada` na primeira cópia, a saída não tem "Para desfazer". Com uma cópia tirada e a segunda falhando, a saída tem. Com a pasta protegida sem poder voltar (caso da linha 539), a saída tem.
- **Cuidado:** a `SKILL.md:94` diz que a última linha é sempre `Para desfazer: …`; o texto muda junto.

### 1.5 `$CLAUDE_CONFIG_DIR/skills` como pasta global do Claude Code

- **O que é:** a skill supõe que, com `CLAUDE_CONFIG_DIR` ligado, o Claude Code lê as skills globais em `$CLAUDE_CONFIG_DIR/skills` e não em `~/.claude/skills` (`duplicadas.sh:28`, tabela da `SKILL.md:255`). É a suposição A-001 do DEFINE da F25. O experimento 1 mediu só o `~/.claude/skills`, porque o Claude Code exige login e o HOME de teste não tem login.
- **Risco se a suposição estiver errada:** um aluno com `CLAUDE_CONFIG_DIR` ligado recebe um diagnóstico que procura a cópia global na pasta errada. Pode ver alerta falso ou deixar de ver uma duplicada real. A limpeza não erra de cópia, porque só tira o que o plano mostrou e o aluno aprovou.
- **Experimento:** num HOME temporário com login copiado (nunca o HOME real), ligar `CLAUDE_CONFIG_DIR` para uma pasta com uma skill de nome único e perguntar ao Claude Code quais skills ele vê (`--tools Skill`, `--no-session-persistence`). Repetir com a skill só em `~/.claude/skills`. Guardar o log como evidência.
- **Depois:** se a medição confirmar, só marcar a suposição como medida. Se contrariar, corrigir a linha 28 e a tabela, com um teste.

## 2. Restrições que valem para a frente

- Código roda no bash 3.2 (macOS) e no Git Bash do Windows; o CI do PR tem as 16 fatias do Windows.
- No gawk, `or`, `and`, `xor` etc. são funções: nunca nomes de variável (landmine da F25).
- Testes sempre em HOME temporário; o npx de teste recusa HOME fora da pasta de teste.
- O starter muda só por `scripts/starter/trocas/sdd-checar-ambiente.md` e `gerar-starter.py`, nunca à mão.
- A versão sobe para `1.6.1` na `SKILL.md` e no `tests/test_f16_textos.py`.
- Documentos só na branch de documentos.

## 3. Fora do escopo

- Renomear skills (DC4 da F25).
- Mudar o comportamento da limpeza além do texto dos itens 2 e 4.
