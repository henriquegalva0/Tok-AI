import pygame
import math
import sys
import random
import os
import glob
from time import sleep

finalizar_gravacao = False

# ==================== CONFIGURAÇÕES DE IMAGENS ====================
# Configurações para seleção aleatória de imagens
PASTA_IMAGENS = "ImagesColiseum"  # Pasta com as imagens das bolas
USAR_IMAGENS_ALEATORIAS = True    # True para selecionar imagens aleatórias, False para usar caminhos fixos
CAMINHO_IMAGEM_BOLA_1 = ""        # Deixe vazio se usar imagens aleatórias
CAMINHO_IMAGEM_BOLA_2 = ""        # Deixe vazio se usar imagens aleatórias

# ==================== CONFIGURAÇÕES DE PLANO DE FUNDO E TÍTULO ====================
CAMINHO_PLANO_FUNDO = "BackgroundColiseum/campo_plano.jpg"  # Caminho da imagem de fundo (JPG/PNG)
CAMINHO_TITULO = "BackgroundColiseum/titulo_jogo.png"       # Caminho da imagem do título (PNG)
USAR_PLANO_FUNDO = True                  # True para usar imagem, False para cor sólida
USAR_TITULO = True                       # True para mostrar título, False para ocultar

# ==================== CONFIGURAÇÕES DO CRONÔMETRO E PLACAR ====================
TEMPO_JOGO = 20  # Tempo do jogo em segundos
TEMPO_ACRESCIMOS = 10  # Tempo dos acréscimos em segundos
COR_CRONOMETRO = (255, 255, 255)  # Cor do texto do cronômetro
COR_PLACAR = (255, 255, 255)      # Cor do texto do placar
TAMANHO_FONTE_CRONOMETRO = 36     # Tamanho da fonte do cronômetro
TAMANHO_FONTE_PLACAR = 48         # Tamanho da fonte do placar
TAMANHO_FONTE_NOMES = 24          # Tamanho da fonte dos nomes das equipes

def random_color():
    return (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))

def carregar_imagem_bola(caminho, tamanho):
    """Carrega e redimensiona uma imagem para o tamanho da bola"""
    if caminho and os.path.exists(caminho):
        try:
            imagem = pygame.image.load(caminho)
            # Redimensiona para o tamanho da bola (diâmetro)
            imagem = pygame.transform.scale(imagem, (tamanho * 2, tamanho * 2))
            return imagem
        except pygame.error:
            print(f"Erro ao carregar imagem: {caminho}")
            return None
    return None

def carregar_plano_fundo(caminho, largura, altura):
    """Carrega e redimensiona a imagem de plano de fundo"""
    if caminho and os.path.exists(caminho):
        try:
            imagem = pygame.image.load(caminho)
            # Redimensiona para o tamanho da tela
            imagem = pygame.transform.scale(imagem, (largura, altura))
            return imagem
        except pygame.error:
            print(f"Erro ao carregar plano de fundo: {caminho}")
            return None
    return None

def carregar_titulo(caminho, largura_maxima=None):
    """Carrega a imagem do título, opcionalmente redimensionando"""
    if caminho and os.path.exists(caminho):
        try:
            imagem = pygame.image.load(caminho)
            # Se especificada largura máxima, redimensiona mantendo proporção
            if largura_maxima and imagem.get_width() > largura_maxima:
                altura_original = imagem.get_height()
                largura_original = imagem.get_width()
                nova_altura = int((altura_original * largura_maxima) / largura_original)
                imagem = pygame.transform.scale(imagem, (largura_maxima, nova_altura))
            return imagem
        except pygame.error:
            print(f"Erro ao carregar título: {caminho}")
            return None
    return None

def extrair_nome_arquivo(caminho):
    """Extrai o nome do arquivo sem extensão do caminho"""
    if caminho:
        nome_arquivo = os.path.basename(caminho)
        nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
        return nome_sem_extensao.replace("_", " ").title()
    return "Jogador"

