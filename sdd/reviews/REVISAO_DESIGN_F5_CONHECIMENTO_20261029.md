# REVISÃO DO DESIGN F5_CONHECIMENTO — contexto fresco (modo contrato, antes do build)

> Bloco devolvido pelo revisor em contexto fresco (subagente sem a conversa do design), sobre
> `DESIGN_F5_CONHECIMENTO.md` v1.0 e `DEFINE_F5_CONHECIMENTO.md` v1.2, com a branch em `2fcdda1`.
> Logs das sondas em `sdd/reports/evidence/F5_CONHECIMENTO/AVAL-DESIGN-*.log` (12 arquivos). As decisões
> sobre cada ajuste estão no Advisor Ledger do DESIGN (v1.1).

VEREDITO: NEEDS_WORK — 2 HIGH, 4 MEDIUM, 2 LOW.

- **H1** — o `init --vendors claude|cursor` copia a skill para o adaptador com 2 linhas `sdd-open:generated`
  em todo arquivo não-JSON; ali o exemplo normativo reprova (SHA-256 e RULE_MAP) e o gate sairia vermelho;
  CRLF de checkout Windows também quebra o SHA. Links relativos `assets/…` levam o agente à cópia gerada.
- **H2** — o passo 10 com bloco cercado + comentário não bate com a exceção declarada do `comandos-intactos`
  (o `extrai()` da F4 pega a linha inteira do bloco).
- **M1** — `d=$(projeto …)` engole o `falha()` (o `exit 2` sai só do subshell); `troca … || exit 2` sai sem
  `🛑`/`RESULTADO`/`→`; `$T/saida` velho pode vazar para outro caso.
- **M2** — o RULE_MAP escapa `|` como `\|`; split ingênuo no `kb-dominios.py` lê a coluna errada.
- **M3** — o `skill-lint --conversa` aceita pergunta de fato fechada com `(recomendado)`: o AT-011 provaria só
  a confirmação, não que público/estágio/referência são abertas.
- **M4** — o teste de texto da `sdd-kb` não pega "pasta de bases", `python scripts/validate_kb.py`,
  `scripts/kb_normativo.py` cru (12 linhas no starter).
- **L1** — `bom-codigo` e `placeholder-codigo` perdem a fidelidade às fixtures do starter (bloco `text` com
  chave dupla; placeholder em bloco cercado, não em crase).
- **L2** — `RULE_TEMPLATE.md`/`normativo.md` precisam dizer que `teste` é caminho a partir da raiz;
  a Decision 4 punha `→` antes de `RESULTADO: VERDE`.

Sondas que confirmaram o resto do desenho: 4 aceitas e 12 rejeitadas com a razão esperada (validador do
starter + Pattern 2); os 62 testes passam no 3.9.6 com o `--strict` novo; a skill crua no pacote só derruba
os 3 testes de contagem; 0 achado de G2, integridade e agnosticismo na fonte.
