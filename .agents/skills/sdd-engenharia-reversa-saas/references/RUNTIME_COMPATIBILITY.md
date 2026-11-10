# Compatibilidade por capacidades

| Capacidade | Uso | Ausência |
|---|---|---|
| Leitura de recursos | Protocolos instalados, fontes e contexto do projeto | Pedir somente o recurso inacessível; não alegar leitura. |
| Pesquisa web | Descobrir e consultar informações públicas atuais | Usar materiais disponíveis; relatar cobertura parcial. |
| Navegação/conector | Observação em conta autorizada, em leitura | Registrar não observação; conta não é pré-requisito. |
| Escrita de arquivos | Três documentos e revisões | Entregar Markdown completo com nomes sugeridos. |
| Python 3.9+ | Lint próprio e testes locais, sem bibliotecas externas | Checklist manual, com status não executado. |
| Skills SDD instaladas | Brainstorm e Define canônicos | Pausar apenas a fase dependente, preservando levantamento. |

Usar conectores disponíveis antes de navegação quando cobrirem a leitura necessária. Não exigir navegador, conector ou modelo específico. Não presumir delegação, rede, execução, login, acesso a APIs ou permissão de escrita.

Resolver caminhos a partir dos recursos reais da skill e das dependências. Os exemplos com `SKILL_ROOT` exigem que o executor defina essa variável para o diretório encontrado; não é variável garantida de plataforma. Os scripts próprios também funcionam com caminhos absolutos, a partir de qualquer pasta corrente. O lint imprime JSON com acentos: precisa da saída padrão em UTF-8 (o padrão do Python 3); com a saída forçada para ASCII, um código de erro acentuado derruba o script com exit 1, sem o JSON.

A skill é instrução operacional de perfil C, sem motor de cálculo profissional. Pesquisa é datada a cada execução; não há período universal de cobertura ou versão permanente dos SaaS. Não há promessa de conformidade jurídica, DLP, autenticação de autorização ou isolamento técnico.

A confirmação de criação foi conversacional, pois o validador de escopo da meta-skill aceita somente quatro áreas profissionais e não engenharia de software. Isso não foi contornado atribuindo uma área falsa nem alterando o validador original. Os lints de pacote são controles diferentes; o que rodou em cada versão está em `manifest.json`.

Não há certificação de execução em todos os agentes fora dos declarados em `manifest.json`. O pacote foi concebido para consumo de documentos no ponto anterior ao Brainstorm. A disponibilidade das skills e regras do projeto precisa ser reconhecida em cada ambiente.
