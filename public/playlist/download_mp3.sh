#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
NOME="$1"
mkdir -p "$DIR"
echo "🔍 NEXUS buscando via Python 3.14: $NOME..."

# Adicionamos --no-part para não criar arquivos temporários .part (economiza RAM no J7)
# Adicionamos --prefer-free-formats para facilitar a vida do processador
python -m yt_dlp \
    -x \
    --audio-format mp3 \
    --force-ipv4 \
    --no-check-certificate \
    --default-search "ytsearch1" \
    --no-part \
    --output "$DIR/%(title)s.%(ext)s" \
    "$NOME"

if [ $? -eq 0 ]; then
    echo "✅ Download de '$NOME' finalizado!"
else
    echo "❌ Erro Crítico. Verifique o espaço ou instale o FFmpeg (pkg install ffmpeg)."
fi
