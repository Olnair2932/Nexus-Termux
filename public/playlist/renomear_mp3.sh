#!/usr/bin/env bash

set -euo pipefail

BASE="$(cd "$(dirname "$0")" && pwd)"
LOG="$BASE/rename_log.txt"

mkdir -p "$BASE"
cd "$BASE"

echo "==============================" >> "$LOG"
echo "DATA: $(date)" >> "$LOG"
echo "INICIANDO RENOMEAÇÃO INTELIGENTE" >> "$LOG"

# função simples para remover acentos
remove_acentos() {
    echo "$1" \
    | sed 'y/áàãâäéèêëíìîïóòõôöúùûüç/aaaaaeeeeiiiiooooouuuuc/' \
    | sed 'y/ÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ/AAAAAEEEEIIIIOOOOOUUUUC/'
}

echo "[INFO] Processando arquivos..."

for file in *.mp3; do
    [ -e "$file" ] || continue

    base_name="${file%.mp3}"

    # remove lixo de caracteres
    clean=$(echo "$base_name" \
        | sed 's/[[:space:]]\+/ /g' \
        | sed 's/[^a-zA-Z0-9À-ÿ -]//g' \
        | sed 's/^ *//;s/ *$//')

    # remove acentos para padronização IA-friendly
    clean_no_accent=$(remove_acentos "$clean")

    # tenta detectar padrão simples "Artista - Música"
    if [[ "$clean_no_accent" == *"-"* ]]; then
        final_name="$clean_no_accent.mp3"
    else
        final_name="$clean_no_accent.mp3"
    fi

    # se não mudou, ignora
    if [ "$file" = "$final_name" ]; then
        echo "[OK] Sem mudança: $file"
        continue
    fi

    echo "[RENAME] $file -> $final_name"
    echo "$file -> $final_name" >> "$LOG"

    mv -n "$file" "$final_name"

done

echo "FINALIZADO" >> "$LOG"
echo "[DONE] Biblioteca organizada."
