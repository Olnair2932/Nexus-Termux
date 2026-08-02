#!/usr/bin/env bash

FILE=$1
FEEDBACK=$2

if [ -z "$FILE" ] || [ -z "$FEEDBACK" ]; then
  echo "Uso: ./nexus_feedback.sh arquivo.json positivo|negativo"
  exit 1
fi

jq ".feedback=\"$FEEDBACK\"" "$FILE" > tmp.json && mv tmp.json "$FILE"

echo "[FEEDBACK] Atualizado para: $FEEDBACK"
