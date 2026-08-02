#!/usr/bin/env bash

FILE="$HOME/sentinela_dev/nexus_learning.json"
ACTION=$1
FEEDBACK=$2

if [ -z "$ACTION" ] || [ -z "$FEEDBACK" ]; then
  echo "Uso: ./nexus_learn.sh acao positivo|negativo"
  exit 1
fi

VALUE=$(jq -r ".\"$ACTION\"" "$FILE")

if [ "$VALUE" == "null" ]; then
  VALUE=0
fi

if [ "$FEEDBACK" == "positivo" ]; then
  VALUE=$((VALUE + 1))
else
  VALUE=$((VALUE - 1))
fi

jq ".\"$ACTION\"=$VALUE" "$FILE" > tmp.json && mv tmp.json "$FILE"

echo "[LEARNING] $ACTION agora tem score $VALUE"
