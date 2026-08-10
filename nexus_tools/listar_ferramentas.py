import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKILLS_FILE = BASE / "skills.json"


def listar_ferramentas():
    if not SKILLS_FILE.exists():
        print("Arquivo skills.json não encontrado.")
        return

    try:
        dados = json.loads(
            SKILLS_FILE.read_text(encoding="utf-8")
        )

        skills = dados.get("skills", {})

        print("=== FERRAMENTAS NEXUS ===")
        print(f"Total: {len(skills)}")
        print()

        for nome, skill in skills.items():
            executor = skill.get("executor", "desconhecido")
            script = skill.get("script", "")

            print(f"- {nome}")
            print(f"  Executor: {executor}")
            print(f"  Script: {script}")
            print()

    except Exception as e:
        print("Erro ao listar ferramentas:", e)


if __name__ == "__main__":
    listar_ferramentas()
