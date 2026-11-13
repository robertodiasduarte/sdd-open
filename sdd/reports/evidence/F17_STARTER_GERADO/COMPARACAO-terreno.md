# Comparação skill a skill, starter (v1.5.16) × Open (feat/f17 sobre v2.12.1) — terreno

Agente em contexto novo, só leitura, 2026-11-12. S = skill no starter; O = skill no Open; R = raiz do Open.

## agents/openai.yaml — (B) o Open tirou de propósito
`O/sdd-higiene-dado/CHANGELOG.md:18` ("sai agents/openai.yaml"); commit 4ee5470 ("Sem agents/openai.yaml, sem npx do
starter, sem sdd/ambiente.md"); `R/tests/test_matriz_new_session.py:105-110` reprova o arquivo nas skills portadas;
`R/bin/sdd-open.sh:836`: o `doctor` usa o arquivo para avisar "skills do sdd-starter detectadas". Na geração, recriá-lo
é decisão do gerador.

## sdd-checar-ambiente (S 1.2.0, O 1.5.1) — nada a trazer
(D) sem git e sem a skill irmã, o starter manda `npx skills add …sdd-starter` (S/scripts/checar.sh:144-145); o Open manda
rodar o init (O/scripts/checar.sh:348-349): o gerador troca a frase. (D) `sdd/ambiente.md`. (A) editores: lista maior no
Open. (A) 52 dos 53 testes com o mesmo nome em R/tests/test_checar.py; o 53º foi renomeado com o item (D).

## sdd-iniciar-repo (S 1.1.0, O 1.2.0) — nada a trazer
(D) `npx skills add` para a higiene (S/SKILL.md:217-218 × O/SKILL.md:247-248). (A) gh no Mac. (A) inventario.sh = o do
starter + a linha gh:. (A) os 24 testes em R/tests/test_inventario.py.

## sdd-higiene-dado (S 1.1.0, O 1.2.0) — nada a trazer
(B, correção) caminho do hook por `git rev-parse --git-path` (O/scripts/alarme.sh:34-36). (B) testes fora da pasta da
skill (CHANGELOG 1.1.1; 28 do starter em R/tests/test_alarme.py, que tem 36). evals e pre-commit.sh sem mudança.

## sdd-kb (S 2.1.0, O 2.2.1) — nada a trazer
(B) caminho fixo `sdd/kb/` (O/CHANGELOG.md:12). (B) links `.agents/skills/sdd-kb/…` no SKILL.md (O/SKILL.md:30): no
starter instalado por npx ou zip esse caminho pode não existir — o gerador reescreve. (A) gate.sh do Open cobre os casos
das fixtures do starter e confere o motivo. (A) pergunta do perfil em references/como-falar.md.

## sdd-new-session (S 1.3.0, O 1.5.1) — trazer C1, C2, C3 (C4 opcional)
A do Open nasceu no Open (80d7887) e recebeu do starter só o pré-voo por script (4ee5470).
- C1 pré-voo à mão (sem bash) com a checagem da pasta sincronizada e os casos A–D (S/SKILL.md:121-144, porquê :370-375);
  o Open só diz "terminal na pasta errada ou projeto sem git" (O/SKILL.md:116-120). O texto já existe em
  O/sdd-checar-ambiente/SKILL.md:111-127.
- C2 skills do agente fora do git copiadas para a frente e a sdd-release conferida (S :263-265, :322-330); o Open só copia
  .env e documentos (O :284-295).
- C3 duas notas de "Por que": a mesma branch não abre em duas worktrees; `-d` só apaga branch integrada (S :363-369).
- C4 (baixo) dizer o que não vai acontecer antes de criar; "commit" e "dependências" no glossário; "Build, commit e push
  rodam lá dentro" também com editor.
- (A) projeto sem git, mensagens das paradas, colisão de nome, revisão, refazer base, sem editor não aborta.
- (incerto) O/SKILL.md:108-110 e :190 fecham toda parada com "peça a frente de novo"; o starter dizia que a oferta da
  sdd-iniciar-repo não leva essa frase (S :186).
- Cenário de branching A/B/C: não trazer (o Open usa o slot default_branch; repositório de uma pessoa quase nunca é C).
- (D) ambiente.md, npx, detecção de checar-ambiente antiga, linha de identificação.

## Alerta para a geração
Texto do Open cita o que não existe num projeto do starter: `sdd/templates/fragments/PERGUNTA_DECISAO.md`,
`sdd/bin/sdd-fluxo.sh`, `sdd/config.yaml`, `.agents/skills/sdd-kb/…`, "rode o init do sdd-open".