def selecionar_imagens_aleatorias(pasta_imagens):
    """
    Seleciona duas imagens aleatórias da pasta especificada
    pasta_imagens: caminho da pasta com as imagens
    Retorna: tupla com dois caminhos de imagens diferentes
    """
    # Busca todas as imagens PNG na pasta
    padrao = os.path.join(pasta_imagens, "*.png")
    imagens_disponiveis = glob.glob(padrao)
    
    # Adiciona também imagens JPG se existirem
    padrao_jpg = os.path.join(pasta_imagens, "*.jpg")
    imagens_disponiveis.extend(glob.glob(padrao_jpg))
    
    # Adiciona também imagens JPEG se existirem
    padrao_jpeg = os.path.join(pasta_imagens, "*.jpeg")
    imagens_disponiveis.extend(glob.glob(padrao_jpeg))
    
    if len(imagens_disponiveis) < 2:
        print(f"AVISO: Apenas {len(imagens_disponiveis)} imagem(s) encontrada(s) em {pasta_imagens}")
        print("Usando cores padrão para as bolas restantes.")
        return imagens_disponiveis + [""] * (2 - len(imagens_disponiveis))
    
    # Seleciona duas imagens aleatórias diferentes
    imagens_selecionadas = random.sample(imagens_disponiveis, 2)
    
    print(f"Imagens selecionadas aleatoriamente:")
    for i, imagem in enumerate(imagens_selecionadas, 1):
        nome = extrair_nome_arquivo(imagem)
        print(f"  Bola {i}: {nome} ({imagem})")
    
    return imagens_selecionadas

# Inicialização do Pygame
pygame.init()

# ==================== CONFIGURAÇÕES DA JANELA ====================
LARGURA = 480  # Largura da janela
ALTURA = 854    # Altura da janela
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Bolas com Contorno Fixo")

# ==================== CORES (CONFIGURÁVEIS) ====================
COR_FUNDO = (0, 0, 0)        # Preto - cor do fundo (usado se não houver imagem)
COR_BOLA_VERMELHA = random_color()  # Cor da primeira bola
COR_BOLA_AZUL = random_color()      # Cor da segunda bola
COR_CONTORNO_FIXO = (255, 255, 255)  # Branco - cor do contorno fixo

# ==================== CONFIGURAÇÕES DAS BOLAS (CONFIGURÁVEIS) ====================
RAIO_BOLA = 25              # Raio das bolas
GRAVIDADE = 0.3             # Força da gravidade aplicada às bolas
FORCA_QUIQUE = 1.0         # Força do quique (0.0 a 1.0)
ACELERACAO_QUIQUE = 5     # Multiplicador de aceleração após cada quique
VELOCIDADE_MAXIMA = 20      # Velocidade máxima que as bolas podem atingir

# ==================== CONFIGURAÇÕES DO CONTORNO FIXO ====================
RAIO_CONTORNO_FIXO = 200    # Raio do contorno fixo central
ESPESSURA_CONTORNO = 5      # Espessura da linha do contorno
INTENSIDADE_PULSO = 10      # Intensidade do efeito de pulso
DURACAO_PULSO = 20          # Duração do pulso em frames

