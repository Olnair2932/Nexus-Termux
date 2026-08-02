#!/usr/bin/env bash

ROOT="$HOME/sentinela_dev/public/assets/docs/Playlist"
REGISTRY="$HOME/sentinela_dev/script_registry.json"

ACTION=$1
PARAMS=$2

get_script() {
  jq -r ".\"$ACTION\".primary" "$REGISTRY"
}

get_fallbacks() {
  jq -r ".\"$ACTION\".fallback[]" "$REGISTRY"
}

execute_script() {
  local script=$1

  if [ ! -f "$ROOT/$script" ]; then
    return 1
  fi

  echo "[ROUTER v2] Executando: $script"
  bash "$ROOT/$script" "$PARAMS"
  return $?
}

PRIMARY=$(get_script)

if [ "$PRIMARY" == "null" ]; then
  echo "[ROUTER v2] Ação desconhecida: $ACTION"
  exit 1
fi

# tenta principal
execute_script "$PRIMARY"
STATUS=$?

# se falhar, tenta fallback
if [ $STATUS -ne 0 ]; then
  echo "[ROUTER v2] Falha no principal, tentando fallback..."

  for fb in $(get_fallbacks); do
    echo "[ROUTER v2] Tentando fallback: $fb"
    execute_script "$fb" && exit 0
  done

  echo "[ROUTER v2] Todos os scripts falharam"
  exit 1
fi
