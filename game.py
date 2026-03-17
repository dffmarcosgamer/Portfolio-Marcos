import random
import math
import json
import os
import cv2
import sys
import pygame

try:
    import numpy as np
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- INICIALIZAÇÃO ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

info_tela = pygame.display.Info()
largura_tela = info_tela.current_w
altura_tela  = info_tela.current_h

tela = pygame.display.set_mode((largura_tela, altura_tela), pygame.FULLSCREEN)
pygame.display.set_caption("Note Kingdoms")

# --- CAMINHOS ---
MUSICA_MENU     = resource_path("assets/menumusic.mp3")
MUSICA_GAMEPLAY = resource_path("assets/gameplaymusic.mp3")
CAMINHO_VIDEO   = resource_path("assets/cut1 of.mp4")
SOM_VIDEO       = resource_path("assets/MUSICINE!OOF.mp3")

# --- SONS SINTÉTICOS ---
def _gerar_som(freq, dur, vol=0.25, forma='sine', decay=2.0):
    """Gera som sintético simples sem dependências externas."""
    if not NUMPY_OK:
        return None
    try:
        sr = 44100
        n  = int(sr * dur)
        t  = np.linspace(0, dur, n, False)
        if   forma == 'sine':   w = np.sin(2 * np.pi * freq * t)
        elif forma == 'square': w = np.sign(np.sin(2 * np.pi * freq * t))
        elif forma == 'noise':  w = np.random.uniform(-1, 1, n)
        else:                   w = np.sin(2 * np.pi * freq * t)
        env  = np.linspace(1, 0, n) ** decay
        wave = (w * env * vol * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack([wave, wave]))
    except Exception:
        return None

SOM_TIRO         = _gerar_som(700,  0.08, 0.18, 'square', 1.5)
SOM_IMPACTO      = _gerar_som(300,  0.10, 0.20, 'noise',  1.8)
SOM_MORTE_INI    = _gerar_som(450,  0.15, 0.20, 'sine',   2.0)
SOM_DANO_PLAYER  = _gerar_som(160,  0.18, 0.28, 'noise',  1.5)
SOM_SAVE         = _gerar_som(880,  0.25, 0.14, 'sine',   1.0)
SOM_NOTEBOOK     = _gerar_som(1000, 0.20, 0.14, 'sine',   1.2)
SOM_PROJINIMIGO  = _gerar_som(250,  0.08, 0.14, 'square', 1.8)

def tocar(som):
    if som:
        try: som.play()
        except Exception: pass

# --- SAVE ---
arquivo_save = "save_Note_Kingdon.json"

# --- ESTADOS ---
menu                   = True
menu_note              = False
confirmando_novo_jogo  = False
confirmando_voltar_menu= False
confirmando_sair_jogo  = False
morreu                 = False
fases_desbloqueadas    = [0]
colidindo_notebook     = False

# Notificação de save
save_notif_timer  = 0
save_notif_ativo  = False
save_notif_dur    = 2500

# Screen shake
shake_fim   = 0
shake_mag   = 0

# Guardamos os rects de botões do último frame desenhado
_btn_menu_cache  = None
_btn_morte_cache = None
_btn_conf_cache  = None

# --- JOGADOR ---
largura_q, altura_q = 50, 50
x, y        = largura_tela // 2, altura_tela // 2
velocidade  = 10
hp          = 100
max_hp      = 100
cor_olho    = (255, 0, 255)
cor_jogador = (255, 255, 255)

