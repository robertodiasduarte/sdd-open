# GOVERNANÇA: F28_REVISORES_OPENROUTER

| Feature | Data | Padrão do projeto | DEFINE |
|---|---|---|---|
| F28_REVISORES_OPENROUTER | 2026-11-18 | uso = clientes também · multi_cnpj = não · IA grava sozinha = não · guarda = outro prazo — enquanto o repositório existir | /Users/robertoduarte/rdd-worktrees/sdd-open-f28-revisores-openrouter/sdd/features/DEFINE_F28_REVISORES_OPENROUTER.md |

Usando o padrão do projeto: uso = clientes também, multi_cnpj = não, IA grava sozinha = não, responsável técnico = Roberto Dias Duarte — sem CRC: o SDD Open não faz escrituração, guarda = outro prazo — enquanto o repositório existir: o histórico do git, as tags e os anexos das Releases são o registro do produto, públicos e permanentes.

**Gatilhos encontrados:** dinheiro / preço / pagamento — o aluno paga o OpenRouter por uso, fora de assinatura, e a skill mostra o preço do par de modelos lido do `precos.tsv` (linhas 42, 57, 75, 84 `$?`; AT-007, linha 121) · saldo / crédito — a skill classifica a conta e a chave por valores em dólar lidos da API: "sem crédito", "limite da chave esgotado: o que resta é zero", "sem limite de gasto", e decide não usar o saldo (`GET /api/v1/credits`) (linhas 79-81, 165; AT-003, linha 117, que imprime "a classe e números") · dado pessoal, pelo sentido — o diff e os documentos SDD do projeto do aluno saem do computador para um terceiro, com a regra de não guardar o dado e o lembrete da `sdd-higiene-dado` (AT-007, linha 121; linhas 201-202 `dado-de-terceiros`; AT-010, `data_collection = "deny"`). Nenhum gatilho de lançamento, nota fiscal, tributo ou folha.

**Cobertura:** 20 itens: 0 já cobertos · 1 lacunas · 18 N.A. · 1 na 2ª camada

## Lacunas

### G09 — Aritmética exata · severidade alta

**O que muda no app:** todo valor em dólar que a skill lê (o que resta do limite da chave, o limite, o uso) ou mostra (o preço do par, do `precos.tsv`) passa a ser tratado como decimal exato, com a regra escrita de quando o limite está "esgotado" (o que resta ≤ 0, inclusive negativo e fração de centavo, nunca "igual a zero") e de como o número é arredondado na tela.

**Por quê:** o DEFINE decide um estado da conta por um valor monetário — a linha 80 diz "o que resta é zero" — e o AT-003 manda imprimir "a classe e números", sem dizer como o valor é lido, comparado e mostrado. O JSON da API traz o valor como número; lido como ponto flutuante binário, a comparação "é zero" falha nos casos que importam: o que resta negativo (a conta passou do limite), o que resta de US$ 0,0004 (classificado como "aceita" e a revisão real cai em 402 depois de o aluno ouvir "está pronto"), e o preço mostrado com dízima ou arredondado de jeito diferente entre a skill e o META da revisão. Sem a regra escrita, o Build escolhe uma por acaso, o teste não pega a borda e a prova do fim da skill ("chave aceita", linha 190) pode afirmar o contrário do que acontece na primeira revisão paga. **Base legal:** o catálogo não aponta base legal para este item — o fundamento técnico vale por si.

**Requisito (EARS):** **If** a consulta da chave devolve o que resta do limite menor ou igual a US$ 0,00 depois de lido como decimal exato e truncado em centavos (zero, negativo ou fração de centavo), **then** the system **shall** recusar a classificação "aceita", dar o estado "limite da chave esgotado" com a frase do aluno e o passo, e mostrar todo valor em dólar (o que resta, o limite, o preço do par) a partir de decimal exato, nunca de ponto flutuante binário, com a regra de arredondamento escrita na skill.

**Como provar:** `prova_manual` adaptado: 1) com o servidor local no lugar do OpenRouter, devolva na consulta da chave o que resta = `0` e rode o diagnóstico com `--testar`: sai "limite da chave esgotado"; 2) repita com `-0.01`: mesmo estado; 3) repita com `0.0004` (fração de centavo): mesmo estado, nunca "aceita"; 4) repita com `1.00`: sai "aceita" (controle — sem ele, um diagnóstico que nunca dá "aceita" passaria nos passos 1 a 3); 5) confira que o preço do par mostrado antes do OK de gravar é o do `precos.tsv` com as casas da regra escrita, sem dízima. Com o Verify Gate por comando do DEFINE (`unittest`): o `prova_script` do catálogo para este item é SQL de leitura do catálogo do Postgres (`forma: catalogo`) e não se adapta — a frente não tem banco (Technical Context, linha 279). A prova por comando equivalente é um caso no teste novo da skill (o que cobre o AT-003, com o servidor HTTP local), com os 4 valores acima e a mesma inversão: o caso só passa quando 0, -0,01 e 0,0004 dão "limite da chave esgotado" **e** 1,00 dá "aceita"; e um mutante a mais na lista das Sabotagens (linha 106) — trocar a comparação "≤ 0" por "igual a 0" — tem de derrubar esse caso pelo nome.

