# AVALIACAO F4_CONVERSA — ciclo 2 (contexto fresco, sobre `fd94876`)

> Bloco devolvido por um 2º avaliador em contexto fresco. Ele recebeu os achados do ciclo 1 como
> brief de conferência e a worktree destacada em `fd94876`. O veredito, a tabela e os achados estão
> como ele escreveu, com as reproduções resumidas. As sondas completas estão em
> `sdd/reports/evidence/F4_CONVERSA/AVAL2-*.log`. As decisões estão no Advisor Ledger de
> `sdd/reports/BUILD_REPORT_F4_CONVERSA.md`.

```text
<<<AVALIACAO
Veredito: PASS. Achados novos: 0 HIGH, 0 MEDIUM, 6 LOW.

Os 4 MEDIUM do ciclo 1 estão fechados. Dos 8 LOW, 7 estão fechados; o L1 está fechado na mensagem e
aceito com motivo na opção desconhecida (= 64, DESIGN Decisão 2, docs/cli-conventions.md:50). Nenhum
contrato de exit 0/1/64 quebrou. Suíte no piso (Python 3.9.6, bash 3.2.57): 382 testes, OK.
comandos-intactos.py sai 0. skill-lint --conversa nas 16, check-versions --base v2.2.4
--base-obrigatoria e design-lint nos DESIGN F1–F4 reais saem 0.

Achados do ciclo 1: M1 FECHADO · M2 FECHADO · M3 FECHADO · M4 FECHADO (10 de 10 sabotagens falham com
o teste nomeado) · L1 FECHADO (mensagem) / ACEITO-COM-MOTIVO (opção desconhecida = 64) · L2 FECHADO ·
L3 FECHADO · L4 FECHADO · L5 FECHADO (falta teste: LOW-5) · L6 FECHADO · L7 FECHADO (13 de 13) · L8 FECHADO.

Achados novos (só no diff 4e77a1f..fd94876), todos LOW:
LOW-1 — citação com linha ">" vazia ainda esconde a pergunta (o M1 na forma citada): exit 0, esperado 1.
LOW-2 — OUTRO não pega o plural ("Outros", "Outras"); lista numerada, negrito __…__ e uma linha de prosa
  entre a pergunta e as opções também passam sem conferência (fora do formato "- **rótulo**" do DEFINE).
LOW-3 — qualquer ✅ na célula Status dispensa o prompt ("🔨 em andamento (build ✅, falta release)" → exit 0).
LOW-4 — test_agnostico passou a ignorar arquivo não-UTF-8 sem avisar (deixou de falhar fechado); um .md
  em Latin-1 em sdd/templates/ com AskUserQuestion dá achados() == [].
LOW-5 — o ramo "arquivo ilegível sai 1" do AT-013 (v1.2) não tem teste.
LOW-6 — o corpo do DESIGN v1.1 contradiz o código e a própria linha 1.1 do histórico (Decisão 4 ainda
  lista «» e diz "ilegível, 64"; Decisão 5 sem a exceção ✅; Decisão 2 sem "*" nem linha em branco;
  docstring do skill-lint ainda diz "- **rótulo**").

Nenhuma brecha nova em exit 0/1/64, nem incompatibilidade com Python 3.9 ou bash 3.2.

Contagem: HIGH 0 · MEDIUM 0 · LOW 6
>>>
```