notebook_rect = pygame.Rect(largura_tela // 2 - 40, altura_tela // 2 - 30, 80, 50)

# --- PROJÉTEIS ---
projetil_velocidade      = 15
projetil_lista           = []
cooldown_tiro            = 600
ultimo_tiro              = 0
direcao_jogador          = "direita"
projetil_inimigo_lista   = []
cooldown_tiro_inimigo    = 1200
cor_fundo                = (70, 30, 80)
cor_inimigo              = (255, 0, 0)
cor_guardiao             = (0, 0, 0)
ultimo_dano              = 0
intervalo_dano           = 1000

# --- PARTÍCULAS ---
particles            = []   # partículas de gameplay
bg_particles         = []   # poeira de fundo (jogo)
menu_particles       = []   # partículas do menu

# Preenche bg
for _ in range(160):
    bg_particles.append({
        'x': random.randint(0, largura_tela),
        'y': random.randint(0, altura_tela),
        'sz': random.uniform(0.8, 2.5),
        'sp': random.uniform(0.15, 0.6),
        'base_alpha': random.randint(40, 180),
        'cor': random.choice([(255,255,255),(210,160,255),(130,80,220),(180,120,255)])
    })

for _ in range(70):
    menu_particles.append({
        'x':  random.randint(0, largura_tela),
        'y':  random.randint(0, altura_tela),
        'dx': random.uniform(-0.4, 0.4),
        'dy': random.uniform(-0.9, -0.2),
        'sz': random.uniform(1.0, 3.5),
        'cor': random.choice([(255,80,200),(180,40,255),(80,200,255),(255,180,80),(120,255,180)])
    })

# --- FASES ---
fases_originais = {
    0: [{"rect":[largura_tela*0.1, altura_tela*0.1, 50,50],"hp":3,"tipo":"morador"},
        {"rect":[largura_tela*0.5, altura_tela*0.3, 50,50],"hp":3,"tipo":"morador"},
        {"rect":[largura_tela*0.8, altura_tela*0.7, 50,50],"hp":3,"tipo":"morador"},
        {"rect":[largura_tela*0.2, altura_tela*0.8, 50,50],"hp":3,"tipo":"morador"},
        {"rect":[largura_tela*0.7, altura_tela*0.2, 50,50],"hp":3,"tipo":"morador"}],
    1: [{"rect":[random.randint(100,largura_tela-100),random.randint(100,altura_tela-100),50,50],"hp":4,"tipo":"morador"} for _ in range(4)],
    2: [{"rect":[random.randint(100,largura_tela-100),random.randint(100,altura_tela-100),60,60],"hp":8,"tipo":"guardiao","ultimo_ataque":0} for _ in range(3)],
    3: [{"rect":[random.randint(100,largura_tela-100),random.randint(100,altura_tela-100),50,50],"hp":5,"tipo":"morador"} for _ in range(5)],
    4: [{"rect":[random.randint(100,largura_tela-100),random.randint(100,altura_tela-100),60,60],"hp":10,"tipo":"guardiao","ultimo_ataque":0} for _ in range(4)],
    5: [{"rect":[random.randint(100,largura_tela-100),random.randint(100,altura_tela-100),55,55],"hp":7,"tipo":"morador"} for _ in range(6)]
}

fase_atual = 0
inimigos   = []

def resetar_inimigos_fase(f):
    global inimigos
    inimigos = []
    for i in fases_originais[f]:
        d = dict(i)
        d["rect"]         = pygame.Rect(i["rect"])
        d["max_hp"]       = i["hp"]
        d.setdefault("ultimo_ataque", 0)
        inimigos.append(d)

resetar_inimigos_fase(fase_atual)

# ============================================================
# UTILITÁRIOS DE TRANSIÇÃO
# ============================================================

def fade(para_preto: bool, duracao_ms: int = 500):
    """Faz fade para preto ou para o jogo com surface overlay."""
    surf = pygame.Surface((largura_tela, altura_tela))
    surf.fill((0, 0, 0))
    passos = 20
    delay  = max(1, duracao_ms // passos)
    for i in range(passos + 1):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        alpha = int(255 * i / passos) if para_preto else int(255 * (1 - i / passos))
        surf.set_alpha(alpha)
        tela.blit(surf, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)

# ============================================================
# SISTEMA DE PARTÍCULAS
# ============================================================

def spawn_particulas_tiro(px, py, dx, dy):
    ang_base = math.atan2(dy, dx)
    # Muzzle flash
    particles.append({'x':px,'y':py,'dx':0,'dy':0,'life':6,'max_life':6,'sz':14,'cor':(255,255,200),'flash':True})
    # Faíscas
    for _ in range(10):
        ang = ang_base + random.uniform(-0.45, 0.45)
        spd = random.uniform(3, 7)
        particles.append({'x':px,'y':py,
                          'dx':math.cos(ang)*spd,'dy':math.sin(ang)*spd,
                          'life':random.randint(8,20),'max_life':20,
                          'sz':random.uniform(2,5),
                          'cor':random.choice([(255,255,80),(255,200,40),(255,140,0)])})

def spawn_particulas_impacto(px, py):
    for _ in range(14):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(1.5, 6)
        particles.append({'x':px,'y':py,
                          'dx':math.cos(ang)*spd,'dy':math.sin(ang)*spd,
                          'life':random.randint(10,28),'max_life':28,
                          'sz':random.uniform(2,6),
                          'cor':random.choice([(255,60,0),(255,120,30),(200,0,0)])})

def spawn_particulas_morte(px, py):
    for _ in range(30):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(2, 9)
        particles.append({'x':px,'y':py,
                          'dx':math.cos(ang)*spd,'dy':math.sin(ang)*spd - 1.5,
                          'life':random.randint(20,45),'max_life':45,
                          'sz':random.uniform(3,9),
                          'cor':random.choice([(255,0,0),(200,0,0),(255,100,0),(130,0,0)])})

def spawn_particulas_dano_player(px, py):
    for _ in range(18):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(2, 7)
        particles.append({'x':px,'y':py,
                          'dx':math.cos(ang)*spd,'dy':math.sin(ang)*spd,
                          'life':random.randint(12,22),'max_life':22,
                          'sz':random.uniform(2,5),
                          'cor':(255,50,50)})

def spawn_particulas_notebook(rx, ry, rw, rh):
    if random.random() < 0.35:
        px = rx + random.randint(0, rw)
        py = ry + random.randint(0, rh)
        particles.append({'x':px,'y':py,
                          'dx':random.uniform(-0.6,0.6),'dy':random.uniform(-1.8,-0.4),
                          'life':random.randint(18,35),'max_life':35,
                          'sz':random.uniform(1.5,3.5),'cor':(0,255,100)})

def atualizar_particulas():
    global particles
    vivos = []
    for p in particles:
        p['x']  += p['dx']
        p['y']  += p['dy']
        p['dy'] += 0.14
        p['dx'] *= 0.94
        p['life'] -= 1
        if p['life'] > 0:
            ratio = p['life'] / p['max_life']
            sz    = max(1, int(p['sz'] * ratio))
            r,g,b = p['cor']
            if p.get('flash'):
                surf = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255,255,220,int(ratio*220)), (sz+1,sz+1), sz)
                tela.blit(surf, (int(p['x'])-sz, int(p['y'])-sz))
            else:
                col = (min(255,r), min(255,g), min(255,b))
                pygame.draw.circle(tela, col, (int(p['x']), int(p['y'])), sz)
            vivos.append(p)
    particles = vivos

