#!/data/data/com.termux/files/usr/bin/bash

FILE=$1

if [ -z "$FILE" ]; then
  echo "Uso: ./nexus_replay.sh logs/arquivo.json"
  exit 1
fi

echo "[REPLAY NEXUS] Executando log: $FILE"
cat "$FILE"
echo ""
echo "[REPLAY] Simulação concluída"
