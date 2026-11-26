<<<AVALIACAO
FEATURE: F30_QUALIDADE_CODIGO · fatia S3 (AT-017 a AT-023) · ciclo 1 · HEAD 814a3a5
VEREDITO: PASS

Ressalva: NÃO rodei a suíte inteira (proibido na chamada). Do AT-023 ficou sem prova minha só o `discover -p 'test_*.py'`. Este PASS depende do verify-gate completo com exit 0, em log próprio; não vi um GATE_S3*.log na pasta de evidências.

Ambiente: lizard 1.26.1 e jscpd 5.4.3 reais, /bin/bash, repositórios git temporários. `ARVORE_IGUAL` = shasum de todos os arquivos mais a lista de caminhos, fora o `.git`.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-017 | Frente com função de complexidade 15 e cópia de bloco; depois, sem commit, complexidade 41, 1201 linhas e 110 parâmetros num nome com espaço e acento | Os dois achados com arquivo, linhas, valor e limite; exit 0; árvore igual | `src/nova.py:1-31` complexidade 15 (limite 10); `copia.py:1-11` repete `notas.py:1-11`; exit 0; ARVORE_IGUAL nas duas; TMPDIR limpo | PASS |
| AT-018 | Ambas ausentes; só uma; cada ferramenta com exit 3, saída vazia, lixo, kill -9, 127 e CSV curto; 8 JSONs malformados | `não medido` com causa e comando; a outra medida; exit 0; nada instalado | Exit 0 em todas. Ausente traz `pip install lizard` / `npm install -g jscpd`. Falhas com causa. Nenhum "0 achados" nem "nenhum aviso" em métrica não medida (exceções: L2 e L6) | PASS |
| AT-019 | Dívida antiga intocada; diff só README; diff vazio; rename puro; 1 linha mudada; linha apagada; função nova no mesmo arquivo da antiga; par antigo intocado e depois tocado de um lado; função pequena nova | Só o que tem linha no diff; sem código, o texto exato; função sem achado conta como medida | Tudo conforme; `nenhum aviso (1 função medida no diff)` | PASS |
| AT-020 | Sem config; valores vazios; 15 e 14; CRLF; aspas; 13 valores inválidos, mais x nas outras 3 chaves; fronteiras 10/11, 60/61, 5/6 e 58 tokens | Usa o valor, ou o padrão; inválido ⇒ 64 com chave e conserto | Conforme; só 11, 61 e 6 acusam; 64 com `qualidade.<chave> … não é um inteiro maior que zero: <valor>` (texto do conserto: L3) | PASS |
| AT-021 | Clone com o BUILD_REPORT real da S2 (o resto verde), variando config e seção | Mapa sem seção, vazia ou só em cerca ⇒ 1 com conserto em 1 linha; sem mapa ⇒ aviso e 0; achado nunca reprova | 1/1/1, única violação `[qualidade]`; sem config ou sem mapa: 0 com aviso; complexidade 99 na seção: 0; "não medido": 0 | PASS |
| AT-022 | grep da ordem na SKILL, moldes, config, EVIDENCIA e cli-conventions; starter gerado de verdade; test_f30_textos_s3 | Chamada antes do relatório; seção nos 2 moldes; 4 limites; web e starter sem `sdd/bin/` | Chamada no 5b (linha 250), antes do `### 6` (293); 2 moldes; 10/60/5/50; `sdd/bin` = 0 em MODO_WEB, na referência e nos 16 arquivos do sdd-build do starter; 6 testes OK | PASS |
| AT-023 | check-versions; publish-gate CI sobre `git archive HEAD`; grep F29; report-lint antigo × novo em todos os BUILD_REPORTs; 10 módulos f30 (bash 3.2, py 3.9); 5 módulos alterados | Tudo verde; relatórios antigos não mudam | check-versions VERDE; gate GREEN exit 0; todos os BUILD_REPORTs com o mesmo exit antes e depois e 0 violações `qualidade`; 10/10 módulos OK; test_f30_metricas 40 OK com as ferramentas reais (sem elas, 1 skip); 5/5 OK. Suíte inteira: não rodada por mim | PASS (com a ressalva) |