# ============================================================
# FUNDO DINÂMICO
# ============================================================

def desenhar_fundo_jogo():
    t = pygame.time.get_ticks()
    for bp in bg_particles:
        bp['y'] -= bp['sp']
        if bp['y'] < -4:
            bp['y'] = altura_tela + 4
            bp['x'] = random.randint(0, largura_tela)
        pulse = int(abs(math.sin(t * 0.001 + bp['x'] * 0.012)) * 90 + bp['base_alpha'] - 45)
        pulse = max(15, min(230, pulse))
        sz    = max(1, int(bp['sz']))
        s = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
        r,g,b = bp['cor']
        pygame.draw.circle(s, (r,g,b,pulse), (sz+1, sz+1), sz)
        tela.blit(s, (int(bp['x'])-sz, int(bp['y'])-sz))

def desenhar_fundo_menu():
    t = pygame.time.get_ticks()
    for mp in menu_particles:
        mp['x'] += mp['dx']
        mp['y'] += mp['dy']
        if mp['y'] < -5:
            mp['y'] = altura_tela + 5
            mp['x'] = random.randint(0, largura_tela)
        if mp['x'] < -5 or mp['x'] > largura_tela + 5:
            mp['x'] = random.randint(0, largura_tela)
        alpha = int(abs(math.sin(t * 0.0025 + mp['x'] * 0.01)) * 110 + 70)
        sz    = max(1, int(mp['sz']))
        s = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
        r,g,b = mp['cor']
        pygame.draw.circle(s, (r,g,b,alpha), (sz+1, sz+1), sz)
        tela.blit(s, (int(mp['x'])-sz, int(mp['y'])-sz))

# ============================================================
# HUD & UI
# ============================================================

def desenhar_barra_hp_player(surf, bx, by, _hp, _max):
    larg, alt = 200, 25
    hp_v = max(0, min(_hp, _max))
    prop = hp_v / _max
    pygame.draw.rect(surf, (50,50,50), (bx, by, larg, alt))
    if hp_v > 0:
        r = int(255*(1-prop)); g = int(255*prop)
        pygame.draw.rect(surf, (r,g,0), (bx, by, int(larg*prop), alt))

def desenhar_barra_hp_inimigo(ini):
    r    = ini["rect"]
    prop = max(0.0, ini["hp"] / max(1, ini["max_hp"]))
    bx, by = r.x, r.y - 13
    larg, alt = r.width, 7
    pygame.draw.rect(tela, (40,10,10), (bx, by, larg, alt))
    if prop > 0:
        vr = int(255*(1-prop)); vg = int(200*prop)
        pygame.draw.rect(tela, (vr,vg,0), (bx, by, int(larg*prop), alt))
    pygame.draw.rect(tela, (180,180,180), (bx, by, larg, alt), 1)

def desenhar_hud_tab():
    if len(fases_desbloqueadas) > 1:
        t   = pygame.time.get_ticks()
        txt = pygame.font.SysFont('Arial', 22, bold=True).render("[TAB] NOTEBOOK", True, (0,255,100))
        txt.set_alpha(int(abs(math.sin(t*0.005))*255))
        tela.blit(txt, (largura_tela - 210, 30))

def desenhar_notificacao_save(agora):
    global save_notif_ativo
    if not save_notif_ativo: return
    elapsed = agora - save_notif_timer
    if elapsed >= save_notif_dur:
        save_notif_ativo = False
        return
    alpha = 255
    fade_start = save_notif_dur * 0.55
    if elapsed > fade_start:
        alpha = int(255 * (1 - (elapsed - fade_start) / (save_notif_dur - fade_start)))
    fonte = pygame.font.SysFont('Arial', 30, bold=True)
    txt   = fonte.render("✓  JOGO SALVO!", True, (255, 220, 0))
    txt.set_alpha(max(0, alpha))
    tela.blit(txt, (largura_tela - txt.get_width() - 20, 65))

# ============================================================
# DESIGN ORIGINAL (mantido)
# ============================================================

