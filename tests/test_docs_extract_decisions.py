"""sdd/bin/docs-extract-decisions.sh (F12, C4): índice de ADR a partir dos títulos de decisão dos DESIGNs.

DEFINE F12 AT-018: um ID por bloco (<STEM>#D<N>, número repetido com sufixo b), DESIGN sem bloco vai para
Órfãos com o motivo, conservação extraídos + órfãos = lidos; a sabotagem que perde um órfão sai 2.
"""
from __future__ import annotations

import shutil

from apoio import BASH, RAIZ, Sandbox

SCRIPT = "sdd/bin/docs-extract-decisions.sh"

DESIGN_A = """# DESIGN: A

| Attribute | Value |
|---|---|
| **Feature** | PEDIDOS |
| **Date** | 2026-11-01 |

## Key Decisions

### Decision 1: Fila por pedido

| **Status** | Accepted | · | **Date** | 2026-11-02 |

**Consequences:** mais simples.

### Decision 2: Correção da decisão anterior

texto

### Decision 2: Repetida

```text
### Decision 9: dentro de cerca não conta
```

## File Manifest
"""

DESIGN_SEM_NUMERO = "# DESIGN: B\n\n## Key Decisions\n\n### Decision: sem número\n\ntexto\n"


class Extrator(Sandbox):
    def setUp(self):
        super().setUp()
        self.p = self.tmp / "proj"
        self.escreve(self.p, "sdd/features/DESIGN_PEDIDOS.md", DESIGN_A)
        self.escreve(self.p, "sdd/features/DESIGN_SEM_BLOCO.md", DESIGN_SEM_NUMERO)
        self.escreve(self.p, "sdd/features/DEFINE_PEDIDOS.md", "não é DESIGN\n")

    def roda_extrator(self, *args: str, script: str | None = None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, script or str(RAIZ / SCRIPT), *args], self.tmp)
        return rc, out + err

    def test_indice_com_ids_sufixo_orfaos_e_conservacao(self):
        rc, out = self.roda_extrator("--root", str(self.p))
        self.assertEqual(rc, 0, out)
        self.assertIn("lidos=2 extraidos=1 orfaos=1 decisoes=3", out)
        idx = (self.p / "docs/adr/index.md").read_text(encoding="utf-8")
        self.assertIn("| `PEDIDOS#D1` | Fila por pedido | PEDIDOS | 2026-11-02 | Accepted | ✓ |", idx)
        self.assertIn("`PEDIDOS#D2`", idx)
        self.assertIn("`PEDIDOS#D2b`", idx)
        self.assertIn("⚠️ revisar", idx)
        self.assertNotIn("PEDIDOS#D9", idx)
        self.assertIn("[DESIGN_SEM_BLOCO.md](../../sdd/features/DESIGN_SEM_BLOCO.md) | bloco sem número", idx)
        self.assertIn("extraídos (1) + órfãos (1) = lidos (2) ✓", idx)

    def test_out_e_projeto_sem_design(self):
        vazio = self.tmp / "vazio"
        vazio.mkdir()
        rc, out = self.roda_extrator("--root", str(vazio), "--out", str(self.tmp / "i.md"))
        self.assertEqual(rc, 0, out)
        self.assertIn("lidos=0", out)
        self.assertIn("_Nenhum._", (self.tmp / "i.md").read_text(encoding="utf-8"))

    def test_uso_sai_64(self):
        for args in (("--root",), ("--x",), ("--root", str(self.tmp / "nao-existe"))):
            with self.subTest(args=args):
                rc, _ = self.roda_extrator(*args)
                self.assertEqual(rc, 64)

    def test_sabotagem_que_perde_um_orfao_viola_a_conservacao(self):
        texto = (RAIZ / SCRIPT).read_text(encoding="utf-8")
        alvo = "else { norf++;"
        self.assertIn(alvo, texto)
        sab = self.tmp / "sab.sh"
        sab.write_text(texto.replace(alvo, "else { perdido++;"), encoding="utf-8")
        rc, out = self.roda_extrator("--root", str(self.p), script=str(sab))
        self.assertEqual(rc, 2, out)
        self.assertIn("conservação violada", out)
        self.assertFalse((self.p / "docs/adr/index.md").exists())
