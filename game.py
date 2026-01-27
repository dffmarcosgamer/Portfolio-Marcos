import random
import math
import json
import os
import cv2
import sys
import pygame 

# Força o Python a olhar para a pasta onde o arquivo .py está salvo
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- CAMINHOS DINÂMICOS ---
def resource_path(relative_path):
    """ Retorna o caminho absoluto, funcionando no script e no executável """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- INICIALIZAÇÃO ---
pygame.init()
pygame.mixer.init()

info_tela = pygame.display.Info()
largura_tela = info_tela.current_w
altura_tela = info_tela.current_h

tela = pygame.display.set_mode((largura_tela, altura_tela), pygame.FULLSCREEN)
pygame.display.set_caption("Prison Realms")

# --- CONFIGURAÇÃO DE PASTAS ---
# Mantendo o sistema simples como solicitado
MUSICA_MENU = "assets/menumusic.mp3"
MUSICA_GAMEPLAY = "assets/gameplaymusic.mp3"
CAMINHO_VIDEO = "assets/cine1.mp4"
SOM_VIDEO = "assets/cine1.mp3"

# --- SISTEMA DE SAVE ---
arquivo_save = "save_prison_realms.json"

# Variáveis de Estado
menu = True
menu_note = False 
confirmando_novo_jogo = False
confirmando_voltar_menu = False
confirmando_sair_jogo = False
morreu = False
fases_desbloqueadas = [0] 
colidindo_notebook = False 

# Atributos do Jogador
largura_q, altura_q = 50, 50
x, y = largura_tela // 2, altura_tela // 2
velocidade = 10
hp = 100
max_hp = 100
cor_olho = (255, 0, 255)
cor_jogador = (255, 255, 255)

