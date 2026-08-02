
from logger import registrar

def consulta(pergunta):
    registrar("CONSULTA", pergunta)

def aprendizado(assunto):
    registrar("APRENDIZADO", assunto)

def erro(msg):
    registrar("ERRO", msg)

def melhoria(msg):
    registrar("MELHORIA", msg)

if __name__ == "__main__":
    consulta("teste")
    aprendizado("sed")
    erro("Erro de exemplo")
    melhoria("Otimização aplicada")
    print("✅ events.py funcionando.")