Bordas aprovadas: nome com crase, quebra de linha ou `-x.py` não abre seção; `json.py`/`lizard.py` plantados no projeto não são importados; `.jscpd.json`, `package.json` e `.gitignore` do projeto não mudam a medida; SIGTERM sai 143 e apaga a cópia temporária; opção, base ou pasta inválida sai 64.

ACHADOS (nenhum bloqueante)

M1 (MED): arquivo do diff que o jscpd pula vira `nenhum aviso` e `RESULTADO: NADA ACHADO`. Arquivo em Latin-1 é pulado calado pelo jscpd. Se outro arquivo do diff foi lido, a duplicação real some; a única pista é "1 … lidos, de 2", e o RESULTADO não vira NÃO MEDIDO (com arquivo acima de 5 MB vira).
 Repro: seção "arquivo latin1 duplicado" do AVAL-S3-bordas.log. Em main, `src/notas.py` (função de 59 tokens). Na frente, `src/lat.py` = `printf '# a\347\343o\n'` + cópia do bloco, e `src/ok.py` distinto com mais de 50 tokens. Rodar com as ferramentas reais ⇒ `nenhum aviso (1 arquivo do diff lidos, de 2)` · `NADA ACHADO`. A mesma cópia em UTF-8 acusa (AT-017).
 Conserto sugerido: dizer quantos não foram lidos e que podem ser curtos ou ilegíveis; ou transcodificar a cópia para UTF-8.

L1 (LOW): nome de arquivo com aspas derruba a complexidade inteira. `src/as"pas,x.py` no diff ⇒ `lizard devolveu saída que não entendi (linha com 13 colunas)` para todos. Falha honesta.

L2 (LOW): lizard que sai 0 com saída vazia dá `não medido: nenhuma função nova ou alterada encontrada no diff`. É "não medido", mas a causa é errada se a ferramenta quebrou. Repro: lizard falso `exit 0`. O lizard real também sai vazio para arquivo sem função que ele reconheça, inclusive `def seis(a,b,c,d,e,f): return 1` numa linha só (função invisível, limite da ferramenta; AVAL-S3-AT-020b.log).

L3 (LOW): a seta do exit 64 por limite inválido fala da base: `→ corrija (a base se passa por --base REF)…`. A chave está na linha acima. Repro: `qualidade:\n  max_linhas: 0`.

L4 (LOW): `qualidade: {max_complexidade: abc}` (forma inline) é ignorado calado: usa o padrão, sem 64, e o report-lint não o vê como mapa. Igual ao leitor dos outros mapas.

L5 (LOW): `---`, comentário HTML ou só subtítulos contam como seção "não vazia". Repro: `## Qualidade (avisos)\n\n---\n\n## Z` com mapa ⇒ exit 0.

L6 (LOW): comentários no código suprimem a medida. `#lizard forgives` tira a função (de 2 funções novas, a seção diz `nenhum aviso (1 função medida no diff)`); `jscpd:ignore-start` dá `não medido: jscpd não leu…`. O DESIGN trata só o config do projeto; vale decidir ou documentar.

L7 (LOW): TMPDIR dentro do projeto mede o próprio `nucleo.py`. Repro: `mkdir tmp; TMPDIR=$PWD/tmp bash sdd/bin/metricas-diff.sh` com 1 função nova ⇒ "32 funções medidas no diff".

L8 (LOW): arquivo de código sem permissão de leitura ⇒ exit 64 `[Errno 13]` + "ERRO DE USO", com o caminho absoluto; a chamada não tem erro de uso. Repro: `chmod 000 src/nova.py`.

L9 (cosmético): "1 arquivo do diff lidos" (concordância).
>>>
