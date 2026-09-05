# Fragmento — EARS (gramática dos Acceptance Tests)

> Reusável. Lido pelo `/define` (Step 4.5) e pelo `/bug-pipeline` (DEFINE de fix).
> EARS = Easy Approach to Requirements Syntax (Alistair Mavin, Rolls-Royce 2009).
> **Por quê:** cada padrão mapeia mecanicamente num tipo de teste do Verify Gate, e o
> padrão *Unwanted* obriga a enumerar o comportamento indesejado ANTES do build — a
> classe de bug que as landmines do playbook (`sdd/playbook.md`) mostram que mais escapa (provedor que responde "enviado" sem entregar,
> knob ausente, clamp de régua…).

## Regras

1. **Keywords em inglês** (When/While/If-Then/Where/shall — âncora grepável); corpo em PT-BR.
2. Todo AT usa **exatamente um** padrão da tabela e declara **um** comportamento observável.
3. **Bugfix ⇒ ≥1 cláusula "shall continue to"** (não-regressão): o que NÃO pode mudar,
   escrito como requisito, vira entrada de regressão no gate.
4. Adjetivo sem número não é critério ("rápido" → "em <2s").
5. **Máx ~10 ATs por DEFINE** — acima disso o gate vira cerimônia; agrupar por risco ou
   cortar o que não é MUST.
6. **Considerar OBRIGATORIAMENTE os padrões State (While), Unwanted (If/Then) e Optional
   (Where)** — são as 3 classes que mais mordem nesta plataforma: estado não lido, erro
   silencioso (provedor que responde "enviado" sem entregar), flag de config (ex.: `ehMatriz`). "Considerar" = para cada um dos
   3, ou existe ≥1 AT ou o DEFINE registra em 1 linha por que o padrão não se aplica.
7. **⛔ EARS não cobre UX visual** (estética, contraste, craft percebido) — isso é gate
   `manual-ux`/rubrica, nunca AT EARS.
8. **Rastreabilidade AT→gate:** todo AT declara na coluna `Gate (kind)` o tipo de teste que
   o cobre, e o `cmd` do `## Verify Gate` deve exercitar cada AT declarado — AT sem
   cobertura no gate = DEFINE incompleto.

## Os 5 padrões + não-regressão

| Padrão | Forma | Exemplo | Gate (`kind`) |
|---|---|---|---|
| **Ubiquitous** | The ⟨system⟩ **shall** ⟨response⟩ | O sistema shall exibir o menu principal em toda página autenticada | `test`/`typecheck` |
| **Event-driven** | **When** ⟨trigger⟩, the ⟨system⟩ **shall** ⟨response⟩ | **When** o cliente envia a resposta, the system **shall** gravar `turno='atendente'` | `test` (dispara evento, asserta estado) |
| **State-driven** | **While** ⟨state⟩, the ⟨system⟩ **shall** ⟨response⟩ | **While** o pedido estiver arquivado, the system **shall** ocultar o botão de edição | `test` (fixture de estado) |
| **Unwanted behaviour** | **If** ⟨trigger indesejado⟩, **then** the ⟨system⟩ **shall** ⟨response⟩ | **If** o provedor de mensagens estiver desconectado, **then** the system **shall** marcar a mensagem como não-entregue | `smoke`/`test` **negativo** (provocar pelo caminho real, nunca só o caminho feliz) |
| **Optional feature** | **Where** ⟨feature presente⟩, the ⟨system⟩ **shall** ⟨response⟩ | **Where** o kill-switch estiver ligado, the system **shall** suprimir o envio | `test` (matriz de flag) |
| **Non-regression** (bugfix) | The ⟨system⟩ **shall continue to** ⟨comportamento existente⟩ | The system **shall continue to** enviar o relatório semanal na segunda às 08h00 | `test` (entrada de regressão) |

Combinações (Complex) são permitidas: `While ⟨estado⟩, when ⟨trigger⟩, the system shall …`.

## Mapa padrão → teste (como derivar o Verify Gate)

- **When** → o teste dispara o evento e asserta a resposta.
- **If/Then** → teste **negativo**: provoca o gatilho indesejado pelo caminho real e asserta o
  tratamento (nunca só o caminho feliz).
- **While** → o teste monta a fixture do estado e asserta o comportamento sob ele.
- **Where** → o teste roda com a feature ligada E desligada (matriz).
- **shall continue to** → vira caso de regressão explícito no gate do fix.

## Checklist de recusa (o `/define` aplica em DEFINE novo/retocado)

- [ ] Todo AT usa um padrão da tabela (keyword presente)
- [ ] ≥1 AT **Unwanted** quando a feature tem gatilho indesejado plausível (provider fora,
      linha ausente, permissão negada, fila cheia)
- [ ] Padrões **While / If-Then / Where** considerados: AT presente ou N.A. justificado
      em 1 linha (as 3 classes que mais mordem: estado · erro silencioso · flag de config)
- [ ] Bugfix: ≥1 **shall continue to**
- [ ] Zero adjetivo sem número
- [ ] ≤ ~10 ATs no total
- [ ] Nenhum AT de UX visual (estética/craft → `manual-ux`, fora do EARS)
- [ ] Todo AT tem `kind` na coluna Gate e é coberto pelo `cmd` do `## Verify Gate`

> **Limite deste slice (v5.0):** a conformidade EARS é disciplina de prompt + este checklist —
> não há linter mecânico de ATs. Linter determinístico + rastreabilidade AT-ID→assert do gate
> composto são escopo da **v5.1** (ver PESQUISA_FRAMEWORKS_SDD_2026-08-15).