class Cronometro:
    """Classe para gerenciar o cronômetro do jogo"""
    
    def __init__(self, tempo_total):
        """
        Inicializa o cronômetro
        tempo_total: tempo total do jogo em segundos
        """
        self.tempo_total = tempo_total
        self.tempo_restante = tempo_total
        self.ativo = True
        self.fonte = pygame.font.Font(None, TAMANHO_FONTE_CRONOMETRO)
        self.em_acrescimos = False
    
    def atualizar(self, dt):
        """
        Atualiza o cronômetro
        dt: delta time em segundos
        """
        if self.ativo and self.tempo_restante > 0:
            self.tempo_restante -= dt
            if self.tempo_restante <= 0:
                self.tempo_restante = 0
                self.ativo = False
                return True  # Tempo acabou
        return False
    
    def iniciar_acrescimos(self):
        """Inicia os acréscimos"""
        self.em_acrescimos = True
        self.tempo_restante = TEMPO_ACRESCIMOS
        self.ativo = True
        print("ACRÉSCIMOS INICIADOS!")
    
    def get_tempo_formatado(self):
        """Retorna o tempo formatado como string"""
        minutos = int(self.tempo_restante) // 60
        segundos = int(self.tempo_restante) % 60
        prefixo = "ACRÉSCIMOS " if self.em_acrescimos else ""
        return f"{prefixo}{minutos:02d}:{segundos:02d}"
    
    def desenhar(self, tela, x, y):
        """Desenha o cronômetro na tela"""
        cor = (255, 255, 0) if self.em_acrescimos else COR_CRONOMETRO  # Amarelo nos acréscimos
        texto = self.fonte.render(self.get_tempo_formatado(), True, cor)
        rect = texto.get_rect()
        rect.center = (x, y)
        tela.blit(texto, rect)
    
    def tempo_acabou(self):
        """Verifica se o tempo acabou"""
        return self.tempo_restante <= 0

class Placar:
    """Classe para gerenciar o placar do jogo"""
    
    def __init__(self, nome_jogador_1, nome_jogador_2):
        """
        Inicializa o placar
        nome_jogador_1: nome do primeiro jogador
        nome_jogador_2: nome do segundo jogador
        """
        self.pontos_jogador_1 = 0
        self.pontos_jogador_2 = 0
        self.nome_jogador_1 = nome_jogador_1
        self.nome_jogador_2 = nome_jogador_2
        self.fonte_placar = pygame.font.Font(None, TAMANHO_FONTE_PLACAR)
        self.fonte_nomes = pygame.font.Font(None, TAMANHO_FONTE_NOMES)
        self.pontuacao_empate = 0  # Para controlar os acréscimos
    
    def marcar_ponto_jogador_1(self, em_acrescimos=False):
        """Marca pontos aleatórios para o jogador 1"""
        if em_acrescimos:
            # Nos acréscimos, pontos vão da pontuação de empate até empate + 3
            pontos = random.randint(self.pontuacao_empate, self.pontuacao_empate + 3)
        else:
            pontos = random.choice([0,1,1,1,2,2,2,2,2,2,3,3,4,5])
        
        self.pontos_jogador_1 = pontos
        print(f"{self.nome_jogador_1} marcou {pontos} pontos! Total: {self.pontos_jogador_1}")
        return pontos
    
    def marcar_ponto_jogador_2(self, em_acrescimos=False):
        """Marca pontos aleatórios para o jogador 2"""
        if em_acrescimos:
            # Nos acréscimos, pontos vão da pontuação de empate até empate + 3
            pontos = random.randint(self.pontuacao_empate, self.pontuacao_empate + 3)
        else:
            pontos = random.choice([0,1,1,1,2,2,2,2,2,2,3,3,4,5])
        
        self.pontos_jogador_2 = pontos
        print(f"{self.nome_jogador_2} marcou {pontos} pontos! Total: {self.pontos_jogador_2}")
        return pontos
    
    def definir_pontuacao_empate(self):
        """Define a pontuação de empate para os acréscimos"""
        self.pontuacao_empate = self.pontos_jogador_1  # Ambos têm a mesma pontuação no empate
        print(f"Pontuação de empate definida: {self.pontuacao_empate}")
    
    def get_placar_texto(self):
        """Retorna o texto do placar formatado"""
        return f"{self.pontos_jogador_1} x {self.pontos_jogador_2}"
    
    def desenhar(self, tela, centro_x, y):
        """Desenha o placar na tela"""
        # Desenha o placar principal
        texto_placar = self.fonte_placar.render(self.get_placar_texto(), True, COR_PLACAR)
        rect_placar = texto_placar.get_rect()
        rect_placar.center = (centro_x, y)
        tela.blit(texto_placar, rect_placar)
        
        # Desenha os nomes dos jogadores
        texto_nome_1 = self.fonte_nomes.render(self.nome_jogador_1, True, COR_PLACAR)
        texto_nome_2 = self.fonte_nomes.render(self.nome_jogador_2, True, COR_PLACAR)
        
        # Posiciona os nomes abaixo dos respectivos números
        espacamento_nomes = 80  # Distância entre os nomes
        
        rect_nome_1 = texto_nome_1.get_rect()
        rect_nome_1.center = (centro_x - espacamento_nomes, y + 40)
        
        rect_nome_2 = texto_nome_2.get_rect()
        rect_nome_2.center = (centro_x + espacamento_nomes, y + 40)
        
        tela.blit(texto_nome_1, rect_nome_1)
        tela.blit(texto_nome_2, rect_nome_2)
    
    def get_vencedor(self):
        """Retorna o vencedor do jogo"""
        if self.pontos_jogador_1 > self.pontos_jogador_2:
            return self.nome_jogador_1
        elif self.pontos_jogador_2 > self.pontos_jogador_1:
            return self.nome_jogador_2
        else:
            return "Empate"
    
    def sortear_vencedor_penaltis(self):
        """Sorteia um vencedor para os pênaltis"""
        vencedor = random.choice([self.nome_jogador_1, self.nome_jogador_2])
        print(f"Vencedor sorteado nos pênaltis: {vencedor}")
        return vencedor

