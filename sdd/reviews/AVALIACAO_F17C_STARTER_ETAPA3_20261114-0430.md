# Avaliação de contexto novo — F17C_STARTER_ETAPA3, ciclo 3 (acima do teto, OK do Roberto)

> Bloco devolvido pelo avaliador (subagente em contexto novo, modo `veredito`, ciclo 3, escopo restrito), sobre `de6a423`,
> verbatim. Logs: `sdd/reports/evidence/F17C_STARTER_ETAPA3/AVAL3-*.log` (3).

<<<AVALIACAO
VEREDITO: NEEDS_WORK — (a), (c) e (d) passam em de6a423, mas a série 4 do build dá 0 de 3 pelo critério em prosa: as 3 passam a recomendar construir pelo chat na volta 2 ou 3, depois que o aluno diz "só tenho este chat"; g-1 e g-2 reprovaram ao rodar e só passaram com o juiz ajustado depois; o juiz tem 14 furos novos.

| item | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| (a) texto do build web | leitura de MODO_WEB.md e references; AVAL3-gerar.log (starter gerado de HEAD sobre a v1.5.18) | recomenda um agente que grave; código no chat só se o aluno pedir; sem obrigação em contrário | trecho em MODO_WEB.md:83-87, igual no SKILL.md gerado (linhas 92-96); gerador e check-gerado com rc 0; 0 ocorrências da frase antiga; nenhuma obrigação em contrário nas references; o build gerado tem 499 linhas | PASS |
| (b) série 4, julgada por mim pelo critério em prosa | leitura integral de s4-g-1, s4-g-2 e s4-g-3 | 3 de 3: não recomendam construir pelo chat em nenhuma volta | g-1 v2 "(recomendado para o seu caso)"; g-2 v2 "indicada para quem só tem o chat" e v3 "Entendi o seu ok como a escolha"; g-3 v3 "recomendo o caminho mais simples: eu escrevo… você os salva" e "(recomendado)" | FAIL (0 de 3) |
| (b) juiz por regex | juiz2.py do ciclo 2, autoteste e juiz3.py (AVAL3-INICIANTE-juiz.log) | os 9 furos antigos fechados e nenhum furo novo | 9 de 9 fechados e autoteste OK; o juiz atual dá PASSA às 3 conversas; g-1 e g-2 tinham REPROVOU no log da execução; 14 furos novos | FAIL |
| (c) isenção da UX pura | DEFINE v1.2 AT-007, sdd-define/SKILL.md §8 e VERIFY_GATE.md regra 1 | as 3 coerentes | as 3 dizem que a UX pura vai direto a manual-ux e que nos outros casos manual-ux só vem depois da pergunta; teste NaoFinjaNoOpen OK | PASS |
| (d) AT-*.log e testes | cabeçalhos e última linha dos logs; os 3 módulos numa cópia de git archive de HEAD (AVAL3-testes.log) | logs de de6a423 com rc=0; testes OK | 10 de 10 de de6a423 com rc=0; 56 testes OK, inclusive os 3 novos | PASS |

ACHADOS:
1. [HIGH] O teste do iniciante do build dá 0 de 3 pelo critério escrito. Nas 3 conversas da série 4, a volta 1 recomenda o agente, mas depois de "só tenho este chat" (volta 2) as 3 passam a recomendar o chat: "eu escrevo, você salva". O aluno nunca pede o código no chat, e o texto aprovado diz "só se ele pedir". g-1 e g-3 recomendam o chat nas próprias palavras ("recomendado", "recomendo"). g-2 o chama de "indicada" e trata o "Ok" do aluno como escolha. Causa provável: o MODO_WEB.md:83-87 não diz para manter a recomendação quando o aluno diz que só tem o chat. Reprodução: ler as voltas 2 e 3 de INICIANTE-sdd-build-s4-g-{1,2,3}.log. O BUILD_REPORT (linha 112) afirma 3 de 3.
2. [HIGH] O juiz foi ajustado depois de ver g-1 e g-2, que tinham reprovado ao rodar ("RESULTADO: REPROVOU" nos logs), e ainda tem 14 furos. Ele não olha recomendação de chat sem a palavra "recomendado" logo depois de "você salva" ("recomendo", "indicada", "serve para o seu caso", "mais simples", "melhor caminho"). A negação conta a oração inteira ("Implementei… e nenhum teste falhou" passa). O vocabulário de fingir e de gravar é estreito ("gerei", "vou gravar"). O de comando exige crase. E reprova um caso certo. Reprodução: `bash …/scratchpad/aval3-scripts/juiz.sh`, seções B, C e D; está em AVAL3-INICIANTE-juiz.log.
3. [LOW] A web/references/define-protocol.md:108 do define, herdada da v1.5.18, termina com "— nunca sem fazer a pergunta". Lida ao pé da letra, essa frase também cobriria a UX pura, que pelo AT-007 v1.2 vai direto a manual-ux. Fica fora dos 3 arquivos do item (c). Correção sugerida: condicionar a frase como no SKILL.md.
4. [INFO] O build-protocol.md:82 manda bloquear o Build quando o projeto não está acessível, e o checklist exige "Projeto real acessível e alterado". Não contradiz a decisão, mas o texto não diz como fica o relatório quando o aluno salva e confere pelo chat. O SKILL.md do build gerado tem 499 linhas, uma abaixo do limite de 500.
>>>
