#!/data/data/com.termux/files/usr/bin/bash

DIR="$HOME/sentinela_dev/logs"
mkdir -p "$DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
FILE="$DIR/nexus_$TIMESTAMP.json"

# lê JSON da entrada padrão
cat > "$FILE"

echo "[NEXUS LOGGER] Salvo em: $FILE"