class Bola:
    """Classe que representa uma bola no jogo"""
    
    def __init__(self, x, y, cor, imagem=None, id_jogador=1):
        """
        Inicializa uma bola
        x, y: posição inicial da bola
        cor: cor da bola (RGB)
        imagem: imagem PNG da bola (opcional)
        id_jogador: ID do jogador (1 ou 2)
        """
        self.x = x
        self.y = y
        self.vx = 0  # Velocidade horizontal inicial
        self.vy = 0  # Velocidade vertical inicial
        self.raio = RAIO_BOLA
        self.cor = cor
        self.imagem = imagem
        self.quiques = 0  # Contador de quiques para acelerar
        self.id_jogador = id_jogador
    
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
    
    def colisao_com_contorno_fixo(self, contorno_fixo):
        """
        Verifica e resolve colisão com o contorno fixo
        contorno_fixo: objeto ContornoFixo para verificar colisão
        Retorna True se houve colisão, False caso contrário
        """
        # Calcula a distância entre o centro da bola e o centro do contorno
        distancia = math.sqrt((self.x - contorno_fixo.x)**2 + (self.y - contorno_fixo.y)**2)
        
        # Verifica se a bola está DENTRO do contorno e próxima da borda
        diferenca_raios = abs(distancia - contorno_fixo.raio)
        
        # A bola colide se está dentro do contorno E próxima da borda
        if distancia < contorno_fixo.raio and diferenca_raios <= self.raio + ESPESSURA_CONTORNO:
            # Calcula o ângulo da colisão (do centro do contorno para a bola)
            if distancia > 0:
                angulo = math.atan2(self.y - contorno_fixo.y, self.x - contorno_fixo.x)
                
                # Posiciona a bola DENTRO do contorno, mas longe da borda
                nova_distancia = contorno_fixo.raio - self.raio - ESPESSURA_CONTORNO
                if nova_distancia > 0:
                    self.x = contorno_fixo.x + math.cos(angulo) * nova_distancia
                    self.y = contorno_fixo.y + math.sin(angulo) * nova_distancia
                
                # Calcula a velocidade normal (direção da colisão)
                velocidade_normal = self.vx * math.cos(angulo) + self.vy * math.sin(angulo)
                
                # Inverte a velocidade normal se a bola está se movendo em direção à borda
                if velocidade_normal > 0:
                    self.vx -= 2 * velocidade_normal * math.cos(angulo) * FORCA_QUIQUE
                    self.vy -= 2 * velocidade_normal * math.sin(angulo) * FORCA_QUIQUE
                    
                    # Acelera a bola após o quique
                    self._acelerar_apos_quique()
                    
                    return True  # Houve colisão
        
        return False  # Não houve colisão
    
    def desenhar(self, tela):
        """Desenha a bola na tela"""
        if self.imagem:
            # Desenha a imagem centralizada na posição da bola
            rect = self.imagem.get_rect()
            rect.center = (int(self.x), int(self.y))
            tela.blit(self.imagem, rect)
        else:
            # Desenha um círculo colorido
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)

