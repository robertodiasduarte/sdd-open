# Avaliação de contexto fresco — F21_ENGENHARIA_REVERSA, ciclo 2 (2026-11-10)

Avisos do avaliador antes do bloco: o alvo mudou de `5736ae4` para `ae05d6e` durante o ciclo (aviso de quem despachou); leu `git diff 2af3d6c HEAD` uma vez para localizar os consertos; gravou só 6 arquivos `AVAL2-*.log`; não rodou a suíte inteira nem `tests/test_sdd_open.py`, por instrução.

<<<AVALIACAO
FEATURE: F21_ENGENHARIA_REVERSA
MODO: veredito · ciclo: 2
ALVO: commit ae05d6e, em cópias de `git archive ae05d6e` fora do repositório, sem `.git`; base v2.8.0 = 45e27a9
ALVO MUDOU NO CICLO: o brief dizia 5736ae4. Esse commit levava 3 `tests/__pycache__/*.pyc` e `sdd/traces/F21_ENGENHARIA_REVERSA.jsonl`; numa cópia dele o `publish-gate.sh` sai 1 com 4 "undeclared file". O ae05d6e só tira esses 4 arquivos (`git diff --stat 5736ae4 ae05d6e`: 4 arquivos, 1 linha removida). Em ae05d6e: 0 `.pyc` rastreados, gate GREEN.
AMBIENTE: /usr/bin/python3 3.9.6 · python3 3.15.0 · /bin/bash 3.2 · sem rede · sem credenciais
CONTAMINAÇÃO: leve — li `git diff 2af3d6c HEAD` e os títulos dos commits para localizar os consertos; não abri BUILD_REPORT. Nenhum resultado abaixo vem de leitura de diff.
NÃO EXECUTADO (por instrução do brief, outro processo roda a suíte): a suíte inteira, `tests/test_sdd_open.py`, `tests/test_hooks.py`, `tests/test_drive.py` e, portanto, o comando completo do Verify Gate. Só a primeira metade dele (`publish-gate.sh` em cópia de `git archive`) rodou aqui.

VEREDITO: PASS

