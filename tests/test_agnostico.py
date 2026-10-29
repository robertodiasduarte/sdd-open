"""Texto que vai para o projeto não cita ferramenta de um agente só (parâmetro P2).

O sdd-open roda em vários agentes. O que é próprio de um deles (a ferramenta de pergunta, o hook antes
de gravar, o despacho de subagente, a troca de modelo) mora no adaptador que o `init --vendors` gera,
nunca no texto de skill, template ou playbook. "Subagente" como conceito pode, porque a degradação
por vendor precisa dele; o nome da ferramenta, não.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from apoio import RAIZ, Sandbox

TERMOS = re.compile(
    r"\b(AskUserQuestion|TodoWrite|PreToolUse|PostToolUse|subagent_type)\b"
    r"|\b(Task|Agent) tool\b"
    r"|(?<![\w./-])/model\b"
)
ESCOPO = (".agents/skills", "sdd/templates", "AGENTS.md.tmpl", "sdd/playbook.md")
EXTENSOES = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".tmpl", ".txt"}
# Adaptador declarado de vendor dentro do escopo: caminho isento. Hoje nenhum — o init gera os
# adaptadores a partir de bin/lib/vendors.sh, fora do escopo. Quem acrescentar um template por vendor
# em sdd/templates/ declara o prefixo aqui.
ADAPTADORES: tuple = ()


def arquivos(raiz: Path) -> list:
    saida = []
    for item in ESCOPO:
        p = raiz / item
        if p.is_file():
            saida.append(p)
        elif p.is_dir():
            saida += [f for f in sorted(p.rglob("*")) if f.is_file() and f.suffix in EXTENSOES]
    return [f for f in saida if not str(f.relative_to(raiz)).startswith(ADAPTADORES)]


def achados(raiz: Path) -> list:
    saida = []
    for f in arquivos(raiz):
        for n, linha in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in TERMOS.finditer(linha):
                saida.append(str(f.relative_to(raiz)) + ":" + str(n) + ": " + m.group(0))
    return saida


class Agnostico(Sandbox):
    def test_pacote_sem_ferramenta_de_um_agente_so(self):
        self.assertEqual(achados(RAIZ), [])

    def test_escopo_existe_e_nao_e_vazio(self):
        # Um escopo que não acha arquivo nenhum passaria sempre.
        self.assertGreater(len(arquivos(RAIZ)), 40)
        for item in ESCOPO:
            with self.subTest(item=item):
                self.assertTrue((RAIZ / item).exists())

    def test_fixture_com_nome_de_ferramenta_reprova(self):
        self.escreve(self.tmp, ".agents/skills/sdd-x/SKILL.md",
                     "Pergunte via AskUserQuestion.\nDespache pelo Task tool.\n")
        self.escreve(self.tmp, "sdd/templates/T.md", "Troque com /model opus.\n")
        self.escreve(self.tmp, "sdd/playbook.md", "Hook PreToolUse em Write.\n")
        self.assertEqual(achados(self.tmp), [
            ".agents/skills/sdd-x/SKILL.md:1: AskUserQuestion",
            ".agents/skills/sdd-x/SKILL.md:2: Task tool",
            "sdd/templates/T.md:1: /model",
            "sdd/playbook.md:1: PreToolUse",
        ])

    def test_controle_com_conceito_passa(self):
        self.escreve(self.tmp, ".agents/skills/sdd-x/SKILL.md",
                     "Rode em conversa nova ou despache um subagente onde o vendor tiver.\n"
                     "O modelo fica em app/models/x.py e src/model/y.py; a tarefa (task) segue.\n")
        self.escreve(self.tmp, "AGENTS.md.tmpl", "Pergunte com opções, recomendada primeiro.\n")
        self.assertEqual(achados(self.tmp), [])


if __name__ == "__main__":
    unittest.main()
