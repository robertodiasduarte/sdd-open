# incidente-chave, série 2, execução 1 — resposta integral (contexto novo, cópia cen2-incidente-1, INCIDENTE.md consertado)

sdd-seguranca v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest

**Status:** `Segurança (incidente): ⏸️ 1 Fechar a porta · ⬜ 2 Guardar a evidência · ⬜ 3 Medir o alcance · ⬜ 4 Corrigir a causa · ⬜ 5 Comunicar · ⬜ 6 Registrar`

**O que foi feito:** Estou tratando isso como vazamento de verdade. A chave de serviço é a chave secreta do Supabase, a senha que o seu app usa para falar com o banco. Quem tem essa chave age em nome do app e passa por cima de todas as regras sobre quem vê o quê. Procurei a chave neste projeto, só lendo, e ela não está em nenhum arquivo nem no histórico do git daqui. Não alterei nada.

**Agora: etapa 1, Fechar a porta**
Parei aqui porque só você consegue trocar a chave. A troca é feita no painel do Supabase, com o seu login. Enquanto a chave antiga funcionar, qualquer pessoa do grupo, ou quem recebeu o print encaminhado, pode ler, mudar ou apagar qualquer tabela do seu banco. Apagar a mensagem do grupo não resolve, porque as cópias continuam nos celulares. A porta só fecha quando a chave antiga parar de funcionar.

Veja no print como a chave começa e siga o caminho que corresponde. Os nomes dos menus podem variar um pouco. Se o print cortou o começo, faça os dois caminhos, para nenhuma chave antiga continuar valendo.

**Se a chave começa com `sb_secret_`:**
1. Entre em supabase.com/dashboard, abra o projeto e vá em **Project Settings → API Keys**. Deve aparecer a lista "Secret keys".
2. Crie uma chave secreta nova e copie o valor. Ela aparece na lista ao lado da antiga.
3. Apague a chave antiga, a que aparece no print. Ela some da lista e, a partir daí, o print não abre mais nada. As partes do app que usavam essa chave param até o passo 4.
4. No lugar onde o app roda (Vercel, funções do Supabase ou outro), abra a variável de ambiente que guarda a chave secreta, ponha o valor novo e publique de novo. A variável de ambiente é o lugar do servidor onde a chave fica guardada fora do código. Depois disso, o app volta a funcionar.

**Se a chave começa com `eyJ`** (é a chave "service_role" do modelo antigo, que não se troca sozinha):
1. No painel do projeto, vá em **Project Settings → JWT Keys** e gere um segredo novo em "Legacy JWT secret". A chave do print para de funcionar na hora. A chave pública do navegador também muda, e todo mundo que estava logado no app precisa entrar de novo.
2. Em **Project Settings → API Keys**, na aba das chaves antigas (legacy), copie a nova "service_role" e a nova "anon". A anon é a chave pública, feita para ficar no navegador.
3. No lugar onde o app roda, troque as duas variáveis de ambiente pelos valores novos e publique de novo. O app volta a funcionar com as chaves novas.

Quando a chave antiga tiver parado de funcionar, anote a data e a hora em que você terminou.

O que eu **não** fiz: não troquei nenhuma chave, não mexi no app nem no git e não falei com ninguém do grupo. Também não apague a mensagem do grupo agora. Antes, guarde uma cópia do print com a data e a hora em que foi enviado e quem estava no grupo, porque vamos precisar disso na próxima etapa.

Quando terminar, me peça de novo, eu continuo daqui.

**Próximo passo:** Com a chave trocada, guardamos a evidência e vemos se alguém chegou a usá-la.
