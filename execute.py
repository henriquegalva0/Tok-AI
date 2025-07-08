import os
import random
import subprocess
import sys
from config import nome_do_video

# Lista de scripts disponíveis para execução aleatória
# Adicione novos arquivos aqui conforme necessário
scripts_disponiveis = ["ball_circles.py", "2_balls_circles.py"]

if not scripts_disponiveis:
    print("Nenhum script disponível na lista.")
    sys.exit(1)

# Escolhe um script aleatoriamente
script_escolhido = random.choice(scripts_disponiveis)
caminho_completo_script = os.path.join(os.path.dirname(__file__), script_escolhido)

print(f"Executando aleatoriamente o script: {script_escolhido}")

# Executa o script usando o interpretador Python atual
# sys.executable garante que o mesmo interpretador Python que está rodando 'executar.py' será usado
try:
    subprocess.run([sys.executable, "create_subtitles.py"])
except Exception as e:
    print(f"Ocorreu um erro ao executar o script 'create_subtitles.py': {e}")

try:
    subprocess.run([sys.executable, caminho_completo_script])
except Exception as e:
    print(f"Ocorreu um erro ao executar o script '{script_escolhido}': {e}")