import pygame
import random
import math
import os
import cv2  # Certifique-se de ter instalado: pip install opencv-python

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

# --- FUNÇÕES DE SISTEMA ---
def salvar_jogo(f_atual, desbloqueadas):
    with open("save_prison.txt", "w") as f:
        f.write(f"{f_atual}\n{','.join(map(str, desbloqueadas))}")

def carregar_jogo():
    if os.path.exists("save_prison.txt"):
        with open("save_prison.txt", "r") as f:
            linhas = f.readlines()
            f_idx = int(linhas[0].strip())
            f_desblo = [int(x) for x in linhas[1].strip().split(",")]
            return f_idx, f_desblo
    return None

def rodar_video_intro():
    caminho_video = r"C:\Users\_MARCOS\Downloads\cine1.mp4" 
    if not os.path.exists(caminho_video):
        return

    video = cv2.VideoCapture(caminho_video)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    try:
        pygame.mixer.music.load(caminho_video)
        pygame.mixer.music.play()
    except: pass

    clock_video = pygame.time.Clock()
    rodando_v = True
    while rodando_v:
        ret, frame = video.read()
        if not ret: break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        surface_video = pygame.surfarray.make_surface(frame)
        surface_video = pygame.transform.scale(surface_video, (largura_tela, altura_tela))
        
        tela.blit(surface_video, (0, 0))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN or ev.type == pygame.QUIT:
                rodando_v = False
        clock_video.tick(fps)

    video.release()
    pygame.mixer.music.stop()

# --- ESTADOS E ATRIBUTOS ---
menu = True
menu_note = False  
fases_desbloqueadas = [0]
colidindo_notebook = False

largura_q, altura_q = 50, 50
x, y = largura_tela // 2, altura_tela // 2
velocidade = 10
hp = 100
max_hp = 100
cor_olho = (255, 0, 255)
cor_jogador = (255, 255, 255)

# Projéteis
projetil_lista = []
projetil_inimigo_lista = []
projetil_velocidade = 15
cooldown_tiro = 600  
ultimo_tiro = 0
direcao_jogador = "direita"

# CORES (AQUI ESTAVA O ERRO!)
cor_fundo = (70, 30, 80)
cor_inimigo = (255, 0, 0)
cor_guardiao = (0, 0, 0)
projetil_cor = (255, 255, 0) # <--- Cor amarela para o tiro definida aqui

# Notebook Físico
notebook_rect = pygame.Rect(largura_tela // 2 - 30, altura_tela // 2 - 20, 60, 40)
btn_hud_note = pygame.Rect(largura_tela - 70, 20, 50, 40)

# Inimigos e Fases
fases = {
    0: [{"rect": pygame.Rect(largura_tela * 0.1, altura_tela * 0.1, 50, 50), "hp": 3, "tipo": "morador"} for _ in range(5)],
    1: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 50, 50), "hp": 4, "tipo": "morador"} for _ in range(4)],
    2: [{"rect": pygame.Rect(random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 60, 60), "hp": 8, "tipo": "guardiao", "ultimo_ataque": 0} for _ in range(3)],
}

fase_atual = 0
inimigos = [dict(i) for i in fases[fase_atual]]
lista_botoes_menu = []
intervalo_dano = 1000
ultimo_dano = 0

def desenhar_barra_hp(tela, x, y, hp, max_hp):
    pygame.draw.rect(tela, (50, 50, 50), (x, y, 200, 25))
    largura = max(0, (200 * hp) / max_hp)
    pygame.draw.rect(tela, (255, 0, 0), (x, y, largura, 25))

