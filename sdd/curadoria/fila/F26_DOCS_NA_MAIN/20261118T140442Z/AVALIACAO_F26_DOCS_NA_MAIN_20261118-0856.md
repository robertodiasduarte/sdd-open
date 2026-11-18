<<<AVALIACAO
veredito: PASS_PENDENTE_RECIBO
modo: veredito · ciclo 2 · F26_DOCS_NA_MAIN · HEAD avaliada: 4ccb0ef (feat/f26-docs-na-main)
evidência: sdd/reports/evidence/F26_DOCS_NA_MAIN/AVAL-C2-00..12-*.log. Cada log tem `$ comando` na 1ª linha, a saída verbatim e `[rc=N]` no fim. Não toquei nos AVAL-01..09 nem nos AVAL-V-*. A árvore do projeto só ganhou esses logs, que estão sem commit. A varredura `docs-varredura.sh .` continua VERDE com eles (2.947 arquivos). Nenhum push, tag, commit ou `gh` real no repositório do projeto.

Resumo: os 12 ATs passam na HEAD. Os achados A1, A2, A4, A5 e A6 do ciclo 1 estão resolvidos, e testei cada um executando. O A3 deixou de ser defeito: o que resta é o push da branch de documentos e da tag, que pedem o OK do Roberto.
- O Verify Gate do DEFINE sai 0: 2.586 testes, 4 pulados.
- A suíte rodada num clone com os 2.928 documentos, que é como o CI roda, também sai 0: 2.586 testes, 3 pulados.

