import pygame
import math
import sys
import random
import os
import time

finalizar_gravacao = False
game_start_time = None

def random_color():
    return (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))

def random_confirm():
    return random.choice([True, False])

# Inicialização do Pygame
pygame.init()

# ==================== CONFIGURAÇÕES DA JANELA ====================
LARGURA = 480  # Largura da janela
ALTURA = 854    # Altura da janela
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Efeito Interativo de Bolas - Sistema de Cores")

# ==================== SISTEMA DE CORES (CONFIGURÁVEIS) ====================
# Configurações de randomização
RANDOMIZAR_COR_BOLA = random_confirm()        # True = cor aleatória, False = cor específica
RANDOMIZAR_COR_CONTORNO = random_confirm()    # True = cor aleatória, False = cor específica/lista

# Cor específica da bola (usada quando RANDOMIZAR_COR_BOLA = False)
COR_BOLA = random_color()  # Vermelho - cor padrão da bola

# Cores específicas dos contornos (usadas quando RANDOMIZAR_COR_CONTORNO = False)
# Pode ser uma cor única ou uma lista de cores para alternar
CORES_CONTORNO = [
    (255, 100, 100),  # Vermelho claro
    (100, 100, 255),  # Azul claro
    (100, 255, 100),  # Verde claro
    (255, 255, 100),  # Amarelo claro
    (255, 100, 255),  # Magenta claro
]

# Cores base para randomização
CORES_ALEATORIAS = [
    (255, 0, 0),    # Vermelho
    (0, 255, 0),    # Verde
    (0, 0, 255),    # Azul
    (255, 255, 0),  # Amarelo
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Ciano
    (255, 128, 0),  # Laranja
    (128, 0, 255),  # Roxo
    (255, 192, 203), # Rosa
    (0, 128, 128),  # Verde-azulado
]

# Outras cores
COR_FUNDO = (0, 0, 0)        # Preto - cor do fundo

# ==================== CONFIGURAÇÕES DAS BOLAS (CONFIGURÁVEIS) ====================
RAIO_BOLA = 15             # Raio R das bolas (tamanho médio para pequeno)
GRAVIDADE = 0.7             # Força da gravidade aplicada às bolas
FORCA_QUIQUE = 1.6          # Força do quique (0.0 a 1.0) - quanto maior, mais energia mantém
ACELERACAO_QUIQUE = 1.2     # Multiplicador de aceleração após cada quique
VELOCIDADE_MAXIMA = 15      # Velocidade máxima que as bolas podem atingir

# ==================== CONFIGURAÇÕES DOS CONTORNOS (CONFIGURÁVEIS) ====================
QUANTIDADE_CONTORNOS_SIMULTANEOS = 30  # Quantidade de contornos simultâneos na tela
RAIO_MINIMO_CONTORNO = RAIO_BOLA * 5   # Tamanho mínimo = 5R
RAIO_MAXIMO_INICIAL = 300              # Raio máximo inicial dos contornos
VELOCIDADE_DIMINUICAO = 8            # Velocidade que os contornos diminuem de tamanho
ESPESSURA_CONTORNO = 6               # Espessura da linha do contorno
INTERVALO_CRIACAO = 2                # Intervalo em frames para criar novos contornos

# ==================== TIMER CONFIGURATION ====================
GAME_DURATION = 30  # 30 seconds

