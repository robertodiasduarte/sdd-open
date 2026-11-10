"""Casos sintéticos: consistência de evidências e limites do relatório, não do SaaS."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

# ROOT é a pasta da skill. Este arquivo roda em dois lugares sem mudar um byte: dentro da pasta da skill
# (tests/ ao lado de scripts/) e na suíte do pacote sdd-open (tests/ na raiz, skill em .agents/skills/).
ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "scripts" / "validate_reverse.py").is_file():
    ROOT = ROOT / ".agents" / "skills" / "sdd-engenharia-reversa-saas"
# Sem isto, rodar a suíte sem -B grava scripts/__pycache__/ dentro da pasta da skill, que o init e o zip levariam.
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("reverse_lint", ROOT / "scripts" / "validate_reverse.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SOURCE = "| E001 | documentacao_oficial | Manual Exemplo | seção tarefas | 2026-11-09 | nao disponivel | disponivel | Não testado em conta. |"
FINDING = "| F001 | modulos | O manual descreve tarefas. | documentado | E001 | Declaração documental; funcionamento não executado. |"


def sample() -> str:
    return """# ENGENHARIA REVERSA: Exemplo

## Metadata
| Campo | Valor |
|---|---|
| SaaS | Exemplo |
| URL principal | nao disponivel |
| Data da coleta | 2026-11-09 |
| Plano e versão | nao disponivel |
| Modo de investigação | Documentação fornecida; sem conta. |
| Status da investigação | parcial |
| Nova solução | a definir |

## Objetivo e limites
Investigar tarefas, sem inferir execução ou arquitetura.

## Fontes e evidências
| ID | Tipo | Origem | Localizador | Coleta | Versão ou data da fonte | Acesso | Limites |
|---|---|---|---|---|---|---|---|
""" + SOURCE + """

## Achados classificados
| ID | Dimensão | Afirmação | Classe | Evidências | Condições e limites |
|---|---|---|---|---|---|
""" + FINDING + """

## Inventário funcional
Tarefas, segundo F001; demais módulos não verificados.

## Jornadas e estados
Não verificados.

## Regras e permissões
Não verificadas.

## Dados e integrações
Não verificados.

## Qualidade e operação
Não verificada.

## Cobertura da investigação
| Dimensão | Cobertura | Evidências | Limites e justificativa |
|---|---|---|---|
| modulos | parcial | E001 | Apenas tarefas descritas no manual. |
| jornadas | nao_verificado | — | Sem demonstração. |
| regras_estados | nao_verificado | — | Sem documentação. |
| permissoes | nao_verificado | — | Sem documentação. |
| dados_documentos | nao_verificado | — | Sem documentação. |
| integracoes | nao_verificado | — | Sem documentação. |
| qualidade_operacao | nao_verificado | — | Sem medição ou documentação. |

## Lacunas e contradições
O comportamento de execução não foi observado.

## Insumos para a nova solução
Explorar a necessidade de tarefas com o usuário; F001 não aprova escopo.

## Estado e retomada
| Campo | Valor |
|---|---|
| Etapa atual | brainstorm |
| Status da etapa | aguardando_usuario |
| Documentos | ENGENHARIA_REVERSA_EXEMPLO.md: parcial |
| Dependencias | Resolver SDD Brainstorm antes da fase. |
| Decisoes registradas | Nenhuma decisão de produto. |
| Pergunta pendente | Quem usará a nova solução? |
| Proxima acao | Aguardar resposta; não assumir público. |

