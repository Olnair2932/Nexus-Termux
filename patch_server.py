#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import sys

ARQUIVO = Path("server.js")

if not ARQUIVO.exists():
    print("server.js não encontrado.")
    sys.exit(1)

texto = ARQUIVO.read_text(encoding="utf-8")

marcador = 'let acaoRouter = intent.acao;'

bloco = r'''

            if (intent.acao === "executar_comando") {

                try {

                    const retorno = execSync(
                        `python3 shell_executor.py ${JSON.stringify(intent.params)}`,
                        {
                            cwd: CONFIG.ROOT,
                            encoding: "utf8"
                        }
                    );

                    const resultado = JSON.parse(retorno);

                    execResult = resultado;

                    respostaFinal =
                        resultado.stdout ||
                        resultado.stderr ||
                        resultado.erro ||
                        "Comando executado.";

                    break;

                } catch (e) {

                    respostaFinal =
                        "Erro ao executar comando Shell: " + e.message;

                    break;

                }

            }

'''

if bloco.strip() in texto:
    print("Bloco já existe.")
    sys.exit(0)

if marcador not in texto:
    print("Marcador não encontrado.")
    sys.exit(1)

texto = texto.replace(
    marcador,
    marcador + bloco,
    1
)

ARQUIVO.write_text(texto, encoding="utf-8")

print("server.js atualizado com sucesso.")
