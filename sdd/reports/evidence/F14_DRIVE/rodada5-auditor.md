## 1. Auditoria por achado

**R1@claude**
**Veredito:** AGREE
**Justificativa:** O texto da skill em `.agents/skills/sdd-release/SKILL.md:231` instrui o agente a repetir a chamada sem limite total enquanto o exit for 4, o que anula a garantia de teto de 40 minutos do script e pode deixar o agente em laço infinito caso o workflow nunca seja acionado.

**R2@claude**
**Veredito:** AGREE
**Justificativa:** Em `sdd/bin/deploy-do-sha.sh:130`, o método `gh()` intercepta erros 401 e chama `fim(3)` diretamente, encerrando o script antes que o bloco `except ConsultaFalhou` do chamador possa executar `d.desmarcar()`, deixando a marca de redisparo órfã.

**R3@claude**
**Veredito:** AGREE
**Justificativa:** Em `sdd/bin/sdd-drive.sh:333`, se `os.remove` lançar `OSError` (ex.: permissão negada), o `except OSError: continue` pula o `time.sleep(0.05)` e a verificação de `limite_espera`, criando um laço infinito que consome 100% da CPU.

**R4@claude**
**Veredito:** AGREE
**Justificativa:** Em `sdd/bin/sdd-archive.py:258`, documentos soltos recentes (`idade < dias_b`) caem na lista `nao_class` ("Sem classificação") em vez de `recentes`, divergindo do tratamento aplicado a grupos com a mesma idade e do esperado no AT-028.

**R1@codex**
**Veredito:** DISAGREE_EVIDENCE
**Justificativa:** O DESIGN (Decision 3) e os comentários do código em `sdd/bin/sdd-drive.sh:330` explicitam que a trava é "curta (nunca durante o gate)" e expira por tempo (`ESTADO_ABANDONADO = 60`) justamente como mecanismo para lidar com processos mortos; o cenário de suspensão >60s é um trade-off aceito e documentado, não um defeito de serialização.

## 2. Achados novos

Não há achados novos de severidade HIGH ou MED que as revisões não tenham citado.

## 3. Bloco de vereditos

<<<VERDICTS
{"achado":"R1@claude","veredito":"AGREE","justificativa":"O texto da skill instrui repetição sem limite total, anulando o teto do script e podendo gerar laço infinito no agente."}
{"achado":"R2@claude","veredito":"AGREE","justificativa":"O método gh() chama fim(3) diretamente para 401, bypassando o except que faria desmarcar() e deixando a marca órfã."}
{"achado":"R3@claude","veredito":"AGREE","justificativa":"O except OSError: continue pula o sleep e a verificação de limite, gerando um laço infinito de CPU."}
{"achado":"R4@claude","veredito":"AGREE","justificativa":"Documentos soltos recentes caem em nao_class em vez de recentes, inconsistente com o tratamento de grupos e o AT-028."}
{"achado":"R1@codex","veredito":"DISAGREE_EVIDENCE","justificativa":"O DESIGN e os comentários explicitam que a trava é curta e expira por tempo para lidar com processos mortos, sendo um trade-off aceito."}
VERDICTS>>>