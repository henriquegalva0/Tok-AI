import pygame
import math
import sys
import random
from pyvidplayer import Video
from config import nome_do_video

def random_color():
    return (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))

def random_velocity():
    return random.uniform(2.7, 4.2)

def random_width():
    return random.randint(2, 8)

# Inicialização do Pygame
pygame.init()

vid = Video(f"{nome_do_video}.mp4")
vid.set_size((480, 270))
vid.set_volume(0.5)
vid.seek(270)

# ==================== CONFIGURAÇÕES DA JANELA ====================
LARGURA = 480  # Largura da janela
ALTURA = 854    # Altura da janela
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Efeito Interativo de Bolas - Contornos Móveis e Coloridos")

# ==================== CORES (CONFIGURÁVEIS) ====================
COR_FUNDO = (0, 0, 0)        # Preto - cor do fundo
COR_BOLA_VERMELHA = random_color()  # Vermelho - cor da primeira bola
COR_BOLA_AZUL = random_color()      # Azul - cor da segunda bola
COR_CONTORNO_VERMELHO = COR_BOLA_VERMELHA  # Vermelho claro - contornos vermelhos
COR_CONTORNO_AZUL = COR_BOLA_AZUL     # Azul claro - contornos azuis
COR_CONTORNO_NEUTRO = (255, 255, 255)    # Branco - para referência

# ==================== CONFIGURAÇÕES DAS BOLAS (CONFIGURÁVEIS) ====================
RAIO_BOLA = 15              # Raio R das bolas (tamanho médio para pequeno)
GRAVIDADE = 0.5             # Força da gravidade aplicada às bolas
FORCA_QUIQUE = 1.2         # Força do quique (0.0 a 1.0) - quanto maior, mais energia mantém
ACELERACAO_QUIQUE = 0.9     # Multiplicador de aceleração após cada quique
VELOCIDADE_MAXIMA = 18      # Velocidade máxima que as bolas podem atingir

# ==================== CONFIGURAÇÕES DOS CONTORNOS (CONFIGURÁVEIS) ====================
QUANTIDADE_CONTORNOS_SIMULTANEOS = 8   # Quantidade de contornos simultâneos na tela
RAIO_MINIMO_CONTORNO = RAIO_BOLA * 5   # Tamanho mínimo = 5R
RAIO_MAXIMO_INICIAL = 300              # Raio máximo inicial dos contornos
VELOCIDADE_DIMINUICAO = random_velocity()            # Velocidade que os contornos diminuem de tamanho
ESPESSURA_CONTORNO = random_width()               # Espessura da linha do contorno
INTERVALO_CRIACAO = 15               # Intervalo em frames para criar novos contornos

