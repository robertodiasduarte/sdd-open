#!/usr/bin/env python3
"""Lint estrutural do relatório Markdown. Offline; biblioteca padrão; não prova fontes."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re

SECTIONS = (
    "Metadata", "Objetivo e limites", "Fontes e evidências", "Achados classificados",
    "Inventário funcional", "Jornadas e estados", "Regras e permissões",
    "Dados e integrações", "Qualidade e operação", "Cobertura da investigação",
    "Lacunas e contradições", "Insumos para a nova solução", "Estado e retomada",
    "Histórico de revisões",
)
DIMENSIONS = {
    "modulos", "jornadas", "regras_estados", "permissoes", "dados_documentos",
    "integracoes", "qualidade_operacao",
}
CLASSES = {"observado", "documentado", "informado", "inferido", "nao_verificado"}
TYPES = {
    "site_oficial", "documentacao_oficial", "video_demonstracao", "material_usuario",
    "declaracao_usuario", "sessao_autorizada", "fonte_secundaria",
}
COVERAGE = {"coberto", "parcial", "nao_verificado", "fora_do_escopo"}
EMPTY = {"", "—", "-", "N/A", "nao disponivel"}
MAX_BYTES = 2 * 1024 * 1024  # Limite local do lint; não é limite do domínio ou da plataforma.


def cells(line: str) -> list[str]:
    return [cell.strip().replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip()[1:-1])]


def table(section: str, header: list[str], errors: list[str], code: str) -> list[list[str]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if not lines or not lines[0].endswith("|") or cells(lines[0]) != header:
        errors.append(f"CABECALHO_{code}")
        return []
    if len(lines) < 2 or not all(re.fullmatch(r":?-{3,}:?", v) for v in cells(lines[1])):
        errors.append(f"SEPARADOR_{code}")
        return []
    rows = []
    for line in lines[2:]:
        values = cells(line) if line.endswith("|") else []
        if len(values) != len(header) or not all(values):
            errors.append(f"LINHA_{code}")
        else:
            rows.append(values)
    return rows


def references(raw: str, errors: list[str]) -> list[str]:
    if raw in EMPTY:
        return []
    refs = [v.strip() for v in raw.split(",")]
    if not all(re.fullmatch(r"E\d{3,}", v) for v in refs) or len(refs) != len(set(refs)):
        errors.append("FORMATO_REFERENCIAS")
    return refs


def iso_day(value: str) -> bool:
    try:
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)) and date.fromisoformat(value) is not None
    except ValueError:
        return False


def validate_text(text: str) -> dict:
    errors: list[str] = []
    headings = list(re.finditer(r"^## (.+)$", text, re.M))
    names = [m.group(1).strip() for m in headings]
    sections: dict[str, str] = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[match.group(1).strip()] = text[match.end():end].strip()
    positions = []
    for name in SECTIONS:
        if names.count(name) != 1:
            errors.append("SECAO_AUSENTE_OU_DUPLICADA:" + name)
        else:
            positions.append(names.index(name))
            if not sections.get(name):
                errors.append("SECAO_VAZIA:" + name)
    if positions != sorted(positions):
        errors.append("ORDEM_SECOES")
    if not text.startswith("# ENGENHARIA REVERSA:"):
        errors.append("TITULO")
    if re.search(r"\{[A-Z][A-Z0-9_]*\}", text):
        errors.append("PLACEHOLDER_NAO_PREENCHIDO")

    meta_rows = table(sections.get("Metadata", ""), ["Campo", "Valor"], errors, "METADATA")
    meta = dict(meta_rows)
    if len(meta) != len(meta_rows):
        errors.append("METADATA_DUPLICADA")
    for key in ("SaaS", "URL principal", "Data da coleta", "Plano e versão", "Modo de investigação", "Status da investigação", "Nova solução"):
        if not meta.get(key):
            errors.append("METADATA_AUSENTE:" + key)
    status = meta.get("Status da investigação")
    if status not in {"parcial", "concluida_no_escopo"}:
        errors.append("STATUS_INVESTIGACAO")
    if not iso_day(meta.get("Data da coleta", "")):
        errors.append("DATA_COLETA")

    ev_rows = table(sections.get("Fontes e evidências", ""),
                    ["ID", "Tipo", "Origem", "Localizador", "Coleta", "Versão ou data da fonte", "Acesso", "Limites"], errors, "EVIDENCIAS")
    evidence: dict[str, list[str]] = {}
    for row in ev_rows:
        identifier, kind, origin, locator, collected, _, access, _ = row
        if not re.fullmatch(r"E\d{3,}", identifier):
            errors.append("ID_EVIDENCIA")
        if identifier in evidence:
            errors.append("ID_EVIDENCIA_DUPLICADO")
        evidence[identifier] = row
        if kind not in TYPES:
            errors.append("TIPO_EVIDENCIA")
        if access not in {"disponivel", "indisponivel"}:
            errors.append("ACESSO_EVIDENCIA")
        if origin in EMPTY or locator in EMPTY:
            errors.append("FONTE_SEM_LOCALIZADOR")
        if not iso_day(collected):
            errors.append("DATA_EVIDENCIA")

    findings = table(sections.get("Achados classificados", ""),
                     ["ID", "Dimensão", "Afirmação", "Classe", "Evidências", "Condições e limites"], errors, "ACHADOS")
    seen_findings = set()
    for identifier, dimension, assertion, category, raw_refs, limits in findings:
        if not re.fullmatch(r"F\d{3,}", identifier):
            errors.append("ID_ACHADO")
        if identifier in seen_findings:
            errors.append("ID_ACHADO_DUPLICADO")
        seen_findings.add(identifier)
        if dimension not in DIMENSIONS:
            errors.append("DIMENSAO_ACHADO")
        if category not in CLASSES:
            errors.append("CLASSE_ACHADO")
        if assertion in EMPTY or limits in EMPTY:
            errors.append("ACHADO_SEM_CONTEUDO_OU_LIMITES")
        refs = references(raw_refs, errors)
        if any(ref not in evidence for ref in refs):
            errors.append("REFERENCIA_INEXISTENTE")
        if category != "nao_verificado":
            if not refs:
                errors.append("ACHADO_SEM_EVIDENCIA")
            if any(evidence.get(ref, [None] * 8)[6] != "disponivel" for ref in refs):
                errors.append("SUPORTE_INDISPONIVEL")
        if category == "observado" and not any(
            ref in evidence and evidence[ref][1] == "sessao_autorizada"
            and evidence[ref][6] == "disponivel" for ref in refs
        ):
            errors.append("OBSERVADO_SEM_SESSAO")

    cov_rows = table(sections.get("Cobertura da investigação", ""),
                     ["Dimensão", "Cobertura", "Evidências", "Limites e justificativa"], errors, "COBERTURA")
    covered_dimensions = [row[0] for row in cov_rows]
    if set(covered_dimensions) != DIMENSIONS or len(covered_dimensions) != len(DIMENSIONS):
        errors.append("DIMENSOES_COBERTURA")
    for _, coverage, raw_refs, limits in cov_rows:
        if coverage not in COVERAGE:
            errors.append("VALOR_COBERTURA")
        refs = references(raw_refs, errors)
        if any(ref not in evidence for ref in refs):
            errors.append("REFERENCIA_COBERTURA_INEXISTENTE")
        if coverage in {"coberto", "parcial"} and not any(
            ref in evidence and evidence[ref][6] == "disponivel" for ref in refs
        ):
            errors.append("COBERTURA_SEM_SUPORTE")
        if limits in EMPTY:
            errors.append("COBERTURA_SEM_JUSTIFICATIVA")
    if status == "concluida_no_escopo" and (
        not any(row[1] == "coberto" for row in cov_rows)
        or any(row[1] not in {"coberto", "fora_do_escopo"} for row in cov_rows)
    ):
        errors.append("CONCLUSAO_COM_LACUNAS_OU_ESCOPO_VAZIO")

    state_rows = table(sections.get("Estado e retomada", ""), ["Campo", "Valor"], errors, "ESTADO")
    state = dict(state_rows)
    if len(state) != len(state_rows):
        errors.append("CAMPO_ESTADO_DUPLICADO")
    for key in ("Etapa atual", "Status da etapa", "Documentos", "Dependencias", "Decisoes registradas", "Pergunta pendente", "Proxima acao"):
        if not state.get(key):
            errors.append("ESTADO_AUSENTE:" + key)
    if state.get("Etapa atual") not in {"engenharia_reversa", "brainstorm", "define", "encerrado"}:
        errors.append("ETAPA_INVALIDA")
    if state.get("Status da etapa") not in {"em_andamento", "aguardando_usuario", "aguardando_dependencia", "needs_clarification", "concluida"}:
        errors.append("STATUS_ETAPA_INVALIDO")
    if state.get("Etapa atual") == "encerrado" and state.get("Status da etapa") != "concluida":
        errors.append("ENCERRAMENTO_INCONSISTENTE")
    return {"ok": not errors, "errors": sorted(set(errors)),
            "evidence_count": len(evidence), "finding_count": len(findings),
            "scope": "lint_estrutural_apenas; nao verifica veracidade, autorizacao ou gates SDD"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.report.stat().st_size > MAX_BYTES:
            result = {"ok": False, "errors": ["ARQUIVO_EXCEDE_LIMITE_LOCAL"]}
        else:
            result = validate_text(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        result = {"ok": False, "errors": ["ARQUIVO_INACESSIVEL_OU_NAO_UTF8"]}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