class ContornoFixo:
    """Classe que representa um contorno fixo central com efeito de pulso"""
    
    def __init__(self, x, y, raio):
        """
        Inicializa o contorno fixo
        x, y: posição do centro do contorno
        raio: raio do contorno
        """
        self.x = x
        self.y = y
        self.raio = raio
        self.raio_base = raio
        self.cor = COR_CONTORNO_FIXO
        
        # Sistema de pulso
        self.pulsando = False
        self.frames_pulso = 0
        self.intensidade_atual = 0
    
    def iniciar_pulso(self):
        """Inicia o efeito de pulso"""
        self.pulsando = True
        self.frames_pulso = 0
        self.intensidade_atual = INTENSIDADE_PULSO
    
    def atualizar(self):
        """Atualiza o efeito de pulso"""
        if self.pulsando:
            self.frames_pulso += 1
            
            # Calcula a intensidade do pulso usando uma função senoidal
            progresso = self.frames_pulso / DURACAO_PULSO
            if progresso <= 1.0:
                # Curva senoidal para um pulso suave
                intensidade = INTENSIDADE_PULSO * math.sin(progresso * math.pi)
                self.raio = self.raio_base + intensidade
            else:
                # Termina o pulso
                self.pulsando = False
                self.raio = self.raio_base
    
    def desenhar(self, tela):
        """Desenha o contorno fixo na tela"""
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), int(self.raio), ESPESSURA_CONTORNO)

