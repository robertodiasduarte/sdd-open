"""sdd/bin/governanca-fronteira.sh (F12, C8): prova de que o agente fresco só escreveu o arquivo permitido.

DEFINE F12 AT-005 e AT-006: novo, sobrescrito (inclusive arquivo já sujo antes), apagado, nome com acento,
arquivo novo em pasta sem nada rastreado, arquivo em pasta ignorada de sdd/, caminho por link simbólico; e
os 64 de fronteira não verificada. A sabotagem compara só o caminho (sem o sha) e a sobrescrita some.
"""
from __future__ import annotations

import os
import shutil

from apoio import BASH, RAIZ, Sandbox

SCRIPT = "sdd/bin/governanca-fronteira.sh"


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.w = self.repo("w")
        self.escreve(self.w, ".gitignore", "sdd/reviews/\n")
        self.escreve(self.w, "a.txt", "a\n")
        self.escreve(self.w, "sdd/bin/x.sh", "x\n")
        self.commit(self.w)
        self.s = self.tmp / "snaps"
        self.s.mkdir()
        self.script = str(RAIZ / SCRIPT)
        self.rel = str(self.w / "sdd/reviews/REL.md")

    def fr(self, *args: str, script: str | None = None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, script or self.script, *args], self.w)
        return rc, out + err

    def snap(self, nome: str, script: str | None = None) -> None:
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / nome), self.rel, script=script)
        self.assertEqual(rc, 0, out)

    def comparar(self, script: str | None = None) -> tuple[int, str]:
        return self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), self.rel, script=script)


class Fronteira(Base):
    def test_so_o_permitido_mudou(self):
        self.escreve(self.w, "DEFINE.md", "sujo antes\n")
        self.snap("antes")
        self.escreve(self.w, "sdd/reviews/REL.md", "relatório\n")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 0, out)
        self.assertIn("MUDOU: ", out)
        self.assertIn("RESULTADO: SÓ O PERMITIDO MUDOU", out)
        self.assertNotIn("FORA:", out)

    def test_cada_escrita_fora_do_permitido_aparece(self):
        self.escreve(self.w, "DEFINE.md", "sujo antes\n")
        self.escreve(self.w, "sdd/reviews/velho.md", "v\n")
        self.escreve(self.w, "ação.md", "x\n")
        self.snap("antes")
        self.escreve(self.w, "DEFINE.md", "sobrescrito pelo agente\n")      # já sujo antes
        (self.w / "a.txt").unlink()                                          # apagado
        self.escreve(self.w, "ação.md", "y\n")                               # nome com acento
        self.escreve(self.w, "novo/pasta/arq.md", "n\n")                     # pasta sem nada rastreado
        self.escreve(self.w, "sdd/reviews/velho.md", "mexido\n")             # pasta ignorada de sdd/
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 1, out)
        for p in ("DEFINE.md", "a.txt", "ação.md", "novo/pasta/arq.md", "sdd/reviews/velho.md"):
            with self.subTest(caminho=p):
                self.assertRegex(out, r"(?m)^FORA: .*/" + p.replace(".", r"\.") + "$")
        self.assertIn("RESULTADO: ESCRITA FORA DO PERMITIDO", out)

    def test_permitido_por_link_simbolico_casa_com_a_raiz_canonica(self):
        link = self.tmp / "link-w"
        os.symlink(str(self.w), str(link))
        rel_link = str(link / "sdd/reviews/REL.md")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "antes"), rel_link)
        self.assertEqual(rc, 0, out)
        self.escreve(self.w, "sdd/reviews/REL.md", "r\n")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "depois"), rel_link)
        self.assertEqual(rc, 0, out)
        rc, out = self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), rel_link)
        self.assertEqual(rc, 0, out)


class Uso(Base):
    def test_fronteira_nao_verificada_sai_64(self):
        self.snap("antes")
        casos = {
            "snapshot dentro do worktree": ("--snapshot", str(self.w), str(self.w / "snap.txt")),
            "raiz que é subpasta": ("--snapshot", str(self.w / "sdd"), str(self.s / "x")),
            "incluir fora do worktree": ("--snapshot", str(self.w), str(self.s / "x"), str(self.tmp / "fora.md")),
            "snapshot ausente": ("--comparar", str(self.s / "nao-existe"), str(self.s / "antes"), self.rel),
            "sem permitido": ("--comparar", str(self.s / "antes"), str(self.s / "antes")),
            "sem modo": (),
        }
        for nome, args in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.fr(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)
        self.assertFalse((self.w / "snap.txt").exists())


class Sabotagem(Base):
    def test_comparar_so_o_caminho_esconde_a_sobrescrita(self):
        texto = (RAIZ / SCRIPT).read_text(encoding="utf-8")
        alvo = 'printf \'%s\\t%s\\n\' "${h}" "${WT}/${p}"'
        self.assertIn(alvo, texto)
        sab = self.tmp / "sabotado.sh"
        sab.write_text(texto.replace(alvo, 'printf \'X\\t%s\\n\' "${WT}/${p}"'), encoding="utf-8")
        self.escreve(self.w, "DEFINE.md", "sujo antes\n")
        self.snap("antes", script=str(sab))
        self.escreve(self.w, "DEFINE.md", "sobrescrito\n")
        self.snap("depois", script=str(sab))
        rc, _ = self.comparar(script=str(sab))
        self.assertEqual(rc, 0)       # o sabotado não vê
        self.snap("antes")
        self.escreve(self.w, "DEFINE.md", "de novo\n")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 1, out)  # o real vê
