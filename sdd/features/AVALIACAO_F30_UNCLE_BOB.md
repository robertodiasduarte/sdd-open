# F30 — Avaliação: as práticas de Uncle Bob e o SDD Open

> Registro da conversa de 23/11/2026 com o Roberto que originou a F30. O escopo executável está em
> `sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md`; este documento guarda o **porquê**: o levantamento, o
> mapeamento contra o Open, as 15 propostas com benefício × custo, a nota estimada e as decisões tomadas.

## 1. As práticas consagradas da obra de Robert C. Martin

| Obra | O que virou prática universal |
|---|---|
| *Agile Software Development* (2002), *Clean Architecture* (2017) | **SOLID**:<br>• S, responsabilidade única ("um só ator" que pede mudança);<br>• O, aberto/fechado (Meyer);<br>• L, substituição de Liskov;<br>• I, segregação de interfaces;<br>• D, inversão de dependência.<br>O acrônimo é de Michael Feathers |
| *Clean Code* (2008) | Nomes que revelam intenção; funções pequenas que fazem uma coisa, num nível de abstração e com poucos argumentos; separação entre comando e consulta; sem efeito colateral escondido; exceção no lugar de código de erro; não devolver nem receber `null`; comentário só para o porquê; **regra do escoteiro**; DRY; Lei de Deméter; testes **F.I.R.S.T.** |
| *Clean Code*, *The Clean Coder* (2011), *Clean Craftsmanship* (2021) | **As três leis do TDD** e o ciclo vermelho → verde → refatorar; teste como documentação executável e rede para refatorar; **teste de aceitação automatizado como definição de pronto** |
| *Clean Architecture* (2017) | **Regra de dependência** (aponta para dentro, para o domínio); framework, banco e interface são detalhes; arquitetura que "grita" o domínio; *Humble Object*; princípios de componentes (REP, CCP, CRP, ADP, SDP, SAP) |
| *The Clean Coder*, *Clean Agile* (2019), Manifesto Ágil | Saber dizer não; estimar com faixa de incerteza; prática deliberada (katas); Software Craftsmanship |

**O que é contestado:**
- o tamanho mínimo de função e o "quase nunca comente" (crítica de Ousterhout em *A Philosophy of Software Design*: "módulos rasos");
- o custo de desempenho do polimorfismo onipresente (Casey Muratori);
- os exemplos em Java envelhecidos.

**Consenso atual:** os princípios são universais; as receitas literais pedem juízo.

## 2. O que o Open já tinha em 23/11 (`origin/main` `4aa0cce`, v2.25.1)

| Princípio | Como aparece no Open | Onde |
|---|---|---|
| Teste de aceitação automatizado = pronto | Verify Gate: o aceite é um comando com código de saída, escrito no Define antes do código; fase não fecha vermelha | `sdd/bin/verify-gate.sh` |
| Teste antes do código, no nível do aceite | Ordem Define → Design → Build (ATDD; não é o TDD das três leis) | fluxo |
| Regressão protegida | Bugfix exige ≥1 cláusula `shall continue to`, que entra no gate | `sdd-define`, `fragments/EARS.md:14` |
| Teste que falha no código antigo | `dano=sim` num achado de revisão só com teste que falha na versão anterior | `sdd-build/SKILL.md:241` |
| Teste que se verifica sozinho | "Evidência, não declaração" | `sdd/bin/report-lint.py`, `fragments/EVIDENCIA.md` |
| Cobrir cada critério | Estratégia de testes por AT | `sdd-design/SKILL.md:199` |
| Componentes sem ciclo (ADP) | `design-lint.py` reprova dependência em ciclo no manifest | `sdd/bin/design-lint.py` |
| Decisão de arquitetura explícita | ADRs inline e índice `docs/adr/` | `sdd-design` §3 |
| DRY (só no harness) | Auditoria acha duplicação entre comandos, agentes e skills | `sdd-auditoria-harness` |
| Profissionalismo | `NEEDS CLARIFICATION` ⇒ exit 5; "deve funcionar" = false; publicar com 1 OK | `fragments/CLARIFY.md`, `sdd-release` |
| Definição de pronto | Campo próprio da ficha | `sdd-handoff` |

**O que não tinha:**
- SOLID, nomes, funções pequenas, separação entre comando e consulta, Deméter: nenhuma ocorrência;
- TDD estrito (vermelho antes do verde);
- regra de dependência;
- teste de mutação (a plataforma RDD usa: commit `09543a4fd`, "3 mutantes mortos");
- regra do escoteiro: o oposto está escrito, "não refatorar código adjacente" em `sdd-build/web/MODO_WEB.md:236`.

