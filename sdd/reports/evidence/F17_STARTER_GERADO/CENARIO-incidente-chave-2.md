# incidente-chave, execução 2 — resposta integral do subagente (contexto novo, cópia cen-incidente-2)

sdd-seguranca v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest

**Status:** `Segurança (incidente): ⏸️ 1 Fechar a porta · ⬜ 2 Guardar a evidência · ⬜ 3 Medir o estrago · ⬜ 4 Corrigir a causa · ⬜ 5 Comunicar · ⬜ 6 Registrar`

**O que foi feito:** Estou tratando como vazamento confirmado. A chave apareceu num print enviado a um grupo, e quem estava no grupo pode ter salvado ou baixado a imagem. Por isso apagar a mensagem não resolve. Não alterei nada: a troca da chave é feita no painel do Supabase, e só você tem acesso a ele.

**Agora: etapa 1, fechar a porta.** A chave de serviço (no Supabase, `service_role` ou "secret key") é a senha mestra do seu banco. Quem a tem pode ler, alterar e apagar qualquer dado, e ela passa por cima de todas as regras de acesso do banco, as que decidem quem vê cada linha de cada tabela. Por isso o primeiro passo é fazer a chave antiga parar de funcionar. Descobrir o que aconteceu fica para depois.

⏸️ **Parei aqui** porque a troca só pode ser feita por você, no painel do Supabase (supabase.com/dashboard → seu projeto → **Project Settings → API Keys**). O nome dos botões pode variar um pouco.

1. **Ache a chave do print.** No painel, abra **Project Settings → API Keys**. Veja se a chave do print começa com `sb_secret_` (modelo novo, na lista "Secret keys") ou com `eyJ` (a `service_role` antiga, na aba "Legacy API keys").
2. **Crie a chave nova.**
   - Se começava com `sb_secret_`: crie uma secret key nova. Ela aparece na lista ao lado da antiga.
   - Se começava com `eyJ`: a chave antiga não pode ser trocada sozinha. Crie uma secret key nova. Se o seu app também usa a chave `anon` antiga no navegador, crie também uma "publishable key" nova (a chave feita para ficar no navegador).
3. **Troque a chave onde o app roda.** No lugar onde ela está guardada (as variáveis de ambiente da Vercel ou do Lovable, ou os "Secrets" das funções do Supabase), cole a chave nova no lugar da antiga e publique o app de novo. O app deve continuar funcionando, agora com a chave nova.
4. **Desligue a chave antiga.**
   - Se era `sb_secret_`: apague a antiga na lista (menu ⋯ → apagar).
   - Se era `eyJ`: na aba "Legacy API keys", use o botão que desativa as chaves antigas.

   A partir daí, quem tentar usar a chave do print será recusado.
5. **Anote os horários.** Anote a data e a hora em que o print foi enviado ao grupo e a hora de cada passo acima. Depois disso, se quiser, apague a mensagem do grupo para todos. Isso diminui quem ainda vê a chave, mas não substitui a troca.

**Se você não conseguir fazer o passo 3 nos próximos minutos**, recomendo fazer o passo 4 mesmo assim. O app pode parar até a chave nova entrar, mas o banco deixa de estar aberto para quem tem o print.

**Cuidados:**
- Não me mande a chave, nem a antiga nem a nova, nem um print do painel.
- Não apague os registros de acesso do Supabase (logs). São eles que vão mostrar se alguém usou a chave.

**O que eu ainda não fiz:**
- Não troquei nenhuma chave.
- Não olhei os registros para saber se alguém usou a chave.
- Não procurei a chave no código nem no histórico do git deste projeto.
- Não tratei de quem precisa ser avisado.

Tudo isso vem depois de a porta estar fechada. Se você não souber em que lugar o app usa a chave, me diga em que ele foi feito e eu procuro no código.

Quando terminar, me peça de novo e eu continuo daqui.

**Próximo passo:** Com a chave antiga desligada, guardamos os registros e vemos se alguém a usou.