# ==================== CONFIGURAÇÕES DE MOVIMENTO DOS CONTORNOS ====================
VELOCIDADE_INICIAL_CONTORNO = 10     # Velocidade inicial dos contornos em direção ao centro
ACELERACAO_CONTORNO = 3             # Aceleração inicial dos contornos
DESACELERACAO_CONTORNO = 0.12          # Fator de desaceleração (multiplicador < 1)
DISTANCIA_DESACELERACAO = 100          # Distância do centro onde começa a desaceleração

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
        
        # Determina o tipo da bola baseado na cor
        if cor == COR_BOLA_VERMELHA:
            self.tipo = "vermelho"
        elif cor == COR_BOLA_AZUL:
            self.tipo = "azul"
        else:
            self.tipo = "neutro"
    
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
    
    def colisao_com_bola(self, outra_bola):
        """
        Verifica e resolve colisão entre duas bolas
        outra_bola: a outra bola para verificar colisão
        """
        # Calcula a distância entre os centros das bolas
        distancia = math.sqrt((self.x - outra_bola.x)**2 + (self.y - outra_bola.y)**2)
        
        # Verifica se há colisão
        if distancia < self.raio + outra_bola.raio and distancia > 0:
            # Calcula o ângulo da colisão
            angulo = math.atan2(outra_bola.y - self.y, outra_bola.x - self.x)
            
            # Separa as bolas para evitar sobreposição
            sobreposicao = (self.raio + outra_bola.raio - distancia) / 2
            self.x -= math.cos(angulo) * sobreposicao
            self.y -= math.sin(angulo) * sobreposicao
            outra_bola.x += math.cos(angulo) * sobreposicao
            outra_bola.y += math.sin(angulo) * sobreposicao
            
            # Calcula as novas velocidades após a colisão
            # Velocidade relativa
            vx_rel = self.vx - outra_bola.vx
            vy_rel = self.vy - outra_bola.vy
            
            # Velocidade normal (na direção da colisão)
            velocidade_normal = vx_rel * math.cos(angulo) + vy_rel * math.sin(angulo)
            
            # Só resolve se as bolas estão se aproximando
            if velocidade_normal > 0:
                # Troca as velocidades normais com força de quique
                impulso = 2 * velocidade_normal / 2  # Assumindo massas iguais
                
                self.vx -= impulso * math.cos(angulo) * FORCA_QUIQUE
                self.vy -= impulso * math.sin(angulo) * FORCA_QUIQUE
                outra_bola.vx += impulso * math.cos(angulo) * FORCA_QUIQUE
                outra_bola.vy += impulso * math.sin(angulo) * FORCA_QUIQUE
                
                # Acelera ambas as bolas após a colisão
                self._acelerar_apos_quique()
                outra_bola._acelerar_apos_quique()
    
    def colisao_com_contorno(self, contorno):
        """
        Verifica e resolve colisão com um contorno circular - COM SISTEMA DE CORES
        contorno: objeto Contorno para verificar colisão
        Retorna True se houve colisão e destruição, False caso contrário
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
                
                # SISTEMA DE CORES: Verifica se a bola pode destruir o contorno
                if self.pode_destruir_contorno(contorno):
                    return True  # Pode destruir
                else:
                    # Apenas quica, não destrói
                    print(f"Bola {self.tipo} quicou no contorno {contorno.tipo} (cores incompatíveis)")
                    return False
        
        return False  # Não houve colisão
    
    def pode_destruir_contorno(self, contorno):
        """
        Verifica se a bola pode destruir o contorno baseado nas cores
        Retorna True se pode destruir, False se apenas quica
        """
        return self.tipo == contorno.tipo
    
    def desenhar(self, tela):
        """Desenha a bola na tela"""
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)

class Contorno:
    """Classe que representa um contorno circular móvel e colorido"""
    
    def __init__(self, x, y, raio_inicial, tipo_cor):
        """
        Inicializa um contorno
        x, y: posição inicial do contorno
        raio_inicial: raio inicial do contorno
        tipo_cor: "vermelho" ou "azul"
        """
        self.x = x
        self.y = y
        self.raio = raio_inicial
        self.raio_inicial = raio_inicial
        self.ativo = True
        self.alpha = 255
        self.destruido = False
        
        # Sistema de cores
        self.tipo = tipo_cor
        if tipo_cor == "vermelho":
            self.cor = COR_CONTORNO_VERMELHO
        elif tipo_cor == "azul":
            self.cor = COR_CONTORNO_AZUL
        else:
            self.cor = COR_CONTORNO_NEUTRO
        
        # Sistema de movimento
        self.centro_alvo_x = LARGURA // 2
        self.centro_alvo_y = (ALTURA // 2) * 1.3
        self.vx = 0  # Velocidade horizontal
        self.vy = 0  # Velocidade vertical
        self.velocidade_atual = VELOCIDADE_INICIAL_CONTORNO
        
        # Calcula direção inicial em direção ao centro
        self._calcular_direcao_inicial()
    
    def _calcular_direcao_inicial(self):
        """Calcula a direção inicial do movimento em direção às bolas"""
        # Como os contornos começam no centro, eles se expandem para fora inicialmente
        # Mas depois se movem em direção às bolas quando detectam proximidade
        self.vx = 0
        self.vy = 0
    
    def atualizar(self):
        """Atualiza o contorno (movimento, diminuição de tamanho)"""
        if self.ativo and not self.destruido:
            # Atualiza movimento em direção ao centro
            self._atualizar_movimento()
            
            # Atualiza posição
            self.x += self.vx
            self.y += self.vy
            
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
    
    def _atualizar_movimento(self):
        """Atualiza o movimento do contorno com aceleração em direção às bolas"""
        # Encontra a bola mais próxima (assumindo que há duas bolas no centro)
        # Para simplificar, vamos usar o centro como alvo inicial
        dx = self.centro_alvo_x - self.x
        dy = self.centro_alvo_y - self.y
        distancia_ao_alvo = math.sqrt(dx**2 + dy**2)
        
        if distancia_ao_alvo > 5:  # Evita divisão por zero
            # Normaliza a direção
            direcao_x = dx / distancia_ao_alvo
            direcao_y = dy / distancia_ao_alvo
            
            # Sistema de aceleração/desaceleração baseado na distância
            if distancia_ao_alvo > DISTANCIA_DESACELERACAO:
                # Longe do alvo: acelera
                self.velocidade_atual += ACELERACAO_CONTORNO
                self.velocidade_atual = min(self.velocidade_atual, VELOCIDADE_INICIAL_CONTORNO * 2)
            else:
                # Próximo do alvo: desacelera
                self.velocidade_atual *= DESACELERACAO_CONTORNO
                self.velocidade_atual = max(self.velocidade_atual, 0.5)
            
            # Aplica a velocidade na direção do alvo
            self.vx = direcao_x * self.velocidade_atual
            self.vy = direcao_y * self.velocidade_atual
    
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
    """Classe responsável por gerar contornos infinitamente com cores alternadas"""
    
    def __init__(self):
        self.contador_frames = 0
        self.proximo_raio = RAIO_MAXIMO_INICIAL
        self.alternar_cor = True  # True = vermelho, False = azul
        
        # Centro da tela para spawn dos contornos
        self.centro_x = LARGURA // 2
        self.centro_y = (ALTURA // 2) * 1.3
    
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
                # Alterna cor
                tipo_cor = "vermelho" if self.alternar_cor else "azul"
                self.alternar_cor = not self.alternar_cor
                
                # Cria novo contorno no centro
                novo_contorno = Contorno(self.centro_x, self.centro_y, self.proximo_raio, tipo_cor)
                contornos.append(novo_contorno)
                
                # Incrementa o raio para o próximo contorno
                self.proximo_raio += 25
                if self.proximo_raio > RAIO_MAXIMO_INICIAL + 200:
                    self.proximo_raio = RAIO_MAXIMO_INICIAL  # Reseta para variar
                
                # Reseta o contador
                self.contador_frames = 0
                
                print(f"Novo contorno {tipo_cor} criado no centro! Raio: {self.proximo_raio - 25}")

def main():
    """Função principal do jogo"""
    # Inicializa o relógio para controlar FPS
    clock = pygame.time.Clock()
    
    # Inicializa lista de contornos vazia
    contornos = []
    
    # Cria o gerador de contornos infinitos
    gerador = GeradorContornos()
    
    # Calcula o centro da tela para posicionar as bolas
    centro_x = LARGURA // 2
    centro_y = ALTURA // 2
    
    # Cria as duas bolas no centro da tela
    bola_vermelha = Bola(centro_x - 25, centro_y, COR_BOLA_VERMELHA)
    bola_azul = Bola(centro_x + 25, centro_y, COR_BOLA_AZUL)
    
    # Dá uma pequena velocidade inicial para as bolas se moverem
    bola_vermelha.vx = -2
    bola_azul.vx = 2
    
    print("Aplicativo iniciado com contornos móveis e sistema de cores!")
    print("REGRAS:")
    print("- Contornos VERMELHOS: só a bola vermelha pode destruir")
    print("- Contornos AZUIS: só a bola azul pode destruir")
    print("- Bolas incompatíveis apenas quicam nos contornos")
    
    contornos_destruidos_total = 0
    quiques_incompativeis = 0
    
    # Loop principal do jogo
    rodando = True
    while rodando:
        # Processa eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
        
        # Atualiza o gerador de contornos
        gerador.atualizar(contornos)
        
        # Atualiza as bolas
        bola_vermelha.atualizar()
        bola_azul.atualizar()
        
        # Verifica colisão entre as bolas
        bola_vermelha.colisao_com_bola(bola_azul)
        
        # Atualiza contornos e verifica colisões
        contornos_restantes = []
        for contorno in contornos:
            contorno.atualizar()
            
            # Verifica colisão com bola vermelha
            if contorno.ativo and not contorno.destruido:
                if bola_vermelha.colisao_com_contorno(contorno):
                    if bola_vermelha.pode_destruir_contorno(contorno):
                        contorno.destruir()
                        contornos_destruidos_total += 1
                        print(f"Bola vermelha destruiu contorno {contorno.tipo}! Total: {contornos_destruidos_total}")
                    else:
                        quiques_incompativeis += 1
            
            # Verifica colisão com bola azul
            if contorno.ativo and not contorno.destruido:
                if bola_azul.colisao_com_contorno(contorno):
                    if bola_azul.pode_destruir_contorno(contorno):
                        contorno.destruir()
                        contornos_destruidos_total += 1
                        print(f"Bola azul destruiu contorno {contorno.tipo}! Total: {contornos_destruidos_total}")
                    else:
                        quiques_incompativeis += 1
            
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
        
        # Desenha as bolas
        bola_vermelha.desenhar(TELA)
        bola_azul.desenhar(TELA)
        
        # Atualiza a tela
        vid.draw(TELA, (0, 0))
        pygame.display.update()
        
        # Controla FPS
        if vid.draw(TELA, (0, 0)) == False:
            return 'Fim'
        clock.tick(60)
    
    # Finaliza o Pygame
    pygame.quit()
    print("Aplicativo finalizado!")
    sys.exit()

pygame.display.flip()

# ==================== EXECUÇÃO DO PROGRAMA ====================
if __name__ == "__main__":
    """Executa o programa quando o arquivo é executado diretamente"""
    main()
