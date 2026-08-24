#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from nexus_tools.firebase_storage import ler_arquivo
except Exception as erro:
    print(
        "❌ Não foi possível carregar o armazenamento Firebase: "
        + str(erro)
    )
    raise SystemExit(1)


def main():
    if len(sys.argv) < 2:
        print("Uso: buscar_arquivo <nome_arquivo>")
        raise SystemExit(1)

    nome = Path(sys.argv[1].strip()).name

    if not nome:
        print("❌ Nome de arquivo inválido.")
        raise SystemExit(1)

    destino = ROOT / nome

    if destino.exists():
        print(f"📄 Arquivo já existe localmente: {destino}")
        return

    try:
        dados = ler_arquivo(nome)
    except Exception as erro:
        print(
            "❌ Não foi possível consultar o Firebase: "
            + str(erro)
        )
        raise SystemExit(1)

    if not dados:
        print(f"❌ Arquivo não encontrado no Firebase: {nome}")
        raise SystemExit(1)

    conteudo = dados.get("conteudo")

    if conteudo is None:
        print(f"❌ Arquivo encontrado, mas sem conteúdo: {nome}")
        raise SystemExit(1)

    try:
        destino.write_text(str(conteudo), encoding="utf-8")
    except Exception as erro:
        print(
            "❌ Arquivo encontrado no Firebase, "
            "mas não foi possível recriá-lo localmente: "
            + str(erro)
        )
        raise SystemExit(1)

    print(f"☁️ Arquivo recuperado do Firebase: {nome}")
    print(f"📄 Arquivo recriado: {destino}")


if __name__ == "__main__":
    main()