| AT | Sonda (executada) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | `find` na pasta da skill; busca dos proibidos; leitura por JSON de `manifest.json` e `cases.json`; cada arquivo contra `MANIFEST.txt`; G3 do `publish-gate.sh`; classe `Pacote` | 13 arquivos, nenhum proibido, 1.1.0 nos três lugares, tudo no MANIFEST | 13 arquivos; sem `LICENSE.txt`, `VALIDACAO.md`, `tests/` nem `__pycache__`; `version "1.1.0"` no frontmatter, no manifesto e nos cenários; descrição com 750 caracteres; nenhum arquivo faltando no MANIFEST; G3 verde nos dois sentidos | PASS |
| AT-002 | `skill-lint.py --conversa .agents/skills/*/SKILL.md` nas duas versões; `sdd-decisoes-lint.sh --sites .agents/skills`; sabotagem (tirar "não sei"); `test_skill_lint`, `test_conversa`, `test_decisoes_lint` | exit 0 nas 20; a sabotagem reprova | 20 linhas verdes, exit 0; 27 perguntas em 22 arquivos, exit 0; sabotagem dá VERMELHO em `como-falar.md:68`; 29, 19 e 11 testes OK. O `como-falar.md` consertado continua passando | PASS |
| AT-003 | CLI sobre levantamento válido, 3.9.6 e 3.15, cwd `/`, caminho relativo em pasta com espaço, script da fonte e da cópia `.claude`; SHA-256 antes e depois | `"ok": true`, exit 0, arquivo intacto | exit 0 em todos; SHA-256 igual | PASS |
| AT-004 | 10 malformações, arquivo vazio, ausente, diretório e sem argumento, nas duas versões; 18 testes de `test_validate_reverse.py` | exit diferente de 0 com o código; ausente sem traceback | todas exit 2 com código (`OBSERVADO_SEM_SESSAO`, `REFERENCIA_INEXISTENTE`, `SUPORTE_INDISPONIVEL`, `ACHADO_SEM_EVIDENCIA`, `ID_ACHADO_DUPLICADO`, `DIMENSOES_COBERTURA`, `PLACEHOLDER_NAO_PREENCHIDO`, `LINHA_ACHADOS`, `SECAO_AUSENTE_OU_DUPLICADA`, `CONCLUSAO_COM_LACUNAS_OU_ESCOPO_VAZIO`); ausente dá JSON `ARQUIVO_INACESSIVEL_OU_NAO_UTF8`, exit 2; 18 de 18 em 3.9.6 e 3.15, com e sem `-B`. Ressalva: o limite de A4 | PASS |
| AT-005 | grep da regra nos dois arquivos e da frase antiga; `test_f21_textos` | mesma regra nos dois; sem a frase antiga | regra idêntica em `SKILL.md:43` e `ORQUESTRACAO_SDD.md:55`; frase antiga ausente | PASS |
| AT-006 | grep dos termos; inserção em cópia do primeiro termo proibido e de um termo de ferramenta de um agente; grep de "SDD Brainstorm" e "SDD Define"; 3 sabotagens do nome solto | a suíte falha com arquivo e linha; dependências pelo nome técnico | zero ocorrências; as inserções derrubam `test_sem_produto_real_vitrine_ou_ferramenta_de_um_agente` e `test_agnostico` com `FONTES.md:27`; nome solto só em `ESCOPO_CONFIRMADO.md` (registro da 1.0.0, declarado na linha 76); repor o nome solto em `COMO_FUNCIONA.md`, `cases.json` ou `SKILL.md` derruba `test_dependencias_so_pelo_nome_tecnico` com arquivo e linha | PASS (era FAIL parcial no ciclo 1) |
| AT-007 | grep nos 5 documentos; "19 skills"; `test_docs.py` | linha `ER` entre `KB` e `0`; célula Create/Criar; conceito; ficha; linha e exceção no cli-conventions | tudo presente; nenhum "19 skills"; 23 testes OK. O parágrafo novo do limite de A4 em `cli-conventions.md` não quebrou `test_docs` nem `test_cli_conventions_declara_o_lint` | PASS |
| AT-008 | `git init` e `init --vendors claude --yes` em projeto novo, a partir de uma cópia já usada sem `-B`; `diff -r`; lint da cópia `.claude` nas duas versões; `sync --check`; classe do init em `test_f21_textos` | pasta inteira nas duas localizações; lint exit 0; `sync --check` 0 | init exit 0; `.agents` idêntica à do pacote, 13 arquivos em `.claude`; lint exit 0 nas quatro combinações; `sync --check` EM DIA; nenhum `.pyc` na pasta da skill do projeto | PASS |
| AT-009 | `git diff --quiet v2.8.0 ae05d6e` das pastas `sdd-brainstorm` e `sdd-define`; diff da tabela de fases; `check-versions.py --base v2.8.0`; `test_docs`, `test_conversa`, `test_agnostico`, `test_decisoes_lint` | pastas intactas; só a linha `ER` a mais; arquivos verdes | exit 0; a tabela só ganhou `ER`; check-versions VERDE com 20 skills; os 4 arquivos OK nas duas versões, com e sem `-B`. `test_sdd_open.py` NÃO rodou neste ciclo (41 OK no ciclo 1, em 2af3d6c) | PASS no que rodou; `test_sdd_open` NAO_VERIFICADO neste ciclo |
| AT-010 | leitura por JSON; classe `Manifesto` | 17 cenários; contagem declarada; `testes_escritos` aponta o teste | ER-01 a ER-17; 17 escritos, 3 executados, 14 não executados; verificações da 1.0.0 em `historico_1_0_0`; `testes_escritos` cita `tests/test_validate_reverse.py`; as 2 linhas novas de `o_que_ainda_nao_prova` deixam o JSON válido; 3 testes OK | PASS |

Arquivos de teste rodados (8 arquivos × 2 versões × sem `-B` duas vezes e com `-B`): 48 execuções, todas exit 0. Contagens: 18, 29, 29, 19, 23, 11, 7, 12.

SITUAÇÃO DOS ACHADOS DO CICLO 1

A1 · RESOLVIDO. `sys.dont_write_bytecode = True` está na linha 16 de `tests/test_validate_reverse.py`, antes do `exec_module`. Depois de 3 rodadas sem `-B` no 3.15, `find` na pasta da skill não acha `__pycache__` nem `.pyc`; a segunda rodada de `test_f21_textos` e `test_matriz_new_session` na mesma cópia fica verde; o `init` não leva `.pyc` para a pasta da skill. Tirar a linha derruba `test_o_teste_do_lint_nao_grava_bytecode_na_pasta_da_skill`. Log: `AVAL2-A1-sem-pycache-na-pasta-da-skill.log`.

A2 · RESOLVIDO. `COMO_FUNCIONA.md:19` e `cases.json:57` citam `sdd-brainstorm` e `sdd-define`; há teste com dentes (3 sabotagens, 3 falhas nomeadas). Log: `AVAL2-A2-A3-nome-tecnico-e-exemplo-de-recusa.log`.

