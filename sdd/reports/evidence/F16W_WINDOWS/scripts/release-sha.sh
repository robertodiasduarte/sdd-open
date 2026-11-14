#!/usr/bin/env bash
# release-sha.sh <pasta com os arquivos baixados da Release>: confere cada arquivo contra o SHA256SUMS.txt dela
cd "$1" || exit 64
shasum -a 256 -c SHA256SUMS.txt