notebook_rect = pygame.Rect(largura_tela // 2 - 40, altura_tela // 2 - 30, 80, 50)

# Projéteis e Inimigos
projetil_velocidade = 15
projetil_lista = []
cooldown_tiro = 600  
ultimo_tiro = 0
direcao_jogador = "direita"
projetil_inimigo_lista = []
velocidade_tiro_inimigo = 6
cooldown_tiro_inimigo = 1200
dano_tiro_inimigo = 23
cor_fundo = (70, 30, 80)
cor_inimigo = (255, 0, 0) 
cor_guardiao = (0, 0, 0)   
ultimo_dano = 0
intervalo_dano = 1000

# --- CONFIGURAÇÃO DE FASES ---
fases_originais = {
    0: [{"rect": [largura_tela * 0.1, altura_tela * 0.1, 50, 50], "hp": 3, "tipo": "morador"},
        {"rect": [largura_tela * 0.5, altura_tela * 0.3, 50, 50], "hp": 3, "tipo": "morador"},
        {"rect": [largura_tela * 0.8, altura_tela * 0.7, 50, 50], "hp": 3, "tipo": "morador"},
        {"rect": [largura_tela * 0.2, altura_tela * 0.8, 50, 50], "hp": 3, "tipo": "morador"},
        {"rect": [largura_tela * 0.7, altura_tela * 0.2, 50, 50], "hp": 3, "tipo": "morador"}],
    1: [{"rect": [random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 50, 50], "hp": 4, "tipo": "morador"} for _ in range(4)],
    2: [{"rect": [random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 60, 60], "hp": 8, "tipo": "guardiao", "ultimo_ataque": 0} for _ in range(3)],
    3: [{"rect": [random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 50, 50], "hp": 5, "tipo": "morador"} for _ in range(5)],
    4: [{"rect": [random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 60, 60], "hp": 10, "tipo": "guardiao", "ultimo_ataque": 0} for _ in range(4)],
    5: [{"rect": [random.randint(100, largura_tela-100), random.randint(100, altura_tela-100), 55, 55], "hp": 7, "tipo": "morador"} for _ in range(6)]
}

fase_atual = 0
inimigos = []

def resetar_inimigos_fase(f):
    global inimigos
    inimigos = []
    for i in fases_originais[f]:
        d = dict(i)
        d["rect"] = pygame.Rect(i["rect"])
        inimigos.append(d)

resetar_inimigos_fase(fase_atual)

# --- FUNÇÕES ---

def desenhar_barra_hp(tela, x, y, hp, max_hp):
    largura_barra = 200
    altura_barra = 25
    cor_fundo_barra = (50, 50, 50)
    hp_viz = max(0, min(hp, max_hp))
    proporcao = hp_viz / max_hp
    cor_r = int(255 * (1 - proporcao))
    cor_g = int(255 * proporcao)
    pygame.draw.rect(tela, cor_fundo_barra, (x, y, largura_barra, altura_barra))
    if hp_viz > 0:
        pygame.draw.rect(tela, (cor_r, cor_g, 0), (x, y, int(largura_barra * proporcao), altura_barra))

def desenhar_design_notebook(tela, rect):
    pygame.draw.rect(tela, (40, 40, 40), (rect.x, rect.y + rect.height//2, rect.width, rect.height//2), border_bottom_left_radius=5, border_bottom_right_radius=5)
    pygame.draw.rect(tela, (20, 20, 20), (rect.x + 5, rect.y, rect.width - 10, rect.height//2 + 5), border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.rect(tela, (0, 40, 20), (rect.x + 10, rect.y + 5, rect.width - 20, rect.height//2 - 5))
    pygame.draw.line(tela, (0, 255, 100), (rect.x + 15, rect.y + 10), (rect.x + 40, rect.y + 10), 2)
    pygame.draw.line(tela, (0, 255, 100), (rect.x + 15, rect.y + 15), (rect.x + 30, rect.y + 15), 2)
    for i in range(3):
        pygame.draw.line(tela, (60, 60, 60), (rect.x + 10, rect.y + 32 + i*4), (rect.x + rect.width - 10, rect.y + 32 + i*4), 1)

def desenhar_hud_tab(tela):
    if len(fases_desbloqueadas) > 1:
        fonte = pygame.font.SysFont('Arial', 22, bold=True)
        alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
        txt = fonte.render("[TAB] NOTEBOOK", True, (0, 255, 100))
        txt.set_alpha(int(alpha))
        tela.blit(txt, (largura_tela - 200, 30))

def rodar_video():
    # Para a música do menu antes de começar o vídeo
    pygame.mixer.music.stop()
    
    if not os.path.exists(CAMINHO_VIDEO): 
        print(f"AVISO: Vídeo não encontrado em {CAMINHO_VIDEO}")
        return
    
    cap = cv2.VideoCapture(CAMINHO_VIDEO)
    try:
        # Se existir som do vídeo, toca
        if os.path.exists(SOM_VIDEO):
            pygame.mixer.music.load(SOM_VIDEO)
            pygame.mixer.music.play()
    except Exception as e: 
        print(f"Erro ao carregar som do vídeo: {e}")
        
    clock_v = pygame.time.Clock()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                    cap.release()
                    pygame.mixer.music.stop()
                    return
        
        # Rotacionar e ajustar frame
        frame = cv2.rotate(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.flip(frame, 0)
        surf = pygame.transform.scale(pygame.surfarray.make_surface(frame), (largura_tela, altura_tela))
        tela.blit(surf, (0, 0))
        pygame.display.flip()
        clock_v.tick(30)
    
    cap.release()
    pygame.mixer.music.stop()

def salvar_jogo():
    inimigos_save = []
    for ini in inimigos:
        inimigos_save.append({"rect": [ini["rect"].x, ini["rect"].y, ini["rect"].width, ini["rect"].height], "hp": ini["hp"], "tipo": ini["tipo"]})
    dados = {
        "fases_desbloqueadas": fases_desbloqueadas,
        "fase_atual": fase_atual,
        "player_x": x, "player_y": y,
        "player_hp": hp,
        "inimigos_vivos": inimigos_save
    }
    with open(arquivo_save, "w") as f:
        json.dump(dados, f)

def carregar_jogo():
    global fases_desbloqueadas, fase_atual, inimigos, x, y, hp
    if os.path.exists(arquivo_save):
        with open(arquivo_save, "r") as f:
            dados = json.load(f)
            fases_desbloqueadas = dados.get("fases_desbloqueadas", [0])
            fase_atual = dados.get("fase_atual", 0)
            x = dados.get("player_x", largura_tela // 2)
            y = dados.get("player_y", altura_tela // 2)
            hp = dados.get("player_hp", 100)
            inimigos = []
            for i in dados.get("inimigos_vivos", []):
                inimigos.append({"rect": pygame.Rect(i["rect"]), "hp": i["hp"], "tipo": i["tipo"], "ultimo_ataque": 0})

def novo_jogo():
    global fases_desbloqueadas, fase_atual, x, y, hp, menu, ultimo_tiro
    # 1. Apaga o save antigo
    if os.path.exists(arquivo_save): 
        os.remove(arquivo_save)
     
    # Roda o vídeo
    rodar_video()
    
    # --- CORREÇÃO DE ÁUDIO ---
    # Reinicia o mixer para garantir que a troca de áudio funcione limpa
    try:
        pygame.mixer.quit()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1.0)
    except:
        pass
    # -------------------------
     
    fases_desbloqueadas = [0]
    fase_atual = 0
    resetar_inimigos_fase(fase_atual)
    x, y, hp = largura_tela // 2, altura_tela // 2, 100
     
    # Tenta carregar a música da gameplay
    try:
        print(f"Tentando carregar música gameplay: {MUSICA_GAMEPLAY}")
        if os.path.exists(MUSICA_GAMEPLAY):
            pygame.mixer.music.load(MUSICA_GAMEPLAY)
            pygame.mixer.music.play(-1)
        else:
            print("ARQUIVO DE MUSICA GAMEPLAY NAO ENCONTRADO!")
    except Exception as e:
        print(f"ERRO CRÍTICO NA MÚSICA DE GAMEPLAY: {e}")

    ultimo_tiro = pygame.time.get_ticks() + 1000 
    menu = False

def desenhar_caixa_confirmacao(tela, texto):
    pygame.draw.rect(tela, (30, 30, 30), (largura_tela//2 - 200, altura_tela//2 - 100, 400, 200), border_radius=20)
    pygame.draw.rect(tela, (255, 255, 255), (largura_tela//2 - 200, altura_tela//2 - 100, 400, 200), 2, border_radius=20)
    txt = pygame.font.SysFont('Arial', 25).render(texto, True, (255, 255, 255))
    tela.blit(txt, (largura_tela//2 - txt.get_width()//2, altura_tela//2 - 60))
    btn_sim = pygame.Rect(largura_tela//2 - 110, altura_tela//2 + 10, 100, 50)
    btn_nao = pygame.Rect(largura_tela//2 + 10, altura_tela//2 + 10, 100, 50)
    pygame.draw.rect(tela, (0, 150, 0), btn_sim, border_radius=10)
    pygame.draw.rect(tela, (150, 0, 0), btn_nao, border_radius=10)
    tela.blit(pygame.font.SysFont('Arial', 20, bold=True).render("SIM", True, (255, 255, 255)), (btn_sim.centerx-15, btn_sim.centery-10))
    tela.blit(pygame.font.SysFont('Arial', 20, bold=True).render("NÃO", True, (255, 255, 255)), (btn_nao.centerx-15, btn_nao.centery-10))
    return btn_sim, btn_nao

def desenhar_menu(tela):
    tela.fill(cor_fundo)
    mx, my = pygame.mouse.get_pos()
    fonte_titulo = pygame.font.SysFont('Arial Black', 72)
    titulo = fonte_titulo.render("Prison Realms", True, (255, 255, 255))
    tela.blit(titulo, (largura_tela // 2 - titulo.get_width() // 2, altura_tela // 5))
     
    tem_save = os.path.exists(arquivo_save)
    btn_jogar = pygame.Rect(largura_tela // 2 - 150, altura_tela // 2 - 100, 300, 60)
    btn_novo = pygame.Rect(largura_tela // 2 - 150, altura_tela // 2 - 20, 300, 60)
    btn_sair = pygame.Rect(largura_tela // 2 - 150, altura_tela // 2 + 60, 300, 60)
     
    if not tem_save:
        cor_continuar = (30, 30, 30)
    else:
        cor_continuar = (100, 40, 150) if not btn_jogar.collidepoint((mx, my)) else (140, 60, 200)
         
    pygame.draw.rect(tela, cor_continuar, btn_jogar, border_radius=15)
    pygame.draw.rect(tela, (150, 40, 40) if not btn_novo.collidepoint((mx, my)) else (200, 60, 60), btn_novo, border_radius=15)
    pygame.draw.rect(tela, (50, 50, 50) if not btn_sair.collidepoint((mx, my)) else (80, 80, 80), btn_sair, border_radius=15)
     
    cor_texto_cont = (255, 255, 255) if tem_save else (100, 100, 100)
    tela.blit(pygame.font.SysFont('Arial', 30).render("CONTINUAR", True, cor_texto_cont), (btn_jogar.centerx - 80, btn_jogar.centery - 15))
    tela.blit(pygame.font.SysFont('Arial', 30).render("NOVO JOGO", True, (255, 255, 255)), (btn_novo.centerx - 80, btn_novo.centery - 15))
    tela.blit(pygame.font.SysFont('Arial', 30).render("FECHAR JOGO", True, (255, 255, 255)), (btn_sair.centerx - 90, btn_sair.centery - 15))
     
    btn_s, btn_n = None, None
    if confirmando_novo_jogo:
        btn_s, btn_n = desenhar_caixa_confirmacao(tela, "TEM CERTEZA?")
    elif confirmando_sair_jogo:
        btn_s, btn_n = desenhar_caixa_confirmacao(tela, "QUER SAIR DO JOGO?")
    return btn_jogar, btn_novo, btn_sair, btn_s, btn_n, tem_save

def desenhar_tela_morte(tela):
    s = pygame.Surface((largura_tela, altura_tela))
    s.set_alpha(180); s.fill((0, 0, 0)); tela.blit(s, (0,0))
    txt = pygame.font.SysFont('Arial Black', 80).render("VOCÊ CAIU", True, (255, 0, 0))
    tela.blit(txt, (largura_tela//2 - txt.get_width()//2, altura_tela//3))
    btn_renascer = pygame.Rect(largura_tela//2 - 100, altura_tela//2, 200, 60)
    pygame.draw.rect(tela, (255, 255, 255), btn_renascer, border_radius=10)
    tela.blit(pygame.font.SysFont('Arial', 30, bold=True).render("RENASCER", True, (0, 0, 0)), (btn_renascer.centerx - 70, btn_renascer.centery - 15))
    return btn_renascer

def desenhar_menu_note(tela):
    tela.fill((10, 10, 20))
    mx, my = pygame.mouse.get_pos()
    pygame.draw.rect(tela, (0, 255, 100), (largura_tela//4, 50, largura_tela//2, altura_tela-100), 3, border_radius=15)
    fonte_fases = pygame.font.SysFont('Arial', 28)
    btn_salvar = pygame.Rect(largura_tela // 2 - 100, 100, 200, 50)
    pygame.draw.rect(tela, (0, 100, 255) if not btn_salvar.collidepoint((mx, my)) else (50, 150, 255), btn_salvar, border_radius=10)
    tela.blit(fonte_fases.render("SALVAR JOGO", True, (255, 255, 255)), (btn_salvar.centerx - 80, btn_salvar.centery - 15))
    botoes_fases = {}
    for i in range(6):
        liberada = i in fases_desbloqueadas
        rect_fase = pygame.Rect(largura_tela // 2 - 200, 200 + i * 55, 400, 40)
        cor = (0, 255, 150) if liberada else (120, 120, 120)
        if liberada and rect_fase.collidepoint((mx, my)):
            pygame.draw.rect(tela, (20, 60, 40), rect_fase, border_radius=5)
            cor = (150, 255, 200)
        tela.blit(fonte_fases.render(f"Fase {i}: {'[LIBERADA]' if liberada else '[BLOQUEADA]'}", True, cor), (largura_tela // 2 - 180, 205 + i * 55))
        if liberada: botoes_fases[i] = rect_fase
    return btn_salvar, botoes_fases

def inimigo_seguir_jogador(inimigo, jogador_x, jogador_y, vel):
    dx, dy = jogador_x - inimigo.x, jogador_y - inimigo.y
    dist = math.hypot(dx, dy)
    if dist != 0:
        inimigo.x += (dx / dist) * vel
        inimigo.y += (dy / dist) * vel

# --- LOOP PRINCIPAL ---
try:
    print(f"Carregando música menu: {MUSICA_MENU}")
    pygame.mixer.music.load(MUSICA_MENU)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Erro música menu: {e}")

clock = pygame.time.Clock()
rodando = True
carregar_jogo()

while rodando:
    clock.tick(60)
    agora = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    clique_mouse = pygame.mouse.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: rodando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if menu: confirmando_sair_jogo = not confirmando_sair_jogo
                elif not menu_note and not morreu: confirmando_voltar_menu = not confirmando_voltar_menu
            if evento.key == pygame.K_TAB and not menu and not morreu:
                if len(fases_desbloqueadas) > 1: menu_note = not menu_note

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if menu:
                bj, bn, bs_exit, bs_box, bna_box, tem_save = desenhar_menu(tela) 
                if not confirmando_novo_jogo and not confirmando_sair_jogo:
                    if bj.collidepoint((mx, my)) and tem_save:
                        menu = False; ultimo_tiro = agora + 1000
                        try:
                            # --- CORREÇÃO AQUI ---
                            # Resetar mixer ao carregar jogo salvo também
                            pygame.mixer.music.stop()
                            pygame.mixer.quit()
                            pygame.mixer.init()
                            pygame.mixer.music.set_volume(1.0)
                            # ---------------------
                            print(f"Iniciando música gameplay (continuar): {MUSICA_GAMEPLAY}")
                            pygame.mixer.music.load(MUSICA_GAMEPLAY)
                            pygame.mixer.music.play(-1)
                        except Exception as e: 
                            print(f"ERRO AO CARREGAR MUSICA GAMEPLAY (CONTINUAR): {e}")
                    elif bn.collidepoint((mx, my)): confirmando_novo_jogo = True
                    elif bs_exit.collidepoint((mx, my)): confirmando_sair_jogo = True
                else:
                    if confirmando_novo_jogo:
                        if bs_box and bs_box.collidepoint((mx, my)): confirmando_novo_jogo = False; novo_jogo()
                        elif bna_box and bna_box.collidepoint((mx, my)): confirmando_novo_jogo = False
                    elif confirmando_sair_jogo:
                        if bs_box and bs_box.collidepoint((mx, my)): rodando = False
                        elif bna_box and bna_box.collidepoint((mx, my)): confirmando_sair_jogo = False
            
            elif morreu:
                btn_r = desenhar_tela_morte(tela)
                if btn_r.collidepoint((mx, my)):
                    hp = 100; morreu = False; x, y = largura_tela//2, altura_tela//2
                    resetar_inimigos_fase(fase_atual)
                    projetil_lista.clear(); projetil_inimigo_lista.clear()
            
            elif confirmando_voltar_menu:
                bs_box, bna_box = desenhar_caixa_confirmacao(tela, "VOLTAR AO MENU?")
                if bs_box.collidepoint((mx, my)):
                    salvar_jogo()
                    confirmando_voltar_menu = False; menu = True
                    try: 
                        # --- CORREÇÃO AO VOLTAR PRO MENU ---
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                        pygame.mixer.init()
                        pygame.mixer.music.set_volume(1.0)
                        # -----------------------------------
                        pygame.mixer.music.load(MUSICA_MENU)
                        pygame.mixer.music.play(-1)
                    except Exception as e:
                        print(f"Erro ao voltar para música menu: {e}")
                elif bna_box.collidepoint((mx, my)): confirmando_voltar_menu = False
            
            elif menu_note:
                bs_note, bf = desenhar_menu_note(tela)
                if bs_note.collidepoint((mx, my)): salvar_jogo()
                for n, r in bf.items():
                    if r.collidepoint((mx, my)):
                        fase_atual = n; resetar_inimigos_fase(n); menu_note = False
                        x, y, hp = largura_tela//2, altura_tela//2, 100
                        projetil_lista.clear(); projetil_inimigo_lista.clear()

    if menu:
        desenhar_menu(tela); pygame.display.flip(); continue
    if morreu:
        desenhar_tela_morte(tela); pygame.display.flip(); continue
    if confirmando_voltar_menu:
        desenhar_caixa_confirmacao(tela, "VOLTAR AO MENU?"); pygame.display.flip(); continue
    if menu_note:
        desenhar_menu_note(tela); pygame.display.flip(); continue

    # --- LÓGICA DO JOGO ---
    tela.fill(cor_fundo)
    desenhar_hud_tab(tela)
    teclas = pygame.key.get_pressed()
    dx_move, dy_move = 0, 0
    teclado = any([teclas[pygame.K_a], teclas[pygame.K_d], teclas[pygame.K_w], teclas[pygame.K_s], teclas[pygame.K_LEFT], teclas[pygame.K_RIGHT], teclas[pygame.K_UP], teclas[pygame.K_DOWN]])

    if teclado:
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: dx_move = -velocidade; direcao_jogador = "esquerda"
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx_move = velocidade; direcao_jogador = "direita"
        if teclas[pygame.K_w] or teclas[pygame.K_UP]: dy_move = -velocidade; direcao_jogador = "cima"
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dy_move = velocidade; direcao_jogador = "baixo"
    elif clique_mouse[2]:
        dx_m, dy_m = mx - (x + 25), my - (y + 25)
        dist = math.hypot(dx_m, dy_m)
        if dist > 5:
            dx_move, dy_move = (dx_m/dist)*velocidade, (dy_m/dist)*velocidade
            direcao_jogador = ("direita" if dx_m > 0 else "esquerda") if abs(dx_m) > abs(dy_m) else ("baixo" if dy_m > 0 else "cima")

    x = max(0, min(x + dx_move, largura_tela - largura_q))
    y = max(0, min(y + dy_move, altura_tela - altura_q))

    if (teclas[pygame.K_SPACE] or clique_mouse[0]) and agora >= ultimo_tiro:
        dx_t, dy_t = 0, 0
        if clique_mouse[0]:
            dx_m, dy_m = mx - (x + 25), my - (y + 25)
            dist = math.hypot(dx_m, dy_m)
            if dist > 0: dx_t, dy_t = (dx_m/dist)*projetil_velocidade, (dy_m/dist)*projetil_velocidade
        else:
            if direcao_jogador == "direita": dx_t = projetil_velocidade
            elif direcao_jogador == "esquerda": dx_t = -projetil_velocidade
            elif direcao_jogador == "cima": dy_t = -projetil_velocidade
            else: dy_t = projetil_velocidade
        projetil_lista.append({"rect": pygame.Rect(x+25, y+25, 30, 15), "dx": dx_t, "dy": dy_t})
        ultimo_tiro = agora + cooldown_tiro

    jogador_rect = pygame.Rect(x, y, largura_q, altura_q)
    pygame.draw.rect(tela, cor_jogador, jogador_rect)
    pygame.draw.circle(tela, cor_olho, (int(x + 12), int(y + 18)), 8)
    pygame.draw.circle(tela, cor_olho, (int(x + 38), int(y + 18)), 8)

    if not inimigos:
        desenhar_design_notebook(tela, notebook_rect)
        if jogador_rect.colliderect(notebook_rect):
            if not colidindo_notebook:
                if fase_atual + 1 <= 5 and (fase_atual + 1) not in fases_desbloqueadas:
                    fases_desbloqueadas.append(fase_atual + 1)
                menu_note = True; colidindo_notebook = True
        else: colidindo_notebook = False
    else:
        for ini in inimigos[:]:
            inimigo_seguir_jogador(ini["rect"], x, y, 2)
            pygame.draw.rect(tela, cor_inimigo if ini["tipo"] == "morador" else cor_guardiao, ini["rect"])
            cor_o = (0, 0, 0) if ini["tipo"] == "morador" else (255, 0, 255)
            pygame.draw.circle(tela, cor_o, (ini["rect"].x + 12, ini["rect"].y + 18), 6)
            pygame.draw.circle(tela, cor_o, (ini["rect"].x + 38, ini["rect"].y + 18), 6)
            if ini["tipo"] == "guardiao" and agora - ini.get("ultimo_ataque", 0) >= cooldown_tiro_inimigo:
                dx_i, dy_i = x - ini["rect"].centerx, y - ini["rect"].centery
                dist = math.hypot(dx_i, dy_i)
                if dist != 0:
                    projetil_inimigo_lista.append({"rect": pygame.Rect(ini["rect"].centerx, ini["rect"].centery, 15, 15), "dx": (dx_i/dist)*4, "dy": (dy_i/dist)*4})
                    ini["ultimo_ataque"] = agora
            if jogador_rect.colliderect(ini["rect"]) and agora - ultimo_dano >= intervalo_dano:
                hp -= 15; ultimo_dano = agora

    for p in projetil_lista[:]:
        p["rect"].x += p["dx"]; p["rect"].y += p["dy"]
        pygame.draw.rect(tela, (255, 255, 255), p["rect"])
        for ini in inimigos[:]:
            if p["rect"].colliderect(ini["rect"]):
                ini["hp"] -= 1
                if p in projetil_lista: projetil_lista.remove(p)
                if ini["hp"] <= 0: inimigos.remove(ini)

    for pi in projetil_inimigo_lista[:]:
        pi["rect"].x += pi["dx"]; pi["rect"].y += pi["dy"]
        pygame.draw.circle(tela, (200, 200, 200), pi["rect"].center, 7)
        if pi["rect"].colliderect(jogador_rect):
            hp -= 5; projetil_inimigo_lista.remove(pi)

    desenhar_barra_hp(tela, 20, 20, hp, max_hp)
    pygame.display.flip()
    if hp <= 0: morreu = True

pygame.quit()
