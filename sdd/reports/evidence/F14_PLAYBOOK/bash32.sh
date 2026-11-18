#!/bin/bash
# Sem mapfile, declare -A nem expansão em maiúsculas nos 2 scripts novos: sai 0 só sem achado.
if grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^' sdd/bin/playbook-curator.sh .agents/skills/sdd-new-session/scripts/copiar-docs.sh; then exit 1; fi
/bin/bash -n sdd/bin/playbook-curator.sh && /bin/bash -n .agents/skills/sdd-new-session/scripts/copiar-docs.sh && echo "sem achado; sintaxe ok no bash 3.2"