def desenhar_menu_note(tela):
    global lista_botoes_menu
    lista_botoes_menu = []
    pygame.draw.rect(tela, (40, 40, 45), (largura_tela//4, 50, largura_tela//2, altura_tela-100), border_radius=20)
    fonte = pygame.font.SysFont('Arial', 24)
    for i in range(3): # Simplificado para teste
        liberada = i in fases_desbloqueadas
        btn = pygame.Rect(largura_tela//2 - 100, 150 + i*60, 200, 40)
        pygame.draw.rect(tela, (30, 30, 50), btn)
        txt = fonte.render(f"Fase {i}", True, (0, 255, 0) if liberada else (100, 100, 100))
        tela.blit(txt, (btn.x + 10, btn.y + 5))
        if liberada: lista_botoes_menu.append(("fase", btn, i))

def desenhar_menu(tela):
    tela.fill(cor_fundo)
    btn_novo = pygame.Rect(largura_tela // 2 - 150, altura_tela // 2 - 50, 300, 60)
    pygame.draw.rect(tela, (100, 40, 150), btn_novo)
    return btn_novo

clock = pygame.time.Clock()
rodando = True

while rodando:
    agora = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: rodando = False
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if menu:
                btn_n = pygame.Rect(largura_tela // 2 - 150, altura_tela // 2 - 50, 300, 60)
                if btn_n.collidepoint((mx, my)):
                    rodar_video_intro()
                    menu = False
            elif menu_note:
                for tipo, rect, valor in lista_botoes_menu:
                    if rect.collidepoint((mx, my)):
                        fase_atual = valor
                        inimigos = [dict(i) for i in fases[fase_atual]]
                        menu_note = False

    if menu:
        desenhar_menu(tela)
        pygame.display.flip()
        continue

    if menu_note:
        desenhar_menu_note(tela)
        pygame.display.flip()
        continue

    # --- MOVIMENTAÇÃO E JOGO ---
    tela.fill(cor_fundo)
    teclas = pygame.key.get_pressed()
    
    mirando = mouse_click[2]
    if mirando:
        dx_m, dy_m = mx - (x + 25), my - (y + 25)
        angulo = math.atan2(dy_m, dx_m)
        if teclas[pygame.K_w]:
            x += math.cos(angulo) * velocidade
            y += math.sin(angulo) * velocidade
        direcao_jogador = "mouse"
    else:
        if teclas[pygame.K_a]: x -= velocidade; direcao_jogador = "esquerda"
        if teclas[pygame.K_d]: x += velocidade; direcao_jogador = "direita"
        if teclas[pygame.K_w]: y -= velocidade; direcao_jogador = "cima"
        if teclas[pygame.K_s]: y += velocidade; direcao_jogador = "baixo"

    # Tiro
    if teclas[pygame.K_SPACE] and agora - ultimo_tiro >= cooldown_tiro:
        dx, dy = (projetil_velocidade, 0)
        if direcao_jogador == "mouse":
            dx_m, dy_m = mx - (x + 25), my - (y + 25)
            dist = math.hypot(dx_m, dy_m)
            if dist > 0: dx, dy = (dx_m/dist)*projetil_velocidade, (dy_m/dist)*projetil_velocidade
        projetil_lista.append({"rect": pygame.Rect(x+20, y+20, 15, 15), "dx": dx, "dy": dy})
        ultimo_tiro = agora

    # Desenhar Jogador
    pygame.draw.rect(tela, cor_jogador, (x, y, 50, 50))
    
    # Desenhar Inimigos
    for ini in inimigos[:]:
        dx_i, dy_i = x - ini["rect"].x, y - ini["rect"].y
        dist_i = math.hypot(dx_i, dy_i)
        if dist_i > 0:
            ini["rect"].x += (dx_i/dist_i) * 2
            ini["rect"].y += (dy_i/dist_i) * 2
        pygame.draw.rect(tela, cor_inimigo, ini["rect"])
        if ini["rect"].colliderect(pygame.Rect(x,y,50,50)) and agora - ultimo_dano > 1000:
            hp -= 10
            ultimo_dano = agora

    # Processar Tiros (Onde estava o erro)
    for p in projetil_lista[:]:
        p["rect"].x += p["dx"]
        p["rect"].y += p["dy"]
        pygame.draw.rect(tela, projetil_cor, p["rect"]) # Agora funciona!
        for ini in inimigos[:]:
            if p["rect"].colliderect(ini["rect"]):
                ini["hp"] -= 1
                if p in projetil_lista: projetil_lista.remove(p)
                if ini["hp"] <= 0: inimigos.remove(ini)

    desenhar_barra_hp(tela, 20, 20, hp, max_hp)
    if hp <= 0: rodando = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()