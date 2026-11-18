# BUILD REPORT: F26 Documentos na main e marca do SDD Starter

> Os documentos das frentes passam da branch `docs/incorporar-starter` para a `main`, com duas travas que os seguram
> fora do pacote, varredura própria e a evidência bruta fora do git; as skills geradas para o starter ganham a marca
> "SDD Starter".

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F26_DOCS_NA_MAIN |
| **Date** | 2026-11-18 |
| **Author** | build-agent (sessão do Roberto, execução direta) |
| **DEFINE** | [DEFINE_F26_DOCS_NA_MAIN.md](../features/DEFINE_F26_DOCS_NA_MAIN.md) (rev. 1.5) |
| **DESIGN** | [DESIGN_F26_DOCS_NA_MAIN.md](../features/DESIGN_F26_DOCS_NA_MAIN.md) (rev. 1.3) |
| **Status** | ✅ Complete — Verify Gate verde em `4ccb0ef` (2.586 testes) e a suíte num clone com os documentos verde (2.586 OK, 3 pulados, exit 0 em 2.092 s); revisão do código PRONTO; avaliador fresco PASS_PENDENTE_RECIBO (ciclo 2) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 25/25 linhas do manifest |
| **Files Created** | 8 do pacote e dos testes (`scripts/montar-pacote.sh`, `sdd/bin/docs-varredura.{py,sh}`, `scripts/docs-migracao.py`, `anexar-bruto.sh`, `references/bruto.md`, 2 módulos de teste) e a lista da migração |
| **Lines of Code** | fora das pastas de documento, `git diff --stat 304e60a..HEAD`: 63 arquivos, +1.925 / −123 |
| **Build Time** | 2026-11-17 a 2026-11-18 |
| **Tests Passing** | 2.586 de 2.586 (4 pulados) no Verify Gate em `4ccb0ef` (`VERIFY-GATE-4ccb0ef.log`); a mesma suíte num clone com os documentos, como o CI (`SUITE-CLONE-4ccb0ef.log`); 47 nos 2 módulos da F26 |
| **Agents Used** | 0 especialistas; 3 curadores frescos (2 lotes), 1 avaliador fresco (contrato de aceite) |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 25 linhas de manifest, 2 blocos (documentos na main · marca), migração de uma vez com tag de arquivo |
| Recomendação | execução direta, em ordem: lote da curadoria → código → migração → gate |
| Decisão do usuário | Roberto, 2026-11-17: "Execute o Pipeline ate o release" |

---

## Landmines lidas no build

