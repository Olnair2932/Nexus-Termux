#!/bin/bash

shopt -s nullglob

# Extensões suportadas
arquivos=(
    *.mp3
    *.webm
    *.wmv
)

# Ordena alfabeticamente (ignora maiúsculas/minúsculas)
IFS=$'\n' arquivos=($(printf '%s\n' "${arquivos[@]}" | sort -f))

contador=1

for arquivo in "${arquivos[@]}"; do
    extensao="${arquivo##*.}"

    # Remove numeração antiga, se existir
    nome=$(echo "$arquivo" | sed -E 's/^[0-9]+[[:space:]]*-[[:space:]]*//')

    novo_nome=$(printf "%02d - %s" "$contador" "$nome")

    if [[ "$arquivo" != "$novo_nome" ]]; then
        mv -n -- "$arquivo" "$novo_nome"
        echo "$arquivo -> $novo_nome"
    fi

    ((contador++))
done

echo
echo "Concluído!"
