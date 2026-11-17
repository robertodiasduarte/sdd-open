# DRIVE_REPORT: F25_SKILLS_DUPLICADAS

O teste final passou e os relatórios estão prontos. Nada foi publicado. Rodadas vermelhas: 2 de 3.

| Campo | Valor |
|---|---|
| Motivo | gate-verde |
| DEFINE | `sdd/features/DEFINE_F25_SKILLS_DUPLICADAS.md` |
| Commit inicial | `017f09a39deb` |
| Teste final | `T=$(mktemp -d) && git archive HEAD \| tar -x -C $T && cd $T/tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest test_f25_skills_duplicadas test_checar test_bash32 test_matriz_new_session test_f16_textos test_f17_textos test_gerar_starter && cd $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` |

Rodadas vermelhas: 2 de 3.

## Testes finais

| # | Rodada | Commit | Exit | Log |
|---|---|---|---|---|
| 1 | 1 | `4fa1115c0d90` | 2 | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/DRIVE-gate-r1.log` |
| 2 | 2 | `43c90ebc8775` | 2 | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/DRIVE-gate-r2.log` |
| 3 | 3 | `2fbc1532393e` | 0 | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/DRIVE-gate-r3.log` |

## Commits desde o início

- 2fbc153 feat(f25): test_decisoes_lint.py — contador de perguntas de decisão do pacote 34 → 35 (Exemplo 3 da sdd-checar-ambiente) (diff do protótipo do DESIGN)
- 43c90eb feat(f25): MANIFEST.txt — duplicadas.sh e test_f25_skills_duplicadas.py no pacote, LM-037 (diff do protótipo do DESIGN)
- 4a1bde7 feat(f25): test_matriz_new_session.py — exceção estreita do reconhecedor de origem no test_sem_referencia_ao_starter, exatamente as 2 linhas de padrão do awk (diff do protótipo do DESIGN)
- 0a94543 feat(f25): test_f16_textos.py — sdd-checar-ambiente fixada em 1.6.0 (diff do protótipo do DESIGN)
- cba55ad feat(f25): test_bash32.py — os .sh da sdd-checar-ambiente (checar.sh e duplicadas.sh) no piso bash 3.2 (diff do protótipo do DESIGN)
- ade95c7 feat(f25): test_checar.py — HOME temporário fora de self.tmp no Base, sem CODEX_HOME, CLAUDE_CONFIG_DIR e XDG_STATE_HOME herdados (diff do protótipo do DESIGN)
- 41e4638 feat(f25): test_f25_skills_duplicadas.py — AT-001 a AT-010 com HOME, projeto e CODEX_HOME temporários, npx e agentes falsos, CLI de verdade opcional (copiado do protótipo do DESIGN)
- 4c5d968 feat(f25): como-falar.md da sdd-checar-ambiente — glossário (skill duplicada, global, do projeto, lixeira), Status da etapa 3, Exemplo 3 com a pergunta [D1 · não se desfaz] (diff do protótipo do DESIGN)
- 1e7983f feat(f25): SKILL.md da sdd-checar-ambiente — v1.6.0, etapa 3 Limpar, exceção única à regra Somente leitura, seção 7 (diff do protótipo do DESIGN)
- cf3a0ea feat(f25): checar.sh — modos --duplicadas e --limpar, balde ⚠️ ARRUMAR_DUP e seção 7 (diff do protótipo do DESIGN)
- aaf846b feat(f25): duplicadas.sh — biblioteca de skills duplicadas (varredura, plano, assinatura, limpeza protegida), copiada do protótipo do DESIGN

## Teste final alterado

Nenhuma troca.

## Decidi sozinho

Nada.

Nada foi publicado: publicar é decisão da pessoa, pela sdd-release.
