#!/usr/bin/env bash

ROOT="$HOME/sentinela_dev/public/assets/docs/Playlist"
REGISTRY="$HOME/sentinela_dev/script_registry.json"

ACTION=$1
PARAMS=$2

SCRIPT=$(jq -r ".\"$ACTION\"" "$REGISTRY")

if [ "$SCRIPT" == "null" ]; then
  echo "[ROUTER] Ação desconhecida: $ACTION"
  exit 1
fi

FULL_PATH="$ROOT/$SCRIPT"

if [ ! -f "$FULL_PATH" ]; then
  echo "[ROUTER] Script não encontrado: $FULL_PATH"
  exit 1
fi

echo "[ROUTER] Executando $SCRIPT com params: $PARAMS"

bash "$FULL_PATH" "$PARAMS"
