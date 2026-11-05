# AVALIACAO: F14_PLAYBOOK — ciclo 2

- **Modo:** veredito · **Base:** HEAD `9b3dad1` · **Data:** 2026-11-05
- **Quem avaliou:** agente de contexto fresco; não viu a conversa do build
- **Evidência:** `sdd/reports/evidence/F14_PLAYBOOK/AVAL2-*.log`, `verify-gate-9b3dad1.log`, `baseline-9b3dad1.log`, `sabotagens-9b3dad1.log`

<<<AVALIACAO
VEREDITO: NEEDS_WORK

## Resumo por AT

PASS: 002 a 020, 022, 023, 025 a 037, 039, 042 a 045 e o Verify Gate (1356 testes, exit 0).
PARCIAL: 021 (N-L1), 024 (N-M1, N-L2 a N-L5), 040 (N-L5).
REPROVA: 001 (N-H1), 041 (N-M2).
NAO_VERIFICADO: 038 (agente de fora do Claude; não rodou).

## Passo 17b à letra

(a) caminho feliz, (b) 2ª release sem nada novo, (c) lição antiga nunca classificada, (d) curador que escreve fora, (e) sessão nova: os 5 funcionam seguindo o texto; a seta do script contradiz o texto em (e) (N-M1).

## Mutantes (`AVAL2-M01`, cópia com `git init`, controle verde antes e depois)

40 plantados, 34 mortos, 6 vivos: troca do `check=` · teto de tamanho do veredito · AVALIACAO do archive · 2 invariantes novas de mesmo ID · acento em `a` · cobertura de DELTA de arquivo com espaço. Dos 12 vivos do ciclo 1, 11 morrem.

## Achados do ciclo 1

FECHADOS: H1, H2, H3, H4, M1, M2, M3, M4, M5 (no texto), M6, M7, M8, L2, L3, L5, L6, L8, L9. REGREDIRAM: L1 (criou N-H1 e N-L1b), L4 (criou N-L1). ABERTOS, pendência declarada: L7, L10.

## ACHADOS novos

### Grave

- **N-H1.** Regressão do conserto L1: veredito longo que começa com "mordeu" perde a contagem ou vira `ajudou`. Com outra célula ✔ na linha, sai `DELTA ajudou+1`; sem ela, rc=1 e a curadoria encerra em `Curadoria: 0 deltas`. Contraria AT-001. Nenhum teste protegia o teto.

### Médios

- **N-M1.** A seta do `--retomar` manda "continue do despacho", e o item 1 do 17b manda ir direto para "Na volta": quem segue a seta refaz selo e snapshot, e a escrita do curador vira linha de base.
- **N-M2.** `--preparar` copia a avaliação de outra feature cujo nome começa igual e segue com dígito: `AVALIACAO_F1_2_20261105.md` entra na feature F1. Contraria AT-041.
- **N-M3.** A contagem dobra numa frente nova da mesma feature quando a evidência não é versionada.

### Leves

- **N-L1.** Linha DELTA de arquivo com espaço nunca passa como AUTO. **N-L1b.** Tabela com o veredito antes da coluna do ID perde o delta.
- **N-L2.** Contador e aposentadoria do mesmo bullet passam no conferidor e param no `--cruzar`.
- **N-L3.** Item 6 com `delta.txt` ausente e `inv-linhas.txt` presente sai 2 e manda corrigir o delta.
- **N-L4.** O texto não trata a pasta temporária perdida nem cria `sdd/reports/briefs/`.
- **N-L5.** `--self-test` sem `git` no PATH sai 1 com Traceback.
- **N-L6.** `estado=ok` aceita origem promovida para `.`, `/`, `..`; `check=..` e `check=sdd` passam; `· tarefa: · motivo: m` passa.
- **N-L7.** O conferidor aceita evidência `colheita.rc:1`, `DESCARTAR ()` e `CONTAMINAÇÃO: nãosei`.
- **N-L8.** 2 invariantes novas com o mesmo ID em `inv-linhas.txt`: a 2ª some em silêncio.
- **N-L9.** Delta real sobre playbook CRLF converte o arquivo para LF.
- **N-L10.** A fronteira não acusa `git branch x` nem `git tag x`.
- **N-L11.** O texto não diz como obter a base no conflito; `NAO_JULGADO` entra no registro; o brief pede o bullet inteiro com `--grep-all`, que trunca; a pergunta cita um ID e o bullet pode nascer com outro.
- **N-L12.** 6 mutantes vivos, acima.

Aviso do avaliador: um log dele (`AVAL2-V2-aposentar-e-bordas.log:40`) cita uma lição real e gera contagem falsa na colheita real da F14: é a pendência L10 acontecendo de verdade; na curadoria desta frente, essa linha precisa de DESCARTAR.
>>>
