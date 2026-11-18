# incidente-chave, execução 1 — resposta integral do subagente (contexto novo, cópia cen-incidente-1)

sdd-seguranca v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest

**Status:** `Segurança · incidente: ⏸️ 1 Fechar a porta · ⬜ 2 Guardar a evidência · ⬜ 3 Dimensionar · ⬜ 4 Corrigir a causa · ⬜ 5 Comunicar · ⬜ 6 Registrar`
("Fechar a porta" quer dizer deixar a chave vazada sem uso. "Dimensionar" quer dizer descobrir que dado ficou exposto e se alguém usou a chave.)

**O que foi feito:** Estou tratando como vazamento confirmado. Um print num grupo pode já ter sido salvo, encaminhado ou copiado, e apagar a mensagem não desfaz isso. Nesta pasta só estão as ferramentas do método, não o código do app, então ainda não sei onde a chave está configurada. Nada foi alterado.

**Agora: etapa 1, Fechar a porta.** A chave de serviço é a senha mestra do seu banco. Quem tem essa chave passa por cima de todas as regras de acesso (a RLS, que é a regra do banco que decide quem vê e quem muda cada linha de uma tabela). Com ela, a pessoa lê, altera ou apaga qualquer dado. A única forma de fechar é trocar a chave no Supabase: enquanto a antiga valer, a porta continua aberta. Faça isso antes de investigar o resto.

⏸️ **Parado.** A troca é feita no painel do Supabase, e só você tem acesso a ele.

1. Anote a data e a hora em que o print foi para o grupo, e a hora de agora. Assim saberemos desde quando a chave está exposta.
2. Entre em supabase.com/dashboard, abra o projeto e vá em **Project Settings → API Keys**. Vai aparecer a lista de chaves do projeto.
3. Veja como começa a chave que aparecia no print:
   - **Se começa com `sb_secret_`:** crie uma chave secreta nova e depois apague a que vazou (pelo botão de excluir ao lado dela). Na tela, a antiga deve sumir da lista e a nova deve aparecer.
   - **Se começa com `eyJ`** (é a chave antiga, chamada "service_role"): essa chave não tem como ser apagada sozinha. O caminho é a área **JWT Keys** (ou "JWT Settings"), onde se gera um segredo novo. Isso também troca a chave pública (anon) e desconecta todo mundo que estava logado no app. É o preço de fechar a porta. Na tela, as duas chaves devem ficar diferentes das de antes.
   - **Se não achar o botão ou não puder fazer agora:** em **Project Settings → General**, pause o projeto (Pause project). O app sai do ar, mas a chave para de abrir o banco até você fazer a troca.
4. Ponha a chave nova onde o app usa a antiga (a variável de ambiente no lugar em que ele está publicado, por exemplo Vercel, Lovable ou os segredos das funções do Supabase) e publique de novo. Se a chave era do tipo `eyJ`, troque também a chave pública. Até você fazer isso, a parte do app que usa a chave para de funcionar. Isso é esperado: melhor parado do que aberto.
5. Depois da troca, apague o print do grupo e peça a quem salvou que apague também. Isso reduz as cópias, mas não substitui a troca.

**O que não foi feito:** Não entrei no Supabase, não troquei nem apaguei nenhuma chave e não mexi no app. Também ainda não olhei os registros de acesso, que ficam para a etapa 3. Até lá, não apague nada no banco nem nos registros: eles mostram se alguém usou a chave.

Quando terminar, me diga três coisas: que tipo de chave era (`sb_secret_` ou `eyJ`, **sem colar a chave aqui**), a hora do print e a hora da troca, e onde o app está publicado. Quando terminar, me peça de novo, eu continuo daqui.

**Próximo passo:** Com a chave trocada, guardamos os registros e vemos se alguém usou a chave.