class Bola:
    """Classe que representa uma bola no jogo"""
    
    def __init__(self, x, y, cor):
        """
        Inicializa uma bola
        x, y: posição inicial da bola
        cor: cor da bola (RGB)
        """
        self.x = x
        self.y = y
        self.vx = 0  # Velocidade horizontal inicial
        self.vy = 0  # Velocidade vertical inicial
        self.raio = RAIO_BOLA
        self.cor = cor
        self.quiques = 0  # Contador de quiques para acelerar
    
    def atualizar(self):
        """Atualiza a posição da bola aplicando física"""
        # Aplica gravidade à velocidade vertical
        self.vy += GRAVIDADE
        
        # Limita a velocidade máxima para evitar bolas muito rápidas
        velocidade_atual = math.sqrt(self.vx**2 + self.vy**2)
        if velocidade_atual > VELOCIDADE_MAXIMA:
            fator_limitacao = VELOCIDADE_MAXIMA / velocidade_atual
            self.vx *= fator_limitacao
            self.vy *= fator_limitacao
        
        # Atualiza a posição baseada na velocidade
        self.x += self.vx
        self.y += self.vy
        
        # Verifica colisão com as bordas da tela
        self._colisao_bordas()
    
    def _colisao_bordas(self):
        """Verifica e resolve colisões com as bordas da tela"""
        # Borda esquerda
        if self.x - self.raio <= 0:
            self.x = self.raio
            self.vx = -self.vx * FORCA_QUIQUE
            self._acelerar_apos_quique()
        
        # Borda direita
        elif self.x + self.raio >= LARGURA:
            self.x = LARGURA - self.raio
            self.vx = -self.vx * FORCA_QUIQUE
            self._acelerar_apos_quique()
        
        # Borda superior
        if self.y - self.raio <= 0:
            self.y = self.raio
            self.vy = -self.vy * FORCA_QUIQUE
            self._acelerar_apos_quique()
        
        # Borda inferior
        elif self.y + self.raio >= ALTURA:
            self.y = ALTURA - self.raio
            self.vy = -self.vy * FORCA_QUIQUE
            self._acelerar_apos_quique()
    
    def _acelerar_apos_quique(self):
        """Acelera a bola após um quique"""
        self.quiques += 1
        # Aplica aceleração gradual, mas limitada
        if self.quiques <= 15:  # Limita a quantidade de acelerações
            self.vx *= ACELERACAO_QUIQUE
            self.vy *= ACELERACAO_QUIQUE
    
    def colisao_com_contorno(self, contorno):
        """
        Verifica e resolve colisão com um contorno circular
        contorno: objeto Contorno para verificar colisão
        Retorna True se houve colisão, False caso contrário
        """
        # Calcula a distância entre o centro da bola e o centro do contorno
        distancia = math.sqrt((self.x - contorno.x)**2 + (self.y - contorno.y)**2)
        
        # Verifica se a bola está DENTRO do contorno e próxima da borda
        diferenca_raios = abs(distancia - contorno.raio)
        
        # A bola colide se está dentro do contorno E próxima da borda
        if distancia < contorno.raio and diferenca_raios <= self.raio + ESPESSURA_CONTORNO:
            # Calcula o ângulo da colisão (do centro do contorno para a bola)
            if distancia > 0:
                angulo = math.atan2(self.y - contorno.y, self.x - contorno.x)
                
                # Posiciona a bola DENTRO do contorno, mas longe da borda
                nova_distancia = contorno.raio - self.raio - ESPESSURA_CONTORNO
                if nova_distancia > 0:
                    self.x = contorno.x + math.cos(angulo) * nova_distancia
                    self.y = contorno.y + math.sin(angulo) * nova_distancia
                
                # Calcula a velocidade normal (direção da colisão)
                velocidade_normal = self.vx * math.cos(angulo) + self.vy * math.sin(angulo)
                
                # Inverte a velocidade normal se a bola está se movendo em direção à borda
                if velocidade_normal > 0:
                    self.vx -= 2 * velocidade_normal * math.cos(angulo) * FORCA_QUIQUE
                    self.vy -= 2 * velocidade_normal * math.sin(angulo) * FORCA_QUIQUE
                    
                    # Acelera a bola após o quique
                    self._acelerar_apos_quique()
                    
                    return True  # Indica que houve colisão
        
        return False  # Não houve colisão
    
    def desenhar(self, tela):
        """Desenha a bola na tela"""
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)

