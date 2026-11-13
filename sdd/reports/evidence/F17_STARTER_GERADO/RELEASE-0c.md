# Release 0c — passada de segurança (modelo), sobre d813954

Lista: `bash sdd/bin/seguranca-varredura.sh --checklist` (stack do pacote: nenhuma; 8 itens de stack `todas`). Conferido
contra o diff `e22a1b2..d813954`.

| Item | Marca | Como |
|---|---|---|
| S11 chave secreta | cumprido | a varredura do pacote sai NADA ACHADO (`SEGURANCA.log`); nenhuma chave no diff; a chave da OpenRouter só no ambiente do comando da revisão |
| S05 texto do usuário em SQL | não se aplica | o diff não monta SQL |
| S10 senha ou segredo guardado | não se aplica | nenhum segredo guardado |
| S16 texto virando código | cumprido | o gerador e a trava não usam eval/exec; `subprocess` com lista de argumentos, sem shell; o archive da tag é lido com `tarfile`, recusando caminho absoluto ou com `..` |
| S18 instrução escondida em conteúdo externo | cumprido | o gerador lê só a tag do próprio repositório; as trocas são texto exato, nunca executado; o starter clonado em teste foi tratado como dado |
| S20 agente com poder demais | não se aplica | o diff não roda agente |
| S19 dependência nova | cumprido | nenhuma (Python stdlib; os workflows do starter mantêm as actions fixadas por SHA da v1.5.16) |
| S17 log com linha forjada | não se aplica | as saídas imprimem caminho e linha, nunca o conteúdo do arquivo |

Além da lista:
- **Permissões dos workflows do starter:** iguais às da v1.5.16 — `ci.yml` sem bloco de permissões (como era);
  `auto-release.yml` com `contents: read` e `contents: write` só no job `release`; `release.yml` com `contents: write`. O
  passo novo só roda o `check-gerado.py`, sem segredo nem rede.
- **O gerador apaga no destino** (`skills/<gerada>/` e arquivo de `scripts/` e `.github/workflows/` que saiu da semente):
  só depois de todas as checagens, só num clone git sem mudança (senão 64), e só nas pastas que ele gera; o git do
  starter desfaz.
- **Proteção removida:** nenhuma; a trava do starter é proteção nova.

Veredito 0c: sem achado crítico.
