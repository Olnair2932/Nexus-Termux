#!/usr/bin/env python3

import sys
import json

print("=== NEXUS GERADOR DE CÓDIGO ===")

if len(sys.argv) < 2:
    print("Erro: nenhuma solicitação recebida.")
    raise SystemExit(1)

solicitacao = " ".join(sys.argv[1:]).strip()

print(f"Solicitação: {solicitacao}")
print()
print("Gerador preparado.")
print("A geração será realizada pelo Nexus/Gemini.")
