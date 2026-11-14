# Avaliação de contexto novo — F17C_STARTER_ETAPA3, ciclo 2

> Bloco devolvido pelo avaliador (subagente em contexto novo, modo `veredito`, ciclo 2), sobre `72667a3`: veredito e
> tabela verbatim; achados resumidos sem mudar o sentido. Logs: `sdd/reports/evidence/F17C_STARTER_ETAPA3/AVAL2-*.log` (5).

<<<AVALIACAO
VEREDITO: NEEDS_WORK — os achados 2, 3, 4 e 5 estão consertados e os 10 ATs passam em HEAD, mas os 3 de 3 da série 3 do build não se sustentam pelo critério escrito: as 3 recomendam construir pelo chat e o juiz tem 9 furos.

| item | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | AVAL2-gerar.log; test_gerar_starter e test_f17c_gerador em AVAL2-testes.log | rc 0; 18 skills com GERADO.txt; README e quickstart com as 18, sem validador | gerador rc=0; 18 pastas, 0 sem GERADO.txt; os testes de README, quickstart e baixar-nfse OK | PASS |
| AT-002 | test_f17c_gerador.ModoWeb e diff -r com gerado-head (AVAL2-gerar.log) | só os arquivos de web/; nada do caminho do Open | testes OK; a saída gerada é igual à da série 3 | PASS |
| AT-003 | test_f17c_gerador (AVAL2-testes.log) | 65 sem gravar; a cópia crua reprova | OK | PASS |
| AT-004 | test_f17c_textos.ModoWebGerado | pastas do Open; entrega no chat; handoffs coerentes | OK | PASS |
| AT-005 | test_f17c_textos, mais a busca de "valida" no build gerado | sem comando e sem validador | OK; nenhum "validado"; resta só o estado interno `VALIDATE_REPORT` (build-protocol.md:21), sem validador | PASS |
| AT-006 | test_f17c_textos.MoldesDoOpen | seções e moldes sem sobras | OK | PASS |
| AT-007 | AVAL2-achados-2a5.log e test_f17c_textos.NaoFinjaNoOpen | as 3 com leu, inspecionou, escreveu, gravou, rodou e não inventa caminho; pergunta da 1ª vez; manual-ux nunca como atalho | as 6 marcas nas 3 skills; a pergunta e o "nunca é atalho" no define; o design pergunta a stack | PASS (com a ressalva do achado 3) |
| AT-008 | AVAL2-AT008.log | 9 checagens 0; um byte trocado faz o check-gerado sair 1 | falhas=0; check-gerado da cópia mutada sai 1 | PASS |
| AT-009 | test_f17c_gerador e test_gerar_starter.Recusa | 65 antes de gravar | OK | PASS |
| AT-010 | skill_lint, check_versions, agnostico, decisoes_lint, f17b e f21 em AVAL2-testes.log | continuam verdes; linha do modo condicionada | 519 OK, inclusive a linha nova do desvio | PASS |
| Ciclo 1, achado 1 (HIGH) | AVAL2-INICIANTE-juiz.log e leitura dos logs s3-g-1, s3-g-2 e s3-g-3 | 3 de 3 pelo critério; juiz que reprova o que o critério reprova | as 3 recomendam "eu escrevo, você salva", o caminho que o critério lista como reprovação; o roteiro para na volta 1, e as voltas 2 e 3 nunca rodam; o texto do build web não mudou; o juiz deixa passar 5 casos que o critério reprova e reprova 4 que ele aceita | FAIL |
| Ciclo 1, achado 2 | AVAL2-achados-2a5.log | frase inteira nas 3; teste com a frase | frase igual nas 3; o teste confere a frase inteira | CONSERTADO |
| Ciclo 1, achado 3 | AVAL2-achados-2a5.log | o desvio diz que os caminhos são os de web/ | linha presente nas 3; todos os citados existem em web/; o gerado não cita web/ | CONSERTADO |
| Ciclo 1, achado 4 | AVAL2-achados-2a5.log | nada "validado" no build gerado | 0 ocorrências; description "BUILD_REPORT conferido" | CONSERTADO |
| Ciclo 1, achado 5 | AVAL2-achados-2a5.log | exemplo de manual-ux com "Eu abri … e vi …"; fragmento e define coerentes | 5 frases "Eu … e vi …"; o fragmento ganhou a exceção "Fora da UX pura", que a SKILL.md do define não tem | CONSERTADO, com o achado 3 |
| Ciclo 1, achado 6 | cabeçalhos dos AT-*.log; BUILD_REPORT linha 100; grep nos logs do define | evidência em HEAD; roteiro que exercita a pergunta da 1ª vez | os AT-*.log são de `01f8faf`, de antes do conserto: o AT-007.log rodou a asserção antiga; o roteiro do define não mudou e 0 dos 3 logs mostram a pergunta | NÃO CONSERTADO |

ACHADOS:
1. [HIGH] O teste do iniciante do build não sustenta 3 de 3: as 3 respostas da série 3 recomendam construir pelo chat com o aluno salvando ("existe um caminho que funciona daqui mesmo", "dá para você ser 'as mãos' do build", "isso funciona"); pedir o projeto fica como opção não recomendada; o juiz aprovou por "não consigo gravar/criar arquivos"; o rodador parou na volta 1; o juiz deixa passar 5 casos que o critério reprova e reprova 4 que ele aceita (`AVAL2-INICIANTE-juiz.log`, "FUROS DO JUIZ: 9"); o texto do build web não mudou no ponto (`MODO_WEB.md:83`). Decisão do Roberto: endurecer o texto ou aceitar o caminho no critério; nos dois casos, o juiz roda todas as voltas e os 9 furos ficam fechados.
2. [LOW] A série 3 mudou o ambiente (OpenRouter) só para o build; o OK do Roberto não está no DEFINE. Correção: registrar no DEFINE a mudança do critério.
3. [LOW] O fragmento do Verify Gate isenta a UX pura da pergunta da 1ª vez; o AT-007 e a `sdd-define/SKILL.md` não têm a exceção. Alinhar ou emendar o AT (pergunta ao Roberto).
4. [LOW] Os `AT-*.log` são de `01f8faf`; regerar em HEAD. O roteiro do define não exercita a pergunta da 1ª vez.
5. [INFO] Estado `VALIDATE_REPORT` no `build-protocol.md:21` do build gerado, herdado da `v1.5.18`, sem validador. Opcional.
>>>
