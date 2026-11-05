"""Contrato do sdd/bin/prompt-drift-scan.sh (DEFINE F13 AT-008 a AT-015).

Exit 0 LIMPO · 2 DRIFT (ou self-test falhou) · 64 uso. O script nunca conclui LIMPO sem ter lido: caminho
inexistente, pasta, arquivo ilegível, entrada vazia ou de terminal, slot inválido e grep com saída 2 saem 64.
"""
from __future__ import annotations

import os
import pty
import shutil
import stat
import subprocess
import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/prompt-drift-scan.sh"
PADRAO = 'prompts:\n  wrapper_pattern: "systemPrompt:"\n'


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.p = self.tmp / "proj"
        (self.p / "sdd").mkdir(parents=True)
        self.slot(PADRAO)

    def slot(self, texto: str):
        (self.p / "sdd/config.yaml").write_bytes(texto.encode("utf-8"))

    def com_texto(self, caminho, texto, cwd=None, env=None):
        r = subprocess.run([BASH, str(SCRIPT), "--conteudo", str(caminho)], cwd=str(cwd or self.p), env=env or self.env,
                           input=texto, capture_output=True, encoding="utf-8", timeout=60)
        return r.returncode, r.stdout + r.stderr

    def em_disco(self, *caminhos, cwd=None):
        rc, out, err = self.roda([BASH, SCRIPT, *caminhos], cwd or self.p)
        return rc, out + err

    def arquivo(self, rel, texto="x = 1\n"):
        f = self.p / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(texto, encoding="utf-8")
        return f


class SinaisDeConteudo(Base):
    def test_antes_de_gravar_o_arquivo_nao_existe(self):
        for texto, sinal in (("client.messages.create(model=m)\n", "chamada direta ao SDK"),
                             ("client.chat.completions.create(model=m)\n", "chamada direta ao SDK"),
                             ("client.responses.create(model=m)\n", "chamada direta ao SDK"),
                             ("model.generateContent(x)\n", "chamada direta ao SDK"),
                             ("model.generate_content(x)\n", "chamada direta ao SDK"),
                             ("await model.generateContentStream(x)\n", "chamada direta ao SDK"),
                             ("client.models.generate_content_stream(x)\n", "chamada direta ao SDK"),
                             ("model.generate_content_async(x)\n", "chamada direta ao SDK"),
                             ("client.messages.stream(x)\n", "chamada direta ao SDK"),
                             ("client.responses.stream(x)\n", "chamada direta ao SDK"),
                             ("client.messages.stream(\n  model=m)\n", "chamada direta ao SDK"),
                             ('const system = "You are"\n', "system com texto fixo"),
                             ('system := "x"\n', "system com texto fixo"),
                             ('"system" => "x"\n', "system com texto fixo"),
                             ("msg['role'] = 'system'\n", "role de sistema"),
                             ('  - role: "system"\n', "role de sistema"),
                             ("- role: 'system'\n", "role de sistema"),
                             ("  - role: system\n", "role de sistema"),
                             ("role: system  # o prompt\n", "role de sistema"),
                             ("{role: system, content: x}\n", "role de sistema"),
                             ('obj.role = "system"\n', "role de sistema"),
                             ('- system: "x"\n', "system com texto fixo"),
                             ('  - "system": "x"\n', "system com texto fixo"),
                             ('self.system = "x"\n', "system com texto fixo"),
                             ('config.system: "x"\n', "system com texto fixo"),
                             ('"role" => "system"\n', "role de sistema"),
                             ('run({ system: "x" })\n', "system com texto fixo"),
                             ('run(system: `x`)\n', "system com texto fixo"),
                             ('{ "system": "x" }\n', "system com texto fixo"),
                             ('{ "system" : "x" }\n', "system com texto fixo"),
                             ("system: 'x'\n", "system com texto fixo"),
                             ('ask(system="You are")\n', "system com texto fixo"),
                             ('ask(system=f"You are {x}")\n', "system com texto fixo"),
                             ('{ role: "system", content: x }\n', "role de sistema"),
                             ('{"role": "system"}\n', "role de sistema")):
            with self.subTest(texto=texto):
                rc, out = self.com_texto("src/novo.ts", texto)
                self.assertEqual(rc, 2, out)
                self.assertIn("src/novo.ts :: " + sinal, out)
                self.assertIn("RESULTADO: DRIFT", out)
                self.assertFalse((self.p / "src").exists(), "o scan criou arquivo")
                self.assertRegex(out.splitlines()[-1], r"^→ ")

    def test_system_no_fim_de_um_nome_maior_nao_dispara(self):
        for texto in ('package-ecosystem: "npm"\n', 'filesystem: "ext4"\n', "operating_system: 'linux'\n",
                      '"file_system": "x"\n', 'file_role: "system"\n', 'role: "user"\n', "system = obter()\n",
                      'file system: "ext4"\n', '"operating system": "linux"\n', 'role: "system:admin"\n',
                      "role: system:admin\n", "role: system_admin\n", "role: systems\n", "role = system\n",
                      "- role: user\n", "- name: system\n", '- file system: "ext4"\n', '- package-ecosystem: "npm"\n',
                      "self.system = obter()\n", 'self.system_x = "y"\n', 'my.file_system = "x"\n', 'a.b_role = "system"\n',
                      "messages.createdAt = agora\n", "messages.create_index(x)\n", "responses.createdAt\n",
                      "generateContentHash(x)\n", "generate_content_type = 1\n", "regenerateContent(x)\n",
                      "messages.stream().filter(x)\n", "responses.stream().map(x)\n",
                      "my_generate_content(x)\n", "submessages.create(x)\n", "messages.streaming = True\n",
                      "generateContentStreamed(x)\n", "generate_content_async_pool(x)\n", 'os.system("ls")\n', "a == 'x'\n"):
            with self.subTest(texto=texto):
                rc, out = self.com_texto("src/a.yml", texto)
                self.assertEqual(rc, 0, out)
                self.assertIn("RESULTADO: LIMPO", out)


