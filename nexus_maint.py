
import os
import sys

def manter_nexus():
    files = [f for f in os.listdir('.') if f.endswith('.json') or f.endswith('.py')]
    for file in files:
        with open(file, 'r') as f:
            data = f.read()
            if 'NEXUS_CORE' not in data:
                with open(file, 'a') as f_out:
                    f_out.write(f'\n# NEXUS_CORE_MAINTENANCE_{file}')
    print('Sistema mantido e sincronizado.')

if __name__ == '__main__':
    manter_nexus()