class Contorno:
    """Classe que representa um contorno circular móvel e colorido"""
    
    def __init__(self, x, y, raio_inicial, cor):
        """
        Inicializa um contorno
        x, y: posição inicial do contorno
        raio_inicial: raio inicial do contorno
        cor: cor do contorno (RGB)
        """
        self.x = x
        self.y = y
        self.raio = raio_inicial
        self.raio_inicial = raio_inicial
        self.ativo = True
        self.alpha = 255
        self.destruido = False
        self.cor = cor
    
    def atualizar(self):
        """Atualiza o contorno (diminuição de tamanho apenas)"""
        if self.ativo and not self.destruido:
            # Diminui o raio gradualmente
            self.raio -= VELOCIDADE_DIMINUICAO
            
            # Se o raio ficou muito pequeno, desativa o contorno
            if self.raio <= RAIO_MINIMO_CONTORNO:
                self.ativo = False
        
        # Se foi destruído, aplica efeito fade
        if self.destruido:
            self.alpha -= 15  # Velocidade do fade
            if self.alpha <= 0:
                self.ativo = False

    
    def destruir(self):
        """Marca o contorno para ser destruído com efeito fade"""
        self.destruido = True
    
    def desenhar(self, tela):
        """Desenha o contorno na tela com sua cor específica"""
        if self.ativo and self.raio > 0:
            if self.destruido:
                # Desenha com transparência se está sendo destruído
                superficie_temp = pygame.Surface((self.raio * 2 + 20, self.raio * 2 + 20), pygame.SRCALPHA)
                pygame.draw.circle(superficie_temp, (*self.cor, max(0, self.alpha)), 
                                 (self.raio + 10, self.raio + 10), int(self.raio), ESPESSURA_CONTORNO)
                tela.blit(superficie_temp, (self.x - self.raio - 10, self.y - self.raio - 10))
            else:
                # Desenha normalmente com sua cor
                pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), int(self.raio), ESPESSURA_CONTORNO)

