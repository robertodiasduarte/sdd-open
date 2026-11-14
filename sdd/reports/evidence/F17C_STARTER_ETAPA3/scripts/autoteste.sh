#!/usr/bin/env bash
# autoteste.sh: os juízes do teste do iniciante contra respostas sabotadas (LM-002), com o log de evidência
cd "$(dirname "$0")/.." || exit 64
{ echo "$ python3 -I scripts/iniciante2.py --autoteste"; python3 -I scripts/iniciante2.py --autoteste; echo "rc=$?"; } > INICIANTE-AUTOTESTE.log 2>&1
cat INICIANTE-AUTOTESTE.log
