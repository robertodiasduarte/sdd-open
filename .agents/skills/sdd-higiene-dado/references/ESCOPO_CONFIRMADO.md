# Escopo confirmado — HD001 versão 1

Confirmado pelo responsável em 2026-10-02, depois da apresentação do resumo, com a frase
"CONFIRMO O ESCOPO HD001 V1 E AUTORIZO GERAR A SKILL." Perfil efetivo: C (operacional).
Controle conversacional: o registro não autentica quem confirmou.

## Esta skill (parte B do escopo)

- Instala, com OK explícito, um alarme pre-commit que recusa o commit e ensina.
- Detecta CPF/CNPJ por dígito verificador (com e sem máscara), `.env`/`.env.*` (exceto `.env.example`
  e `.env.sample`), `.pfx`, `.p12`, `.pem` com chave privada e planilha nova de qualquer tamanho.
- A mensagem explica o achado, cita `git commit --no-verify` e diz como desinstalar.
- Se já existe outro alarme (husky, `core.hooksPath`, pre-commit próprio), não instala e explica.

## Fora do escopo

- Consertar, apagar ou reescrever o histórico do git (só entrega o comando).
- Revogar certificado, trocar senha, mexer em conta externa.
- Ler CPF dentro de `.xlsx`/`.xls`/`.ods`; varrer commits antigos.
- Parecer sobre LGPD, sigilo profissional ou responsabilidade do contador.

## Partes A e C do mesmo escopo (fora desta pasta)

- A: novas checagens somente leitura na `sdd-checar-ambiente`.
- C: versão e data (`metadata.version`, `metadata.updated`) e linha de identificação em todas as skills
  do SDD Starter, conferidas no CI.

## Critérios de aceite desta skill

- CPF/CNPJ válidos com e sem máscara bloqueiam; DV errado e sequência repetida não.
- `.pem` só com certificado público não alarma; com chave privada, alarma.
- Com outro alarme instalado, não instala e explica.
- Desinstalar remove só o alarme desta skill.
- Os testes geram os números em tempo de execução; o `publish-check.sh` do repositório continua PASS.
