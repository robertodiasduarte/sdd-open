# Raio de impacto da release (0b da sdd-release) — 3 superfícies, 3 agentes de contexto novo, sobre 28caf3a

## 1. checar.sh (modos normal, --frente, --segredo, --editor) — nenhuma quebra
Consumidores conferidos: bin/sdd-open.sh:836-851 (doctor, --segredo) · sdd-iniciar-repo/SKILL.md:353 (--frente) ·
tests/test_matriz_new_session.py:26-34 · como-falar.md da checar-ambiente · guia-do-aluno.md:262-270 e :516-518 ·
sdd/config.example.yaml:114 (slot editor, lido só pela sdd-new-session) · test_conversa, test_docs, test_f21_textos ·
AGENTS.md.tmpl:10 e sdd-higiene-dado. INV-001 e INV-002 ok. Observações sem quebra: sem gh, o modo normal deixa de ser
uma linha só (o guia já prevê); sem origin, até 10 s a mais pelo gh auth status.

## 2. Guarda de Python (sdd/bin/*.sh, bin/sdd-open.sh, bin/lib/merge.sh) — 1 quebra, consertada em 1bf3b1f
QUEBRA: sdd/bin/lib/python.sh aceitava SDD_PYTHON_RESOLVIDO=python3 herdado sem conferir o PATH do filho; debaixo de
test-baseline.sh:125 (bash -c), verify-gate.sh:282 (pelo sdd-drive.sh:975) e slot.sh:218, os testes "sem python3"
saíam 127 em vez de 64 (test_decisoes_lint:131, test_fluxo:579, test_claude_adapter:147; reproduzido, inclusive pelo
test-baseline.sh). tests/apoio.py:79 copiava o ambiente inteiro. Conserto: o valor herdado só vale com
`command -v python3`; o Sandbox não herda SDD_PYTHON_RESOLVIDO nem PYTHONIOENCODING (BASELINE-vermelho-raio.log).
Pontos menores, sem quebra (pendências): o loop de deriva do doctor (bin/sdd-open.sh:826) não compara
sdd/bin/lib/python.sh; governanca-fronteira.sh:36 chama sdd_python_exigir antes do case de uso (sem Python, até --help
sai 64); docs-extract-decisions.sh sai 64 com RESULTADO: PAROU em vez de ERRO DE USO; no doctor, o aviso "dito uma
vez" pode sair repetido (dentro de $(…)). INV-001 e INV-002 ok.

## 3. inventario.sh (stdout e exits) — nenhuma quebra
A linha gh: sai depois de todo parar/falhou (inventario.sh:161); exits iguais. Consumidores: sdd-iniciar-repo/SKILL.md
(:137, :163, :173-174), tests/test_inventario.py, tests/test_f16_textos.py (blocos idênticos), workflows. Observação:
docs/pt-BR/guia-do-aluno.md:524 descreve o inventário sem citar a linha gh: (nada quebra). INV-001 e INV-002 ok.
