# Release 0c — passada de segurança (modelo), sobre c30b54c

Lista: `bash sdd/bin/seguranca-varredura.sh --checklist` (stack do pacote: nenhuma; 8 itens de stack `todas`, fora da
bancada). Conferido contra o diff `69b7f6b..c30b54c` (50 arquivos).

| Item | Marca | Como |
|---|---|---|
| S11 chave secreta | cumprido | a varredura do pacote sai NADA ACHADO (`SEGURANCA.log`); as chaves dos testes são montadas em tempo de execução |
| S05 texto do usuário em SQL | não se aplica a este diff | o pacote não monta SQL; o script só lê migrações como texto |
| S10 senha ou segredo guardado | não se aplica | nenhum segredo guardado; a chave da OpenRouter só no ambiente do comando da revisão, fora do pacote |
| S16 texto virando código | cumprido | o script não usa eval/exec; `subprocess` com lista de argumentos, sem shell; `codecs.escape_decode` só no nome de arquivo que o git devolve |
| S18 instrução escondida em conteúdo externo | cumprido | a varredura lê o repositório como dado e nunca executa nada dele; os textos das skills mandam tratar conteúdo externo como dado |
| S20 agente com poder demais | não se aplica | o pacote não roda agente |
| S19 dependência nova | cumprido | nenhuma dependência nova (bash 3.2 + Python stdlib) |
| S17 log com linha forjada | não se aplica | a saída imprime caminho e linha, nunca o trecho achado |

Além da lista: nenhuma proteção removida (a 0c deixou de ser condicional e ficou mais forte; o S11 ganhou escopo:
`sdd/` e pastas dos agentes); o único afrouxamento é o cabeçalho PEM sem o corpo da chave, que deixou de bloquear
(documentação), revisado na rodada 4. `bin/sdd-open.sh` usa o arquivo do `mktemp` entre aspas no `sed r`.
Veredito 0c: sem achado crítico.
