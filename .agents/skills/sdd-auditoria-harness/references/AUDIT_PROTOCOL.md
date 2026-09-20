# Protocolo de Auditoria e Evidência

## 1. Princípio de prova

A auditoria separa três coisas:
1. fato observado;
2. inferência;
3. recomendação.

Somente fatos observáveis sustentam achados. Inferências incertas ficam em “Dúvidas”.

## 2. Rótulos oficiais

### EXCESSO
Use quando houver volume/escopo que objetivamente aumenta ruído ou superfície desnecessária.
Evidências aceitáveis:
- acúmulo sem política de arquivamento;
- permissões mais amplas que os comandos realmente exigem;
- documentação monolítica que duplica conteúdo operacional já mantido em outro lugar.

### OBSOLETO
Use quando o item foi substituído ou depende de infraestrutura que não existe mais.
Obrigatório:
- citar o substituto, quando houver;
- mostrar a evidência da substituição/deriva.

### SUPÉRFLUO
Use quando o item funciona, mas não agrega ao fluxo SDD principal.
Exemplos:
- sobra de template;
- exemplo permanente sem uso;
- agente genérico sem papel no fluxo principal.
Evite esse rótulo sem evidência de não integração.

### NÃO UTILIZADO
Pré-condição mínima:
- zero referências de entrada; e
- nenhum sinal de execução encontrado.
Se houver indício de uso raro/sazonal, trate como dúvida.

### AMBÍGUO
Use quando dois lugares/documentos disputam o mesmo papel ou quando o gatilho de uso é objetivamente indistinguível.
Cite os dois lados da ambiguidade.

### CONFLITANTE
Use quando o item contradiz o SDD principal estabelecido no início.
Exemplos:
- fases diferentes;
- comando diferente para a mesma fase;
- path de artefato divergente;
- regra operacional incompatível.

## 3. Evidências obrigatórias

Uma linha de achado deve conter pelo menos um destes tipos de evidência concreta:
- `0 referências de entrada`;
- `N referências em: <paths>`;
- `último commit: AAAA-MM-DD`;
- `mencionado em relatório/log: <path>`;
- `linha X cita <path/comando> que não existe`;
- `linhas X-Y contradizem <fonte de verdade>: linhas A-B`;
- `propósito/saída duplicado com <item>, evidenciado por <trechos/paths>`.

Sempre verifique existência de paths antes de acusar deriva.

## 4. Referências cruzadas

Para cada item:
1. procure pelo path relativo completo;
2. procure pelo nome de arquivo;
3. procure pelo identificador invocável relevante, quando aplicável:
   - comando: `/nome`;
   - agente/skill: nome declarado/frontmatter;
   - script: path de execução.
4. exclua autorreferência do próprio item.
5. registre arquivos distintos que referenciam o item.

Zero referência textual não é prova absoluta de nunca ter sido usado.

## 5. Recência

Preferência:
`git log -1 --format=%cs -- <arquivo>`

Se o arquivo não estiver no Git, registre:
`sem histórico Git verificável`.

Não use data de mtime como substituto silencioso.

## 6. Sinal de execução

Procure em diretórios de reports/logs do SDD por:
- nome do item;
- comando;
- path relativo;
- identificador declarado.

Uma menção pode ser evidência de execução passada, mas leia o contexto para distinguir execução real de documentação.

## 7. Duplicação

Antes de classificar duplicação, compare:
- gatilho;
- responsabilidade;
- artefato produzido;
- diretório de saída;
- consumidor seguinte.

Dois itens parecidos, mas com fases/consumidores diferentes, não são necessariamente duplicados.

## 8. Deriva

Extraia referências locais de:
- links Markdown;
- trechos em crase;
- valores JSON;
- comandos e exemplos.

Ignore como “inexistente” até resolver:
- URLs;
- variáveis (`$VAR`, `${VAR}`);
- placeholders (`<...>`);
- globs;
- paths explicitamente exemplificativos;
- arquivos gerados apenas em runtime.

## 9. Segurança operacional

Comandos tipicamente aceitáveis em forma read-only:
- `git status --short`
- `git log`
- `git diff`
- `git ls-files`
- `git grep`
- `rg`
- `grep`
- `find` sem `-delete` e sem execução mutante
- `cat`
- `sed` sem `-i`
- `awk`
- `head`, `tail`, `wc`

Nunca usar durante a auditoria:
- `git add`, `commit`, `push`, `pull`, `fetch`
- `git checkout`, `switch`, `restore`, `reset`, `clean`
- `rm`, `mv`, `cp`, `rsync`
- `touch`, `mkdir`
- `sed -i`, `perl -pi`
- `tee`, redirecionamento `>`/`>>`
- instaladores/deploys
- qualquer script sem comprovação de comportamento read-only

A exceção única de escrita é a criação do relatório final novo.

## 10. Regra de justiça

Inclua também 3–5 padrões saudáveis em “O que está BOM”.
Auditoria justa não força achados onde a evidência não existe.
