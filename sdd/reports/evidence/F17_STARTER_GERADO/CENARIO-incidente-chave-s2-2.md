# incidente-chave, série 2, execução 2 — resposta integral (contexto novo, cópia cen2-incidente-2, INCIDENTE.md consertado)

sdd-seguranca v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest

**Status**: `Segurança · incidente: ⏸️ 1 Fechar a porta · ⬜ 2 Guardar a evidência · ⬜ 3 Medir o estrago · ⬜ 4 Corrigir a causa · ⬜ 5 Comunicar · ⬜ 6 Registrar`
(⏸️ quer dizer que estou parado esperando você. "Fechar a porta" é fazer a chave vazada parar de funcionar.)

**O que foi feito**: Tratei o caso como vazamento. Um print mandado num grupo já é uma cópia fora do seu controle, e apagar a mensagem não alcança quem já viu ou salvou. A chave de serviço do Supabase é a senha que o seu app usa para falar com o banco. Ela passa por cima de todas as regras de quem vê o quê: quem tem essa chave consegue ler, alterar e apagar qualquer dado. Também conferi esta pasta do projeto, e a chave não aparece em nenhum arquivo nem no histórico do git.

**Agora: etapa 1, Fechar a porta**: Parei aqui porque a troca da chave só se faz no painel do Supabase, com o seu login, e eu não tenho acesso a ele. Faça isto agora, antes de qualquer outra coisa. Anotar, avisar e investigar vêm depois.

1. Abra https://supabase.com/dashboard, entre no projeto e vá em **Project Settings → API Keys**. Na tela aparece a lista de chaves do projeto.
2. Veja como começa a chave que estava no print:
   - **Se começa com `sb_secret_`**: na aba das chaves novas ("publishable and secret"), crie uma chave secreta nova. Depois apague a antiga pelo menu "⋯" ao lado dela. Na tela, a chave antiga some da lista.
   - **Se começa com `eyJ`** (é a chave antiga, chamada `service_role`, e fica na aba "Legacy"): não dá para trocar só ela. Na aba das chaves novas, crie uma chave publishable e uma secret. Logo em seguida, desative as chaves antigas em **Disable JWT-based API keys**. Na tela, a aba Legacy passa a mostrar as chaves como desativadas. Atenção: isso desliga também a chave pública antiga (`anon`), e o app fica fora do ar até você terminar o passo 3. Recomendo aceitar esses minutos parado: enquanto a chave de serviço estiver valendo, o banco inteiro está exposto.
3. Ponha a chave nova no lugar onde o app guarda a antiga e publique o app de novo. Esse lugar costuma ser o painel da hospedagem (na Vercel, Settings → Environment Variables) ou, no Supabase, Edge Functions → Secrets. Se a sua chave começava com `eyJ`, troque também a chave pública que fica no navegador pela publishable nova. Ao final, o app volta a funcionar com as chaves novas.
4. Só depois disso, apague o print do grupo e peça a quem o baixou que apague também. Isso diminui as cópias, mas não substitui a troca da chave.

Assim que terminar o passo 2, anote a hora: ela entra no registro do incidente.

Depois do passo 2, a chave do print não abre mais nada. O que continua em aberto é saber se alguém a usou enquanto ela valia. Isso é a próxima etapa, feita com os registros do Supabase.

**O que não foi feito**: Não troquei nenhuma chave e não mexi no código nem no banco. Também ainda não verifiquei se alguém usou a chave, nem se é caso de avisar clientes. Isso vem nas etapas 2 a 5.

Se não souber como a chave começa, ou se não achar essa tela, me diga o que aparece em Project Settings → API Keys, sem colar a chave, e eu te guio.

Quando terminar, me peça de novo, eu continuo daqui.

**Próximo passo**: Com a chave trocada, guardamos os registros do Supabase e vemos se alguém a usou.
