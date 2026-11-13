#!/usr/bin/env python3
"""sdd-kb 2.0 — normative profile. Each case copies the canonical example-kb-normativo,
applies ONE mutation and asserts the validator's exit code AND the reason it prints.

Mutating the current example (instead of keeping cloned bad fixtures) means the bad cases can
never drift away from what the skill actually ships.

Run: python3 -B -m unittest discover -s tests -p 'test_sdd_kb_*.py'
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sdd-kb"
VALIDATOR = SKILL / "scripts" / "validate_kb.py"
RULEMAP = SKILL / "scripts" / "kb_normativo.py"
EXAMPLE = SKILL / "assets" / "example-kb-normativo"
NAME = "kb_norm"


def registry(perfil):
    line = f"    perfil: {perfil}\n" if perfil else ""
    return (
        "version: \"1.0\"\ndomains:\n"
        f"  {NAME}:\n    name: teste\n    description: teste\n    path: {NAME}/\n{line}"
        "    updated: 2026-10-04\n"
    )


class NormativeKB(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sddkb-"))
        self.kb = self.tmp / NAME
        shutil.copytree(EXAMPLE, self.kb)
        self.set_perfil("normativo")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # helpers ---------------------------------------------------------------
    def set_perfil(self, perfil):
        (self.tmp / "_index.yaml").write_text(registry(perfil), encoding="utf-8")

    def edit(self, rel, old, new, count=1):
        p = self.kb / rel
        text = p.read_text(encoding="utf-8")
        self.assertIn(old, text, f"mutation anchor not found in {rel}: {old!r}")
        p.write_text(text.replace(old, new, count), encoding="utf-8")

    def regen_rule_map(self):
        subprocess.run([sys.executable, str(RULEMAP), "rule-map", str(self.kb)], check=True,
                       capture_output=True, text=True)

    def run_validator(self, *extra):
        r = subprocess.run(
            [sys.executable, str(VALIDATOR), str(self.kb), str(self.tmp / "_index.yaml"), *extra],
            capture_output=True, text=True,
        )
        return r.returncode, r.stdout + r.stderr

    def assert_fails(self, reason):
        rc, out = self.run_validator()
        self.assertEqual(rc, 2, out)
        self.assertRegex(out, reason)

    # good ------------------------------------------------------------------
    def test_example_passes_with_pending_warning(self):
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)
        self.assertIn("normativo: 3 rule(s), 4 source(s), 1 table(s), 1 case(s)", out)
        self.assertIn("WARN: index.md: PENDENTE", out)

    def test_optional_dirs_absent_still_passes(self):
        shutil.rmtree(self.kb / "tabelas")
        shutil.rmtree(self.kb / "casos")
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)
        self.assertIn("0 table(s), 0 case(s)", out)

    def test_catalogued_local_file_is_hashed(self):
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)
        cat = (self.kb / "fontes" / "CATALOGO.md").read_text(encoding="utf-8")
        self.assertIn("| registro-captura-2026-09-27.txt | ", cat)

    # AT-002 mutations a..i -------------------------------------------------
    def test_mut_a_rule_without_vigencia_de(self):
        self.edit("rules/UB12-10-CRT3.md", "  de: 2026-08-03\n", "")
        self.assert_fails(r"UB12-10-CRT3\.md: vigencia\.de missing")

    def test_mut_a_rule_with_ate_before_de(self):
        self.edit("rules/UB12-10-CRT3.md", "  ate: null", "  ate: 2026-01-01")
        self.assert_fails(r"vigencia\.ate '2026-01-01' is not a date on/after")

    def test_mut_a_rule_with_impossible_date(self):
        self.edit("rules/UB12-10-CRT3.md", "  de: 2026-08-03", "  de: 2026-13-01")
        self.assert_fails(r"UB12-10-CRT3\.md: vigencia\.de missing or not AAAA-MM-DD")

    def test_mut_b_source_not_catalogued(self):
        self.edit("rules/UB12-10-CRT3.md", "  id: NT2025002-151", "  id: NT-INEXISTENTE")
        self.assert_fails(r"fonte\.id 'NT-INEXISTENTE' not in fontes/CATALOGO\.md")

    def test_mut_k_conflict_target_unknown(self):
        self.edit("rules/ALIQ-REF-2026.md", "conflito_com: [REPORT-2026]", "conflito_com: [NAO-EXISTE]")
        self.assert_fails(r"conflito_com 'NAO-EXISTE' is neither a rule nor a catalogued source")

    def test_mut_c_sha_mismatch(self):
        f = self.kb / "fontes" / "registro-captura-2026-09-27.txt"
        f.write_text(f.read_text(encoding="utf-8") + "linha acrescentada depois da captura\n", encoding="utf-8")
        self.assert_fails(r"CAPTURA-2026-09-27: SHA-256 of fontes/registro-captura-2026-09-27\.txt differs from the catalog")

    def test_mut_o_catalogued_file_missing(self):
        (self.kb / "fontes" / "registro-captura-2026-09-27.txt").unlink()
        self.assert_fails(r"file listed in CATALOGO not found: fontes/registro-captura-2026-09-27\.txt")

    def test_mut_n_unknown_degrau(self):
        self.edit("fontes/CATALOGO.md", "| LC214-2025 | Lei Complementar nº 214, de 16 de janeiro de 2025 (compilada) | lei-complementar |",
                  "| LC214-2025 | Lei Complementar nº 214, de 16 de janeiro de 2025 (compilada) | lei |")
        self.assert_fails(r"fontes/CATALOGO\.md: LC214-2025: degrau 'lei' unknown")

    def test_mut_l_open_table_not_last(self):
        nova = self.kb / "tabelas" / "2027-01-01"
        nova.mkdir()
        (nova / "aliquotas-referencia.json").write_text(
            '{"vigencia": {"de": "2027-01-01", "ate": "2027-12-31"}, "fonte": {"id": "NT2025002-151", "localizador": "x"}, "dados": {}}',
            encoding="utf-8")
        self.edit("tabelas/2026-01-01/aliquotas-referencia.json", '"ate": "2026-12-31"', '"ate": null')
        self.assert_fails(r"tabelas/2026-01-01/aliquotas-referencia\.json: overlaps tabelas/2027-01-01")

    def test_mut_e_table_folder_not_a_date(self):
        (self.kb / "tabelas" / "2026-01-01").rename(self.kb / "tabelas" / "2026-13-01")
        self.assert_fails(r"tabelas/2026-13-01/: folder name must be the start date")

    def test_mut_k_conflict_id_is_prefix_of_cited_id(self):
        # review R1: "ALIQ-REF" dentro de "ALIQ-REF-2026" não conta como citado
        src = (self.kb / "rules" / "UB12-10-CRT3.md").read_text(encoding="utf-8")
        (self.kb / "rules" / "ALIQ-REF.md").write_text(
            src.replace("regra: UB12-10-CRT3", "regra: ALIQ-REF").replace("conflito_com: []", "conflito_com: [REPORT-2026]"),
            encoding="utf-8")
        self.regen_rule_map()
        self.assert_fails(r"rule ALIQ-REF has conflito_com but is not explained")

    def test_mut_a_ate_not_a_scalar_fails_cleanly(self):
        # review R2: lista em vigencia.ate reprova com motivo (exit 2), nunca traceback
        self.edit("rules/UB12-10-CRT3.md", "  ate: null", "  ate: [2026-12-31]")
        self.regen_rule_map()
        rc, out = self.run_validator()
        self.assertEqual(rc, 2, out)
        self.assertNotIn("Traceback", out)
        self.assertIn("vigencia.ate must be a single value, got ['2026-12-31']", out)

    def test_mut_e_table_ate_not_a_scalar_fails_cleanly(self):
        self.edit("tabelas/2026-01-01/aliquotas-referencia.json", '"ate": "2026-12-31"', '"ate": ["2026-12-31"]')
        nova = self.kb / "tabelas" / "2027-01-01"
        nova.mkdir()
        (nova / "aliquotas-referencia.json").write_text(
            '{"vigencia": {"de": "2027-01-01", "ate": null}, "fonte": {"id": "NT2025002-151", "localizador": "x"}, "dados": {}}',
            encoding="utf-8")
        rc, out = self.run_validator()
        self.assertEqual(rc, 2, out)
        self.assertNotIn("Traceback", out)

    def test_mut_m_empty_value_is_null_not_block(self):
        # review R4: `implementacao:` sem valor vira null — RULE_MAP mostra —, nunca {}
        self.edit("rules/UB12-10-CRT3.md", "implementacao: null", "implementacao:")
        self.regen_rule_map()
        rm = (self.kb / "RULE_MAP.md").read_text(encoding="utf-8")
        self.assertNotIn("{}", rm)
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)

    # review rodada 2: tipo errado dentro da gramática = FAIL nomeando o campo, nunca traceback
    def assert_fails_cleanly(self, reason):
        rc, out = self.run_validator()
        self.assertEqual(rc, 2, out)
        self.assertNotIn("Traceback", out)
        self.assertNotIn("stopped on unexpected content", out)
        self.assertRegex(out, reason)

    def test_mut_a_vigencia_scalar_with_case(self):
        self.edit("rules/UB12-10-CRT3.md", "vigencia:\n  de: 2026-08-03\n  ate: null\n", "vigencia: 2026-08-03\n")
        self.assert_fails_cleanly(r"UB12-10-CRT3\.md: vigencia must be a block")

    def test_mut_b_fonte_id_list(self):
        self.edit("rules/UB12-10-CRT3.md", "  id: NT2025002-151", "  id: [NT2025002-151, LC214-2025]")
        self.assert_fails_cleanly(r"UB12-10-CRT3\.md: fonte\.id must be a single value")

    def test_mut_b_status_list(self):
        self.edit("rules/UB12-10-CRT3.md", "status: confirmado", "status: [confirmado]")
        self.assert_fails_cleanly(r"UB12-10-CRT3\.md: status must be a single value")

    def test_mut_b_localizador_list_rule_map_survives(self):
        self.edit("rules/UB12-10-CRT3.md", "  localizador: p. 42, regra UB12-10, Observações 1 e 2", "  localizador: [p. 42, p. 45]")
        self.assert_fails_cleanly(r"fonte\.localizador must be a single value")
        r = subprocess.run([sys.executable, str(RULEMAP), "rule-map", str(self.kb)], capture_output=True, text=True)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_mut_f_case_regra_list(self):
        self.edit("casos/ub12-crt3-2026-09.json", '"regra": "UB12-10-CRT3"', '"regra": ["UB12-10-CRT3"]')
        self.assert_fails_cleanly(r"casos/ub12-crt3-2026-09\.json: regra \['UB12-10-CRT3'\] does not exist|regra None does not exist")

    def test_mut_e_table_fonte_id_list(self):
        self.edit("tabelas/2026-01-01/aliquotas-referencia.json", '"fonte": {"id": "NT2025002-151"', '"fonte": {"id": ["NT2025002-151"]')
        self.assert_fails_cleanly(r"aliquotas-referencia\.json: fonte\.id not in fontes/CATALOGO\.md")

    def test_vale_para_without_bold_is_accepted(self):
        self.edit("concepts/ano-teste-2026.md", "> **Vale para:**", "> Vale para:")
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)

    def test_mut_d_index_without_data_base(self):
        self.edit("index.md", "> **Data-base:** 2026-09-27\n", "")
        self.assert_fails(r"index\.md: Data-base missing")

    def test_mut_d_index_without_conflicts_section(self):
        self.edit("index.md", "## Conflitos entre fontes", "## Divergências")
        self.assert_fails(r"section `## Conflitos entre fontes` missing")

    def test_mut_d_index_without_notice(self):
        self.edit("index.md", "esta base não é aconselhamento tributário", "esta base é só um exemplo")
        self.assert_fails(r"responsibility notice missing")

    def test_mut_k_conflict_not_explained_in_index(self):
        self.edit("index.md", "- **UB12-10-EXC1** —", "- **Exceção 1** —")
        self.assert_fails(r"rule UB12-10-EXC1 has conflito_com but is not explained")

    def test_mut_e_table_vigencia_differs_from_folder(self):
        self.edit("tabelas/2026-01-01/aliquotas-referencia.json", '"de": "2026-01-01"', '"de": "2026-02-01"')
        self.assert_fails(r"vigencia\.de '2026-02-01' differs from the folder 2026-01-01")

    def test_mut_l_tables_overlap(self):
        nova = self.kb / "tabelas" / "2026-06-01"
        nova.mkdir()
        src = (self.kb / "tabelas" / "2026-01-01" / "aliquotas-referencia.json").read_text(encoding="utf-8")
        (nova / "aliquotas-referencia.json").write_text(
            src.replace('"de": "2026-01-01"', '"de": "2026-06-01"'), encoding="utf-8")
        self.assert_fails(r"tabelas/2026-01-01/aliquotas-referencia\.json: overlaps tabelas/2026-06-01")

    def test_mut_f_case_outside_rule_vigencia(self):
        self.edit("casos/ub12-crt3-2026-09.json", '"data_fato": "2026-09-15"', '"data_fato": "2026-07-15"')
        self.assert_fails(r"data_fato 2026-07-15 is outside the vigência of UB12-10-CRT3")

    def test_mut_f_case_with_unknown_rule(self):
        self.edit("casos/ub12-crt3-2026-09.json", '"regra": "UB12-10-CRT3"', '"regra": "UB99"')
        self.assert_fails(r"regra 'UB99' does not exist in rules/")

    def test_mut_g_rule_map_drift(self):
        self.edit("RULE_MAP.md", "| E | 1115 |", "| A | 1115 |")
        self.assert_fails(r"RULE_MAP\.md: missing or differs from rules/")

    def test_mut_g_rule_change_without_regenerating(self):
        self.edit("rules/UB12-10-CRT3.md", 'codigo: "1115"', 'codigo: "9999"')
        self.assert_fails(r"RULE_MAP\.md: missing or differs")
        self.regen_rule_map()
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)

    def test_mut_h_concept_without_vale_para(self):
        self.edit("concepts/ano-teste-2026.md", "> **Vale para:**", "> **Período:**")
        self.assert_fails(r"concepts/ano-teste-2026\.md: `> \*\*Vale para:\*\*` missing")

    def test_mut_i_confirmed_on_doctrine(self):
        self.edit("rules/ALIQ-REF-2026.md", "  id: NT2025002-151", "  id: REPORT-2026")
        self.edit("rules/ALIQ-REF-2026.md", "conflito_com: [REPORT-2026]", "conflito_com: []")
        self.regen_rule_map()
        self.assert_fails(r"status confirmado rests on a doutrina source \(REPORT-2026\)")

    def test_mut_m_frontmatter_outside_grammar(self):
        self.edit("rules/UB12-10-CRT3.md", "status: confirmado", "    status confirmado")
        self.assert_fails(r"UB12-10-CRT3\.md:\d+: frontmatter line not understood")

    # AT-004 --strict -------------------------------------------------------
    def test_strict_refuses_pending(self):
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 2, out)
        self.assertIn("--strict refuses an unreviewed normative KB", out)

    def test_strict_refuses_pending_in_any_case(self):
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO", "> **Revisado por:** Pendente de revisão")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 2, out)

    def test_strict_refuses_pending_outside_reviewer_line(self):
        # review r3 A1 (HIGH): pendência em outra linha, sem "Revisado por:", não pode passar no --strict
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)",
                  "> **Situação:** PENDENTE DE REVISÃO")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 2, out)
        self.assertIn("Revisado por:**` missing", out)
        self.assertIn("--strict refuses an unreviewed normative KB", out)

    def test_strict_refuses_empty_reviewer_followed_by_heading(self):
        # review rodada 4 A1: "Revisado por:" vazio não pega a linha seguinte como assinatura
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)",
                  "> **Revisado por:**\n\n## Notas")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 2, out)
        self.assertIn("Revisado por:**` missing", out)

    def test_pending_inside_fenced_block_is_not_pending(self):
        # review rodada 4 R2: exemplo do molde dentro de bloco cercado não é o estado da base
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)",
                  "> **Revisado por:** Contadora Fictícia, CRC 0000")
        self.edit("index.md", "## O que este domínio NÃO cobre",
                  "## Como marcar pendência\n\n```text\n> **Revisado por:** PENDENTE DE REVISÃO\n```\n\n## O que este domínio NÃO cobre")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 0, out)

    def test_strict_accepts_independent_reviewer(self):
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)",
                  "> **Revisado por:** Maria Fictícia — revisora independente, CRC 0000")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 0, out)

    def test_mut_m_duplicate_key(self):
        # review r3 R1@kimi: chave repetida reprova nomeando a linha, nunca "a última vence"
        self.edit("rules/UB12-10-CRT3.md", "status: confirmado", "status: confirmado\nstatus: premissa")
        self.assert_fails(r"UB12-10-CRT3\.md:\d+: key 'status' repeated")

    def test_mut_m_duplicate_block(self):
        self.edit("rules/UB12-10-CRT3.md", "status: confirmado", "status: confirmado\nvigencia:\n  de: 2027-01-01")
        self.assert_fails(r"UB12-10-CRT3\.md:\d+: key 'vigencia' repeated")

    def test_strict_accepts_signed_base_mentioning_pending_items(self):
        # review r3 R2: "pendentes" depois da assinatura não é base pendente
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)",
                  "> **Revisado por:** Contadora Fictícia, CRC 0000 (revisão parcial — itens pendentes anotados no index)")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("PENDENTE", out)

    def test_rule_with_bom_is_read(self):
        # review r3 R3: regra salva como "UTF-8 com BOM" continua legível
        p = self.kb / "rules" / "UB12-10-CRT3.md"
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes())
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)

    def test_pipe_in_localizador_keeps_rule_map_columns(self):
        # review r3 R1: "|" no localizador não pode virar coluna extra no RULE_MAP
        self.edit("rules/UB12-10-CRT3.md", "  localizador: p. 42, regra UB12-10, Observações 1 e 2",
                  "  localizador: art. 5º, § 1º | inciso II")
        self.regen_rule_map()
        linha = next(l for l in (self.kb / "RULE_MAP.md").read_text(encoding="utf-8").splitlines() if l.startswith("| UB12-10-CRT3 "))
        self.assertEqual(len(re.findall(r"(?<!\\)\|", linha)), 10, linha)
        self.assertNotIn("\\\\|", linha)

    def test_strict_passes_reviewed(self):
        self.edit("index.md", "> **Revisado por:** PENDENTE DE REVISÃO", "> **Revisado por:** Contador Fictício, CRC 0000")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("WARN: index.md: PENDENTE", out)

    # perfil ----------------------------------------------------------------
    def test_mut_j_perfil_with_trailing_comment_stays_normativo(self):
        # review A1 (HIGH): comentário no fim da linha não pode rebaixar o domínio para geral
        (self.tmp / "_index.yaml").write_text(
            registry("normativo").replace("perfil: normativo", "perfil: normativo  # legislação"), encoding="utf-8")
        rc, out = self.run_validator("--strict")
        self.assertEqual(rc, 2, out)
        self.assertIn("--strict refuses an unreviewed normative KB", out)

    def test_mut_f_case_source_not_catalogued(self):
        # review A2: a fonte do gabarito também é rastreável
        self.edit("casos/ub12-crt3-2026-09.json", '"fonte": {"id": "NT2025002-151"', '"fonte": {"id": "FONTE-INEXISTENTE"')
        self.assert_fails(r"casos/ub12-crt3-2026-09\.json: fonte\.id 'FONTE-INEXISTENTE' not in fontes/CATALOGO\.md")

    def test_mut_j_unknown_perfil_fails(self):
        self.set_perfil("fiscal")
        self.assert_fails(r"perfil 'fiscal' for 'kb_norm' — use `normativo` or `geral`")

    # AT-003 / AT-005 geral --------------------------------------------------
    def test_geral_skips_normative_checks_and_warns(self):
        self.set_perfil(None)
        self.edit("index.md", "> **Data-base:** 2026-09-27\n", "")
        rc, out = self.run_validator()
        self.assertEqual(rc, 0, out)
        self.assertRegex(out, r"WARN: parece normativo \(")
        self.assertNotIn("normativo:", out.split("PASS:")[-1])

    def test_geral_warning_does_not_hide_failures(self):
        self.set_perfil("geral")
        (self.kb / "quick-reference.md").write_text("x\n" * 101, encoding="utf-8")
        rc, out = self.run_validator()
        self.assertEqual(rc, 2, out)
        self.assertIn("quick-reference.md has 101 lines", out)


class GeralNonUtf8(unittest.TestCase):
    def test_latin1_reference_file_does_not_crash_geral(self):
        # review R3: arquivo Latin-1 em reference/ (que a 1.0.1 não abria) não vira traceback
        tmp = Path(tempfile.mkdtemp(prefix="sddkb-geral-"))
        try:
            kb = tmp / NAME
            shutil.copytree(SKILL / "assets" / "example-kb", kb)
            (kb / "reference").mkdir()
            (kb / "reference" / "tabela-antiga.md").write_bytes("al\xedquota antiga\n".encode("latin-1"))
            (tmp / "_index.yaml").write_text(registry(None), encoding="utf-8")
            r = subprocess.run([sys.executable, str(VALIDATOR), str(kb), str(tmp / "_index.yaml")],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn("Traceback", r.stderr)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class GeralNormativeMarkers(unittest.TestCase):
    """Avaliador ciclo 1: markers are tokens — "LC nº 123", "EC nº 132", "a NT da SEFAZ" count;
    a word or code that only contains them ("EC2", "ECONOMIA", "NTFS") does not."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sddkb-marcadores-"))
        self.kb = self.tmp / NAME
        shutil.copytree(SKILL / "assets" / "example-kb", self.kb)
        (self.tmp / "_index.yaml").write_text(registry(None), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_with_line(self, line):
        concept = self.kb / "concepts" / "regime-de-competencia.md"
        concept.write_text(concept.read_text(encoding="utf-8") + "\n" + line + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(VALIDATOR), str(self.kb), str(self.tmp / "_index.yaml")],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_lc_ec_aliquota_without_digit_right_after_warns(self):
        rc, out = self.run_with_line(
            "Conforme a LC nº 123/2006 e a EC nº 132/2023, a alíquota efetiva muda por faixa.")
        self.assertEqual(rc, 0, out)
        self.assertIn("WARN: parece normativo", out)
        self.assertIn("PASS: KB lint passed", out)

    def test_nt_art_lc_vigencia_warns(self):
        rc, out = self.run_with_line("Ver a NT da SEFAZ, o art. 5º da LC e a vigência da regra.")
        self.assertEqual(rc, 0, out)
        self.assertIn("WARN: parece normativo", out)
        self.assertIn("PASS: KB lint passed", out)

    def test_marker_inside_other_word_or_code_does_not_count(self):
        # 3 would-be markers (EC, NT, LC) so a prefix-only regex (\bEC, \bNT, \bLC) crosses the threshold
        rc, out = self.run_with_line("A instância EC2 mostra o relatório de ECONOMIA num monitor LCD, disco NTFS.")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("WARN", out)


class RuleMapCheckArgOrder(unittest.TestCase):
    """Avaliador ciclo 1: `rule-map --check <dir>` (flag first, like validate_kb --strict) exits 0."""

    def run_rulemap(self, *args):
        r = subprocess.run([sys.executable, str(RULEMAP), *args], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_check_before_dir(self):
        rc, out = self.run_rulemap("rule-map", "--check", str(EXAMPLE))
        self.assertEqual(rc, 0, out)
        self.assertIn("PASS: RULE_MAP.md matches rules/", out)

    def test_check_after_dir(self):
        rc, out = self.run_rulemap("rule-map", str(EXAMPLE), "--check")
        self.assertEqual(rc, 0, out)
        self.assertIn("PASS: RULE_MAP.md matches rules/", out)

    def test_check_without_dir_is_usage_error(self):
        rc, out = self.run_rulemap("rule-map", "--check")
        self.assertEqual(rc, 64, out)


class GeralUntouched(unittest.TestCase):
    def test_v1_example_still_passes_without_warning(self):
        r = subprocess.run([sys.executable, str(VALIDATOR), str(SKILL / "assets" / "example-kb")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("WARN", r.stdout)
        self.assertTrue(re.match(r"PASS: KB lint passed \(1 concept\(s\), 1 pattern\(s\)\)\n$", r.stdout), r.stdout)


if __name__ == "__main__":
    unittest.main()
