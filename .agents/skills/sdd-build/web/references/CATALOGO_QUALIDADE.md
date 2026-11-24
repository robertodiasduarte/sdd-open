# Catálogo de qualidade

> Fonte única das regras de forma do código que o agente segue ao construir (Clean Code, na parte que vale para
> qualquer linguagem, mais o que cada stack pede) e das ferramentas que conferem essa forma. As regras gerais valem
> sempre; as de uma stack, só quando o projeto usa essa stack. No SDD Open, quem lê este arquivo por máquina é o
> script de regras de qualidade, que monta o bloco "Qualidade ao construir" do AGENTS.md; no starter, a build o lê
> antes de escrever.

## Como ler uma ficha

Cada regra é um título `### Qnn — <regra>` seguido de exatamente 2 linhas, nesta ordem:

| Campo | O que diz | Valores |
|---|---|---|
| `stack` | onde a regra vale | `todas` · `python` · `js` · `ts` · `php` · `sql` |
| `frase` | a regra que o agente segue ao escrever, em 1 frase positiva | texto |

Cada ferramenta é um título `### <stack>` em `## Ferramentas por stack`, seguido de exatamente 5 linhas:

| Campo | O que diz |
|---|---|
| `detecta` | arquivos que mostram que o projeto usa a stack (separados por vírgula; `*.ext` = algum arquivo com a extensão) |
| `config` | arquivos que mostram um linter já configurado; `arquivo[chave]` = a chave aparece dentro do arquivo |
| `lint` | comando de lint sugerido, sem caminho no fim: o Build acrescenta os arquivos da tarefa (sem arquivos, ele confere a pasta do projeto) |
| `tipos` | comando de checagem de tipos sugerido, ou `—` |
| `instalar` | comando que instala as ferramentas, para o aluno rodar depois do sim |

Uma stack com `lint: —` só serve para escolher regras: não há ferramenta a sugerir. Com `ts` no projeto, a sugestão
de `ts` vale no lugar da de `js`.

## Regras

### Q01 — Erro tratado ou propagado
- stack: todas
- frase: Trate cada erro onde dá para decidir o que fazer, ou deixe-o subir com a causa na mensagem; o erro calado vira um defeito que ninguém vê.

### Q02 — Nome que diz o que é
- stack: todas
- frase: Dê a cada variável, função e arquivo um nome que diga o que a coisa é ou faz, no vocabulário do domínio do projeto.

### Q03 — Só o código que roda
- stack: todas
- frase: Apague o código morto e o código comentado; o histórico do git guarda o que saiu.

### Q04 — Reusar antes de criar
- stack: todas
- frase: Antes de criar uma função, procure no projeto uma que já faça o mesmo e reuse-a; duas funções iguais divergem no primeiro conserto.

### Q05 — Constante com nome
- stack: todas
- frase: Troque número e texto mágicos por uma constante com nome que explique o valor.

### Q06 — Uma coisa por função
- stack: todas
- frase: Escreva funções que fazem uma coisa só, num nível de abstração, com poucos parâmetros; quando uma função pede um "e" para ser descrita, divida-a.

### Q07 — Exceção específica em Python
- stack: python
- frase: Capture a exceção específica que você sabe tratar (`except ValueError`), com tipos nas funções públicas, e deixe o `ruff check` sem erro.

### Q08 — Recursos fechados em Python
- stack: python
- frase: Abra arquivo, conexão e trava com `with`, para que se fechem também quando der erro.

### Q09 — Promessa com tratamento em JavaScript
- stack: js
- frase: Todo `await` e toda promessa têm o erro tratado (`try`/`catch` ou `.catch`), e as variáveis nascem com `const`, salvo as que mudam.

### Q10 — Tipos explícitos em TypeScript
- stack: ts
- frase: Declare os tipos nas fronteiras (parâmetros, retorno, resposta de API) e use `unknown` com verificação no lugar de `any`; o `tsc --noEmit` fica sem erro.

### Q11 — Tipos estritos em PHP
- stack: php
- frase: Comece cada arquivo com `declare(strict_types=1);`, declare os tipos de parâmetro e de retorno, e siga o padrão PSR-12.

### Q12 — Migração pequena e com nome
- stack: sql
- frase: Faça uma mudança por migração, com um nome que diga o que ela faz, e nomeie as colunas em cada consulta.

## Ferramentas por stack

### python
- detecta: pyproject.toml, setup.py, requirements.txt, *.py
- config: ruff.toml, .ruff.toml, .flake8, mypy.ini, pyproject.toml[tool.ruff], pyproject.toml[tool.mypy], pyproject.toml[tool.flake8]
- lint: ruff check
- tipos: mypy .
- instalar: python3 -m pip install ruff mypy

### js
- detecta: package.json
- config: eslint.config.js, eslint.config.mjs, eslint.config.cjs, eslint.config.ts, .eslintrc, .eslintrc.js, .eslintrc.cjs, .eslintrc.json, .eslintrc.yml, .eslintrc.yaml, package.json[eslintConfig], package.json["lint"]
- lint: npx eslint
- tipos: —
- instalar: npm init @eslint/config@latest

### ts
- detecta: tsconfig.json
- config: eslint.config.js, eslint.config.mjs, eslint.config.cjs, eslint.config.ts, .eslintrc, .eslintrc.js, .eslintrc.cjs, .eslintrc.json, .eslintrc.yml, .eslintrc.yaml, package.json[eslintConfig], package.json["lint"]
- lint: npx eslint
- tipos: npx tsc --noEmit
- instalar: npm init @eslint/config@latest && npm install --save-dev typescript

### php
- detecta: composer.json, *.php
- config: phpcs.xml, phpcs.xml.dist, .phpcs.xml, .php-cs-fixer.php, .php-cs-fixer.dist.php
- lint: vendor/bin/phpcs --standard=PSR12
- tipos: —
- instalar: composer require --dev squizlabs/php_codesniffer

### sql
- detecta: *.sql
- config: —
- lint: —
- tipos: —
- instalar: —
