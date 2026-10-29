# Catálogo de fontes

> Cada documento citado por uma regra, tabela ou caso tem uma linha aqui. **A data do arquivo e o nome não provam vigência**: valem a versão, a data de captura e o SHA-256 registrados abaixo, conferidos na fonte oficial.

| ID | Documento | Degrau | Versão | Origem | Capturado em | Arquivo | SHA-256 |
|---|---|---|---|---|---|---|---|
| {ID} | {nome oficial do documento} | {degrau} | {versão ou data de publicação} | {URL oficial} | {AAAA-MM-DD} | {caminho em fontes/ ou —} | {64 hex ou —} |

## Degraus (do mais forte ao mais fraco)

`constituicao` · `lei-complementar` · `lei-ordinaria` · `decreto` · `ato-normativo` (resolução, instrução normativa, portaria) · `ato-tecnico` (nota técnica, informe técnico, manual oficial, ato conjunto) · `solucao-de-consulta` · `doutrina` (artigo, curso, reportagem, parecer de terceiro) · `pratica-propria`

---

> `Arquivo` com caminho ⇒ o arquivo está em `fontes/` e o validador recalcula o SHA-256 (mudou ⇒ reprova). `—` ⇒ só a referência; o SHA, se houver, é o do arquivo conferido na captura.
> Calcule com `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py sha sdd/kb/<slug>/fontes/<arquivo>`. Versão nova de um documento = linha nova com id novo; a antiga fica para as regras que ainda a citam.
