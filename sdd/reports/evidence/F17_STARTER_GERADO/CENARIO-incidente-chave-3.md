# incidente-chave, execução 3 — resposta integral do subagente (contexto novo, cópia cen-incidente-3)

`sdd-seguranca v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

**Status:** `Segurança · incidente: ⏸️ 1 Fechar a porta · ⬜ 2 Guardar a evidência · ⬜ 3 Medir o estrago · ⬜ 4 Corrigir a causa · ⬜ 5 Comunicar · ⬜ 6 Registrar`
(São as seis etapas de um vazamento, nesta ordem: primeiro trancar, depois entender. ⏸️ quer dizer que estou parado esperando você fazer a etapa 1.)

**O que foi feito:** Conferi o projeto: a chave não aparece no código nem no histórico do git. O vazamento é só o print. Não alterei nada.

**Parado: só você consegue trocar a chave, e isso vem antes de tudo.**
A chave de serviço do Supabase é a senha mestra do seu banco. Quem tem essa chave lê, altera e apaga qualquer dado, sem passar pela RLS (a regra do banco que decide quem vê cada linha). Apagar o print do grupo é bom, mas não resolve: quem viu ou salvou a imagem continua com a chave. O que resolve é trocar a chave, e isso se faz no painel do Supabase.

Antes de começar, anote a hora de cada passo. Essas horas vão para o registro do incidente.

1. Abra supabase.com/dashboard, entre no projeto e vá em **Project Settings → API Keys**.
   Na tela: a lista de chaves do projeto.
2. Olhe como começa a chave que aparece no print:
   - **se começa com `sb_secret_`**: clique para criar uma chave secreta nova (botão parecido com "New secret key").
     Na tela: duas chaves secretas, a antiga e a nova.
   - **se começa com `eyJ`** (é o formato antigo, chamado "service_role"): abra a aba das chaves novas ("Publishable and secret API keys") e crie uma chave secreta.
     Na tela: uma chave nova começando com `sb_secret_`.
3. Coloque a chave nova onde o app guarda a antiga. Esse lugar é a variável de ambiente: um campo do servidor onde a chave fica guardada, fora do código. Em geral fica na Vercel, em Settings → Environment Variables, ou no próprio Supabase, em Edge Functions → Secrets. Substitua o valor e salve.
   Na tela: a variável salva com o valor novo.
4. Publique o app de novo (na Vercel, "Redeploy") e abra o app para ver se funciona.
   Na tela: o app funcionando como antes.
5. Desative a chave que vazou:
   - **`sb_secret_`**: apague a chave antiga na lista (menu da linha → Delete).
   - **`eyJ`**: na aba "Legacy API Keys", desligue as chaves antigas (botão parecido com "Disable JWT-based API keys"). Atenção: isso desliga também a chave pública antiga, a "anon", que costuma ficar no navegador. Se o seu app usa a anon, troque-a antes pela chave pública nova (`sb_publishable_`), do mesmo jeito do passo 3.
   Na tela: a chave antiga sumiu da lista ou aparece como desligada.

Se você não souber onde o app usa a chave, faça o passo 5 mesmo assim. Deixar o app fora do ar algumas horas sai mais barato do que deixar o banco aberto. Depois a gente acerta o app.

**O que eu não fiz:** não troquei nem desliguei nenhuma chave (não tenho acesso ao seu painel). Não apaguei registros. Não falei com ninguém do grupo. E não apague você também os registros de acesso do Supabase: são eles que vão mostrar se alguém usou a chave.

**Para quando você voltar:** me diga **em que dia e hora você mandou o print no grupo**, **quantas pessoas estão no grupo** e **que tipo de dado fica nesse banco** (por exemplo: dados de clientes, CPF, folha). Se não souber algum, responda "não sei". Com isso eu sei de que período olhar os registros.

Quando terminar, me peça de novo, eu continuo daqui.

**Próximo passo:** com a chave trocada, guardamos os registros e vemos se alguém usou a chave.
