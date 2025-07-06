import os
import random
import subprocess
import sys

# Define o caminho para a pasta modelos
# os.path.dirname(__file__) obtém o diretório do arquivo executar.py
# os.path.join() constrói um caminho compatível com o sistema operacional
modelos_path = os.path.join(os.path.dirname(__file__), "modelos")

# Lista todos os arquivos na pasta modelos e filtra apenas os .py (exceto __init__.py)
try:
    scripts_disponiveis = [f for f in os.listdir(modelos_path) if f.endswith(".py") and f != "__init__.py"]
except FileNotFoundError:
    print(f"Erro: A pasta 'modelos' não foi encontrada em '{modelos_path}'. Certifique-se de que a estrutura de pastas está correta.")
    sys.exit(1)

if not scripts_disponiveis:
    print(f"Nenhum script Python (.py) encontrado na pasta '{modelos_path}'.")
    sys.exit(1)

# Escolhe um script aleatoriamente
script_escolhido = random.choice(scripts_disponiveis)
caminho_completo_script = os.path.join(modelos_path, script_escolhido)

print(f"Executando aleatoriamente o script: {script_escolhido}")

# Executa o script usando o interpretador Python atual
# sys.executable garante que o mesmo interpretador Python que está rodando 'executar.py' será usado
try:
    subprocess.run([sys.executable, caminho_completo_script])
except Exception as e:
    print(f"Ocorreu um erro ao executar o script '{script_escolhido}': {e}")