class SinaisDeCaminho(Base):
    def test_pasta_prompts_em_qualquer_profundidade(self):
        for caminho in ("prompts/a.txt", "x/prompts/v1/a.ts", "./x/prompts/a.ts", "x/Prompts/a.txt", "PROMPTS/a.txt"):
            with self.subTest(caminho=caminho):
                rc, out = self.com_texto(caminho, "qualquer texto\n")
                self.assertEqual(rc, 2, out)
                self.assertIn("pasta prompts/", out)

    def test_nome_com_prompt_em_qualquer_caixa_exceto_md(self):
        for caminho in ("src/prompt.py", "src/Agent_PROMPT.ts"):
            with self.subTest(caminho=caminho):
                rc, out = self.com_texto(caminho, "x = 1\n")
                self.assertEqual(rc, 2, out)
                self.assertIn("nome com prompt", out)
        self.assertEqual(self.com_texto("docs/prompt-guia.md", "x\n")[0], 0)
        self.assertEqual(self.com_texto("docs/prompts/guia.md", "x\n")[0], 2, "template em prompts/ conta")

    def test_pasta_prompts_vence_a_exclusao_por_nome_e_a_pasta_de_teste_vence_prompts(self):
        for caminho in ("src/prompts/test_plan.txt", "prompts/a.spec.txt"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.com_texto(caminho, "x\n")[0], 2)
        self.assertEqual(self.com_texto("tests/prompts/a.txt", "x\n")[0], 0)

    def test_arquivo_chamado_prompts_sem_ser_pasta_nao_e_sinal_de_pasta(self):
        rc, out = self.com_texto("src/prompts", "x = 1\n")
        self.assertEqual(rc, 2)
        self.assertIn("nome com prompt", out)
        self.assertNotIn("pasta prompts/", out)

    def test_absoluto_dentro_da_raiz(self):
        rc, out = self.com_texto(self.p / "src/prompts/a.txt", "x\n")
        self.assertEqual(rc, 2, out)
        self.assertIn("pasta prompts/", out)

    def test_absoluto_por_link_simbolico_para_o_projeto_nao_vira_limpo(self):
        link = self.tmp / "link"
        os.symlink(str(self.p), str(link))
        rc, out = self.com_texto(link / "src/prompts/a.txt", "x\n", cwd=link)
        self.assertEqual(rc, 2, out)
        self.assertIn("pasta prompts/", out)
        # A exclusão de teste também vê a raiz física.
        rc, out = self.com_texto(link / "tests/a.py", 'client.messages.create(x)\n', cwd=link)
        self.assertEqual(rc, 0, out)

    def test_pasta_tests_acima_da_raiz_nao_exclui(self):
        fora = self.tmp / "tests" / "proj"
        (fora / "sdd").mkdir(parents=True)
        (fora / "sdd/config.yaml").write_text(PADRAO, encoding="utf-8")
        rc, out = self.com_texto("src/a.ts", 'client.messages.create(x)\n', cwd=fora)
        self.assertEqual(rc, 2, out)
        # Absoluto dentro dessa raiz: idem.
        rc, out = self.com_texto(fora / "src/a.ts", 'client.messages.create(x)\n', cwd=fora)
        self.assertEqual(rc, 2, out)

    def test_absoluto_fora_da_raiz_ve_prompts_e_nao_ve_tests(self):
        outro = self.tmp / "tests" / "prompts"
        outro.mkdir(parents=True)
        rc, out = self.com_texto(outro / "a.txt", "x\n")
        self.assertEqual(rc, 2, out)
        self.assertIn("pasta prompts/", out)


