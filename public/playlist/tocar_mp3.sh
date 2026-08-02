#!/data/data/com.termux/files/usr/bin/bash

MUSICA="$1"
DIR="$(cd "$(dirname "$0")" && pwd)"

ARQUIVO=$(find "$DIR" -type f \( -iname "*$MUSICA*" \) | head -n 1)

if [ -z "$ARQUIVO" ]; then
    echo "❌ Arquivo não encontrado: $MUSICA"
    exit 1
fi

echo "▶️ Reproduzindo: $ARQUIVO"

termux-media-player stop >/dev/null 2>&1
termux-media-player play "$ARQUIVO"
