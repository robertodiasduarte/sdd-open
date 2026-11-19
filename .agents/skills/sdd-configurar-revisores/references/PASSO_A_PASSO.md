# Passo a passo — OpenRouter, a chave e o perfil do terminal

> Lido pela skill `sdd-configurar-revisores` na etapa 3 (Chave). Mostre **um bloco por resposta**, no máximo 5
> passos, cada um com um clique ou um comando e o que o aluno deve ver depois (`→`). Nunca peça a chave na conversa.

## Fontes e data da conferência

| O quê | Fonte | Conferido em |
|---|---|---|
| Página de créditos (`openrouter.ai/settings/credits`), cartão, AliPay ou cripto, taxa de 5,5% (mínimo de US$ 0,80) na compra, crédito sem uso pode expirar depois de 1 ano | https://openrouter.ai/docs/faq | 2026-11-18 |
| Página de chaves (`openrouter.ai/settings/keys`); a chave ganha um nome e um limite de crédito (ou nenhum), que pode ser diário, semanal ou mensal e muda depois na página da chave; a chave fica fora do código, em variável de ambiente | https://openrouter.ai/docs/api-reference/authentication | 2026-11-18 |
| Consulta de leitura da chave (`GET /api/v1/key`) e o saldo só com chave de gestão (`/api/v1/credits`) | https://openrouter.ai/docs/api-reference/limits · https://openrouter.ai/docs/api-reference/get-credits | 2026-11-18 |
| VS Code (e editores da mesma família) abre um shell de login interativo ao iniciar para ler o ambiente | https://code.visualstudio.com/docs/configure/command-line | 2026-11-18 |
| Janela de variáveis de ambiente do Windows ("Editar as variáveis de ambiente para sua conta", "Novo") | tutorial da Alura (não há página oficial da Microsoft com o texto em português) | 2026-11-18 |

O texto exato dos botões das páginas logadas do OpenRouter **não** está na documentação: os passos abaixo dizem o
endereço da página e o que ela pede (nome, limite), não o rótulo do botão. O caminho do Windows **não foi testado**
nesta versão (sem um Windows na conferência); o do macOS e do Linux foi testado pelos testes do pacote.

## Bloco 1 — Conta e crédito (no navegador)

1. Abra `https://openrouter.ai` e entre (com Google, GitHub ou e-mail) → você vê a página inicial com o seu avatar
   no canto.
2. Abra `https://openrouter.ai/settings/credits` → você vê a página de créditos, com o saldo em US$ 0.
3. Compre o mínimo que quiser (US$ 5 bastam para muitas revisões) com cartão → o saldo da página mostra o valor.
   A compra tem taxa de 5,5% (no mínimo US$ 0,80), e crédito sem uso pode expirar depois de 1 ano.

## Bloco 2 — A chave, com limite de gasto (no navegador)

1. Abra `https://openrouter.ai/settings/keys` → você vê a lista de chaves (vazia na 1ª vez).
2. Crie uma chave nova. No nome, ponha `sdd-revisao`; no limite de crédito, ponha um valor (US$ 5, por exemplo) →
   a página mostra a chave **uma vez só**, começando por `sk-or-`.
3. Use o botão de copiar da página. **Não cole a chave nesta conversa**: ela iria para o histórico do agente.
   → nada muda na tela; a chave está na sua área de transferência.

O limite é o teto de gasto desta chave: se algo der errado, a revisão para ali, não no seu saldo inteiro.

## Bloco 3 — Guardar a chave no seu computador

### macOS, Linux e Windows com WSL

1. Abra uma janela de terminal **sua** (no Mac: aplicativo Terminal), fora da conversa com o agente → você vê o
   prompt do terminal.
2. Entre na pasta do projeto: `cd "<pasta do projeto>"` → o prompt mostra o nome da pasta.
3. Rode `bash <pasta desta skill>/scripts/guardar-chave.sh` → ele pede a chave.
4. Cole a chave e tecle Enter (ela **não aparece** enquanto você cola) → você vê `✅ Chave gravada em ~/.zshrc (o
   valor não foi mostrado).` (ou `~/.bashrc`, `~/.bash_profile`).
5. Feche e abra o agente (bloco 4).

O comando recusa (e não grava nada) se rodar dentro do agente, se a chave vier vazia ou com espaço ou aspas, e se o
perfil for um atalho para outro arquivo (em geral, um repositório de configurações: a chave iria parar lá). Nesse
último caso, escreva à mão, num editor, a linha `export OPENROUTER_API_KEY='<a chave>'` num arquivo que fique fora
do repositório e que o seu perfil já leia (muitos lêem `~/.zshrc.local`).

**Não guarde o perfil numa pasta sincronizada (iCloud, OneDrive, Dropbox, Google Drive) nem num repositório público
de configurações:** a chave está em texto puro lá.

### Windows com Git Bash

1. No menu Iniciar, digite `variáveis` e abra **Editar as variáveis de ambiente para sua conta** → abre a janela
   das variáveis, com a lista de cima para o seu usuário.
2. Na lista de cima, clique em **Novo** → abre a caixa com nome e valor.
3. Nome: `OPENROUTER_API_KEY`; valor: cole a chave → os dois campos preenchidos.
4. **OK** na caixa e **OK** na janela → a janela fecha.
5. Feche o editor e o terminal por completo e abra de novo (bloco 4). Se a chave ainda não chegar, saia da sua
   conta do Windows e entre de novo.

## Bloco 4 — Reabrir o agente

O agente só enxerga a chave se for aberto **depois** de ela ser gravada.

- **Agente no terminal:** feche a janela do terminal (ou digite `exit`), abra outra, entre na pasta do projeto e
  abra o agente de novo → o agente começa sem histórico.
- **Agente dentro do editor (extensão):** feche o editor por completo (no Mac, ⌘Q; fechar só a janela não basta) e
  abra de novo pelo ícone → o editor reabre na pasta do projeto.

Depois, peça: **continue a configuração dos revisores**.

## Chave colada na conversa, ou vazada

1. Abra `https://openrouter.ai/settings/keys` → você vê a chave na lista, pelo nome.
2. Apague (ou desative) essa chave → ela some da lista ou aparece desativada; quem tiver o texto dela não usa mais.
3. Crie outra (bloco 2) e guarde (bloco 3).