Varredura do DESIGN refeita no build; entradas inteiras lidas.

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| gate que confere fiação | LM-001 | ✔ tratado | os testes executam montador, gate, varredura, migração, anexo e gerador sobre repositórios de teste, com o lado que reprova |
| asserção sem baseline | LM-002 | ✔ tratado | `AVAL-05-conferir-baseline.log` e `AVAL-08` (vermelhos antes); o teste novo do `--conferir` falhou contra o script anterior antes da correção |
| review sobre diff vazio | LM-003 | ✔ tratado | commit por bloco antes de cada revisão |
| gate sem `.git` | LM-006 | ✔ tratado | conferência e varredura na árvore real; o resto numa cópia de `git archive` |
| `--no-renames` | LM-007 | ✔ tratado | o `--conferir` lê o commit da migração com `--no-renames` |
| número longo no pacote | LM-012 | mordeu | CNPJ e CPF de teste montados em execução; mas o comentário do conserto A6 levou um CPF de exemplo por extenso a `sdd/bin/docs-varredura.py`, e o G2 do pacote reprovou o gate de `8f48705` (`4ccb0ef` tirou o número) |
| edição de teste por corte | LM-013 | ✔ tratado | versões fixadas trocadas por troca exata, com contagem antes |
| saída em cp1252 / `subprocess` | LM-014 · LM-015 · LM-030 | ✔ tratado | a troca da saída é o 1º comando do `__main__` dos 2 scripts novos (a guarda da F16W2 pegou a falta na suíte inteira) |
| fallback calado | LM-017 | ✔ tratado | sem gitleaks a varredura sai 2; teste com `path_restrito` |
| `[exit=]` no zsh | LM-018 | ✔ tratado | logs por script bash com `rc=$?`; a lista de pares do lote dentro do zsh não se dividiu e foi refeita em bash |
| chave falsa por extenso | LM-020 | ✔ tratado | segredos de teste montados em execução; 6 logs antigos com chave falsa por extenso ficaram só na tag (varredura) |
| gerador / version gate do destino | LM-022 | ✔ tratado | as 18 skills sobem versão no Open |
| exceção que cala a linha | LM-023 | ✔ tratado | aceite só com motivo, na linha e na de baixo |
| `bash` sem caminho / PATH restrito no Windows | LM-029 · LM-034 | ✔ tratado | constantes de `tests/apoio.py` |
| texto da skill gerada | LM-035 | ✔ tratado | `test_gerar_starter` verde antes do gate |
| arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | 8 linhas novas; publish-gate numa cópia antes do gate |
| teto da `SKILL.md` | LM-038 | ✔ tratado | `sdd-release` com 452 linhas |
| plataforma por `os.name` | LM-042 | ✔ tratado | os testes usam as constantes de `tests/apoio.py` |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `export-ignore` `-export-ignore` `git archive` `.gitattributes` `sdd/bin/**`
regra: Numa lista de permissão do `.gitattributes`, `pasta/** -export-ignore` sem a linha `pasta -export-ignore` (a própria pasta) deixa a pasta inteira fora do `git archive`, calado: o atributo da pasta pai vence o do conteúdo. Na F26, `sdd/bin` sumiria do pacote sem nenhum aviso. **Do instead:** para cada pasta liberada, escreva as 2 linhas (`pasta -export-ignore` e `pasta/** -export-ignore`) e prove pelo tarball montado, nunca pelo `check-attr` de um arquivo só.
evidencia: sdd/features/DESIGN_F26_DOCS_NA_MAIN.md (Landmines aplicáveis, a landmine nova medida)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `regex` `e-mail` `quadrático` `linha longa` `re.finditer`
regra: Regex de e-mail com quantificador sem teto (`[\w.+-]+@[\w-]+(\.[\w-]+)+`) tem custo quadrático numa linha longa sem `@` (log minificado, base64): na F26, a varredura dos documentos levou a suíte de 28 para 74 minutos e um teste estourou o tempo. **Do instead:** quantificadores com teto (`{1,64}`, `{1,253}`) e só avaliar a linha que tem `@`; meça com uma linha de 600 KB antes do gate.
evidencia: sdd/reports/BUILD_REPORT_F26_DOCS_NA_MAIN.md (Issues Encountered)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `tar` `COPYFILE_DISABLE` `._` `macOS` `anexo`
regra: O `tar` do macOS põe arquivos `._<nome>` (atributos estendidos) dentro do pacote: um anexo montado no Mac tem arquivos que a pasta não tem, e a conferência por lista reprova. **Do instead:** `COPYFILE_DISABLE=1 tar …` em todo pacote montado por script, e confira a lista do pacote contra a pasta.
evidencia: sdd/reports/BUILD_REPORT_F26_DOCS_NA_MAIN.md (Issues Encountered)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `-text` `CRLF` `.gitattributes` `blob` `evidência do Windows`
regra: Log de evidência gravado no Windows tem CRLF; com a normalização de fim de linha, o mesmo arquivo copiado para outra branch vira outro blob, e toda conferência por blob (migração, selo) reprova. **Do instead:** `sdd/reports/evidence/** -text` no `.gitattributes`: evidência é guardada byte a byte.
evidencia: sdd/features/DESIGN_F26_DOCS_NA_MAIN.md (Revision History 1.1: CRLF medido)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `--conferir` `HEAD` `commit da migração` `migração de uma vez`
regra: A conferência de uma migração feita uma vez não pode ler a `HEAD`: os commits normais de depois (o papel da release, uma entrada nova na fila) a deixam vermelha e travam o passo seguinte (aposentar a origem) à toa. Na F26, o `--conferir` lia a `HEAD` e o `--pode-aposentar` nunca sairia 0 depois da release. **Do instead:** a conferência lê o commit que a migração criou (o que adicionou a lista, `git log --diff-filter=A`); teste com um commit de documento e uma entrada de fila depois da migração.
evidencia: sdd/features/DESIGN_F26_DOCS_NA_MAIN.md (Revision History 1.3)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `git archive` `checkout` `os.walk` `documentos` `Verify Gate`
regra: O Verify Gate que roda a suíte numa cópia de `git archive` não vê o teste que percorre o checkout: com documentos na `main` (fora do pacote pela trava), o CI roda no checkout e acha o que a cópia não tem. Na F26, `test_seguranca_catalogo` reprovou um documento migrado só no clone. **Do instead:** quando a frente põe arquivos fora do pacote no repositório, rode a suíte também num clone (com o checkout inteiro) antes de declarar o gate verde.
evidencia: sdd/reviews/AVALIACAO_F26_DOCS_NA_MAIN_20261118-0753.md (A2)
ficha: —
mordeu_antes: —
>>>
```

---

## Drift detectado

| Item | DESIGN | Código | Ação |
|---|---|---|---|
| `--conferir` | "mesmo blob na `HEAD`" (1.2) | lê o commit da migração | DESIGN 1.3: o papel da release e a fila nova reprovariam o `--pode-aposentar` à toa; teste novo, vermelho contra o script anterior |
| lote da curadoria | 2 entradas | 2 lotes | a entrada velha da F25 (recusada) saiu pela colheita nova, que trouxe 7 itens só dela; julgados num 2º lote (Roberto: 2 aceitas, 2 recusadas) |
| textos que mandavam o documento para a branch de documentos | — | PLANO (Regra e linha da F26), ficha mestre, prompt de retomada, alerta da ficha da F25 | gravados na própria branch de documentos (`511d6fa`, o último commit dela) e migrados como `igual`: o PR não mexe em documento migrado, e a conferência fecha também com a F26 entrando na `main` por squash (`SQUASH-SIMULADO.log`) |
| branch de documentos depois da tag | tag no último commit | outra sessão gravou `6f15b7b` (escopo da checar-ambiente) depois da 1ª tag | Roberto, 2026-11-18: branch congelada até a F26 entrar na `main`; tag refeita em `511d6fa` e migração refeita (local, nada publicado); a história anterior fica na branch local `f26-reserva-antes-da-remigracao` |

---

## Files Created

| Arquivo | Linhas | Propósito |
|---|---|---|
| `scripts/montar-pacote.sh` | 48 | monta o pacote por `git archive` (trava 2 no CI) |
| `sdd/bin/docs-varredura.py` | 332 | regras e saída da varredura dos documentos (AT-004, AT-012) |
| `sdd/bin/docs-varredura.sh` | 42 | entrada da varredura (Python pela `lib/python.sh`) |
| `scripts/docs-migracao.py` | 321 | `--copiar`, `--conferir`, `--pode-aposentar` (AT-005, AT-006) |
| `.agents/skills/sdd-release/scripts/anexar-bruto.sh` | 83 | anexo do bruto na Release, conferido byte a byte (AT-011) |
| `.agents/skills/sdd-release/references/bruto.md` | 39 | o passo do bruto para quem conduz a release |
| `tests/test_f26_docs_na_main.py` | 600 | AT-001 a AT-007, AT-011, AT-012 |
| `tests/test_f26_marca_starter.py` | 165 | AT-008 a AT-010 |
| `sdd/reports/MIGRACAO_DOCS_F26.tsv` | 3.267 | a lista da migração: 2.866 igual · 1 ajustado · 399 fora |

---

## Verification Results

### Lint · Typecheck

`bash -n` nos scripts novos (passo "Shell syntax" do CI, agora sobre o pacote); `playbook-lint` e `--anti-collapse`
0 nos 2 lotes; `--validar-inv` 0 (par válido).

### Testes

| Rodada | Resultado | Log |
|---|---|---|
| suíte inteira em `8457d33^` | 23 falhas: 20 versões fixadas, a guarda UTF-8 da F16W2 nos 2 scripts novos, o passo do Windows | corrigidas em `8457d33` |
| suíte inteira em `8457d33` | ✅ 2.576 testes OK (4 pulados), 1.709 s | — |
| Verify Gate inteiro em e99136d | ✅ exit 0 (história antes da remigração; o commit está na branch local `f26-reserva-antes-da-remigracao`) | `VERIFY-GATE-e99136d.log` |
| Verify Gate inteiro em 8f48705 | ❌ exit 1: o G2 do publish-gate barrou um número de 11 dígitos num comentário (LM-012) | consertado em `4ccb0ef` |
| Verify Gate inteiro em 4ccb0ef | ✅ exit 0 em 2.245 s: conferência VERDE · varredura VERDE · 135 nomeados OK · publish-gate GREEN sobre o pacote · suíte 2.586 OK (4 pulados) | `sdd/reports/evidence/F26_DOCS_NA_MAIN/VERIFY-GATE-4ccb0ef.log` |
| suíte inteira num clone com os documentos, em 4ccb0ef (como o CI) | verde (2.586 OK, 3 pulados, exit 0 em 2.092 s) | `sdd/reports/evidence/F26_DOCS_NA_MAIN/SUITE-CLONE-4ccb0ef.log` |

### Migração (na árvore real)

| Passo | Resultado |
|---|---|
| tag `arquivo/docs-incorporar-starter` | `511d6fa`, local (o push é da release, com o OK do Roberto); a 1ª tag (`f2fecf7`) ficou velha com o commit `6f15b7b` de outra sessão |
| `--copiar` | 3.266 documentos: 2.866 igual · 1 ajustado · 399 fora (392 bruto, 6 reprovados pela varredura, 1 acima de 256 KB) |
| commit da migração | `d761bb4`, só documentos e a lista (2.868 arquivos) |
| `--conferir` | VERDE na branch; VERDE também com a F26 inteira num commit só sobre `304e60a` e com um commit de papel depois (`SQUASH-SIMULADO.log`) |
| `docs-varredura.sh .` | VERDE: 2.889 arquivos, nada achado, 2 s |

---

## Segurança

S17 aplicado: a saída da varredura diz arquivo, linha e regra, sem o conteúdo achado; nome de arquivo com quebra de
linha não forja linha. Os 6 logs com chave falsa por extenso e o log com e-mail ficaram só na tag. O G2 e o G3 não
foram afrouxados: o publish-gate confere o pacote montado.

---

## Issues Encountered

| Issue | Resolução |
|---|---|
| regex de e-mail sem teto: custo quadrático em linha longa (suíte de 28 → 74 min, 1 teste estourou o tempo) | quantificadores com teto e só a linha com `@`; 600 KB em 0,16 s (`4e1980f`) |
| o `tar` do macOS pôs `._` no anexo | `COPYFILE_DISABLE=1` (`4e1980f`) |
| e-mails por extenso na própria varredura e CNPJ de 12 dígitos num teste reprovavam o G2 do pacote | montados em execução |
| 40 logs do Windows com CRLF mudariam de blob na migração | `sdd/reports/evidence/** -text` (DESIGN 1.1) |
| suíte inteira: 23 falhas (versões fixadas, guarda UTF-8 da F16W2, passo do Windows) | `8457d33` |
| a colheita guardada da F25 tinha 18 impressões a menos que os documentos (entrada recusada) | colheita refeita; o lote 1 julgou a nova; a velha saiu pela 3ª colheita, julgada no lote 2 |
| `--conferir` lia a `HEAD` | lê o commit da migração (`7375d01`, DESIGN 1.3) |
| outra sessão gravou na branch de documentos depois da 1ª tag (`6f15b7b`) | Roberto congelou a branch até a F26 entrar na `main`; tag refeita no último commit (`511d6fa`) e migração refeita |
| o gate numa cópia de `git archive` não vê teste que percorre o checkout (`test_seguranca_catalogo` com os documentos migrados; avaliador, A2) | pastas de documento fora da varredura do teste; a suíte passa também num clone com os documentos, como o CI |
| comentário com CPF de exemplo por extenso (conserto do A6) barrou o G2 do pacote | `4ccb0ef`; o publish-gate sobre o pacote roda depois de cada commit de código |
| avaliador A7 (o `--padrao` com `--ref` não olha o histórico) e A8 (a `sdd-release` não diz o que fazer com o exit 2 da varredura) | pendências ✨, baixas: o CONTRIBUTING manda usar `--texto`, que olha o histórico; nesta release, o exit 2 é tratado como abortar |

---

## Deviations from Design

Só as do quadro de drift; a do `--conferir` está no Revision History do DESIGN (1.3).

---

## Blockers (if any)

Nenhum. Pendem da release, com o OK do Roberto: o push da branch de documentos e da tag de arquivo.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 3 (pacote e CI · documentos e migração · gerador do starter)
**Contrato de aceite (passo 1.5 da `sdd-build`):** 5 propostas, 5 aceitas (DESIGN › Contrato de aceite; `AVAL-01..09.log`)
**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO — `sdd/reviews/AVALIACAO_F26_DOCS_NA_MAIN_20261118-0856.md` (ciclo 2: 12 de 12 ATs por execução, A1 a A6 do ciclo 1 resolvidos, 2 achados baixos); ciclo 1 NEEDS_WORK em `sdd/reviews/AVALIACAO_F26_DOCS_NA_MAIN_20261118-0753.md`. Recibos pendentes da publicação: o CI do PR nos 3 sistemas, o push da branch de documentos e da tag de arquivo (`--pode-aposentar` 0), o envio real do bruto (a F26 não tem bruto: SEM BRUTO)

---

## Acceptance Test Verification

| AT | Critério | Passou | Evidência |
|----|----------|--------|-----------|
| AT-001 | pacote por `git archive` sem documento; `extrair_tag` do gerador idem; baseline sem a trava | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-001.log` |
| AT-002 | arquivo fora do `MANIFEST.txt` no pacote ⇒ publish-gate vermelho; workflows só leem o pacote | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-002.log` |
| AT-003 | checkout com número longo, `/Users/`, `.sh` em evidência: gate e shell verdes sobre o pacote | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-003.log` |
| AT-004 | varredura: cada regra reprova, aceite só com motivo, saída sem o trecho, sem gitleaks nunca verde | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-004.log` |
| AT-005 | `--copiar` classifica; `--conferir` 0 só sem desvio, lendo o commit da migração | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-005.log` |
| AT-006 | `--pode-aposentar` só com a tag no último commit do remoto e a conferência verde | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-006.log` |
| AT-007 | push só de documento não publica; `init` de um clone não instala documento; suíte no piso | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-007.log` |
| AT-008 | as 18 skills geradas com "SDD Starter" na descrição e na linha; `check-versions` aceita a nova | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-008.log` |
| AT-009 | descrição acima de 1.024 ⇒ 65 sem gravar | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-009.log` |
| AT-010 | Open sem a marca; `checar.sh` separa as origens; gerador recusa cópia sem versão maior | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-010.log` |
| AT-011 | anexo do bruto conferido pelo download; sem Release ou varredura vermelha ⇒ nada anexado | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-011.log` |
| AT-012 | `CONTRIBUTING.md` com os 3 lugares e 30 dias; `--padrao` prova a remoção | true | `sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-012.log` |

---

## Final Status

✅ Complete. Verify Gate verde em `4ccb0ef` e a suíte num clone com os documentos verde (2.586 OK, 3 pulados, exit 0 em 2.092 s); 12 de 12 ATs com evidência por execução; migração refeita na tag `511d6fa` e conferida, também por squash simulado; fila da curadoria vazia; revisão do código PRONTO (8 aplicadas, 2 rebatidas); avaliador fresco PASS_PENDENTE_RECIBO no ciclo 2.

---

## Next Step

**Ready for:** `/sdd-release F26` — o push da branch, o PR com o CI nos 3 sistemas e o push da branch de documentos e da tag de arquivo pedem o OK do
Roberto para cada envio.