A3 · RESOLVIDO. O corpo do exemplo de recusa não traz mais "Diga a frase…" nem `SKILL.md`; a orientação subiu para a linha de Situação; o texto canônico de recusa segue idêntico em `SKILL.md:190` e `como-falar.md:86`. Repor a instrução derruba `test_exemplo_de_recusa_nao_traz_instrucao_ao_agente`.

A4 · DECLARADO COMO LIMITE (comportamento inalterado). `PYTHONIOENCODING=ascii` com erro acentuado ainda dá `UnicodeEncodeError` e exit 1, nas duas versões; o mesmo com `LC_ALL=C PYTHONCOERCECLOCALE=0 PYTHONUTF8=0`. O limite está em `manifest.json` (`o_que_ainda_nao_prova`) e em `docs/cli-conventions.md:102-104`, e o texto bate com o que medi. O script continua com o SHA-256 `6abb0ab7…`. Log: `AVAL2-A4-A5-A6-limites-declarados.log`.

A5 · RESOLVIDO. O comando do Success Criteria do DEFINE v1.2, como escrito, sai 0 com 20 linhas verdes.

A6 · DECLARADO COMO LIMITE. `{saas}`, `{DATA-ISO}` e separador `|---|` seguem aprovados (exit 0); `{SAAS}` reprova. Declarado em `manifest.json`; o molde não tem marcador fora de maiúsculas com sublinhado.

A7 · ENCERRADO. Os consertos estão commitados; `git status` não mostra arquivo rastreado modificado.

ACHADOS DESTE CICLO

B1 · INFO · O commit 5736ae4, alvo original do brief, não passa no gate.
  Reprodução: `T=$(mktemp -d) && git archive 5736ae4 | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T` — exit 1, 4 "undeclared file". Resolvido em ae05d6e (mesmo comando, exit 0). Se o histórico for publicado sem squash, 5736ae4 fica nele com os `.pyc`. Log: `AVAL2-alvo-mudou-pyc-versionado.log`.

B2 · INFO · A causa de B1 continua aberta: o repositório não tem `.gitignore`.
  Reprodução, em cópia de `git archive ae05d6e`: `python3 -m unittest discover -s tests -p test_skill_lint.py` (3.15, sem `-B`) e depois `find . -name __pycache__` — aparecem `tests/__pycache__` e `sdd/bin/__pycache__`. Nessa cópia usada o `publish-gate.sh` bloqueia com 10 "undeclared file", e o `init` leva `sdd/bin/__pycache__/skill-lint.cpython-315.pyc` para o projeto novo. Com o 3.9.6 da Apple nada é gravado. Não medi em v2.8.0; `sdd/bin` e os testes antigos não são da F21, então é provável que já fosse assim. Não viola AT. Sugestão: `.gitignore` com `__pycache__/`, declarado no MANIFEST, ou `git add` por caminho.

B3 · INFO · O limite de A4 não está onde o agente lê.
  `grep -n ASCII` na pasta da skill só acha `manifest.json:235`; `SKILL.md` e as referências não citam. `docs/cli-conventions.md` cita, mas não vai para o projeto pelo `init`. Sem AT violado.

B4 · INFO · O log `AVAL2-A2-A3-…` tem um erro meu: `cat -A` não existe no macOS, e o trecho das linhas 78-90 do `como-falar.md` não foi impresso. O conteúdo aparece mais abaixo no mesmo log, na saída da sabotagem de A3.

REGRESSÃO CAUSADA PELOS CONSERTOS: nenhuma encontrada no que rodou. Cópia sabotada foi restaurada e conferida por `diff -r` contra cópia intacta.

EVIDÊNCIA (em `sdd/reports/evidence/F21_ENGENHARIA_REVERSA/`):
AVAL2-alvo-mudou-pyc-versionado.log · AVAL2-testes-f21-e-leves-sem-B-e-com-B.log · AVAL2-A1-sem-pycache-na-pasta-da-skill.log · AVAL2-A2-A3-nome-tecnico-e-exemplo-de-recusa.log · AVAL2-A4-A5-A6-limites-declarados.log · AVAL2-reprova-dos-ATs.log

CONTAGEM: ciclo 1 — 4 resolvidos (A1, A2, A3, A5), 2 declarados como limite (A4, A6), 1 encerrado (A7), 0 abertos. Ciclo 2 — 4 achados novos, todos informativos (B1 a B4); nenhum pede conserto para o aceite.
CONDIÇÃO DO PASS: a suíte inteira com `test_sdd_open.py` verde em ae05d6e, que o outro processo está rodando; eu não a executei.
>>>