## 3. As 15 propostas, por benefício × custo

**Premissa de desenho:** só **bloqueia** o que é objetivo (teste, erro de lint ou de tipos); métrica **avisa**. Gate subjetivo trava o aluno iniciante e vira dispensa automática.

| # | Proposta | Benefício | Custo | Quadrante | Decisão 23/11 |
|---|---|---|---|---|---|
| 1 | Lint e tipos de verdade no Build, a cada tarefa (hoje só uma frase genérica em `sdd-build/SKILL.md:188`) | alto | baixo (~1 dia) | faça já | ✅ F30 S1 |
| 2 | Vermelho antes do verde (TDD no nível do aceite) | alto | baixo (~1–2 dias) | faça já | ✅ F30 S2 |
| 3 | Regras de qualidade por stack no AGENTS.md (molde `{{SEGURANCA}}`) | alto | baixo (~2 dias) | faça já | ✅ F30 S1 |
| 4 | Descobrir o linter e, sem linter, propor o padrão da stack | alto | baixo (~2 dias) | faça já | ✅ F30 S1 |
| 5 | Duplicação no diff (`jscpd`), só aviso | alto | médio (~3–4 dias) | planeje | ✅ F30 S3 |
| 6 | Mutação mínima do gate (sabotagem em cópia descartável) | alto | médio (~3 dias) | planeje | ✅ F30 S2 |
| 7 | Refatorar depois do verde, só nos arquivos tocados | alto | médio (~1–2 dias + tokens) | planeje | ✅ F30 S2 |
| 8 | Complexidade no diff (`lizard`), só aviso | alto | médio (~3 dias) | planeje | ✅ F30 S3 |
| 9 | Dimensão "manutenibilidade" na revisão adversarial | médio | baixo | talvez | ⏸️ reavaliar depois da S3 |
| 10 | Código morto e export sem uso (`knip`, `vulture`) | médio | médio | talvez | ❌ fora |
| 11 | Cobertura no diff (`diff-cover`) | médio | médio | talvez | ❌ fora (incentiva teste vazio) |
| 12 | Hook de formatação no pre-commit | médio | baixo | talvez | ❌ fora (o item 1 cobre) |
| 13 | Regra de dependência da *Clean Architecture* | médio (alto para a Turma Bravo) | alto | não agora | ⏸️ opção futura para a Turma Bravo |
| 14 | Mutação completa (Stryker, mutmut) | médio | alto | não agora | ❌ o item 6 entrega ~80% a ~10% do custo |
| 15 | Checklist SOLID como gate | baixo | médio | não agora | ❌ subjetivo; o agente faz teatro |

As estimativas de dias são julgamento, não medição.

## 4. Nota teórica de aderência (0–10, julgamento, sem medição)

| Dimensão | Peso | Hoje | Com 1–8 |
|---|---|---|---|
| Correção e testes | 25% | 7 | 9 |
| Segurança | 15% | 7,5 | 7,5 |
| Legibilidade e estilo | 15% | 4 | 8 |
| Simplicidade (complexidade, duplicação) | 15% | 4 | 7 |
| Design e arquitetura | 20% | 5,5 | 6 |
| Manutenção no longo prazo | 10% | 6 | 6,5 |
| **Ponderada** | | **≈ 5,8** | **≈ 7,5** |

- Agente sem método: 4 a 5.
- Margem de ±0,5 conforme o modelo e a stack.

**Por que não chega a 9 ou 10:**
1. design não se mede por ferramenta;
2. aviso não é bloqueio;
3. só o código novo é medido, e ele imita o vizinho;
4. os itens 13 a 15 ficaram fora.

**Caminho para 8,5 ou mais:** o item 13 como opção da Turma Bravo e o item 8 bloqueando acima do limite (custa atrito).

**Para trocar o julgamento por medição** (candidata a frente seguinte): a mesma feature em 2 ou 3 projetos de exemplo, antes e depois de cada fatia, medindo:
- violações de lint por mil linhas;
- complexidade média;
- % de duplicação;
- mutantes mortos.

A régua serve também à página `/sdd/` e às aulas: "o mesmo pedido, com e sem o método".

## 5. Decisões do Roberto (23/11)

- Fazer os **itens 1 a 8** na F30, em 3 fatias:
  - S1: 1, 3, 4;
  - S2: 2, 6, 7;
  - S3: 5, 8.
- Ordem recomendada: S1 → S2 → S3.
- Nome da frente: `f30-sdd-open-uncle-bob` (worktree e branch).
- As decisões de desenho D1 a D7 ficam para o Define, com as recomendações do ESCOPO §4.
