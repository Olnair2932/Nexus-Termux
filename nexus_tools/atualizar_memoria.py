#!/usr/bin/env python3

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent

SKILLS_FILE = BASE / "skills.json"
BRAIN_FILE = BASE / "brain.json"

BACKUP_FILE = BASE / "brain.json.backup_antes_atualizar_memoria.json"


def carregar_json(caminho):
    if not caminho.exists():
        return {}

    with caminho.open("r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho, dados):
    with caminho.open("w", encoding="utf-8") as f:
        json.dump(
            dados,
            f,
            ensure_ascii=False,
            indent=2
        )
        f.write("\n")


def main():

    print("=== ATUALIZADOR DE MEMÓRIA NEXUS ===")

    if not SKILLS_FILE.exists():
        print("❌ skills.json não encontrado.")
        return 1

    if not BRAIN_FILE.exists():
        print("❌ brain.json não encontrado.")
        return 1

    try:
        skills_data = carregar_json(SKILLS_FILE)
        brain = carregar_json(BRAIN_FILE)

        skills = skills_data.get("skills", {})

        if not isinstance(skills, dict):
            print("❌ Estrutura inválida em skills.json.")
            return 1

        # Backup antes de alterar a memória
        shutil.copy2(BRAIN_FILE, BACKUP_FILE)

        ferramentas = {}

        for nome, skill in sorted(skills.items()):
            ferramentas[nome] = {
                "executor": skill.get("executor", ""),
                "script": skill.get("script", ""),
                "descricao": skill.get("descricao", ""),
                "frases": skill.get("frases", [])
            }

        # Preserva todo o brain existente.
        # Apenas substitui/atualiza o catálogo de ferramentas.
        brain["ferramentas"] = ferramentas

        brain["memoria_ferramentas_atualizada"] = (
            datetime.now(timezone.utc).isoformat()
        )

        salvar_json(BRAIN_FILE, brain)

        print()
        print("✅ Memória atualizada.")
        print(f"Ferramentas sincronizadas: {len(ferramentas)}")
        print(f"Backup: {BACKUP_FILE}")
        print(f"Memória: {BRAIN_FILE}")

        if "teste_tool" in ferramentas:
            print()
            print("✅ teste_tool encontrado na memória.")
            print(
                "   Executor:",
                ferramentas["teste_tool"]["executor"]
            )
            print(
                "   Script:",
                ferramentas["teste_tool"]["script"]
            )

        return 0

    except json.JSONDecodeError as e:
        print("❌ JSON inválido:", e)
        return 1

    except Exception as e:
        print("❌ Erro ao atualizar memória:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
