"""Padrões de PII brasileira em scripts/publish-gate-patterns.txt (camada pública do G2).

As amostras positivas são CONCATENADAS em tempo de execução: escritas inteiras aqui, fariam o
próprio publish-gate reprovar a pasta tests/. Os padrões são aplicados com `grep -E -i`, as mesmas
flags do G2, e um teste roda o publish-gate.sh inteiro sobre uma árvore com um arquivo plantado.
"""
from __future__ import annotations

import shutil
import unittest

from apoio import BASH, RAIZ, Sandbox

PADROES = RAIZ / "scripts/publish-gate-patterns.txt"
GATE = RAIZ / "scripts/publish-gate.sh"

POSITIVOS = {
    "CPF com pontuação": "cliente " + "123.456" + ".789-09" + " pagou",
    "CNPJ com pontuação": "empresa " + "12.345" + ".678/0001-95",
    "celular com DDD entre parênteses": "ligar (11) 9" + "1234-5678",
    "celular com DDD sem parênteses": "ligar 11 9" + "1234-5678",
    "fixo com DDD": "fixo (21) 3" + "456-7890",
}

NEGATIVOS = [
    "data 2026-10-29 e 29/10/2026",
    "carimbo 2026-10-29T12:30:00Z",
    "versão v2.10.0 e 1.024 caracteres",
    "exits 0/2/3/4/5/64 e LM-004",
    "commit 80d7887 e sha 3f2a9c1",
    "intervalo 8080-8090",
    "AT-001 a AT-026",
]


def padroes() -> list[str]:
    linhas = PADROES.read_text(encoding="utf-8").splitlines()
    return [l for l in linhas if l.strip() and not l.startswith("#")]


class Padroes(Sandbox):
    def casa(self, texto: str) -> list[str]:
        """Padrões que casam com o texto, aplicados com as flags do G2."""
        alvo = self.escreve(self.tmp, "amostra.txt", texto + "\n")
        hits = []
        for rx in padroes():
            rc, _out, err = self.roda(["grep", "-InE", "-i", "--", rx, alvo], self.tmp)
            self.assertLessEqual(rc, 1, "padrão inválido para o grep: /" + rx + "/ " + err)
            if rc == 0:
                hits.append(rx)
        return hits

    def test_positivos_casam(self):
        for nome, texto in POSITIVOS.items():
            with self.subTest(caso=nome):
                self.assertTrue(self.casa(texto), nome + " não foi pego por nenhum padrão")

    def test_negativos_nao_casam(self):
        for texto in NEGATIVOS:
            with self.subTest(texto=texto):
                self.assertEqual(self.casa(texto), [], "falso positivo bloquearia a publicação")

    def test_todo_padrao_e_ere_valida(self):
        for rx in padroes():
            with self.subTest(padrao=rx):
                rc, _out, err = self.roda(["grep", "-E", "-i", "--", rx, PADROES], self.tmp)
                self.assertLessEqual(rc, 1, err)


@unittest.skipUnless(shutil.which("gitleaks"), "gitleaks ausente: o G1 do publish-gate sai antes do G2 (no CI ele está instalado)")
class GateInteiro(Sandbox):
    def arvore(self, plantado: str | None) -> tuple[int, str]:
        arv = self.tmp / "arvore"
        self.copia("scripts/publish-gate-patterns.txt", arv)
        self.escreve(arv, "README.md", "Projeto de exemplo.\n")
        if plantado:
            self.escreve(arv, "docs/planilha.md", plantado + "\n")
        env = dict(self.env, PUBLISH_GATE_MODE="ci")
        rc, out, err = self.roda([BASH, GATE, arv], self.tmp, env=env)
        return rc, out + err

    def test_cpf_plantado_bloqueia_no_g2(self):
        rc, out = self.arvore(POSITIVOS["CPF com pontuação"])
        self.assertNotEqual(rc, 0, out)
        self.assertIn("pattern matched:", out)
        self.assertIn("docs/planilha.md", out)

    def test_sem_plantio_o_g2_nao_acusa(self):
        rc, out = self.arvore(None)
        self.assertNotIn("pattern matched:", out)
        self.assertIn("no forbidden pattern matched", out)


if __name__ == "__main__":
    unittest.main()