def mostrar_tela_empate(tela, placar):
    """Mostra a tela de empate por 3 segundos"""
    fonte_titulo = pygame.font.Font(None, 48)
    fonte_resultado = pygame.font.Font(None, 36)
    
    # Limpa a tela
    tela.fill((0, 0, 0))
    
    # Título
    texto_titulo = fonte_titulo.render("EMPATE!", True, (255, 255, 0))
    rect_titulo = texto_titulo.get_rect()
    rect_titulo.center = (LARGURA // 2, ALTURA // 2 - 100)
    tela.blit(texto_titulo, rect_titulo)
    
    # Placar final
    texto_placar = fonte_resultado.render(f"{placar.get_placar_texto()}", True, (255, 255, 255))
    rect_placar = texto_placar.get_rect()
    rect_placar.center = (LARGURA // 2, ALTURA // 2 - 50)
    tela.blit(texto_placar, rect_placar)
    
    # Mensagem de acréscimos
    texto_acrescimos = fonte_resultado.render("Indo para os acréscimos...", True, (255, 255, 0))
    rect_acrescimos = texto_acrescimos.get_rect()
    rect_acrescimos.center = (LARGURA // 2, ALTURA // 2 + 50)
    tela.blit(texto_acrescimos, rect_acrescimos)
    
    pygame.display.flip()
    sleep(3)  # Pausa por 3 segundos

def mostrar_tela_final(tela, placar, cronometro, tipo_vitoria="normal"):
    """Mostra a tela final do jogo com o resultado"""
    fonte_titulo = pygame.font.Font(None, 48)
    fonte_resultado = pygame.font.Font(None, 36)
    fonte_instrucao = pygame.font.Font(None, 24)
    
    # Limpa a tela
    tela.fill((0, 0, 0))
    
    # Título
    texto_titulo = fonte_titulo.render("Fim de Jogo", True, (255, 255, 255))
    rect_titulo = texto_titulo.get_rect()
    rect_titulo.center = (LARGURA // 2, ALTURA // 2 - 100)
    tela.blit(texto_titulo, rect_titulo)
    
    # Placar final
    texto_placar = fonte_resultado.render(f"{placar.get_placar_texto()}", True, (255, 255, 255))
    rect_placar = texto_placar.get_rect()
    rect_placar.center = (LARGURA // 2, ALTURA // 2 - 50)
    tela.blit(texto_placar, rect_placar)
    
    # Vencedor com tipo de vitória
    vencedor = placar.get_vencedor()
    if tipo_vitoria == "acrescimos":
        texto_vencedor = fonte_resultado.render(f"VITÓRIA DE {vencedor.upper()}", True, (0, 255, 0))
        texto_tipo = fonte_resultado.render("NOS ACRÉSCIMOS!", True, (255, 255, 0))
    elif tipo_vitoria == "penaltis":
        vencedor_penaltis = placar.sortear_vencedor_penaltis()
        texto_vencedor = fonte_resultado.render(f"VITÓRIA DE {vencedor_penaltis.upper()}", True, (0, 255, 0))
        texto_tipo = fonte_resultado.render("NOS PÊNALTIS!", True, (255, 255, 0))
    elif vencedor == "Empate":
        # Este caso não deveria acontecer mais, mas mantemos por segurança
        vencedor_penaltis = placar.sortear_vencedor_penaltis()
        texto_vencedor = fonte_resultado.render(f"VITÓRIA DE {vencedor_penaltis.upper()}", True, (0, 255, 0))
        texto_tipo = fonte_resultado.render("NOS PÊNALTIS!", True, (255, 255, 0))
    else:
        texto_vencedor = fonte_resultado.render(f"VENCEDOR: {vencedor.upper()}!", True, (0, 255, 0))
        texto_tipo = None
    
    rect_vencedor = texto_vencedor.get_rect()
    rect_vencedor.center = (LARGURA // 2, ALTURA // 2)
    tela.blit(texto_vencedor, rect_vencedor)
    
    if texto_tipo:
        rect_tipo = texto_tipo.get_rect()
        rect_tipo.center = (LARGURA // 2, ALTURA // 2 + 40)
        tela.blit(texto_tipo, rect_tipo)
    
    pygame.display.flip()

def main():
    """Função principal do jogo"""
    # Inicializa o relógio para controlar FPS
    clock = pygame.time.Clock()
    
    # Seleciona imagens das bolas
    if USAR_IMAGENS_ALEATORIAS:
        # Seleciona imagens aleatórias da pasta
        caminhos_imagens = selecionar_imagens_aleatorias(PASTA_IMAGENS)
        caminho_imagem_1 = caminhos_imagens[0] if len(caminhos_imagens) > 0 else ""
        caminho_imagem_2 = caminhos_imagens[1] if len(caminhos_imagens) > 1 else ""
    else:
        # Usa caminhos fixos
        caminho_imagem_1 = CAMINHO_IMAGEM_BOLA_1
        caminho_imagem_2 = CAMINHO_IMAGEM_BOLA_2
    
    # Carrega imagens das bolas
    imagem_bola_1 = carregar_imagem_bola(caminho_imagem_1, RAIO_BOLA)
    imagem_bola_2 = carregar_imagem_bola(caminho_imagem_2, RAIO_BOLA)
    
    # Carrega plano de fundo (se especificado)
    plano_fundo = None
    if USAR_PLANO_FUNDO:
        plano_fundo = carregar_plano_fundo(CAMINHO_PLANO_FUNDO, LARGURA, ALTURA)
        if plano_fundo:
            print(f"Plano de fundo carregado: {CAMINHO_PLANO_FUNDO}")
        else:
            print(f"Não foi possível carregar o plano de fundo: {CAMINHO_PLANO_FUNDO}")
    
    # Carrega título (se especificado)
    titulo = None
    if USAR_TITULO:
        titulo = carregar_titulo(CAMINHO_TITULO, LARGURA - 40)  # Margem de 20px de cada lado
        if titulo:
            print(f"Título carregado: {CAMINHO_TITULO}")
        else:
            print(f"Não foi possível carregar o título: {CAMINHO_TITULO}")
    
    # Extrai nomes dos jogadores dos arquivos de imagem
    nome_jogador_1 = extrair_nome_arquivo(caminho_imagem_1)
    nome_jogador_2 = extrair_nome_arquivo(caminho_imagem_2)
    
    while True:  # Loop para permitir reiniciar o jogo
        # Inicializa componentes do jogo
        cronometro = Cronometro(TEMPO_JOGO)
        placar = Placar(nome_jogador_1, nome_jogador_2)
        
        # Calcula o centro da tela
        centro_x = LARGURA // 2
        centro_y = ALTURA // 2
        
        # Cria o contorno fixo no centro da tela
        contorno_fixo = ContornoFixo(centro_x, centro_y, RAIO_CONTORNO_FIXO)
        
        # Cria as duas bolas no centro da tela
        bola_1 = Bola(centro_x - random.randint(20, 25), centro_y, COR_BOLA_VERMELHA, imagem_bola_1, 1)
        bola_2 = Bola(centro_x + random.randint(20, 25), centro_y, COR_BOLA_AZUL, imagem_bola_2, 2)
        
        # Dá uma pequena velocidade inicial para as bolas se moverem
        bola_1.vx = -2
        bola_2.vx = 2
        
        print("Jogo de Bolas com Contorno Fixo iniciado!")
        print(f"- Cronômetro: {TEMPO_JOGO} segundos")
        print(f"- Jogadores: {nome_jogador_1} vs {nome_jogador_2}")
        print("- Contorno fixo central com efeito de pulso")
        print("- Bolas quicam no contorno e causam pulso")
        if plano_fundo:
            print("- Usando plano de fundo personalizado")
        if titulo:
            print("- Título personalizado carregado")
        if USAR_IMAGENS_ALEATORIAS:
            print("- Seleção aleatória de imagens ativada")
        if imagem_bola_1:
            print(f"- Bola 1: {nome_jogador_1} (imagem carregada)")
        else:
            print(f"- Bola 1: {nome_jogador_1} (cor padrão)")
        if imagem_bola_2:
            print(f"- Bola 2: {nome_jogador_2} (imagem carregada)")
        else:
            print(f"- Bola 2: {nome_jogador_2} (cor padrão)")
        
        # Loop principal do jogo
        rodando = True
        jogo_terminado = False
        em_acrescimos = False
        tipo_vitoria = "normal"
        
        while rodando:
            # Calcula delta time
            dt = clock.tick(60) / 1000.0  # Delta time em segundos
            
            # Processa eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if jogo_terminado:
                            pygame.quit()
                            sys.exit()
                        else:
                            rodando = False
                    elif evento.key == pygame.K_SPACE and jogo_terminado:
                        rodando = False  # Reinicia o jogo
            
            if not jogo_terminado:
                # Atualiza o cronômetro
                if cronometro.atualizar(dt):
                    # Tempo acabou
                    vencedor = placar.get_vencedor()
                    
                    if vencedor == "Empate" and not em_acrescimos:
                        # Primeiro empate - vai para acréscimos
                        print(f"TEMPO ESGOTADO! Placar: {placar.get_placar_texto()} - EMPATE!")
                        placar.definir_pontuacao_empate()
                        mostrar_tela_empate(TELA, placar)
                        
                        # Inicia acréscimos
                        cronometro.iniciar_acrescimos()
                        em_acrescimos = True
                        tipo_vitoria = "acrescimos"
                        
                        # Reinicia as bolas para os acréscimos
                        bola_1.x = centro_x - random.randint(20, 25)
                        bola_1.y = centro_y
                        bola_2.x = centro_x + random.randint(20, 25)
                        bola_2.y = centro_y
                        bola_1.vx = -2
                        bola_2.vx = 2
                        bola_1.vy = 0
                        bola_2.vy = 0
                        
                    elif vencedor == "Empate" and em_acrescimos:
                        # Segundo empate - vai para pênaltis
                        print(f"ACRÉSCIMOS TERMINADOS! Placar: {placar.get_placar_texto()} - EMPATE!")
                        print("Indo para os pênaltis...")
                        tipo_vitoria = "penaltis"
                        jogo_terminado = True
                        
                    else:
                        # Há um vencedor
                        if em_acrescimos:
                            print(f"ACRÉSCIMOS TERMINADOS! Placar final: {placar.get_placar_texto()}")
                            print(f"Vencedor nos acréscimos: {vencedor}")
                        else:
                            print(f"TEMPO ESGOTADO! Placar final: {placar.get_placar_texto()}")
                            print(f"Vencedor: {vencedor}")
                        jogo_terminado = True
                
                # Atualiza o contorno fixo
                contorno_fixo.atualizar()
                
                # Atualiza as bolas
                bola_1.atualizar()
                bola_2.atualizar()
                
                # Verifica colisão entre as bolas
                bola_1.colisao_com_bola(bola_2)
                
                # Verifica colisões com o contorno fixo e atualiza placar
                if bola_1.colisao_com_contorno_fixo(contorno_fixo):
                    contorno_fixo.iniciar_pulso()
                    pontos = placar.marcar_ponto_jogador_1(em_acrescimos)
                
                if bola_2.colisao_com_contorno_fixo(contorno_fixo):
                    contorno_fixo.iniciar_pulso()
                    pontos = placar.marcar_ponto_jogador_2(em_acrescimos)
            
            # ==================== DESENHO ====================
            if not jogo_terminado:
                # Desenha o plano de fundo
                if plano_fundo:
                    TELA.blit(plano_fundo, (0, 0))
                else:
                    # Limpa a tela com cor de fundo preta
                    TELA.fill(COR_FUNDO)
                
                # Desenha o contorno fixo
                contorno_fixo.desenhar(TELA)
                
                # Desenha as bolas
                bola_1.desenhar(TELA)
                bola_2.desenhar(TELA)
                
                # Desenha o título (se carregado)
                if titulo:
                    # Calcula posição do título (centralizado horizontalmente, na parte superior)
                    titulo_rect = titulo.get_rect()
                    titulo_x = (LARGURA - titulo_rect.width) // 2
                    titulo_y = 20  # 20 pixels do topo
                    
                    # Verifica se não vai sobrepor o contorno (ajusta posição se necessário)
                    distancia_do_contorno = centro_y - RAIO_CONTORNO_FIXO - ESPESSURA_CONTORNO
                    if titulo_y + titulo_rect.height > distancia_do_contorno - 20:  # Margem de 20px
                        titulo_y = max(10, distancia_do_contorno - titulo_rect.height - 20)
                    
                    TELA.blit(titulo, (titulo_x, titulo_y))
                
                # Desenha o cronômetro (canto superior direito)
                cronometro.desenhar(TELA, LARGURA - 240, ALTURA - 50)
                
                # Desenha o placar (entre o contorno e a parte inferior)
                placar_y = centro_y + RAIO_CONTORNO_FIXO + 80
                placar.desenhar(TELA, centro_x, placar_y)
                
                # Atualiza a tela
                pygame.display.flip()
            else:
                # Mostra tela final
                mostrar_tela_final(TELA, placar, cronometro, tipo_vitoria)
                sleep(3)
                pygame.quit()
                print("Jogo finalizado!")
                sys.exit()
        
        # Se chegou aqui, o jogo vai reiniciar (a menos que tenha saído)
        if not jogo_terminado:
            break  # Sai do loop principal se ESC foi pressionado durante o jogo
    
    # Finaliza o Pygame
    pygame.quit()
    print("Jogo finalizado!")
    sys.exit()
    finalizar_gravacao = True

# ==================== EXECUÇÃO DO PROGRAMA ====================
if __name__ == "__main__":
    """Executa o programa quando o arquivo é executado diretamente"""
    main()
