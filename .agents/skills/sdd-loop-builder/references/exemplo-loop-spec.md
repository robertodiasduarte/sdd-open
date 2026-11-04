# Exemplo de LOOP_SPEC v2, perfil `standard`

Um processo fictício, para mostrar a forma: um redator de notas de versão que cita o commit de cada item e
é conferido por código. Os números são do exemplo, não recomendação.

```text
<LOOP_SPEC v="2" perfil="standard" nome="notas_de_versao">
<intent>
Objetivo: produzir NOTAS.md com um item por mudança visível ao usuário entre 2 tags.
Pronto: conferir_citacoes sai 0 e toda mudança da lista de commits tem item ou motivo de exclusão.
Invariantes: nenhum item sem commit citado; nenhum commit citado fora do intervalo.
Não-objetivos: traduzir, publicar, escolher a versão.
Modelo de dano: item inventado é pior que item faltando, porque a nota é lida como fato.
Desempate: na dúvida entre incluir e excluir, exclua e registre o motivo.
Contrato v1, dono: quem mantém a release.
</intent>
<control_state>
ciclo; id do commit em foco; hash de NOTAS.md; registro de tentativas por (commit, hash, assinatura do erro);
tokens gastos por estágio; métrica de progresso. Persiste em estado.json, ao lado de NOTAS.md.
</control_state>
<cycle_protocol>
SNAPSHOT → PROPOSTA (redigir) → VALIDAÇÃO PRÉ-AÇÃO (orçamento e registro) → EXECUÇÃO (gravar o rascunho) →
OBSERVAÇÃO (rodar conferir_citacoes) → VERIFICAÇÃO → TRANSIÇÃO (reescrever, ou um estado terminal).
Quem redige não roda o verificador.
</cycle_protocol>
<context_assembly>
Normativo, imutável: lista de commits do intervalo, gerada por código. Informativo: rascunho anterior e a saída do
verificador. Relido a cada ciclo: só os itens reprovados. O hash da lista muda: VERIFIER_FAILURE.
</context_assembly>
<action_space>
gravar_rascunho: reversível, idempotente, 10 s. Escopo negativo: o laço não toca a lista de commits, o verificador,
os critérios de pronto nem as fixtures.
</action_space>
<observation>
Código de saída e linhas de conferir_citacoes. Assinatura do erro: <regra>:<commit>. Sem saída do verificador, a
evidência é ambígua: rode de novo antes de reescrever.
</observation>
<verifier>
conferir_citacoes, código puro: todo item cita um commit da lista; todo commit tem item ou motivo. Saída 0 aprova, 1
reprova com a lista, qualquer outra é VERIFIER_FAILURE. Quem redige não altera o script nem a lista.
</verifier>
<recovery_and_convergence_policy>
RECOVERABLE: citação errada, reescreve. TRANSIENT: tempo esgotado ou limite de taxa, 2 novas tentativas com espera
crescente. BLOCKED: mesma assinatura em 3 tentativas. VERIFIER_FAILURE: saída fora de 0 e 1. Progresso = itens aprovados ÷
commits da lista. W = 2 ciclos sem variação: NON_CONVERGENCE.
</recovery_and_convergence_policy>
<stop_rules>
DONE: verificador aprovou e invariantes intactos. EXHAUSTED: orçamento. BLOCKED, NON_CONVERGENCE e VERIFIER_FAILURE: acima.
NEEDS_INPUT: commit sem descrição legível, com a pergunta estruturada.
</stop_rules>
<budget>
Máximo de 4 ciclos e 5 minutos. redigir: 4000 tokens por ciclo. reescrever: 2000 tokens por ciclo. Reserva: 1 execução do
verificador e o relatório final. Sem saldo para 1 ciclo inteiro: NEEDS_INPUT.
</budget>
<observability>
rastro.jsonl, ao lado de NOTAS.md: ciclo, hash, assinaturas, veredito, progresso, tokens restantes e o estado terminal
com o motivo.
</observability>
</LOOP_SPEC>

ESTÁGIOS:
| # | estágio | tipo | entrada → saída | verificador | maxTokens | nova tentativa | arquivo |
|---|---|---|---|---|---|---|---|
| 1 | coletar | código | 2 tags → lista de commits | código de saída do git | — | 0 | — |
| 2 | redigir | LLM | lista de commits → rascunho | conferir_citacoes | 4000 | 2 transitórias | notas/redigir.txt |
| 3 | conferir_citacoes | código | rascunho + lista → aprovados e reprovados | testes do próprio script | — | 0 | — |
| 4 | reescrever | LLM | reprovados + lista → itens novos | conferir_citacoes | 2000 | 2 transitórias | notas/reescrever.txt |

PROMPTS PENDENTES:
- redigir: um item por commit visível, em Markdown, cada um com o hash do commit.
- reescrever: só os itens reprovados, no mesmo formato, usando somente a lista de commits.

VERIFY GATE: sem ground truth: definir o eval antes da release.
```