Faltam 3 recibos:
- o CI do PR nos 3 sistemas: o PR ainda não existe, e a branch não está no remoto;
- o envio real do anexo do bruto;
- o push da branch e da tag de arquivo, que libera o `--pode-aposentar`.

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| Gate | C2-00: o `cmd` do Verify Gate, literal, na HEAD 4ccb0ef | exit 0 | `--conferir` VERDE (d761bb4 contra a tag 511d6fa); varredura VERDE (2.930 arquivos); 135 testes nomeados OK; publish-gate GREEN sobre o pacote; discover com 2.586 OK; rc=0 | PASS |
| AT-001 | C2-03: tarball como no release.yml, a partir da HEAD real; `extrair_tag` num clone com a tag vTESTE; baseline sem `sdd/** export-ignore` | 0 documentos; MANIFEST nos 2 sentidos; o baseline vaza | 2.929 documentos na HEAD. No tarball: 0 documentos, 751 de 751 linhas do MANIFEST, 0 sobrando (a "1" listada é a pasta do prefixo). Árvore do `extrair_tag`: 0 documentos. Sem a trava: 3.053 documentos no archive | PASS |
| AT-002 | C2-04 S3, S4, S6: o `run:` literal dos passos dos 2 workflows, num clone | ≠0 nomeando o arquivo; release preso | S3 (sem a trava): rc=1 nos 3 jobs, nomeando `BRAINSTORM_F2_TERRENO.md`. S4 (`notas-frente/F99.md`): rc=1 com "undeclared file". S6 (montador fora de um repositório git): rc=1. `needs: [testes, testes-macos, testes-windows]` | PASS |
| AT-003 | C2-04 S0, S1, S2 | gate e shell 0 com os documentos; `.sh` inválido em `scripts/` ≠0; número longo no pacote faz o G2 ≠0 | S0: 5 passos com rc=0. S1: rc=1 com `bash -n failed: ./scripts/quebrado.sh`. S2: rc=1 com `⛔ pattern matched: /[0-9]{11,}/` | PASS |
| AT-004 | C2-05, 05b, 05c, 05d: repositório mínimo com o `sdd/bin` da HEAD e valores montados em execução | cada regra sai 1, os casos vizinhos saem 0, nada do conteúdo achado na saída, sem gitleaks ≠0 | Saem 1: segredo, e-mail real, `.pfx`/`.P12`, as 3 chaves privadas, CPF e CNPJ com e sem pontuação, CPF colado a letras, 262.145 bytes e 257 KB, documento sem commit, compactado. Saem 0: exemplo/noreply, DV inválido, `/Users/`, aceite com motivo, 262.144 bytes, `--pasta` grande. Aceite 2 linhas acima, sem motivo ou só com pontuação sai 1. vazou=0 em todos. Nome de arquivo forjado: 1 linha só de RESULTADO. Sem gitleaks ou com gitleaks falho: rc=2. A `sdd-release` roda a varredura no item 10, antes do push | PASS |
| AT-005 | C2-06: N0 a N10 num clone, por amend do d761bb4, com o script da HEAD | 0 sem desvio; 1 com o caminho em cada desvio | N0 e N0b: 0. N1 a N9: rc=1, cada um com o caminho (igual alterado ou ausente, fila pendente, `bin/lib/merge.sh` vindo da tag, fora da lista, fora↔igual, bruto presente, linha estranha, fora sem motivo). N10 (commit depois da migração): 0, como desenhado | PASS |
| AT-006 | C2-06 R0–R3 com um remoto bare temporário; C2-12 no repositório real, só leitura | 1 com motivo enquanto a tag não está no último commit ou a conferência ≠0 | R0, R1 e R3: rc=1 com motivo. R2: rc=0, "PODE … pede o OK do Roberto". Real: rc=1, "tag 511d6fa ≠ origin 6f15b7b", porque o 511d6fa está só na branch local | PASS |
| AT-007 | C2-07: `init` a partir de um clone e do tarball; `push-de-papel`. C2-00 e C2-01: suíte no piso, na cópia e no clone com documentos | init sem documentos; NAO_PUBLICA/PUBLICA; suíte verde; CI do PR nos 3 sistemas | init: 698 arquivos instalados e 0 documentos, nas 2 origens. Só documentos: NAO_PUBLICA (rc=1). Playbook e documento+playbook: PUBLICA (rc=0). Suíte: 2.586 OK nos 2 modos. O CI do PR não existe: `gh pr list` devolve `[]` e a branch não está no remoto | PASS no local; CI sem recibo |
| AT-008 | C2-08: starter clonado do GitHub (só leitura); `gerar-starter --tag v2.23.0` na HEAD, num clone; `check-versions` na forma nova e na antiga | marca nos 60 primeiros caracteres, sem "SDD Open", linha nova; a forma nova passa e a antiga é recusada | 18 de 18 com `desc_ok` e `linha_ok` (posição 0 a 39, maior descrição 1.002). 0 documentos no starter. Forma nova: PASS. Forma antiga da sdd-kb: FAIL, rc=1. `check-gerado` VERDE numa geração limpa (C2-09)* | PASS |
| AT-009 | C2-09: descrição da sdd-checar-ambiente +30 caracteres, com versão maior | 65, com a skill e o tamanho; nada gravado | rc=65, "1032 caracteres; o limite é 1.024"; mudanças no starter: 0/0 | PASS |
| AT-010 | C2-08, 09, 09b, 09c | Open sem marca; origens bem classificadas; recusa sem versão maior; a linha do Open muda só pela versão | Open sem marca nas 18. `dup_meta`: 18 starter e 18 open, 0 erradas. Sem versão maior: rc=65. As 18 sobem a versão. Linha igual fora a versão em 17. Na sdd-higiene-dado muda também o mês (out→nov), que segue o `updated` | PASS |
| AT-011 | C2-10: `anexar-bruto.sh` com `gh` falso (`SDD_ANEXAR_GH`) | sem bruto 0; sem Release, varredura ≠0 ou sem gitleaks: nada enviado e 1; anexo igual; download diferente dá ANEXO DIFERENTE | `.gitignore:9`. Sem bruto: 0. Sem Release: 1, 0 enviados. E-mail no bruto: 1, 0 enviados. Caminho feliz: ANEXADO, IGUAL em nomes NFC e bytes (com um nome acentuado e 400 KB). Download diferente: 1. Sem gitleaks: 1, 0 enviados | PASS; envio real sem recibo |
| AT-012 | C2-11: texto do CONTRIBUTING; `--texto` e `--padrao` num repositório de teste com tag e anexo | a seção com os 3 lugares, os passos e 30 dias; 1 enquanto acha, 0 depois | A seção está completa. Antes da remoção: main, ref e pasta saem 1. Depois dos passos 1, 2b (órfão) e 3: 0. Tag regravada num filho, com `--texto`: 1, pelo histórico (A4 resolvido). `--padrao '('`: 64 | PASS (observação A7) |

\* No C2-08, o `check-gerado` saiu rc=1 depois que a própria sonda mexeu na sdd-kb. A regeração dentro da sonda caiu no "destino com mudança não commitada" e a saída estava descartada. É defeito da sonda, não do código. Numa geração limpa o C2-09 dá VERDE, rc=0.

