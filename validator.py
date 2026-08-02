import os
import json
import ast

def validar_arquivo(caminho):
    try:
        if caminho.endswith('.py'):
            with open(caminho, 'r') as f:
                ast.parse(f.read())
            return True, 'Python OK'
        elif caminho.endswith('.json'):
            with open(caminho, 'r') as f:
                json.load(f)
            return True, 'JSON OK'
        return True, 'Ignorado'
    except Exception as e:
        return False, str(e)

print('Iniciando varredura de integridade...')
for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith(('.py', '.json')) and 'node_modules' not in root:
            path = os.path.join(root, file)
            status, msg = validar_arquivo(path)
            if not status:
                print(f'[ERRO] {path}: {msg}')
            else:
                print(f'[OK] {path}')