def desenhar_design_notebook(surf, rect):
    pygame.draw.rect(surf, (40,40,40),
                     (rect.x, rect.y + rect.height//2, rect.width, rect.height//2),
                     border_bottom_left_radius=5, border_bottom_right_radius=5)
    pygame.draw.rect(surf, (20,20,20),
                     (rect.x+5, rect.y, rect.width-10, rect.height//2+5),
                     border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.rect(surf, (0,40,20),
                     (rect.x+10, rect.y+5, rect.width-20, rect.height//2-5))
    pygame.draw.line(surf, (0,255,100), (rect.x+15, rect.y+10), (rect.x+40, rect.y+10), 2)
    pygame.draw.line(surf, (0,255,100), (rect.x+15, rect.y+15), (rect.x+30, rect.y+15), 2)
    for i in range(3):
        pygame.draw.line(surf, (60,60,60),
                         (rect.x+10, rect.y+32+i*4), (rect.x+rect.width-10, rect.y+32+i*4), 1)

def desenhar_notebook_com_brilho(agora):
    pulse = abs(math.sin(agora * 0.004)) * 35 + 8
    gw, gh = notebook_rect.width+24, notebook_rect.height+24
    gs = pygame.Surface((gw, gh), pygame.SRCALPHA)
    pygame.draw.rect(gs, (0,255,100,int(pulse)), (0,0,gw,gh), border_radius=12)
    tela.blit(gs, (notebook_rect.x-12, notebook_rect.y-12))
    spawn_particulas_notebook(notebook_rect.x, notebook_rect.y,
                              notebook_rect.width, notebook_rect.height)
    desenhar_design_notebook(tela, notebook_rect)

# ============================================================
# TELAS
# ============================================================

def desenhar_caixa_confirmacao(texto):
    bx, by = largura_tela//2 - 200, altura_tela//2 - 100
    pygame.draw.rect(tela, (30,30,30), (bx, by, 400, 200), border_radius=20)
    pygame.draw.rect(tela, (255,255,255), (bx, by, 400, 200), 2, border_radius=20)
    txt = pygame.font.SysFont('Arial', 25).render(texto, True, (255,255,255))
    tela.blit(txt, (largura_tela//2 - txt.get_width()//2, by+40))
    btn_sim = pygame.Rect(largura_tela//2-110, altura_tela//2+10, 100, 50)
    btn_nao = pygame.Rect(largura_tela//2+10,  altura_tela//2+10, 100, 50)
    pygame.draw.rect(tela, (0,150,0),  btn_sim, border_radius=10)
    pygame.draw.rect(tela, (150,0,0),  btn_nao, border_radius=10)
    f = pygame.font.SysFont('Arial', 20, bold=True)
    tela.blit(f.render("SIM", True, (255,255,255)), (btn_sim.centerx-18, btn_sim.centery-12))
    tela.blit(f.render("NÃO", True, (255,255,255)), (btn_nao.centerx-18, btn_nao.centery-12))
    return btn_sim, btn_nao

def desenhar_menu():
    global _btn_menu_cache
    tela.fill(cor_fundo)
    desenhar_fundo_menu()
    agora = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()

    # Título animado
    ty_off = math.sin(agora * 0.002) * 8
    ft = pygame.font.SysFont('Arial Black', 72)
    titulo = ft.render("Note Kingdon", True, (255,255,255))
    glow   = ft.render("Note Kingdon", True, (200,100,255))
    glow_a = int(abs(math.sin(agora*0.003))*60+25)
    glow.set_alpha(glow_a)
    tx = largura_tela//2 - titulo.get_width()//2
    ty = int(altura_tela//5 + ty_off)
    tela.blit(glow,  (tx+3, ty+3))
    tela.blit(titulo,(tx,   ty))

    tem_save = os.path.exists(arquivo_save)
    bj = pygame.Rect(largura_tela//2-150, altura_tela//2-100, 300, 60)
    bn = pygame.Rect(largura_tela//2-150, altura_tela//2-20,  300, 60)
    bs = pygame.Rect(largura_tela//2-150, altura_tela//2+60,  300, 60)

    # Hover glow
    for btn, hover_cor, base_cor in [
        (bj, (140,60,200), (100,40,150) if tem_save else (30,30,30)),
        (bn, (200,60,60),  (150,40,40)),
        (bs, (80,80,80),   (50,50,50))
    ]:
        cor = hover_cor if btn.collidepoint((mx,my)) and (btn!=bj or tem_save) else base_cor
        if btn.collidepoint((mx,my)) and (btn!=bj or tem_save):
            gs = pygame.Surface((btn.width+16, btn.height+16), pygame.SRCALPHA)
            r,g,b = hover_cor
            pygame.draw.rect(gs, (r,g,b,50), (0,0,btn.width+16,btn.height+16), border_radius=18)
            tela.blit(gs, (btn.x-8, btn.y-8))
        pygame.draw.rect(tela, cor, btn, border_radius=15)

    f30 = pygame.font.SysFont('Arial', 30)
    ct  = (255,255,255) if tem_save else (100,100,100)
    tela.blit(f30.render("CONTINUAR",  True, ct),          (bj.centerx-80, bj.centery-15))
    tela.blit(f30.render("NOVO JOGO",  True, (255,255,255)),(bn.centerx-75, bn.centery-15))
    tela.blit(f30.render("FECHAR JOGO",True, (255,255,255)),(bs.centerx-85, bs.centery-15))

    bs_box = bn_box = None
    if   confirmando_novo_jogo: bs_box, bn_box = desenhar_caixa_confirmacao("TEM CERTEZA?")
    elif confirmando_sair_jogo: bs_box, bn_box = desenhar_caixa_confirmacao("QUER SAIR DO JOGO?")

    desenhar_notificacao_save(agora)
    _btn_menu_cache = (bj, bn, bs, bs_box, bn_box, tem_save)
    return _btn_menu_cache

def desenhar_tela_morte():
    global _btn_morte_cache
    s = pygame.Surface((largura_tela, altura_tela))
    s.set_alpha(185); s.fill((0,0,0)); tela.blit(s,(0,0))
    agora = pygame.time.get_ticks()
    pulse = abs(math.sin(agora*0.004))*40
    txt = pygame.font.SysFont('Arial Black',80).render("VOCÊ CAIU",True,(255,int(pulse),int(pulse)))
    tela.blit(txt,(largura_tela//2-txt.get_width()//2, altura_tela//3))
    btn = pygame.Rect(largura_tela//2-100, altura_tela//2, 200, 60)
    pygame.draw.rect(tela, (255,255,255), btn, border_radius=10)
    tela.blit(pygame.font.SysFont('Arial',30,bold=True).render("RENASCER",True,(0,0,0)),
              (btn.centerx-70, btn.centery-15))
    _btn_morte_cache = btn
    return btn

def desenhar_menu_note():
    tela.fill((10,10,20))
    mx, my = pygame.mouse.get_pos()
    agora  = pygame.time.get_ticks()

    # Borda animada (design original mantido)
    ba = int(abs(math.sin(agora*0.003))*100+155)
    bs2 = pygame.Surface((largura_tela//2+10, altura_tela-90), pygame.SRCALPHA)
    pygame.draw.rect(bs2,(0,255,100,ba),(0,0,largura_tela//2,altura_tela-100),3,border_radius=15)
    tela.blit(bs2,(largura_tela//4,50))

    f28 = pygame.font.SysFont('Arial',28)
    btn_salvar = pygame.Rect(largura_tela//2-100, 100, 200, 50)
    hover_save = btn_salvar.collidepoint((mx,my))
    if hover_save:
        gs = pygame.Surface((220,70),pygame.SRCALPHA)
        pygame.draw.rect(gs,(0,100,255,55),(0,0,220,70),border_radius=12)
        tela.blit(gs,(btn_salvar.x-10, btn_salvar.y-10))
    pygame.draw.rect(tela,(50,150,255) if hover_save else (0,100,255), btn_salvar, border_radius=10)
    tela.blit(f28.render("SALVAR JOGO",True,(255,255,255)),(btn_salvar.centerx-82, btn_salvar.centery-15))

    botoes_fases = {}
    for i in range(6):
        lib  = i in fases_desbloqueadas
        rf   = pygame.Rect(largura_tela//2-200, 200+i*55, 400, 40)
        cor  = (0,255,150) if lib else (120,120,120)
        if lib and rf.collidepoint((mx,my)):
            pygame.draw.rect(tela,(20,60,40),rf,border_radius=5)
            gs = pygame.Surface((420,60),pygame.SRCALPHA)
            pygame.draw.rect(gs,(0,255,100,40),(0,0,420,60),border_radius=7)
            tela.blit(gs,(rf.x-10,rf.y-10))
            cor = (150,255,200)
        label = f"Fase {i}: {'[LIBERADA]' if lib else '[BLOQUEADA]'}"
        tela.blit(f28.render(label,True,cor),(largura_tela//2-180, 205+i*55))
        if lib: botoes_fases[i] = rf

    desenhar_notificacao_save(agora)
    return btn_salvar, botoes_fases

# ============================================================
# LÓGICA
# ============================================================

def separar_inimigos():
    sep  = 85
    forca= 2.2
    n    = len(inimigos)
    for i in range(n):
        for j in range(i+1, n):
            a, b = inimigos[i]["rect"], inimigos[j]["rect"]
            dx = a.centerx - b.centerx
            dy = a.centery - b.centery
            d  = math.hypot(dx, dy)
            if 0 < d < sep:
                f  = (sep - d) / sep * forca
                nx, ny = dx/d, dy/d
                a.x = max(0, min(int(a.x + nx*f), largura_tela-a.width))
                a.y = max(0, min(int(a.y + ny*f), altura_tela-a.height))
                b.x = max(0, min(int(b.x - nx*f), largura_tela-b.width))
                b.y = max(0, min(int(b.y - ny*f), altura_tela-b.height))

def inimigo_seguir_jogador(rect, jx, jy, vel=2):
    dx, dy = jx - rect.x, jy - rect.y
    d = math.hypot(dx, dy)
    if d: rect.x += (dx/d)*vel; rect.y += (dy/d)*vel

def salvar_jogo():
    global save_notif_ativo, save_notif_timer
    if morreu: return
    ini_save = [{"rect":[i["rect"].x,i["rect"].y,i["rect"].width,i["rect"].height],
                 "hp":i["hp"],"max_hp":i["max_hp"],"tipo":i["tipo"]} for i in inimigos]
    dados = {"fases_desbloqueadas":fases_desbloqueadas,"fase_atual":fase_atual,
             "player_x":x,"player_y":y,"player_hp":hp,"inimigos_vivos":ini_save}
    try:
        with open(arquivo_save,"w") as f: json.dump(dados,f)
        save_notif_ativo  = True
        save_notif_timer  = pygame.time.get_ticks()
        tocar(SOM_SAVE)
    except Exception as e:
        print(f"Erro ao salvar: {e}")

def carregar_jogo():
    global fases_desbloqueadas, fase_atual, inimigos, x, y, hp
    if not os.path.exists(arquivo_save): return
    try:
        with open(arquivo_save,"r") as f: dados = json.load(f)
        fases_desbloqueadas = dados.get("fases_desbloqueadas",[0])
        fase_atual          = dados.get("fase_atual",0)
        x  = dados.get("player_x", largura_tela//2)
        y  = dados.get("player_y", altura_tela//2)
        hp = dados.get("player_hp",100)
        inimigos = []
        for i in dados.get("inimigos_vivos",[]):
            d = {"rect":pygame.Rect(i["rect"]),"hp":i["hp"],
                 "max_hp":i.get("max_hp", i["hp"]),
                 "tipo":i["tipo"],"ultimo_ataque":0}
            inimigos.append(d)
    except Exception as e:
        print(f"Save corrompido: {e}")

def rodar_video():
    """Roda a cutscene com fade in/out e tela preta de delay."""
    if not os.path.exists(CAMINHO_VIDEO):
        return

    # Fade para preto antes
    fade(para_preto=True, duracao_ms=500)

    # Tela preta por 400ms
    tela.fill((0,0,0))
    pygame.display.flip()
    inicio = pygame.time.get_ticks()
    while pygame.time.get_ticks() - inicio < 400:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.time.delay(10)

    cap = cv2.VideoCapture(CAMINHO_VIDEO)
    fps_v = cap.get(cv2.CAP_PROP_FPS)
    if fps_v <= 0: fps_v = 30

    if os.path.exists(SOM_VIDEO):
        pygame.mixer.music.load(SOM_VIDEO)
        pygame.mixer.music.play()

    clk_v = pygame.time.Clock()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                cap.release(); pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                cap.release(); pygame.mixer.music.stop()
                fade(para_preto=False, duracao_ms=400)
                return
        frame = cv2.cvtColor(cv2.resize(frame,(largura_tela,altura_tela)), cv2.COLOR_BGR2RGB)
        tela.blit(pygame.surfarray.make_surface(frame.swapaxes(0,1)),(0,0))
        pygame.display.flip()
        clk_v.tick(fps_v)

    cap.release()
    pygame.mixer.music.stop()
    fade(para_preto=False, duracao_ms=400)

def novo_jogo():
    global fases_desbloqueadas, fase_atual, x, y, hp, menu, ultimo_tiro
    pygame.mixer.music.stop()
    rodar_video()

    if os.path.exists(arquivo_save): os.remove(arquivo_save)
    fases_desbloqueadas = [0]
    fase_atual  = 0
    resetar_inimigos_fase(0)
    x, y, hp    = largura_tela//2, altura_tela//2, 100
    particles.clear()

    if os.path.exists(MUSICA_GAMEPLAY):
        pygame.mixer.music.load(MUSICA_GAMEPLAY)
        pygame.mixer.music.play(-1)

    ultimo_tiro = pygame.time.get_ticks() + 1000
    menu = False
    salvar_jogo()

# ============================================================
# ARRANQUE
# ============================================================
if os.path.exists(MUSICA_MENU):
    pygame.mixer.music.load(MUSICA_MENU)
    pygame.mixer.music.play(-1)

carregar_jogo()
fade(para_preto=False, duracao_ms=500)   # Fade-in na abertura

clock   = pygame.time.Clock()
rodando = True

# ============================================================
# LOOP PRINCIPAL
# ============================================================
while rodando:
    clock.tick(60)
    agora         = pygame.time.get_ticks()
    mx, my        = pygame.mouse.get_pos()
    clique_mouse  = pygame.mouse.get_pressed()

    # ---------- EVENTOS ----------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            if not menu and not morreu: salvar_jogo()
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if menu:
                    confirmando_sair_jogo = not confirmando_sair_jogo
                elif not menu_note and not morreu:
                    confirmando_voltar_menu = not confirmando_voltar_menu
            if evento.key == pygame.K_TAB and not menu and not morreu:
                if len(fases_desbloqueadas) > 1:
                    menu_note = not menu_note
                    tocar(SOM_NOTEBOOK)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

            # ---- MENU PRINCIPAL ----
            if menu and _btn_menu_cache is not None:
                bj,bn,bse,bsbox,bnbox,tem_save = _btn_menu_cache
                if not confirmando_novo_jogo and not confirmando_sair_jogo:
                    if bj.collidepoint((mx,my)) and tem_save:
                        fade(para_preto=True, duracao_ms=350)
                        menu         = False
                        ultimo_tiro  = agora + 1000
                        pygame.mixer.music.stop()
                        if os.path.exists(MUSICA_GAMEPLAY):
                            pygame.mixer.music.load(MUSICA_GAMEPLAY)
                            pygame.mixer.music.play(-1)
                        # Primeiro frame do jogo já renderizado antes do fade-out
                        fade(para_preto=False, duracao_ms=350)
                    elif bn.collidepoint((mx,my)):
                        confirmando_novo_jogo = True
                    elif bse.collidepoint((mx,my)):
                        confirmando_sair_jogo = True
                else:
                    if confirmando_novo_jogo:
                        if bsbox and bsbox.collidepoint((mx,my)):
                            confirmando_novo_jogo = False; novo_jogo()
                        elif bnbox and bnbox.collidepoint((mx,my)):
                            confirmando_novo_jogo = False
                    elif confirmando_sair_jogo:
                        if bsbox and bsbox.collidepoint((mx,my)):
                            rodando = False
                        elif bnbox and bnbox.collidepoint((mx,my)):
                            confirmando_sair_jogo = False

            # ---- TELA DE MORTE ----
            elif morreu and _btn_morte_cache and _btn_morte_cache.collidepoint((mx,my)):
                hp = 100; morreu = False
                x, y = largura_tela//2, altura_tela//2
                resetar_inimigos_fase(fase_atual)
                projetil_lista.clear(); projetil_inimigo_lista.clear()
                particles.clear()

            # ---- CONFIRMAÇÃO VOLTAR MENU ----
            elif confirmando_voltar_menu and _btn_conf_cache:
                bs_c, bn_c = _btn_conf_cache
                if bs_c.collidepoint((mx,my)):
                    salvar_jogo()
                    fade(para_preto=True, duracao_ms=350)
                    confirmando_voltar_menu = False; menu = True
                    if os.path.exists(MUSICA_MENU):
                        pygame.mixer.music.load(MUSICA_MENU); pygame.mixer.music.play(-1)
                    fade(para_preto=False, duracao_ms=350)
                elif bn_c.collidepoint((mx,my)):
                    confirmando_voltar_menu = False

            # ---- NOTEBOOK ----
            elif menu_note:
                bs_note, bf = desenhar_menu_note()
                if bs_note.collidepoint((mx,my)):
                    salvar_jogo()
                for n, rf in bf.items():
                    if rf.collidepoint((mx,my)):
                        fase_atual = n; resetar_inimigos_fase(n); menu_note = False
                        x,y,hp = largura_tela//2, altura_tela//2, 100
                        projetil_lista.clear(); projetil_inimigo_lista.clear()
                        particles.clear()

    # ---------- DESENHO: ESTADOS ESPECIAIS ----------
    if menu:
        desenhar_menu()
        pygame.display.flip()
        continue

    if morreu:
        desenhar_tela_morte()
        pygame.display.flip()
        continue

    if confirmando_voltar_menu:
        tela.fill(cor_fundo)
        desenhar_fundo_jogo()
        _btn_conf_cache = desenhar_caixa_confirmacao("VOLTAR AO MENU?")
        desenhar_notificacao_save(agora)
        pygame.display.flip()
        continue

    if menu_note:
        desenhar_menu_note()
        pygame.display.flip()
        continue

    # ============================================================
    # LÓGICA DO JOGO
    # ============================================================
    # Screen shake offset
    ox = oy = 0
    if agora < shake_fim:
        ox = random.randint(-shake_mag, shake_mag)
        oy = random.randint(-shake_mag, shake_mag)

    tela.fill(cor_fundo)
    desenhar_fundo_jogo()
    desenhar_hud_tab()

    # Movimento do jogador
    teclas = pygame.key.get_pressed()
    dx_m = dy_m = 0
    teclado = any(teclas[k] for k in (pygame.K_a,pygame.K_d,pygame.K_w,pygame.K_s,
                                       pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN))
    if teclado:
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:  dx_m=-velocidade; direcao_jogador="esquerda"
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx_m=velocidade; direcao_jogador="direita"
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:   dy_m=-velocidade; direcao_jogador="cima"
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dy_m=velocidade; direcao_jogador="baixo"
    elif clique_mouse[2]:
        ddx,ddy = mx-(x+25), my-(y+25)
        dist    = math.hypot(ddx,ddy)
        if dist > 5:
            dx_m,dy_m = (ddx/dist)*velocidade,(ddy/dist)*velocidade
            direcao_jogador = ("direita" if ddx>0 else "esquerda") if abs(ddx)>abs(ddy) else ("baixo" if ddy>0 else "cima")

    x = max(0, min(x+dx_m, largura_tela-largura_q))
    y = max(0, min(y+dy_m, altura_tela-altura_q))

    # Tiro do jogador
    if (teclas[pygame.K_SPACE] or clique_mouse[0]) and agora >= ultimo_tiro:
        dx_t = dy_t = 0
        if clique_mouse[0]:
            ddx,ddy = mx-(x+25), my-(y+25)
            d = math.hypot(ddx,ddy)
            if d > 0: dx_t,dy_t = (ddx/d)*projetil_velocidade,(ddy/d)*projetil_velocidade
        else:
            mapa = {"direita":(projetil_velocidade,0),"esquerda":(-projetil_velocidade,0),
                    "cima":(0,-projetil_velocidade),"baixo":(0,projetil_velocidade)}
            dx_t,dy_t = mapa[direcao_jogador]
        projetil_lista.append({"rect":pygame.Rect(x+25,y+25,30,15),"dx":dx_t,"dy":dy_t})
        spawn_particulas_tiro(x+25, y+25, dx_t, dy_t)
        tocar(SOM_TIRO)
        ultimo_tiro = agora + cooldown_tiro

    # Desenha jogador (com shake offset)
    jogador_rect = pygame.Rect(x, y, largura_q, altura_q)
    pygame.draw.rect(tela, cor_jogador, (x+ox, y+oy, largura_q, altura_q))
    pygame.draw.circle(tela, cor_olho, (x+12+ox, y+18+oy), 8)
    pygame.draw.circle(tela, cor_olho, (x+38+ox, y+18+oy), 8)

    # Notebook ou inimigos
    if not inimigos:
        desenhar_notebook_com_brilho(agora)
        if jogador_rect.colliderect(notebook_rect):
            if not colidindo_notebook:
                prox = fase_atual + 1
                if prox <= 5 and prox not in fases_desbloqueadas:
                    fases_desbloqueadas.append(prox)
                tocar(SOM_NOTEBOOK)
                menu_note = True; colidindo_notebook = True
        else:
            colidindo_notebook = False
    else:
        separar_inimigos()
        for ini in inimigos[:]:
            inimigo_seguir_jogador(ini["rect"], x, y, 2)
            # Cor conforme tipo (design original)
            cor_body = cor_inimigo if ini["tipo"]=="morador" else cor_guardiao
            pygame.draw.rect(tela, cor_body,
                             (ini["rect"].x+ox, ini["rect"].y+oy, ini["rect"].width, ini["rect"].height))
            # Olhos — mesma escala que o jogador (raio 8), cores originais mantidas
            cor_eye = (0,0,0) if ini["tipo"]=="morador" else (255,0,255)
            pygame.draw.circle(tela, cor_eye, (ini["rect"].x+12+ox, ini["rect"].y+18+oy), 8)
            pygame.draw.circle(tela, cor_eye, (ini["rect"].x+38+ox, ini["rect"].y+18+oy), 8)
            # Barra de HP do inimigo
            desenhar_barra_hp_inimigo(ini)

            # Tiro do guardião
            if ini["tipo"]=="guardiao" and agora - ini.get("ultimo_ataque",0) >= cooldown_tiro_inimigo:
                ddx = x - ini["rect"].centerx; ddy = y - ini["rect"].centery
                d   = math.hypot(ddx,ddy)
                if d:
                    projetil_inimigo_lista.append({"rect":pygame.Rect(ini["rect"].centerx,ini["rect"].centery,15,15),
                                                   "dx":(ddx/d)*4,"dy":(ddy/d)*4})
                    tocar(SOM_PROJINIMIGO)
                    ini["ultimo_ataque"] = agora

            # Colisão inimigo→player
            if jogador_rect.colliderect(ini["rect"]) and agora - ultimo_dano >= intervalo_dano:
                hp          -= 15
                ultimo_dano  = agora
                spawn_particulas_dano_player(x+25, y+25)
                tocar(SOM_DANO_PLAYER)
                shake_fim = agora + 320; shake_mag = 6

    # Projéteis do jogador
    for p in projetil_lista[:]:
        p["rect"].x += p["dx"]; p["rect"].y += p["dy"]
        bx,by = p["rect"].x+ox, p["rect"].y+oy
        # Corpo do projétil
        pygame.draw.rect(tela, (220,220,80), (bx, by, p["rect"].width, p["rect"].height))
        # Brilho central
        pygame.draw.circle(tela, (255,255,200), (int(bx+p["rect"].width//2), int(by+p["rect"].height//2)), 7)
        # Fora da tela
        if p["rect"].x<-50 or p["rect"].x>largura_tela+50 or p["rect"].y<-50 or p["rect"].y>altura_tela+50:
            if p in projetil_lista: projetil_lista.remove(p)
            continue
        # Colisão com inimigos
        acertou = False
        for ini in inimigos[:]:
            if p["rect"].colliderect(ini["rect"]):
                ini["hp"] -= 1
                spawn_particulas_impacto(p["rect"].centerx, p["rect"].centery)
                tocar(SOM_IMPACTO)
                if p in projetil_lista: projetil_lista.remove(p)
                if ini["hp"] <= 0:
                    spawn_particulas_morte(ini["rect"].centerx, ini["rect"].centery)
                    tocar(SOM_MORTE_INI)
                    inimigos.remove(ini)
                acertou = True
                break

    # Projéteis dos inimigos
    for pi in projetil_inimigo_lista[:]:
        pi["rect"].x += pi["dx"]; pi["rect"].y += pi["dy"]
        cx,cy = pi["rect"].center
        # Glow externo
        pygame.draw.circle(tela, (120,30,30), (cx+ox, cy+oy), 10)
        pygame.draw.circle(tela, (200,200,200),(cx+ox, cy+oy), 7)
        # Fora da tela
        if pi["rect"].x<-50 or pi["rect"].x>largura_tela+50 or pi["rect"].y<-50 or pi["rect"].y>altura_tela+50:
            if pi in projetil_inimigo_lista: projetil_inimigo_lista.remove(pi)
            continue
        if pi["rect"].colliderect(jogador_rect):
            hp -= 5
            spawn_particulas_dano_player(x+25, y+25)
            tocar(SOM_DANO_PLAYER)
            shake_fim = agora + 200; shake_mag = 4
            if pi in projetil_inimigo_lista: projetil_inimigo_lista.remove(pi)

    # Partículas
    atualizar_particulas()

    # HUD player
    desenhar_barra_hp_player(tela, 20, 20, hp, max_hp)
    desenhar_notificacao_save(agora)
    pygame.display.flip()

    if hp <= 0: morreu = True

pygame.quit()
