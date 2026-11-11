# Modo incidente — quando a falha já aconteceu

> Para quando a pessoa diz "vazou a chave", "a tabela ficou aberta", "um cliente viu o dado de outro" ou
> "recebi um aviso de acesso estranho". A ordem importa: primeiro fechar, depois entender. Cada minuto aberto
> é mais dado fora.

Este roteiro organiza a resposta técnica e o registro. Ele **não** é parecer jurídico: a decisão de comunicar,
o texto da comunicação e o prazo aplicável são de quem responde pelo tratamento do dado, com quem o assessora.

## 1. Fechar a porta (agora, antes de tudo)

| O que aconteceu | Fechar |
|---|---|
| chave secreta exposta (código, repositório, print, conversa) | revogue ou troque a chave no painel do serviço; atualize a variável de ambiente; publique de novo. Apagar o arquivo **não** basta: o histórico do git e as cópias continuam com ela |
| tabela sem RLS ou com política aberta | ligue a RLS na tabela e troque a política aberta pela do dono; se não der agora, revogue a leitura do papel anônimo |
| cadastro aberto, abuso de login ou de chamadas pagas | desligue o cadastro público, ligue o limite de tentativas, baixe o teto de uso |
| agente de IA fazendo o que não devia | desligue o agente (o interruptor que o Design registrou) e revogue a credencial dele |
| não sabe a causa | tire o app do ar ou ponha em manutenção |

Não espere entender para fechar. Diga à pessoa, em uma frase, o que foi fechado e o que ainda está aberto.

## 2. Preservar a evidência

- Não apague registros nem "limpe" o banco. Exporte os registros do período (API, login, arquivos, funções) e
  guarde fora do app.
- Anote data e hora de cada passo, inclusive do passo 1.

## 3. Dimensionar

Responda, com os registros na mão: que dado ficou exposto? De quantas pessoas? Desde quando e até quando? Há
sinal de acesso de fato (chamadas de origem estranha, picos, horários fora do padrão)? A IA ajuda a ler os
registros; a conclusão é de quem responde pelo sistema.

## 4. Corrigir a causa

Volte ao item do catálogo (`references/CATALOGO_SEGURANCA.md`) que corresponde à falha, aplique o "evitar" e
prove pelo "confira" e pelo teste do item. Rode `bash sdd/bin/seguranca-varredura.sh` antes de publicar a correção.

## 5. Comunicar

No Brasil, a LGPD obriga o controlador do dado a comunicar à ANPD e aos titulares o incidente que possa causar
risco ou dano relevante, no prazo que o regulamento da ANPD fixa (confira o regulamento vigente). Quem presta
serviço para um cliente costuma ser **operador**: comunica o cliente (o controlador) de imediato e o apoia na
comunicação dele; o contrato entre os dois deve dizer como. Dado de CPF, renda, folha e saúde costuma ser risco
relevante: não presuma que "era pouca coisa".

A comunicação diz, em linguagem simples: que dado foi exposto, de quem, como aconteceu, o que foi feito para
conter, o que a pessoa pode fazer para se proteger e um contato. Na dúvida jurídica, chame quem assessora.

## 6. Registrar

Um documento por incidente, guardado com o projeto (sem dado pessoal dentro dele), com: linha do tempo
(descoberta, contenção, correção, comunicação), a falha e o item do catálogo, o dado e as pessoas afetadas
(em número), a evidência guardada, as comunicações feitas com a data, e a mudança que impede a repetição.
Quase sempre a mudança é uma regra a mais no `AGENTS.md` do projeto e um item a mais no que se confere antes
de publicar.

Referência pública: guia de resposta a incidentes do NIST (SP 800-61); OWASP A09:2021.