## Histórico de revisões
| Revisão | Data | Mudança e motivo |
|---|---|---|
| 1 | 2026-11-09 | Caso sintético inicial. |
"""


class ReportTests(unittest.TestCase):
    def reject(self, text, code):
        result = module.validate_text(text)
        self.assertFalse(result["ok"])
        self.assertIn(code, result["errors"])

    def test_partial_documented_report_is_valid(self):
        self.assertTrue(module.validate_text(sample())["ok"])

    def test_observed_requires_session_evidence(self):
        self.reject(sample().replace("| documentado | E001 |", "| observado | E001 |"), "OBSERVADO_SEM_SESSAO")

    def test_observed_with_session_is_structurally_valid(self):
        text = sample().replace("| documentacao_oficial |", "| sessao_autorizada |")
        text = text.replace("| documentado | E001 |", "| observado | E001 |")
        self.assertTrue(module.validate_text(text)["ok"])

    def test_unknown_reference_rejected(self):
        self.reject(sample().replace("| documentado | E001 |", "| documentado | E999 |"), "REFERENCIA_INEXISTENTE")

    def test_inaccessible_source_cannot_support_documented_claim(self):
        self.reject(sample().replace("| disponivel |", "| indisponivel |"), "SUPORTE_INDISPONIVEL")

    def test_inference_needs_support(self):
        self.reject(sample().replace("| documentado | E001 |", "| inferido | — |"), "ACHADO_SEM_EVIDENCIA")

    def test_no_sources_is_valid_when_explicitly_unknown(self):
        text = sample().replace(SOURCE, "Nenhuma fonte acessível.")
        text = text.replace(FINDING, "| F001 | modulos | Existência de tarefas ainda não confirmada. | nao_verificado | — | Sem fonte acessível. |")
        text = text.replace("| modulos | parcial | E001 |", "| modulos | nao_verificado | — |")
        self.assertTrue(module.validate_text(text)["ok"])

    def test_duplicate_evidence_rejected(self):
        self.reject(sample().replace(SOURCE, SOURCE + "\n" + SOURCE), "ID_EVIDENCIA_DUPLICADO")

    def test_duplicate_findings_rejected(self):
        self.reject(sample().replace(FINDING, FINDING + "\n" + FINDING), "ID_ACHADO_DUPLICADO")

    def test_missing_dimension_rejected(self):
        self.reject(sample().replace("| jornadas | nao_verificado | — | Sem demonstração. |", ""), "DIMENSOES_COBERTURA")

    def test_conclusion_with_gaps_rejected(self):
        self.reject(sample().replace("| Status da investigação | parcial |", "| Status da investigação | concluida_no_escopo |"), "CONCLUSAO_COM_LACUNAS_OU_ESCOPO_VAZIO")

    def test_conclusion_with_narrow_explicit_scope_is_valid(self):
        text = sample().replace("| Status da investigação | parcial |", "| Status da investigação | concluida_no_escopo |")
        text = text.replace("| modulos | parcial |", "| modulos | coberto |").replace("| nao_verificado |", "| fora_do_escopo |")
        self.assertTrue(module.validate_text(text)["ok"])

    def test_unfilled_asset_rejected(self):
        self.reject((ROOT / "assets" / "ENGENHARIA_REVERSA_TEMPLATE.md").read_text(encoding="utf-8"), "PLACEHOLDER_NAO_PREENCHIDO")

    def test_truncated_table_rejected(self):
        self.reject(sample().replace(FINDING, "| F001 | modulos |"), "LINHA_ACHADOS")

    def test_escaped_pipe_supported(self):
        text = sample().replace("O manual descreve tarefas.", r"O manual descreve tarefas \| calendário.")
        self.assertTrue(module.validate_text(text)["ok"])

    def test_duplicated_required_section_rejected(self):
        self.reject(sample() + "\n## Metadata\nDuplicação.\n", "SECAO_AUSENTE_OU_DUPLICADA:Metadata")

    def test_cli_works_outside_bundle_and_does_not_write_report(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "relatorio.md"
            report.write_text(sample(), encoding="utf-8")
            before = report.read_bytes()
            process = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_reverse.py"), str(report)], cwd=directory, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0)
            self.assertTrue(json.loads(process.stdout)["ok"])
            self.assertEqual(before, report.read_bytes())

    def test_cli_missing_file_returns_safe_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_reverse.py"), str(Path(directory) / "missing.md")], capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads(process.stdout)["errors"], ["ARQUIVO_INACESSIVEL_OU_NAO_UTF8"])
            self.assertNotIn("Traceback", process.stderr)


if __name__ == "__main__":
    unittest.main()
