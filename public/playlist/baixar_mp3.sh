#!/bin/bash
# Script: baixar_mp3.sh
# Descrição: Busca e faz o download de áudio via yt-dlp

DIR="$(cd "$(dirname "$0")" && pwd)"
NOME="$1"

if [ -z "$NOME" ]; then
    echo "❌ Erro: Nenhum nome de música fornecido."
    exit 1
fi

mkdir -p "$DIR"

echo "🔍 NEXUS buscando: $NOME..."

# --restrict-filenames: Garante nomes compatíveis com sistemas sem problemas de espaço
# --audio-quality 0: Melhor qualidade possível
python -m yt_dlp \
    -x \
    --audio-format mp3 \
    --audio-quality 0 \
    --force-ipv4 \
    --default-search "ytsearch1" \
    --no-check-certificate \
    --restrict-filenames \
    --trim-filenames 180 \
    --embed-metadata \
    --no-playlist \
    --output "$DIR/%(title)s.%(ext)s" \
    "$NOME"

if [ $? -eq 0 ]; then
    echo "✅ Download finalizado com sucesso!"
    exit 0
else
    echo "❌ Erro ao baixar música via yt-dlp."
    exit 1
fi
