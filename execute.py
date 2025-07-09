import os
import random
import subprocess
import sys
import threading
import time
import pyautogui
import cv2
import numpy as np
import psutil
import win32gui
import win32con
import win32api

# Lista de scripts disponíveis para execução aleatória
scripts_disponiveis = ["MarbleGames/two_balls_circles.py","MarbleGames/ball_circles.py", "MarbleGames/img_coliseum.py"]

if not scripts_disponiveis:
    print("Nenhum script disponível na lista.")
    sys.exit(1)

# Escolhe um script aleatoriamente
script_escolhido = random.choice(scripts_disponiveis)
caminho_completo_script = os.path.join(os.path.dirname(__file__), script_escolhido)

print(f"Executando aleatoriamente o script: {script_escolhido}")

# Configurações de gravação
resolution = (480,854)
filename = "output.avi"
fps = 24.0  # FPS mais baixo para duração correta

# Configuração do codec
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # type: ignore
out = cv2.VideoWriter(filename, fourcc, fps, resolution)

if not out.isOpened():
    print("Erro: Não foi possível configurar o codec de vídeo")
    sys.exit(1)

print("Codec XVID configurado com sucesso")

# Variáveis de controle
script_process = None
pygame_window_handle = None

def find_pygame_window():
    """Encontra a janela do pygame"""
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            # Lista de títulos possíveis dos scripts pygame
            titulos_pygame = [
                "Efeito Interativo de Bolas - Sistema de Cores",
                "Efeito Interativo de Bolas - Contornos Móveis e Coloridos", 
                "Jogo de Bolas com Contorno Fixo"
            ]
            if any(titulo in window_title for titulo in titulos_pygame):
                windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows[0] if windows else None

def get_window_screenshot(hwnd):
    """Captura somente o conteúdo da janela (área do cliente)"""
    try:
        # Tamanho da área do cliente
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bottom - top

        # Posição do canto superior esquerdo da área do cliente na tela
        point = win32gui.ClientToScreen(hwnd, (left, top))
        x, y = point

        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Redimensiona para a resolução desejada
        frame = cv2.resize(frame, resolution)
        return frame
    except Exception as e:
        print(f"Erro ao capturar janela: {e}")
        return None

def check_finalizar_gravacao():
    """Verifica se deve finalizar a gravação"""
    try:
        # Verifica se o processo do script ainda está rodando
        if script_process and script_process.poll() is not None:
            return True
        
        # Verifica se a janela do pygame ainda existe
        if pygame_window_handle:
            try:
                if not win32gui.IsWindow(pygame_window_handle):
                    return True
            except:
                return True
        
        return False
    except:
        return False

# Inicia o script
script_process = subprocess.Popen([sys.executable, caminho_completo_script])

print("Iniciando gravação...")

# Aguarda um pouco para o script inicializar
time.sleep(2)

# Aguarda a janela do pygame aparecer
print("Aguardando janela do pygame...")
for _ in range(50):  # Tenta por 5 segundos
    pygame_window_handle = find_pygame_window()
    if pygame_window_handle:
        print("Janela do pygame encontrada!")
        break
    time.sleep(0.1)

if not pygame_window_handle:
    print("Aviso: Janela do pygame não encontrada, usando captura de tela completa")

# Loop principal de gravação
frame_count = 0
last_time = time.time()
try:
    while True:
        # Captura o frame
        if pygame_window_handle:
            frame = get_window_screenshot(pygame_window_handle)
        else:
            # Fallback para captura de tela completa
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, resolution)
        
        if frame is not None:
            # Escreve o frame no vídeo
            success = out.write(frame)
            if not success:
                print("Aviso: Falha ao escrever frame")
            
            frame_count += 1
            if frame_count % int(fps) == 0:  # Print a cada segundo
                print(f"Frames gravados: {frame_count}")
        
        # Verifica se deve finalizar
        if check_finalizar_gravacao():
            print("Sinal de finalização recebido")
            break
        
        # Espera para manter o FPS estável
        elapsed = time.time() - last_time
        sleep_time = max(0, (1/fps) - elapsed)
        time.sleep(sleep_time)
        last_time = time.time()

except KeyboardInterrupt:
    print("Gravação interrompida pelo usuário")
except Exception as e:
    print(f"Erro durante a gravação: {e}")
finally:
    # Finaliza o processo do script se ainda estiver rodando
    if script_process and script_process.poll() is None:
        print("Finalizando processo do script...")
        script_process.terminate()
        try:
            script_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            script_process.kill()
    
    # Limpeza final
    if out and out.isOpened():
        out.release()
    
    print(f"Gravação finalizada. Arquivo salvo como: {filename}")
    print(f"Total de frames gravados: {frame_count}")
