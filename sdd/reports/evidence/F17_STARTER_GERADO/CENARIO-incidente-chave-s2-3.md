# incidente-chave, série 2, execução 3 — resposta integral (contexto novo, cópia cen2-incidente-3, INCIDENTE.md consertado)

sdd-seguranca v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest

**Status**: `Segurança (incidente): ⏸️ 1 Fechar a porta · ⬜ 2 Guardar a evidência · ⬜ 3 Medir o estrago · ⬜ 4 Corrigir a causa · ⬜ 5 Comunicar · ⬜ 6 Registrar`
(⏸️ quer dizer que estou esperando você. "Fechar a porta" é tornar inútil a chave que apareceu no print.)

**Por que parei aqui**: a chave de serviço só pode ser trocada no painel do Supabase, e só você tem acesso a ele. A chave de serviço é a chave secreta do Supabase, a senha que o seu app usa para falar com o banco com poder total. Até você trocá-la, quem viu o print pode ler, alterar e apagar todos os dados do app, sem passar pela RLS (a regra do banco que decide quem vê cada linha). **Por enquanto nada foi fechado: a chave do print ainda funciona.**

**Faça agora, no painel do Supabase** (uns 10 minutos). O app pode ficar fora do ar entre o passo 2 e o passo 4. Esse é o preço de fechar primeiro, e vale a pena.

1. Entre em supabase.com/dashboard, abra o projeto do app e vá em **Project Settings → API Keys**. Vai aparecer a lista de chaves do projeto.
2. Ache a chave do print pelo começo dela e desative-a:
   - **Se começa com `sb_secret_`**: clique em **New secret key** para criar a nova. Depois, na linha da chave antiga, abra o menu **⋯ → Delete**. O que você vai ver: a chave antiga some da lista.
   - **Se começa com `eyJ`** (é a `service_role`, na aba **Legacy API keys**): essa não dá para apagar sozinha. Na aba das chaves novas, crie uma **secret key** e confira se já existe uma **publishable key**, a chave pública, feita para ficar no navegador. Depois, na aba Legacy, clique em **Disable legacy API keys**. O que você vai ver: as chaves antigas aparecem como desativadas. Isso desliga também a chave pública antiga, por isso no passo 3 você troca as duas.
3. Abra o painel do serviço onde o app está hospedado (Vercel, Netlify, Lovable ou outro) e procure as variáveis de ambiente. Elas guardam as senhas do app fora do código. Troque o valor da chave de serviço (o nome costuma ser parecido com `SUPABASE_SERVICE_ROLE_KEY`) pela secret key nova. Se a sua chave era do tipo `eyJ`, troque também a chave pública (o nome costuma ser parecido com `SUPABASE_ANON_KEY`) pela publishable key.
4. Publique o app de novo e abra-o. Ele deve funcionar normalmente. Se aparecer erro de chave, ficou faltando trocar alguma variável do passo 3.

Não cole a chave aqui nem em lugar nenhum: eu não preciso dela. E não gaste tempo agora apagando o print do grupo, porque apagar não muda nada para quem já viu. O que protege os dados é trocar a chave. Quando a chave estiver trocada, e não antes, guarde uma cópia do print e anote a hora em que ele foi enviado e a hora em que você fez a troca.

**O que não foi feito**: não mexi no Supabase nem no app, porque a troca só você pode fazer. Procurei nos arquivos desta pasta e não achei nenhuma chave escrita, mas também não há código do app aqui. Por isso não sei onde a chave é usada. Se ela também for usada nas funções que rodam dentro do Supabase (Edge Functions), me avise, porque elas podem precisar de um ajuste. Sei que o app usa Supabase porque você me contou. Ainda não vimos se alguém chegou a usar a chave.

Quando terminar, me peça de novo, eu continuo daqui. Se travar em alguma tela, me diga o que aparece nela.

**Próximo passo**: com a chave trocada, guardamos os registros do Supabase e vemos se alguém usou a chave.