CONFERÊNCIA DOS ACHADOS DO CICLO 1
- A1 RESOLVIDO.
  - C2-02: `Portadas.test_sem_referencia_ao_starter` dá OK na cópia do git archive e no clone.
  - Há 0 ocorrências de `sdd-starter` no `checar.sh` do Open.
  - C2-08: o checar.sh do starter gerado imprime `sdd-checar-ambiente v1.6.1 · SDD Starter · nov/2026 · …/sdd-starter/…`, e o do Open imprime a mesma linha sem a marca.
- A2 RESOLVIDO.
  - C2-02: `SemMaterialDeOrigem` dá OK no clone com 2.928 documentos.
  - C2-01: a suíte inteira no clone sai 0, então nenhum outro teste que percorre o checkout quebra.
- A3 SEM DEFEITO, ESTADO PENDENTE.
  - C2-12: a tag e a branch local estão em 511d6fa. Esse commit é filho do 6f15b7b, e o `ESCOPO_CHECAR_AMBIENTE_1_6_1.md` está na HEAD como `igual` na lista.
  - O origin ainda está em 6f15b7b, e a tag `arquivo/*` não está no remoto.
  - O `--pode-aposentar` real sai 1, como deve. Depois do push da branch e da tag (OK do Roberto), deve sair 0, o que vale como recibo.
- A4 RESOLVIDO para o procedimento do CONTRIBUTING: `--ref` com `--texto` dá 1 enquanto o histórico guarda o dado, e 0 com a tag órfã. O CONTRIBUTING pede o histórico reescrito.
- A5 RESOLVIDO. C2-05c: `.zip`, `.tar.gz`, gzip com nome `.log` e tar sem compressão com nome `.bin` saem 1. Isso vale no modo repositório, no `--ref`, no `--padrao` e no `--pasta`, e o controle sai 0.
  - Medi que nem a HEAD nem a tag de arquivo têm arquivo compactado, nem pelo nome nem pela assinatura. Por isso a regra não trava a prova de remoção.
- A6 RESOLVIDO. C2-05d: `CPF<11 dígitos>`, `x<num>y` e `CPF:<pontuado>` saem 1. DV inválido, número dentro de um número maior e aceite com motivo saem 0.

ACHADOS NOVOS (nenhum bloqueia)
A7 (baixa). Com `--ref`, só o `--texto` olha o histórico; o `--padrao` não.
- O AT-012 nomeia o `--padrao` como a prova. Uma tag regravada num commit filho, provada com `--padrao`, sai 0 enquanto o histórico ainda guarda o dado.
- Reprodução, em C2-11, passo 2:
  1. Num repositório com o dado commitado e a tag `arquivo/t`, rode `git rm` do arquivo e faça o commit.
  2. Rode `git tag -f -a arquivo/t -m x HEAD`.
  3. Rode `bash sdd/bin/docs-varredura.sh --ref arquivo/t --padrao 'Maria \(Exemplo\)'`.
- Resultado: rc=0, mas `git log -p arquivo/t | grep -cF '<dado>'` dá 4. O mesmo caso com `--texto` dá rc=1.
- O CONTRIBUTING manda usar `--texto` e diz que um commit filho não basta, então o procedimento escrito está certo. Sugestão: fazer o `--padrao` com `--ref` olhar o histórico (`git log -G`), ou o CONTRIBUTING dizer que só o `--texto` prova a tag.

A8 (baixa; achado de leitura, não executado). A `sdd-release` não diz o que fazer quando a varredura dos documentos sai 2 (sem gitleaks).
- Na linha 146 da `SKILL.md`, o parêntese da `docs-varredura.sh` cobre só o 1 ("FAIL") e o 64 ("pulado e dito"). O exit 2 fica de fora; as regras de "2 ⇒ abortar" da linha seguinte são da `seguranca-varredura`.
- O script nunca dá verde sem gitleaks, porque sai 2 (C2-05). O risco é o agente da release ler o 2 como "pulado".
- Sugestão: escrever "2 ⇒ abortar (NÃO CONFERIDO)" no parêntese.

Observação, sem achado. Com a lookbehind só de dígitos, um hash hex com 11 dígitos de CPF válido no meio (`abc<num>def`) também reprova (C2-05d). É falso positivo aceitável: a main sai 0 e o aceite com motivo dispensa.

Para fechar:
1. abrir o PR e guardar o recibo do CI nos 3 sistemas;
2. na release, com o OK do Roberto, fazer o push da branch de documentos (511d6fa) e da tag de arquivo, e rodar `--pode-aposentar` de novo (esperado: 0);
3. guardar o recibo do envio real do bruto;
4. A7 e A8 ficam à escolha do build.
>>>
