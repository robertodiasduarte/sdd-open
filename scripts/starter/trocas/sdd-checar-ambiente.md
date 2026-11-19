# Trocas da sdd-checar-ambiente para o starter: as skills se atualizam pelo npx, não pelo init.

## scripts/checar.sh
<<<< antes
               "git init, rode o init do sdd-open de novo (ele traz a skill sdd-iniciar-repo, que falta ao lado desta) e peça a sdd-iniciar-repo"
====
               "a skill sdd-iniciar-repo faz isso; atualize as skills: npx skills add robertodiasduarte/sdd-starter -a <claude-code ou codex> -g -y"
>>>> depois

## SKILL.md
<<<< antes
**8. Revisores da revisão adversarial** (só no modo normal, e só em projeto com `sdd/bin/adversarial-review.sh`)
- `review.revisor1` ou `review.auditor` vazios no `sdd/config.yaml` **e** no `git config` deste computador
  (`git config --get sdd.revisor1`, `sdd.auditor`) ⇒ ⚠️ "Os revisores da revisão adversarial não estão configurados —
  sem eles, a publicação pede para seguir sem revisão.", com a skill `sdd-configurar-revisores`.
- Revisor ou auditor no OpenRouter e a chave fora do ambiente (`[ -z "${OPENROUTER_API_KEY:-}" ]`, só a existência;
  nunca `echo`, `env` ou `ps`) ⇒ ⚠️ com a mesma skill. **Nunca 🔴**: a revisão se dispensa com motivo.
====
>>>> depois

## scripts/checar.sh
<<<< antes
# ── 8. revisores da revisão adversarial (F28) ────────────────────────────────
# Só em projeto com a revisão do SDD Open (o starter não tem). Nunca 🔴: a revisão se dispensa com motivo. A chave do
# OpenRouter só tem a existência testada; o valor nunca é lido. O slot do time (sdd/config.yaml) vence o git config.
revisor_de() {   # $1 = revisor1 | auditor
  local v
  v="$(awk -v k="$1" '
    /^[^[:space:]#]/ { dentro = ($0 ~ /^review:[[:space:]]*(#.*)?$/); next }
    dentro && $0 ~ "^[[:space:]]+" k ":" { sub("^[[:space:]]+" k ":[[:space:]]*", ""); sub(/[[:space:]]+#.*$/, ""); sub(/[[:space:]]+$/, "");
                                          gsub(/^["'\'']|["'\'']$/, ""); print; exit }' "${RAIZ}/sdd/config.yaml" 2>/dev/null)"
  [ -n "${v}" ] || v="$(git -C "${RAIZ}" config --get "sdd.$1" 2>/dev/null)"
  printf '%s' "${v}"
}
if [ -f "${RAIZ}/sdd/bin/adversarial-review.sh" ]; then
  REV1="$(revisor_de revisor1)"; AUD1="$(revisor_de auditor)"
  if [ -z "${REV1}" ] || [ -z "${AUD1}" ]; then
    add_arrumar "Os revisores da revisão adversarial não estão configurados — sem eles, a publicação pede para seguir sem revisão." \
                "peça ao agente: use a skill sdd-configurar-revisores (ela conduz passo a passo)"
  fi
  case "${REV1},${AUD1}" in
    *openrouter*)
      if [ -z "${OPENROUTER_API_KEY:-}" ]; then
        add_arrumar "A revisão adversarial usa o OpenRouter e a chave dele (OPENROUTER_API_KEY) não está no ambiente deste agente — a revisão vai parar por credencial." \
                    "peça ao agente: use a skill sdd-configurar-revisores (ela confere se a chave está gravada e diz o que falta)"
      fi ;;
  esac
fi
====
# (No starter não há revisão adversarial: o aviso dos revisores é só do SDD Open.)
>>>> depois