class Wrapper(Base):
    def test_slot_seguido_de_texto_fixo(self):
        for abre in ("`", "'", '"'):
            with self.subTest(aspa=abre):
                rc, out = self.com_texto("src/a.ts", "ask({ systemPrompt: %sx%s })\n" % (abre, abre))
                self.assertEqual(rc, 2, out)
                self.assertIn("prompts.wrapper_pattern", out)
                self.assertNotIn("vazio", out)

    def test_slot_com_contrabarra_dobrada_em_aspas_duplas(self):
        self.slot('prompts:\n  wrapper_pattern: "callLLM\\\\("\n')
        self.assertEqual(self.com_texto("src/a.ts", 'callLLM("x")\n')[0], 2)
        self.assertEqual(self.com_texto("src/a.ts", "callLLM(SYSTEM_X)\n")[0], 0)

    def test_slot_em_aspas_simples_e_sem_aspas(self):
        self.slot("prompts:\n  wrapper_pattern: 'callLLM\\('\n")
        self.assertEqual(self.com_texto("src/a.ts", 'callLLM("x")\n')[0], 2)
        self.slot("prompts:\n  wrapper_pattern: systemPrompt:  # comentário\n")
        self.assertEqual(self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")[0], 2)

    def test_alternativa_vale_inteira(self):
        self.slot('prompts:\n  wrapper_pattern: "foo|bar:"\n')
        self.assertEqual(self.com_texto("src/a.ts", 'foo "x"\n')[0], 2)
        self.assertEqual(self.com_texto("src/a.ts", 'bar: "x"\n')[0], 2)
        rc, out = self.com_texto("src/a.ts", "foo SYSTEM_X\n")
        self.assertEqual(rc, 0, "a alternativa sem parênteses dispararia em todo foo: " + out)

    def test_comentario_depois_da_aspa_e_crlf_nao_entram_no_valor(self):
        self.slot('prompts:\n  wrapper_pattern: "systemPrompt:"  # comentário\n')
        self.assertEqual(self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")[0], 2)
        self.slot('prompts:\r\n  wrapper_pattern: "systemPrompt:"\r\n')
        self.assertEqual(self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")[0], 2)

    def test_ancora_e_tag_no_cabecalho_do_bloco(self):
        for cabecalho in ("prompts: &llm", "prompts: !!map", "prompts: &llm  # comentário"):
            with self.subTest(cabecalho=cabecalho):
                self.slot(cabecalho + '\n  wrapper_pattern: "systemPrompt:"\n')
                self.assertEqual(self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")[0], 2)

    def test_chaves_entre_aspas(self):
        self.slot('"prompts":\n  "wrapper_pattern": "systemPrompt:"\n')
        self.assertEqual(self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")[0], 2)

    def test_chave_de_outro_bloco_nao_conta(self):
        self.slot('outro:\n  wrapper_pattern: "systemPrompt:"\nprompts:\n  builder_skill: "x"\n')
        rc, out = self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")
        self.assertEqual(rc, 0, out)
        self.assertIn("wrapper_pattern vazio", out)

    def test_raiz_ignora_git_dir_herdado_de_um_hook(self):
        outro = self.tmp / "outro"
        outro.mkdir()
        self.git(outro, "init", "-q")
        (outro / "sdd").mkdir()
        (outro / "sdd/config.yaml").write_text('prompts:\n  wrapper_pattern: "OUTRO:"\n', encoding="utf-8")
        self.git(self.p, "init", "-q")
        env = dict(self.env, GIT_DIR=str(outro / ".git"), GIT_WORK_TREE=str(outro))
        rc, out = self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n", env=env)
        self.assertEqual(rc, 2, "leu o config do outro repositório: " + out)


class Exclusoes(Base):
    def test_arquivo_de_teste_de_qualquer_linguagem(self):
        for caminho in ("src/a.test.ts", "src/a.spec.js", "src/a_test.go", "src/a_spec.rb", "src/test_a.py", "src/FooTest.java",
                        "src/FooTests.cs", "tests/a.py", "test/a.rb", "spec/a.rb", "src/__tests__/a.js", "tests/prompts/a.txt"):
            with self.subTest(caminho=caminho):
                rc, out = self.com_texto(caminho, 'client.messages.create(x)\nsystemPrompt: `x`\n')
                self.assertEqual(rc, 0, out)
                self.assertIn("RESULTADO: LIMPO", out)

    def test_identificador_importado(self):
        for texto in ("ask({ systemPrompt: SYSTEM_X })\n",):
            self.assertEqual(self.com_texto("src/a.ts", texto)[0], 0)

    def test_md_fora_de_prompts_so_cita(self):
        rc, out = self.com_texto("docs/a.md", "use client.messages.create\nsystemPrompt: `x`\n")
        self.assertEqual(rc, 0, out)

    def test_literal_na_linha_seguinte_nao_dispara_e_esta_documentado(self):
        self.assertEqual(self.com_texto("src/a.ts", "systemPrompt:\n  `x`\n")[0], 0)
        self.assertIn("linha a linha", SCRIPT.read_text(encoding="utf-8"))


class SlotVazio(Base):
    def conferir(self):
        rc, out = self.com_texto("src/a.ts", "soma = a + b\n")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️ prompts.wrapper_pattern vazio", out)
        self.assertIn("sdd/config.yaml", out)
        self.assertIn("RESULTADO: LIMPO", out)
        rc, out = self.com_texto("src/a.ts", "client.messages.create(x)\n")
        self.assertEqual(rc, 2, out)
        self.assertIn("⚠️ prompts.wrapper_pattern vazio", out)
        self.assertIn("RESULTADO: DRIFT", out)

    def test_vazio(self):
        self.slot('prompts:\n  wrapper_pattern: ""\n')
        self.conferir()

    def test_vazio_com_comentario(self):
        self.slot('prompts:\n  wrapper_pattern: ""  # vazio\n')
        self.conferir()

    def test_sem_a_chave(self):
        self.slot('prompts:\n  builder_skill: "x"\n')
        self.conferir()

    def test_null_e_til_sao_vazios(self):
        for valor in ("null", "~"):
            with self.subTest(valor=valor):
                self.slot("prompts:\n  wrapper_pattern: %s\n" % valor)
                self.conferir()

    def test_mapa_em_linha_sem_o_slot_e_vazio(self):
        for texto in ("prompts: {}\n", "prompts: { builder_skill: x }\n"):
            with self.subTest(texto=texto):
                self.slot(texto)
                self.conferir()

    def test_sem_o_config(self):
        (self.p / "sdd/config.yaml").unlink()
        self.conferir()

    def test_com_o_slot_nao_ha_aviso(self):
        rc, out = self.com_texto("src/a.ts", "soma = a + b\n")
        self.assertEqual(rc, 0)
        self.assertNotIn("vazio", out)


class ErroDeUso(Base):
    def conferir(self, rc, out, trecho):
        self.assertEqual(rc, 64, out)
        self.assertIn("RESULTADO: ERRO DE USO", out)
        self.assertNotIn("RESULTADO: LIMPO", out)
        self.assertRegex(out.splitlines()[-1], r"^→ ")
        self.assertIn(trecho, out)

    def test_sem_argumento(self):
        self.conferir(*self.em_disco(), "falta dizer")

    def test_caminho_inexistente_mesmo_em_pasta_prompts(self):
        self.conferir(*self.em_disco("x/prompts/nao-existe.ts"), "caminho inexistente")

    def test_um_inexistente_entre_outros_nao_conclui_limpo(self):
        self.arquivo("src/a.py")
        self.conferir(*self.em_disco("src/a.py", "src/b.py"), "caminho inexistente")

    def test_pasta(self):
        (self.p / "src").mkdir()
        self.conferir(*self.em_disco("src"), "não é um arquivo")

    @unittest.skipIf(os.geteuid() == 0, "root lê qualquer arquivo")
    def test_arquivo_ilegivel(self):
        f = self.arquivo("src/a.py")
        f.chmod(0)
        try:
            self.conferir(*self.em_disco("src/a.py"), "não consegui ler")
        finally:
            f.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def test_expressao_invalida(self):
        for valor in ('"("', '"["'):
            with self.subTest(slot=valor):
                self.slot("prompts:\n  wrapper_pattern: %s\n" % valor)
                self.conferir(*self.com_texto("src/a.ts", "x\n"), "não é uma expressão válida")

    def test_valor_malformado(self):
        for valor in ('"systemPrompt:', '"x" y', "'x"):
            with self.subTest(slot=valor):
                self.slot("prompts:\n  wrapper_pattern: %s\n" % valor)
                self.conferir(*self.com_texto("src/a.ts", "x\n"), "malformado")

    def test_valor_em_forma_que_o_leitor_nao_sustenta_nao_vira_vazio(self):
        for texto in ('prompts: { wrapper_pattern: "x" }\n', "prompts:\n  wrapper_pattern: >-\n    x\n",
                      'prompts:\n  wrapper_pattern: &a "x"\n', 'prompts:\n  wrapper_pattern: !!str "x"\n',
                      "prompts: *llm\n"):
            with self.subTest(texto=texto):
                self.slot(texto)
                self.conferir(*self.com_texto("src/a.ts", "x\n"), "malformado")

    def test_formas_do_slot_que_a_varredura_nao_le_saem_64(self):
        # AT-032 (F14): lista, referência e mapa em várias linhas viravam expressão ou slot vazio, sem aviso.
        casos = {'prompts:\n  wrapper_pattern: [a, b]\n': "lista, mapa ou referência",
                 'prompts:\n  wrapper_pattern: {a: b}\n': "lista, mapa ou referência",
                 'prompts:\n  wrapper_pattern: *pat\n': "lista, mapa ou referência",
                 'prompts: {\n  wrapper_pattern: "x"\n}\n': "mapa entre chaves em várias linhas"}
        for config, trecho in casos.items():
            with self.subTest(config=config):
                self.slot(config)
                rc, out = self.com_texto("src/a.py", "soma = 1\n")
                self.assertEqual(rc, 64, out)
                self.assertIn(trecho, out)
                self.assertNotIn("RESULTADO: LIMPO", out)

    def test_as_mesmas_formas_entre_aspas_continuam_valendo(self):
        self.slot('prompts:\n  wrapper_pattern: "[sS]ystemPrompt:"\n')
        rc, out = self.com_texto("src/a.ts", "ask({ SystemPrompt: `x` })\n")
        self.assertEqual(rc, 2, out)
        self.slot("prompts: {}\n")
        rc, out = self.com_texto("src/a.py", "soma = 1\n")
        self.assertEqual(rc, 0, out)

    def test_bom_no_inicio_do_config(self):
        self.slot('\ufeffprompts:\n  wrapper_pattern: "systemPrompt:"\n')
        self.assertEqual(self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n")[0], 2)

    @unittest.skipIf(os.geteuid() == 0, "root lê qualquer arquivo")
    def test_config_ilegivel_nao_vira_slot_vazio(self):
        cfg = self.p / "sdd/config.yaml"
        cfg.chmod(0)
        try:
            self.conferir(*self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n"), "não consegui ler sdd/config.yaml")
        finally:
            cfg.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def test_config_que_existe_e_nao_se_le_nunca_vira_slot_vazio(self):
        cfg = self.p / "sdd/config.yaml"
        cfg.unlink()
        os.symlink("/nao/existe/config.yaml", str(cfg))
        self.conferir(*self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n"), "não consegui ler sdd/config.yaml")
        cfg.unlink()
        cfg.mkdir()
        self.conferir(*self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n"), "não consegui ler sdd/config.yaml")
        cfg.rmdir()
        os.mkfifo(str(cfg))
        self.conferir(*self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n"), "não consegui ler sdd/config.yaml")

    def test_conteudo_com_pasta_nunca_vira_limpo(self):
        (self.p / "src").mkdir()
        for caminho in ("src", "src/", ".", "/", "novo/", "src/.", "x/.."):
            with self.subTest(caminho=caminho):
                self.conferir(*self.com_texto(caminho, "soma = 1\n"), "--conteudo precisa do caminho de um arquivo")

    def test_conteudo_sem_nada_na_entrada(self):
        self.conferir(*self.com_texto("src/a.ts", ""), "nada chegou")
        self.conferir(*self.com_texto("prompts/a.ts", ""), "nada chegou")

    def test_conteudo_com_a_entrada_no_terminal(self):
        mestre, escravo = pty.openpty()
        try:
            r = subprocess.run([BASH, str(SCRIPT), "--conteudo", "src/a.ts"], cwd=str(self.p), env=self.env, stdin=escravo,
                               capture_output=True, encoding="utf-8", timeout=30)
        finally:
            os.close(escravo)
            os.close(mestre)
        self.conferir(r.returncode, r.stdout + r.stderr, "é o terminal")

    def test_conteudo_com_numero_errado_de_caminhos(self):
        self.conferir(*self.em_disco("--conteudo"), "exatamente 1 caminho")
        self.conferir(*self.em_disco("--conteudo", "a", "b"), "exatamente 1 caminho")

    def test_ponto_ponto_em_pasta_inexistente(self):
        self.conferir(*self.com_texto("nao/existe/../a.ts", "x\n"), "com ..")

    def test_opcao_desconhecida(self):
        self.conferir(*self.em_disco("--nada"), "opção desconhecida")

    @unittest.skipIf(os.geteuid() == 0, "root lê qualquer arquivo")
    def test_pasta_sdd_sem_permissao_nunca_vira_slot_vazio(self):
        sdd = self.p / "sdd"
        sdd.chmod(0)
        try:
            self.conferir(*self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n"), "não consegui ler sdd/config.yaml")
        finally:
            sdd.chmod(stat.S_IRWXU)

    def test_awk_que_falha_nunca_vira_slot_vazio(self):
        stub = self.tmp / "stubawk"
        stub.mkdir()
        (stub / "awk").write_text("#!/bin/sh\nexit 3\n", encoding="utf-8")
        (stub / "awk").chmod(0o755)
        env = dict(self.env, PATH="%s:%s" % (stub, self.env["PATH"]))
        self.conferir(*self.com_texto("src/a.ts", "ask({ systemPrompt: `x` })\n", env=env), "exit 3")

    def test_entrada_lida_pela_metade_nunca_vira_limpo(self):
        # O cat falha depois de gravar um pedaço não vazio: sem conferir a saída dele, o pedaço valeria como varredura.
        stub = self.tmp / "stubcat"
        stub.mkdir()
        (stub / "cat").write_text('#!/bin/sh\nprintf "soma = 1\\n"\nexit 1\n', encoding="utf-8")
        (stub / "cat").chmod(0o755)
        env = dict(self.env, PATH="%s:%s" % (stub, self.env["PATH"]))
        self.conferir(*self.com_texto("src/a.py", "client.messages.create(x)\n", env=env), "entrada padrão inteira")

    def test_grep_com_saida_2_nunca_vira_limpo(self):
        # Um grep que falha não é "não achei": com o stub, toda busca de conteúdo sai 2.
        stub = self.tmp / "stub"
        stub.mkdir()
        grep_real = shutil.which("grep")
        (stub / "grep").write_text(
            '#!/bin/bash\ncase " $* " in\n  *" -- "*) exit 2 ;;\nesac\nexec %s "$@"\n' % grep_real, encoding="utf-8")
        (stub / "grep").chmod(0o755)
        env = dict(self.env, PATH="%s:%s" % (stub, self.env["PATH"]))
        self.conferir(*self.com_texto("src/a.py", "x = 1\n", env=env), "a busca falhou")


class EmDisco(Base):
    def test_todos_os_achados_nomeados(self):
        self.arquivo("src/a.py", "client.messages.create(x)\n")
        self.arquivo("src/b.ts", "ask({ systemPrompt: `x` })\n")
        self.arquivo("src/c.py")
        rc, out = self.em_disco("src/a.py", "src/b.ts", "src/c.py")
        self.assertEqual(rc, 2, out)
        self.assertIn("src/a.py :: ", out)
        self.assertIn("src/b.ts :: ", out)
        self.assertNotIn("src/c.py :: ", out)

    def test_limpo(self):
        self.arquivo("src/c.py")
        rc, out = self.em_disco("src/c.py")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: LIMPO", out)


class AutoTeste(Sandbox):
    def test_cdpath_nao_quebra(self):
        rc, _, err = self.roda([BASH, SCRIPT, "--self-test"], self.tmp, dict(self.env, CDPATH="."))
        self.assertEqual(rc, 0, err)

    def test_vermelho_quando_grep_2_vira_nao_achei(self):
        linha = '  erro_uso "a busca falhou (exit $rc) ao avaliar $CAMINHO" "confira a permissão do arquivo e a expressão de prompts.wrapper_pattern"'
        rc, _, err = self.sabotada(linha, "  return 1")
        self.assertEqual(rc, 2, err)
        self.assertIn("grep com saída 2", err)

    def test_verde_numa_pasta_sem_fixtures_sem_config_e_sem_residuo(self):
        vazia = self.tmp / "vazia"
        vazia.mkdir()
        tmpdir = self.tmp / "tmp"
        tmpdir.mkdir()
        env = dict(self.env, TMPDIR=str(tmpdir))
        rc, out, err = self.roda([BASH, SCRIPT, "--self-test"], vazia, env)
        self.assertEqual(rc, 0, err)
        self.assertIn("RESULTADO: VERDE", out)
        self.assertEqual(list(vazia.iterdir()), [], "ficou arquivo na pasta de quem chamou")
        self.assertEqual(list(tmpdir.iterdir()), [], "ficou resíduo na pasta temporária")

    def test_chamada_por_caminho_relativo(self):
        destino = self.tmp / "sdd/bin"
        destino.mkdir(parents=True)
        shutil.copy(str(SCRIPT), str(destino))
        rc, _, err = self.roda([BASH, "sdd/bin/prompt-drift-scan.sh", "--self-test"], self.tmp)
        self.assertEqual(rc, 0, err)

    def sabotada(self, de: str, para: str):
        copia = self.tmp / "prompt-drift-scan.sh"
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(de, texto)
        copia.write_text(texto.replace(de, para), encoding="utf-8")
        return self.roda([BASH, copia, "--self-test"], self.tmp)

    def test_vermelho_sem_o_sinal_do_wrapper(self):
        rc, _, err = self.sabotada('if [ -n "$WRAPPER" ] && casa "$WRAPPER" "$2"; then', "if false; then")
        self.assertEqual(rc, 2, err)
        self.assertIn("parâmetro do wrapper", err)
        self.assertIn("RESULTADO: VERMELHO", err)

    def test_nao_quebra_onde_link_e_permissao_nao_tem_efeito(self):
        # Git Bash: ln -s falha e chmod 000 não tira a leitura. Os casos que dependem disso são pulados, sem vermelho falso.
        stub = self.tmp / "stubgit"
        stub.mkdir()
        (stub / "ln").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        real = shutil.which("chmod")
        (stub / "chmod").write_text('#!/bin/sh\n[ "$1" = "000" ] && exit 0\nexec %s "$@"\n' % real, encoding="utf-8")
        (stub / "mkfifo").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        for nome in ("ln", "chmod", "mkfifo"):
            os.chmod(str(stub / nome), 0o755)
        env = dict(self.env, PATH="%s:%s" % (stub, self.env["PATH"]))
        rc, out, err = self.roda([BASH, SCRIPT, "--self-test"], self.tmp, env)
        self.assertEqual(rc, 0, out + err)

    def test_vermelho_sem_a_recusa_do_ponto_ponto(self):
        rc, _, err = self.sabotada('*/../*|*/..) erro_uso "caminho com .. numa pasta que não existe: $p" "passe o caminho final, sem .." ;;',
                                   '*/../*|*/..) : ;;')
        self.assertEqual(rc, 2, err)
        self.assertIn(".. em pasta inexistente", err)

    def test_vermelho_quando_o_cat_que_falha_e_ignorado(self):
        rc, _, err = self.sabotada('cat > "$TMP/conteudo" || erro_uso "não consegui ler a entrada padrão inteira" "confira o espaço na pasta temporária e rode de novo; um pedaço do texto não vale como varredura"',
                                   'cat > "$TMP/conteudo"')
        self.assertEqual(rc, 2, err)
        self.assertIn("cat que falha no meio", err)

    def test_vermelho_sem_a_exclusao_de_teste(self):
        rc, _, err = self.sabotada("  nome_de_teste && return 0\n", "")
        self.assertEqual(rc, 2, err)


if __name__ == "__main__":
    unittest.main()
