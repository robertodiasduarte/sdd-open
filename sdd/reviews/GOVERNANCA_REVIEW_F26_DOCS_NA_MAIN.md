# GOVERNANÇA: F26_DOCS_NA_MAIN

| Feature | Data | Padrão do projeto | DEFINE |
|---|---|---|---|
| F26_DOCS_NA_MAIN | 2026-11-17 | uso = clientes também · multi_cnpj = não · IA grava sozinha = não · guarda = outro prazo — enquanto o repositório existir | /Users/robertoduarte/rdd-worktrees/sdd-open-f26-docs-na-main/sdd/features/DEFINE_F26_DOCS_NA_MAIN.md |

Usando o padrão do projeto: uso = clientes também, multi_cnpj = não, IA grava sozinha = não, responsável técnico = Roberto Dias Duarte — sem CRC: o SDD Open não faz escrituração, guarda = outro prazo — enquanto o repositório existir: o histórico do git, as tags e os anexos das Releases são o registro do produto, públicos e permanentes.

**Gatilhos encontrados:** dado pessoal — e-mail real em documento (linhas 27-28, Goal MUST da linha 52, AT-004, linhas 114-118: "o 1 e-mail real medido sai na migração") · dado pessoal — nome de usuário no caminho `/Users/<nome>/` de 439 documentos, que a varredura deixa passar (linhas 27-28, 52, AT-003, linhas 114-116, Out of Scope linha 174) · dado pessoal — número de 11+ dígitos, o tamanho de um CPF, que a varredura deixa passar (linhas 27, 52, AT-003, AT-004) · documentos e evidência bruta públicos e permanentes (tag `arquivo/docs-incorporar-starter` linhas 103-107; anexo da Release AT-011). Nenhum gatilho de dinheiro, saldo, lançamento, nota fiscal, tributo ou folha.

**Cobertura:** 20 itens: 0 já cobertos · 0 lacunas · 18 N.A. · 2 na 2ª camada

## Lacunas

Nenhuma. O único tema achado é dado pessoal em documento público; os itens do catálogo que tocam nele (G14, G16) são da segunda camada e, não cobertos por inteiro, ficam na 2ª camada (recomendados), não como lacuna.

## Já coberto

| Item | Onde no DEFINE (linha ou AT) |
|---|---|
| — | — |

## N.A.

| Item | Motivo |
|---|---|
| G01 — Lançamento que não se apaga | A feature não grava lançamento contábil; o que ela move são arquivos de documento num repositório git. |
| G02 — Partidas dobradas no banco | Sem lançamento nem débito e crédito; a feature não tem banco de dados. |
| G03 — Fechamento de período | Sem competência nem lançamento a travar. |
| G04 — Trilha de auditoria do negócio | A feature não muda dado contábil; quem, quando e o quê de cada mudança de documento já ficam no histórico do git. |
| G05 — Log forense de segurança | O Open não tem login nem lê dado sensível de cliente; a única exportação (anexo da Release, AT-011) é publicação do mantenedor, registrada pelo GitHub e no ledger. |
| G06 — Prova de que o log não foi editado | Sem trilha de negócio própria a encadear; a integridade dos documentos é a do git (blob por hash), que o AT-005 confere. |
| G07 — Segregação de funções | Sem lançamento nem aprovação contábil; as ações sensíveis (apagar a branch, publicar) pedem o OK do Roberto (AT-006, Constraints). |
| G08 — Documento-fonte imutável | Sem lançamento que aponte para documento de origem; a cópia da branch é conferida por blob igual (AT-005). |
| G09 — Aritmética exata | Sem valor monetário; os únicos números são contagens e tamanhos em bytes, inteiros. |
| G10 — Importação idempotente | Sem importação de extrato ou nota; a migração é um commit único conferido arquivo a arquivo (AT-005). |
| G11 — Regra com vigência e memória de cálculo | Sem regra fiscal ou de cálculo. |
| G12 — Conciliação com totais de controle | Sem lote financeiro a conciliar; a conferência da migração (AT-005) já transforma cada diferença em saída 1 com o caminho. |
| G13 — Isolamento entre clientes | N.A. por porte: multi_cnpj = não. |
| G15 — Backup com restauração testada | A feature não tem base de dados do sistema a restaurar; o que ela apaga (a branch de documentos) fica guardado pela tag de arquivo, conferida antes da remoção (AT-005, AT-006). |
| G17 — IA sugere, humano confirma | N.A.: ia_grava_sozinha = não e o DEFINE não tem IA que grave, classifique ou sugira lançamento. |
| G18 — Registro da decisão da IA | N.A.: sem IA que grave lançamento (ia_grava_sozinha = não). |
| G19 — Taxa de correção | N.A.: sem IA que grave lançamento (ia_grava_sozinha = não). |
| G20 — Responsabilidade técnica | N.A.: sem IA que grave lançamento (ia_grava_sozinha = não). |

## 2ª camada

| Item | Por que ficou para depois |
|---|---|
| G14 — Retenção × proteção de dados | Não obrigatório nesta feature. Recomendado porque o DEFINE guarda dado pessoal em registro público e permanente (guarda = enquanto o repositório existir) sem regra de eliminação: a varredura aceita número de 11+ dígitos sem distinguir CPF ou CNPJ com dígito verificador válido de id de run (AT-003, AT-004), aceita o nome de usuário em `/Users/<nome>/` (Out of Scope: não se reescreve), e o 1 e-mail real que sai da `main` na migração continua na tag de arquivo, que guarda tudo (linhas 103 e 117-118). Não há caminho escrito para um pedido de eliminação de dado pessoal de terceiro achado depois. |
| G16 — Certificado digital e segredos | Não obrigatório nesta feature. O AT-004 cobre o segredo em texto nas pastas de documento (gitleaks reprova; sem gitleaks, nunca verde) e no bruto antes do anexo (AT-011); um arquivo de certificado binário (`.pfx`, `.p12`) numa pasta de documento não tem recusa provada no DEFINE, e o bruto antigo que fica só na tag não passa pela varredura. |

## Riscos aceitos

| Item | Quem | Quando | Por quê |
|---|---|---|---|
| — | — | — | nenhum: 0 lacunas; G14 e G16 (2ª camada) aplicados, nada aceito como risco — Roberto, 2026-11-17 |

## Aplicado no DEFINE

- G16 → AT-004 (certificado com chave privada nas pastas de documento e no bruto reprova a varredura).
- G14 → AT-004 (CPF/CNPJ com dígito verificador válido reprova, com dispensa por comentário com motivo) e AT-012 (procedimento de remoção a pedido nos 3 lugares, com prova por `--padrao`).
- Decisões do Roberto em 2026-11-17, no Define.

---

> A skill recomenda; o profissional decide e responde.
>
> No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura (`information_schema`,
> `pg_policies`, `pg_trigger`) que o SQL criou o que estes itens exigem: os itens com `prova pós-build = sim`
> no catálogo têm o que conferir no banco depois de aplicada a migration.
