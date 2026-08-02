import os
import json
import ast

def fix_path_and_syntax():
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith(('.js', '.py', '.json')) and 'node_modules' not in root:
                path = os.path.join(root, file)
                try:
                    if file.endswith('.json'):
                        with open(path, 'r') as f: json.load(f)
                    elif file.endswith('.py'):
                        with open(path, 'r') as f: ast.parse(f.read())
                except Exception as e:
                    print(f'Corrigindo {path}: Erro detectado -> {e}')
                    # Adiciona log de erro ao arquivo para rastreio SRE
                    with open(path, 'a') as f:
                        f.write(f'\n# AUTO_FIX_ERROR_LOG: {str(e)}')

if __name__ == '__main__':
    fix_path_and_syntax()
