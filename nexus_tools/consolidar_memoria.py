#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def carregar_memoria():
    arquivo = ROOT / "brain.json"

    if not arquivo.exists():
        return {}

    with arquivo.open(encoding="utf-8") as f:
        return json.load(f)


def extrair_registros(dados):
    if isinstance(dados, list):
        return dados

    if not isinstance(dados, dict):
        return []

    for chave in ("memoria", "memorias", "memory", "registros", "conhecimento"):
        valor = dados.get(chave)

        if isinstance(valor, list):
            return valor

    return []


def consolidar(registros):
    vistos = set()
    resultado = []

    for registro in registros:
        if isinstance(registro, str):
            texto = registro.strip()

            if not texto:
                continue

            chave = texto.casefold()

            if chave not in vistos:
                vistos.add(chave)
                resultado.append(texto)

        elif isinstance(registro, dict):
            texto = registro.get("texto") or registro.get("conteudo")

            if isinstance(texto, str):
                texto = texto.strip()

                if not texto:
                    continue

                chave = texto.casefold()

                if chave not in vistos:
                    vistos.add(chave)
                    resultado.append(texto)

    return resultado


def main():
    try:
        dados = carregar_memoria()
        registros = extrair_registros(dados)
        consolidados = consolidar(registros)

        print("🧠 CONSOLIDAÇÃO DE MEMÓRIA")
        print("==========================")
        print(f"Registros encontrados: {len(registros)}")
        print(f"Registros consolidados: {len(consolidados)}")

        removidos = len(registros) - len(consolidados)

        if removidos > 0:
            print(f"Duplicados identificados: {removidos}")
        else:
            print("Duplicados identificados: 0")

        print()
        print("✅ Análise concluída.")
        print("ℹ️ A memória original não foi alterada.")

    except json.JSONDecodeError as erro:
        print(f"❌ brain.json contém JSON inválido: {erro}")
        raise SystemExit(1)

    except Exception as erro:
        print(f"❌ Erro ao consolidar memória: {erro}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
