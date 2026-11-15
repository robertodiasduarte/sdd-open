"""F16W2, AT-004: a renderização do init (cabeçalho sdd-open:generated) nos casos de borda, byte a byte.

O init foi reescrito com builtins do bash para lançar menos processos (no Git Bash do Windows cada um custa 10 a 20
ms). A regra não podia mudar: estas 24 entradas cobrem BOM, a declaração de encoding do PEP 263 (linha 1 ou 2), a
declaração <?xml ?> (em 1 ou 2 linhas, com e sem conteúdo depois), o @charset do CSS, byte NUL, .json, binário,
extensão em maiúscula, CRLF, arquivo sem fim de linha e vazio. A saída esperada é a da versão de antes (v2.16.0),
conferida igual à de agora quando a reescrita entrou. As funções saem do próprio bin/sdd-open.sh (sem rodar o main).
"""
from __future__ import annotations

import os

from apoio import BASH, RAIZ, Sandbox, caminho_bash

CASOS = [
    ('L.PY', b'x=1\n', False,
     b'# sdd-open:generated - fonte: .agents/skills/sdd-zz/L.PY\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nx=1\n'),
    ('a.py', b"# -*- coding: latin-1 -*-\nprint('ol\xe1')\n", False,
     b"# -*- coding: latin-1 -*-\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/a.py\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nprint('ol\xe1')\n"),
    ('b.py', b'#!/usr/bin/env python3\n# coding: utf-8\nprint(1)\n', True,
     b'#!/usr/bin/env python3\n# coding: utf-8\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/b.py\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nprint(1)\n'),
    ('bom.md', b'\xef\xbb\xbf# t\xc3\xadtulo\ntexto\n', False,
     b'\xef\xbb\xbf<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/bom.md -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\n# t\xc3\xadtulo\ntexto\n'),
    ('bom.py', b'\xef\xbb\xbf# coding: utf-8\nx=1\n', False,
     b'\xef\xbb\xbf# coding: utf-8\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/bom.py\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nx=1\n'),
    ('c.py', b'\n# coding=ascii\nx=1\n', False,
     b'\n# coding=ascii\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/c.py\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nx=1\n'),
    ('d.xml', b'<?xml version="1.0"?>\n<r/>\n', False,
     b'<?xml version="1.0"?>\n<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/d.xml -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\n<r/>\n'),
    ('e.svg', b'<?xml version="1.0"?><svg/>\n', False,
     b'<?xml version="1.0"?><svg/>\n'),
    ('f.xml', b'<?xml version="1.0"\n encoding="UTF-8"?>\n<r/>\n', False,
     b'<?xml version="1.0"\n encoding="UTF-8"?>\n<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/f.xml -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\n<r/>\n'),
    ('g.css', b'@charset "UTF-8";\nbody{}\n', False,
     b'@charset "UTF-8";\n/* sdd-open:generated - fonte: .agents/skills/sdd-zz/g.css */\n/* sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync */\nbody{}\n'),
    ('h.css', b'@charset "UTF-8"; /* x\n*/ body{}\n', False,
     b'@charset "UTF-8"; /* x\n*/ body{}\n'),
    ('i.md', b'a\x00b\n', False,
     b'a\x00b\n'),
    ('j.json', b'{"a": 1}\n', False,
     b'{"a": 1}\n'),
    ('k.sh', b'#!/bin/zsh\r\necho oi\r\n', True,
     b'#!/bin/zsh\r\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/k.sh\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\necho oi\r\n'),
    ('m.yaml', b'---\na: 1\n', False,
     b'# sdd-open:generated - fonte: .agents/skills/sdd-zz/m.yaml\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\n---\na: 1\n'),
    ('n.txt', b'sem fim de linha', False,
     b'<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/n.txt -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\nsem fim de linha'),
    ('o.md', b'', False,
     b'<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/o.md -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\n'),
    ('p.ts', b'// x\nlet a=1\n', False,
     b'// sdd-open:generated - fonte: .agents/skills/sdd-zz/p.ts\n// sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\n// x\nlet a=1\n'),
    ('q.sql', b'select 1;\n', False,
     b'-- sdd-open:generated - fonte: .agents/skills/sdd-zz/q.sql\n-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nselect 1;\n'),
    ('r', b'#!/bin/sh\necho\n', True,
     b'#!/bin/sh\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/r\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\necho\n'),
    ('s.rb', b'# encoding: utf-8\nputs 1\n', False,
     b'# encoding: utf-8\n# sdd-open:generated - fonte: .agents/skills/sdd-zz/s.rb\n# sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync\nputs 1\n'),
    ('t.png', b'\x89PNG\r\n\x1a\n', False,
     b'\x89PNG\r\n\x1a\n'),
    ('u.md', b'\r\n# crlf\r\n', False,
     b'<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/u.md -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\n\r\n# crlf\r\n'),
    ('v nome com espaÃ§o.md', b'x\n', False,
     b'<!-- sdd-open:generated - fonte: .agents/skills/sdd-zz/v?nome?com?espa????o.md -->\n<!-- sdd-open:generated - sync reescreve este arquivo; edite a fonte e rode sync -->\nx\n'),
]

RENDER = r'''SRC="$1"; FX="$2"; OUT="$3"
eval "$(sed -n "/^MARCA=/p" "$SRC")"
eval "$(sed -n '/^# ── cabeçalho GENERATED/,/^mesmo_bit_x()/p' "$SRC")"
for f in "$FX"/*; do n="${f##*/}"; renderizar_gerado "$f" sdd-zz "$n" > "$OUT/$n"; done
'''


class Render(Sandbox):
    def test_os_casos_de_borda_saem_byte_a_byte_como_antes(self):
        fx = self.tmp / "fx"
        fx.mkdir()
        out = self.tmp / "out"
        out.mkdir()
        for nome, entrada, _x, _saida in CASOS:
            (fx / nome).write_bytes(entrada)
        script = self.escreve(self.tmp, "render.sh", RENDER)
        rc, so, se = self.roda([BASH, caminho_bash(script), caminho_bash(RAIZ / "bin/sdd-open.sh"), caminho_bash(fx),
                                caminho_bash(out)], self.tmp)
        self.assertEqual(rc, 0, so + se)
        for nome, _entrada, _x, saida in CASOS:
            with self.subTest(arquivo=nome):
                self.assertEqual((out / nome).read_bytes(), saida)