**Decisão:** aplicada — 2026-11-18, recomendação aceita como padrão (pedido do Roberto); integrada em AT-003 e numa sabotagem do DEFINE 1.1

## Já coberto

| Item | Onde no DEFINE (linha ou AT) |
|---|---|
| — | — |

## N.A.

| Item | Motivo |
|---|---|
| G01 — Lançamento que não se apaga | A feature não grava lançamento; o único dado que ela grava é a preferência deste computador (`git config --local sdd.revisor1`/`sdd.auditor`, AT-005). |
| G02 — Partidas dobradas no banco | Sem lançamento, débito nem crédito contábil; a frente não tem banco (linha 279). |
| G03 — Fechamento de período | Sem competência nem lançamento a travar. |
| G04 — Trilha de auditoria do negócio | A feature não muda dado contábil; a escolha do revisor é preferência local, e o plano diz de onde veio cada valor (AT-005). |
| G05 — Log forense de segurança | O Open não tem login nem lê dado sensível de cliente; o envio do diff ao OpenRouter é a revisão de hoje, que esta frente não muda (Out of Scope, linha 243), e cada rodada já fica no META da revisão e na linha `review_externo` do ledger da release (AT-010 mantém o `--ledger`). |
| G06 — Prova de que o log não foi editado | Sem trilha de negócio própria a encadear; o vínculo da revisão com o código já é conferido por sha256 no `--conferir`/`--ledger` (AT-010). |
| G07 — Segregação de funções | Sem lançamento nem aprovação contábil. O análogo do processo — quem revisa não audita a própria revisão — já está no DEFINE com recusa provada: o mesmo modelo nos dois papéis continua dando 67 (AT-005, linha 89). |
| G08 — Documento-fonte imutável | Sem lançamento que aponte para documento de origem. |
| G10 — Importação idempotente | Sem importação de extrato ou nota; regravar a escolha só sobrescreve as duas chaves do `git config` (AT-005). |
| G11 — Regra com vigência e memória de cálculo | Sem regra fiscal ou de cálculo a recalcular; o preço mostrado é estimativa para a decisão do aluno, com fonte e data no `precos.tsv` (linhas 57, 185-187). |
| G12 — Conciliação com totais de controle | Sem lote financeiro a conciliar. |
| G13 — Isolamento entre clientes | N.A. por porte: multi_cnpj = não. |
| G14 — Retenção × proteção de dados | A feature não guarda dado pessoal: grava só ids de engine no `git config` local; o que sai do computador (o diff) vai só a provedor que não guarda nem treina com o dado (`data_collection = "deny"`, AT-010) e a skill lembra a `sdd-higiene-dado` antes do OK (AT-007). |
| G15 — Backup com restauração testada | Sem base de dados do sistema a restaurar; perdida a preferência local, a skill a refaz (AT-004, AT-005). |
| G17 — IA sugere, humano confirma | N.A.: ia_grava_sozinha = não; a IA do DEFINE revisa código, não grava, classifica nem sugere lançamento. |
| G18 — Registro da decisão da IA | N.A.: sem IA que grave lançamento (ia_grava_sozinha = não). |
| G19 — Taxa de correção | N.A.: sem IA que grave lançamento (ia_grava_sozinha = não). |
| G20 — Responsabilidade técnica | N.A.: sem IA que grave lançamento (ia_grava_sozinha = não). |

## 2ª camada

| Item | Por que ficou para depois |
|---|---|
| G16 — Certificado digital e segredos | Não obrigatório nesta feature. O AT-002 cobre a metade "fora do código" com recusa provada (0 ocorrências da chave de fixture na saída, nos arquivos e no `git config`; nunca por argumento; perfil reconhecido sem imprimir; chave colada no chat ⇒ revogar). Fica sem requisito: a chave mora em claro no `~/.zshrc`/`~/.bashrc` ou nas variáveis de usuário do Windows (o cofre está fora do escopo, linha 242), e nada confere se esse perfil está numa pasta sincronizada (iCloud, OneDrive) ou num repositório de dotfiles publicado — caminho comum de a chave vazar fora do projeto; o uso da chave só fica registrado indiretamente, pelo META de cada revisão. |

## Riscos aceitos

| Item | Quem | Quando | Por quê |
|---|---|---|---|
| G16 (2ª camada) | Roberto Dias Duarte (padrão aceito pelo pedido da frente) | 2026-11-18 | a chave em claro no perfil do terminal é o caminho pedido; cofre do sistema está fora do escopo; o passo a passo avisa sobre pasta sincronizada e dotfiles publicados, e o limite de gasto na chave limita o dano |

## Aplicado no DEFINE

G09 → AT-003 (decimal exato; "limite esgotado" quando o que resta, truncado em centavos, é ≤ 0; casos 0, -0,01, 0,0004 e 1,00) e a sabotagem `== 0` no lugar de `≤ 0`. Sem `prova_script`: o do catálogo é SQL e a frente não tem banco.

---

> A skill recomenda; o profissional decide e responde.
>
> No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura (`information_schema`,
> `pg_policies`, `pg_trigger`) que o SQL criou o que estes itens exigem: os itens com `prova pós-build = sim`
> no catálogo têm o que conferir no banco depois de aplicada a migration.
