import pygame
import random
import math

# Inicialização
pygame.init()
pygame.mixer.init()

# Pega a resolução da tela do PC
info_tela = pygame.display.Info()
largura_tela = info_tela.current_w
altura_tela = info_tela.current_h

# Configurações de Janela
tela = pygame.display.set_mode((largura_tela, altura_tela), pygame.FULLSCREEN)
pygame.display.set_caption("Prison Realms")

# Estados do Jogo
menu = True
menu_pausa = False
menu_note = False  
fase_zero_completa = False
fases_desbloqueadas = [0] 
colidindo_notebook = False # Variável para evitar que o menu reabra sozinho

# Carregamento da Imagem do Notebook
try:
    img_notebook = pygame.image.load("app_py/download__1_-removebg-preview.png")
    img_notebook = pygame.transform.scale(img_notebook, (largura_tela, altura_tela))
except:
    img_notebook = None

# Atributos do Jogador
largura_q, altura_q = 50, 50
x, y = largura_tela // 2 - largura_q // 2, altura_tela // 2 - altura_q // 2
velocidade = 10
hp = 100
max_hp = 100
cor_olho = (255, 0, 255) # Roxo
cor_jogador = (255, 255, 255) # Branco

# Configuração do Notebook Físico
notebook_rect = pygame.Rect(largura_tela // 2 - 30, altura_tela // 2 - 20, 60, 40)

# Projéteis Jogador
projetil_largura, projetil_altura = 30, 15
projetil_cor = (255, 255, 255)
projetil_velocidade = 15
projetil_lista = []
cooldown_tiro = 600  
ultimo_tiro = 0
direcao_jogador = "direita"

# --- VARIÁVEIS PARA TIROS DOS GUARDIÕES ---
projetil_inimigo_lista = []
velocidade_tiro_inimigo = 4 
cooldown_tiro_inimigo = 3500 
dano_tiro_inimigo = 5 

# Cores e Inimigos
cor_fundo = (70, 30, 80)
cor_inimigo = (255, 0, 0) 
cor_guardiao = (0, 0, 0)   

# Sistema de Dano
ultimo_dano = pygame.time.get_ticks()
intervalo_dano = 1000

# --- DICIONÁRIO DE FASES ---
fases = {
    0: [
        {"rect": pygame.Rect(largura_tela * 0.1, altura_tela * 0.1, 50, 50), "hp": 3, "tipo": "morador"},
        {"rect": pygame.Rect(largura_tela * 0.5, altura_tela * 0.3, 50, 50), "hp": 3, "tipo": "morador"},
        {"rect": pygame.Rect(largura_tela * 0.8, altura_tela * 0.7, 50, 50), "hp": 3, "tipo": "morador"},
        {"rect": pygame.Rect(largura_tela * 0.2, altura_tela * 0.8, 50, 50), "hp": 3, "tipo": "morador"},
        {"rect": pygame.Rect(largura_tela * 0.7, altura_tela * 0.2, 50, 50), "hp": 3, "tipo": "morador"}
    ],
    1: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 50, 50), "hp": 4, "tipo": "morador"} for _ in range(4)],
    2: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 60, 60), "hp": 8, "tipo": "guardiao", "ultimo_ataque": 0} for _ in range(3)],
    3: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 50, 50), "hp": 5, "tipo": "morador"} for _ in range(5)],
    4: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 60, 60), "hp": 10, "tipo": "guardiao", "ultimo_ataque": 0} for _ in range(4)],
    5: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 55, 55), "hp": 7, "tipo": "morador"} for _ in range(6)]
}

fase_atual = 0
inimigos = [dict(inimigo) for inimigo in fases[fase_atual]]

def desenhar_barra_hp(tela, x, y, hp, max_hp):
    largura_barra = 200
    altura_barra = 25
    cor_fundo_barra = (50, 50, 50)
    cor_preenchimento = (255, 0, 0) if hp <= 0 else (255 - int(255 * (hp / max_hp)), int(255 * (hp / max_hp)), 0)
    pygame.draw.rect(tela, cor_fundo_barra, (x, y, largura_barra, altura_barra))
    if hp > 0:
        pygame.draw.rect(tela, cor_preenchimento, (x, y, (largura_barra * hp) / max_hp, altura_barra))