class GeradorContornos:
    """Classe responsável por gerar contornos infinitamente com sistema de cores"""
    
    def __init__(self):
        self.contador_frames = 0
        self.proximo_raio = RAIO_MAXIMO_INICIAL
        self.centro_x = LARGURA // 2
        self.centro_y = (ALTURA // 2) * 1.3
        self.indice_cor_lista = 0  # Para alternar cores quando usando lista
    
    def _obter_cor_contorno(self):
        """
        Obtém a cor do próximo contorno baseado nas configurações
        Retorna uma tupla RGB
        """
        if RANDOMIZAR_COR_CONTORNO:
            # Cor aleatória
            return random.choice(CORES_ALEATORIAS)
        else:
            # Cor específica ou lista de cores
            if isinstance(CORES_CONTORNO, list):
                # Lista de cores - alterna em ordem
                cor = CORES_CONTORNO[self.indice_cor_lista]
                self.indice_cor_lista = (self.indice_cor_lista + 1) % len(CORES_CONTORNO)
                return cor
            else:
                # Cor única
                return CORES_CONTORNO
    
    def atualizar(self, contornos):
        """
        Atualiza o gerador e cria novos contornos quando necessário
        contornos: lista atual de contornos
        """
        self.contador_frames += 1
        
        # Verifica se é hora de criar um novo contorno
        if self.contador_frames >= INTERVALO_CRIACAO:
            # Conta quantos contornos ativos existem
            contornos_ativos = [c for c in contornos if c.ativo and not c.destruido]
            
            # Se há menos contornos que o máximo, cria um novo
            if len(contornos_ativos) < QUANTIDADE_CONTORNOS_SIMULTANEOS:
                # Obtém a cor do contorno
                cor_contorno = self._obter_cor_contorno()
                
                # Cria novo contorno no centro
                novo_contorno = Contorno(self.centro_x, self.centro_y, self.proximo_raio, cor_contorno)
                contornos.append(novo_contorno)
                
                # Incrementa o raio para o próximo contorno
                self.proximo_raio += 40
                
                # Reseta o contador
                self.contador_frames = 0

def obter_cor_bola():
    """
    Obtém a cor da bola baseado nas configurações
    Retorna uma tupla RGB
    """
    if RANDOMIZAR_COR_BOLA:
        # Cor aleatória
        return random.choice(CORES_ALEATORIAS)
    else:
        # Cor específica
        return COR_BOLA

def check_timer():
    """Verifica se o timer de 30 segundos terminou"""
    global game_start_time, finalizar_gravacao
    if game_start_time is None:
        return False
    
    elapsed_time = time.time() - game_start_time
    seconds_passed = int(elapsed_time)
    print(f"Tempo decorrido: {seconds_passed} segundos")
    
    if elapsed_time >= GAME_DURATION:
        finalizar_gravacao = True
        return True
    return False

def main():
    """Função principal do jogo"""
    global game_start_time, finalizar_gravacao
    
    # Inicializa o timer
    game_start_time = time.time()
    print("Jogo iniciado! Timer de 30 segundos começou.")
    
    # Inicializa o relógio para controlar FPS
    clock = pygame.time.Clock()
    
    # Inicializa lista de contornos vazia
    contornos = []
    
    # Cria o gerador de contornos infinitos
    gerador = GeradorContornos()
    
    # Calcula o centro da tela para posicionar a bola
    centro_x = LARGURA // 2 + 30
    centro_y = ALTURA // 2
    
    # Cria UMA ÚNICA bola no centro da tela
    cor_bola = obter_cor_bola()
    bola = Bola(centro_x, centro_y, cor_bola)
    
    # Dá uma pequena velocidade inicial para a bola se mover
    bola.vx = random.uniform(-3, 3)
    bola.vy = random.uniform(-3, 3)
    
    print("Aplicativo iniciado com sistema de cores personalizado!")
    print(f"CONFIGURAÇÕES:")
    print(f"- Randomizar cor da bola: {RANDOMIZAR_COR_BOLA}")
    print(f"- Randomizar cor dos contornos: {RANDOMIZAR_COR_CONTORNO}")
    if not RANDOMIZAR_COR_BOLA:
        print(f"- Cor da bola: {COR_BOLA}")
    if not RANDOMIZAR_COR_CONTORNO:
        if isinstance(CORES_CONTORNO, list):
            print(f"- Cores dos contornos (lista): {len(CORES_CONTORNO)} cores")
        else:
            print(f"- Cor dos contornos: {CORES_CONTORNO}")
    print("Pressione ESC ou feche a janela para sair")
    
    contornos_destruidos = 0
    
    # Loop principal do jogo
    rodando = True
    while rodando:
        # Verifica o timer
        if check_timer():
            print("Tempo esgotado! Finalizando jogo...")
            rodando = False
            break
        
        # Processa eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_SPACE:
                    # Tecla ESPAÇO: muda cor da bola (se randomização estiver ativa)
                    if RANDOMIZAR_COR_BOLA:
                        bola.cor = obter_cor_bola()
        
        # Atualiza o gerador de contornos
        gerador.atualizar(contornos)
        
        # Atualiza a bola
        bola.atualizar()
        
        # Atualiza contornos e verifica colisões
        contornos_restantes = []
        for contorno in contornos:
            contorno.atualizar()
            
            # Verifica colisão com a bola
            if contorno.ativo and not contorno.destruido and bola.colisao_com_contorno(contorno):
                contorno.destruir()
                contornos_destruidos += 1
            
            # Mantém contornos que ainda estão ativos
            if contorno.ativo:
                contornos_restantes.append(contorno)
        
        # Atualiza lista de contornos
        contornos = contornos_restantes
        
        # ==================== DESENHO ====================
        # Limpa a tela com cor de fundo preta
        TELA.fill(COR_FUNDO)
        
        # Desenha todos os contornos
        for contorno in contornos:
            contorno.desenhar(TELA)
        
        # Desenha a bola
        bola.desenhar(TELA)

        # Atualiza a tela
        pygame.display.update()
        clock.tick(60)
    
    # Finaliza o Pygame
    pygame.quit()
    print(f"Aplicativo finalizado! Contornos destruídos: {contornos_destruidos}")
    finalizar_gravacao = True
    sys.exit()

# ==================== EXECUÇÃO DO PROGRAMA ====================
if __name__ == "__main__":
    """Executa o programa quando o arquivo é executado diretamente"""
    main()
