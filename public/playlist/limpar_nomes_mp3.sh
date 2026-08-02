#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

DIR="/data/data/com.termux/files/home/sentinela_dev/public/assets/docs/Playlist"

echo "[INFO] Iniciando limpeza de nomes em: $DIR"

cd "$DIR"

for file in *.mp3; do
    [ -e "$file" ] || continue

    original="$file"

    # remove extensões e limpa ruído comum
    name=$(echo "$file" \
        | sed 's/\.[mM][pP]3$//' \
        | sed 's/[([][^)]*[)\]]//g' \
        | sed 's/⧸.*//' \
        | sed 's/- .* -/-/' \
        | sed 's/  */ /g' \
        | sed 's/[[:space:]]*$//' \
    )

    new_name="$name.mp3"

    # evita sobrescrever
    if [ "$original" != "$new_name" ]; then
        if [ -e "$new_name" ]; then
            echo "[SKIP] Já existe: $new_name"
        else
            mv "$original" "$new_name"
            echo "[OK] $original -> $new_name"
        fi
    else
        echo "[OK] Sem alteração: $original"
    fi
done

echo "[INFO] Limpeza finalizada"