def desenhar_menu_note(tela):
    tela.fill((10, 10, 20))
    pygame.draw.rect(tela, (0, 255, 100), (largura_tela//4, 50, largura_tela//2, altura_tela-100), 3, border_radius=15)
    fonte_titulo = pygame.font.SysFont('Arial Black', 35)
    fonte_fases = pygame.font.SysFont('Arial', 28)
    txt = fonte_titulo.render("NOT_EBOOK: SISTEMA DE FASES", True, (0, 255, 0))
    tela.blit(txt, (largura_tela // 2 - txt.get_width() // 2, 80))
    for i in range(6):
        liberada = i in fases_desbloqueadas
        status = "[LIBERADA]" if liberada else "[BLOQUEADA]"
        cor = (0, 255, 150) if liberada else (120, 120, 120)
        txt_fase = fonte_fases.render(f"Fase {i}: {status}", True, cor)
        tela.blit(txt_fase, (largura_tela // 2 - 180, 180 + i * 55))
        if liberada:
            txt_tecla = fonte_fases.render(f"Pressione {i}", True, (255, 255, 255))
            tela.blit(txt_tecla, (largura_tela // 2 + 80, 180 + i * 55))
    txt_voltar = fonte_fases.render("Pressione 'N' para SAIR", True, (255, 50, 50))
    tela.blit(txt_voltar, (largura_tela // 2 - txt_voltar.get_width() // 2, altura_tela - 130))

def desenhar_menu(tela):
    tela.fill(cor_fundo)
    fonte_titulo = pygame.font.SysFont('Arial Black', 72)
    fonte_texto = pygame.font.SysFont('Arial', 40)
    titulo = fonte_titulo.render("Começe", True, (255, 255, 255))
    sombra = fonte_titulo.render("Começe", True, (100, 0, 150))
    iniciar_texto = fonte_texto.render("Pressione ENTER para começar", True, (255, 255, 255))
    tela.blit(sombra, (largura_tela // 2 - titulo.get_width() // 2 + 4, altura_tela // 4 + 4))
    tela.blit(titulo, (largura_tela // 2 - titulo.get_width() // 2, altura_tela // 4))
    botao_rect = pygame.Rect(largura_tela // 2 - 250, altura_tela // 2 - 40, 500, 80)
    pygame.draw.rect(tela, (100, 40, 150), botao_rect, border_radius=20)
    pygame.draw.rect(tela, (180, 80, 255), botao_rect, 5, border_radius=20)
    tela.blit(iniciar_texto, (largura_tela // 2 - iniciar_texto.get_width() // 2, altura_tela // 2 - iniciar_texto.get_height() // 2))
    cubo_rect = pygame.Rect(botao_rect.x - 80, botao_rect.y + 15, 50, 50)
    pygame.draw.rect(tela, (255, 255, 255), cubo_rect)
    pygame.draw.circle(tela, (160, 70, 255), (cubo_rect.x + 12, cubo_rect.y + 18), 10)
    pygame.draw.circle(tela, (160, 70, 255), (cubo_rect.x + 38, cubo_rect.y + 18), 10)

def inimigo_seguir_jogador(inimigo, jogador_x, jogador_y, vel):
    dx = jogador_x - inimigo.x
    dy = jogador_y - inimigo.y
    distancia = (dx ** 2 + dy ** 2) ** 0.5
    if distancia != 0:
        inimigo.x += (dx / distancia) * vel
        inimigo.y += (dy / distancia) * vel

try:
    pygame.mixer.music.load(r"app_py/menumusic (1).mp3")
    pygame.mixer.music.play(-1, 0.0)
except: pass

clock = pygame.time.Clock()
rodando = True

while rodando:
    clock.tick(60)
    agora = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if menu and evento.key == pygame.K_RETURN:
                menu = False
                try:
                    pygame.mixer.music.load(r"app_py/gameplaymusic (2) (1).mp3")
                    pygame.mixer.music.play(-1, 0.0)
                except: pass
            elif menu_note and evento.key == pygame.K_n:
                menu_note = False
            elif menu_note:
                tecla_pressionada = evento.unicode
                if tecla_pressionada.isdigit():
                    fase_escolhida = int(tecla_pressionada)
                    if fase_escolhida in fases_desbloqueadas:
                        fase_atual = fase_escolhida
                        inimigos = [dict(i) for i in fases[fase_atual]]
                        menu_note = False
                        x, y = largura_tela // 2, altura_tela // 2
                        hp = 100
                        projetil_lista.clear()
                        projetil_inimigo_lista.clear()

    if menu:
        desenhar_menu(tela)
        pygame.display.flip()
        continue
    
    if menu_note:
        desenhar_menu_note(tela)
        pygame.display.flip()
        continue

    tela.fill(cor_fundo)
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: x -= velocidade; direcao_jogador = "esquerda"
    if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: x += velocidade; direcao_jogador = "direita"
    if teclas[pygame.K_w] or teclas[pygame.K_UP]: y -= velocidade; direcao_jogador = "cima"
    if teclas[pygame.K_s] or teclas[pygame.K_DOWN]: y += velocidade; direcao_jogador = "baixo"

    if teclas[pygame.K_SPACE] and agora - ultimo_tiro >= cooldown_tiro:
        pos_tiro = (x + 25, y + 25)
        if direcao_jogador == "direita": dx, dy = projetil_velocidade, 0
        elif direcao_jogador == "esquerda": dx, dy = -projetil_velocidade, 0
        elif direcao_jogador == "cima": dx, dy = 0, -projetil_velocidade
        else: dx, dy = 0, projetil_velocidade
        projetil_lista.append({"rect": pygame.Rect(pos_tiro[0], pos_tiro[1], 30, 15), "dx": dx, "dy": dy})
        ultimo_tiro = agora

    x = max(0, min(x, largura_tela - largura_q))
    y = max(0, min(y, altura_tela - altura_q))

    jogador_rect = pygame.Rect(x, y, largura_q, altura_q)
    pygame.draw.rect(tela, cor_jogador, jogador_rect)
    pygame.draw.circle(tela, cor_olho, (int(x + 12), int(y + 18)), 8)
    pygame.draw.circle(tela, cor_olho, (int(x + 38), int(y + 18)), 8)

    if not inimigos:
        pygame.draw.rect(tela, (50, 50, 50), notebook_rect)
        pygame.draw.rect(tela, (0, 255, 100), (notebook_rect.x + 10, notebook_rect.y + 5, 40, 20))
        
        # CONSERTO DO BOTÃO N (Lógica de detecção única)
        if jogador_rect.colliderect(notebook_rect):
            if not colidindo_notebook: # Só entra aqui uma vez quando encosta
                proxima_fase = fase_atual + 1
                if proxima_fase <= 5 and proxima_fase not in fases_desbloqueadas:
                    fases_desbloqueadas.append(proxima_fase)
                menu_note = True
                colidindo_notebook = True
        else:
            colidindo_notebook = False # Reseta quando o jogador se afasta
    else:
        for ini in inimigos[:]:
            inimigo_seguir_jogador(ini["rect"], x, y, 2)
            cor_c = cor_inimigo if ini["tipo"] == "morador" else cor_guardiao
            pygame.draw.rect(tela, cor_c, ini["rect"])
            cor_o = (0, 0, 0) if ini["tipo"] == "morador" else (255, 0, 255)
            pygame.draw.circle(tela, cor_o, (ini["rect"].x + 12, ini["rect"].y + 18), 6)
            pygame.draw.circle(tela, cor_o, (ini["rect"].x + 38, ini["rect"].y + 18), 6)

            if ini["tipo"] == "guardiao":
                if agora - ini["ultimo_ataque"] >= cooldown_tiro_inimigo:
                    dx_ini = x - ini["rect"].centerx
                    dy_ini = y - ini["rect"].centery
                    dist = math.hypot(dx_ini, dy_ini)
                    if dist != 0:
                        dx_ini /= dist; dy_ini /= dist
                        projetil_inimigo_lista.append({
                            "rect": pygame.Rect(ini["rect"].centerx, ini["rect"].centery, 15, 15),
                            "dx": dx_ini * velocidade_tiro_inimigo, "dy": dy_ini * velocidade_tiro_inimigo
                        })
                        ini["ultimo_ataque"] = agora

            if jogador_rect.colliderect(ini["rect"]) and agora - ultimo_dano >= intervalo_dano:
                hp -= 15
                ultimo_dano = agora

    for p in projetil_lista[:]:
        p["rect"].x += p["dx"]; p["rect"].y += p["dy"]
        pygame.draw.rect(tela, projetil_cor, p["rect"])
        for ini in inimigos[:]:
            if p["rect"].colliderect(ini["rect"]):
                ini["hp"] -= 1
                if p in projetil_lista: projetil_lista.remove(p)
                if ini["hp"] <= 0: inimigos.remove(ini)

    for pi in projetil_inimigo_lista[:]:
        pi["rect"].x += pi["dx"]; pi["rect"].y += pi["dy"]
        pygame.draw.circle(tela, (200, 200, 200), pi["rect"].center, 7)
        if pi["rect"].colliderect(jogador_rect):
            hp -= dano_tiro_inimigo
            projetil_inimigo_lista.remove(pi)
        elif not tela.get_rect().colliderect(pi["rect"]):
            projetil_inimigo_lista.remove(pi)

    desenhar_barra_hp(tela, 20, 20, hp, max_hp)
    if hp <= 0: rodando = False
    
    pygame.display.flip()

pygame.quit()
