# Note Kingdoms — Beta 1.0
import random, math, json, os, cv2, sys
import pygame

try:
    import numpy as np
    NUMPY_OK = True
except ImportError:
    NUMPY_OK = False

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def resource_path(p):
    try: base = sys._MEIPASS
    except: base = os.path.abspath(".")
    return os.path.join(base, p)

# ============================================================
# CONFIGURAÇÕES — EDITE AQUI
# ============================================================
ORBS_PRIMEIRA_VEZ  = 10
ORBS_REVISITA      = 3

CUSTO_DASH         = 15
CUSTO_ESCUDO       = 20
CUSTO_DANO_BOOST   = 25
CUSTO_VIDA_BOOST   = 20
CUSTO_TIRO_MAIOR   = 15
CUSTO_TIRO_FOGO    = 30

CUSTO_FASES_6_11   = 30
CUSTO_FASES_12_17  = 60
CUSTO_FASES_18_21  = 100

DASH_VELOCIDADE    = 28
DASH_DURACAO_MS    = 130
DASH_COOLDOWN_MS   = 2000

ESCUDO_DURACAO_MS  = 3000
ESCUDO_COOLDOWN_MS = 8000

DANO_BOOST_MULT    = 2
VIDA_BOOST_QTD     = 50

FOGO_DANO_TICK     = 1
FOGO_TICKS         = 4
FOGO_INTERVALO_MS  = 600

GUARDIAN_DANO_MULT = 1.5

# ============================================================
# IDIOMA
# ============================================================
idioma = "pt"

STRINGS = {
    "pt": {
        "titulo":        "Note Kingdom",
        "beta":          "BETA 1.0",
        "continuar":     "CONTINUAR",
        "novo_jogo":     "NOVO JOGO",
        "fechar":        "FECHAR JOGO",
        "apagar_save":   "APAGAR SAVE",
        "tem_certeza":   "TEM CERTEZA?",
        "sair_jogo":     "QUER SAIR DO JOGO?",
        "apagar_conf":   "APAGAR SAVE?",
        "voce_caiu":     "VOCÊ CAIU",
        "renascer":      "RENASCER",
        "voltar_menu":   "VOLTAR AO MENU?",
        "salvar_jogo":   "SALVAR JOGO",
        "jogo_salvo":    "✓  JOGO SALVO!",
        "tab_nb":        "[TAB] NOTEBOOK",
        "nb_titulo":     "NOTEBOOK",
        "aba_fases":     "FASES",
        "aba_habs":      "HABILIDADES",
        "voltar":        "< VOLTAR",
        "fase":          "Fase",
        "liberada":      "[LIBERADA]",
        "bloqueada":     "[BLOQUEADA]",
        "comprar":       "COMPRAR",
        "comprado":      "✓ COMPRADO",
        "sem_orbs":      "SEM ORBS",
        "orbs":          "ORBS",
        "comprar_grupo": "COMPRAR FASES",
        "sim":           "SIM",
        "nao":           "NÃO",
        "cutscene":      "assets/cut1 of.mp4",
        "fim_titulo":    "FIM DA BETA 1.0",
        "fim_msg":       "O criador ainda vai fazer mais áreas!",
        "continuar_btn": "CONTINUAR",
        "autor_titulo":  "NOTA DO AUTOR",
        "autor": [
            "Eu gostei quando me chamaram de Nhanga.",
            "Eu queria estudar Pygame com o ChatGPT mas gostei tanto de fazer esse jogo.",
            "Naquela época era 'Prison Realms', hoje é 'Note Kingdom' por direitos autorais.",
            "Fiz esse jogo com muitas IAs: ChatGPT, Gemini e agora Claude AI.",
            "Tenho 14 anos e sou do Brasil.",
            "Meu jogo é um quadrado branco com olhos que luta contra quadrados",
            "vermelhos com olhos pretos. Com um notebook ele vai ganhando habilidades.",
            "Os guardiões (pretos) também ganham essas habilidades.",
            "Os moradores (vermelhos) vivem na simulação.",
            "O quadrado branco é um bug na simulação.",
            "Tenho um primo de TI que prometeu me ajudar quando puder.",
            "Fiz vídeos no TikTok que não foram bem, mas não desisti.",
            "",
            "Obrigado por jogar Note Kingdoms!",
        ],
        "fechar_btn":    "FECHAR",
        "hab_dash":      "DASH",        "dash_desc":   "Q — dash na direção do movimento",
        "hab_escudo":    "ESCUDO",      "escudo_desc": "E — escudo temporário",
        "hab_dano":      "BOOST DANO",  "dano_desc":   "Projéteis causam 2x dano",
        "hab_vida":      "BOOST VIDA",  "vida_desc":   f"+{VIDA_BOOST_QTD} de vida máxima",
        "hab_tiro_m":    "TIRO MAIOR",  "tiro_m_desc": "Projéteis maiores e mais fortes",
        "hab_fogo":      "TIRO FOGO",   "fogo_desc":   "Projéteis causam dano por tempo",
    },
    "en": {
        "titulo":        "Note Kingdoms",
        "beta":          "BETA 1.0",
        "continuar":     "CONTINUE",
        "novo_jogo":     "NEW GAME",
        "fechar":        "CLOSE GAME",
        "apagar_save":   "DELETE SAVE",
        "tem_certeza":   "ARE YOU SURE?",
        "sair_jogo":     "QUIT THE GAME?",
        "apagar_conf":   "DELETE SAVE?",
        "voce_caiu":     "YOU FELL",
        "renascer":      "RESPAWN",
        "voltar_menu":   "BACK TO MENU?",
        "salvar_jogo":   "SAVE GAME",
        "jogo_salvo":    "✓  GAME SAVED!",
        "tab_nb":        "[TAB] NOTEBOOK",
        "nb_titulo":     "NOTEBOOK",
        "aba_fases":     "PHASES",
        "aba_habs":      "ABILITIES",
        "voltar":        "< BACK",
        "fase":          "Phase",
        "liberada":      "[UNLOCKED]",
        "bloqueada":     "[LOCKED]",
        "comprar":       "BUY",
        "comprado":      "✓ BOUGHT",
        "sem_orbs":      "NO ORBS",
        "orbs":          "ORBS",
        "comprar_grupo": "BUY PHASES",
        "sim":           "YES",
        "nao":           "NO",
        "cutscene":      "assets/Video-English.mp4",
        "fim_titulo":    "END OF BETA 1.0",
        "fim_msg":       "The creator will make more areas soon!",
        "continuar_btn": "CONTINUE",
        "autor_titulo":  "AUTHOR'S NOTE",
        "autor": [
            "I like that they call me Nhanga.",
            "I wanted to study Pygame with ChatGPT but I ended up loving making this game.",
            "Back then it was 'Prison Realms', today it's 'Note Kingdom' due to copyright.",
            "I made this game with many AIs: ChatGPT, Gemini and now Claude AI.",
            "I am 14 years old and I am from Brazil.",
            "My game is basically a white square with eyes that fights against",
            "red squares with black eyes. With a notebook it unlocks new abilities.",
            "The guardians (black squares) also get these abilities.",
            "The residents (red squares) live in the simulation.",
            "The white square is a bug in the simulation.",
            "I have a cousin in IT who promised to help me when he can.",
            "I made TikTok videos that didn't do well, but I didn't give up.",
            "",
            "Thank you for playing Note Kingdoms!",
        ],
        "fechar_btn":    "CLOSE",
        "hab_dash":      "DASH",        "dash_desc":   "Q — dash in movement direction",
        "hab_escudo":    "SHIELD",      "escudo_desc": "E — temporary shield",
        "hab_dano":      "DMG BOOST",   "dano_desc":   "Projectiles deal 2x damage",
        "hab_vida":      "HP BOOST",    "vida_desc":   f"+{VIDA_BOOST_QTD} max HP",
        "hab_tiro_m":    "BIG SHOT",    "tiro_m_desc": "Larger, stronger projectiles",
        "hab_fogo":      "FIRE SHOT",   "fogo_desc":   "Projectiles apply fire DoT",
    }
}

def T(k): return STRINGS[idioma].get(k, k)

# ============================================================
# INIT
# ============================================================
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

info_tela    = pygame.display.Info()
largura_tela = info_tela.current_w
altura_tela  = info_tela.current_h
tela = pygame.display.set_mode((largura_tela, altura_tela), pygame.FULLSCREEN)
pygame.display.set_caption("Note Kingdoms")

MUSICA_MENU     = resource_path("assets/menumusic.mp3")
MUSICA_GAMEPLAY = resource_path("assets/gameplaymusic.mp3")
SOM_VIDEO_PATH  = resource_path("assets/MUSICINE!OOF.mp3")

# ============================================================
# SONS — corrigido: verifica pygame.sndarray e trata erros
# ============================================================
def _gerar_som(freq, dur, vol=0.25, forma='sine', decay=2.0):
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
        # canal estéreo: duas colunas iguais
        stereo = np.ascontiguousarray(np.column_stack([wave, wave]))
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"[SOM] Erro ao gerar som freq={freq}: {e}")
        return None

SOM_TIRO        = _gerar_som(700,  0.08, 0.18, 'square', 1.5)
SOM_IMPACTO     = _gerar_som(300,  0.10, 0.20, 'noise',  1.8)
SOM_MORTE_INI   = _gerar_som(450,  0.15, 0.20, 'sine',   2.0)
SOM_DANO_PLAYER = _gerar_som(160,  0.18, 0.28, 'noise',  1.5)
SOM_SAVE        = _gerar_som(880,  0.25, 0.14, 'sine',   1.0)
SOM_NOTEBOOK    = _gerar_som(1000, 0.20, 0.14, 'sine',   1.2)
SOM_PROJINIMIGO = _gerar_som(250,  0.08, 0.14, 'square', 1.8)
SOM_DASH        = _gerar_som(600,  0.06, 0.20, 'square', 2.0)
SOM_ESCUDO      = _gerar_som(500,  0.18, 0.16, 'sine',   1.5)
SOM_ORB         = _gerar_som(1200, 0.12, 0.15, 'sine',   1.2)

# Diagnóstico no console
_nomes_sons = [
    ("TIRO", SOM_TIRO), ("IMPACTO", SOM_IMPACTO), ("MORTE_INI", SOM_MORTE_INI),
    ("DANO_PLAYER", SOM_DANO_PLAYER), ("SAVE", SOM_SAVE), ("NOTEBOOK", SOM_NOTEBOOK),
    ("PROJINIMIGO", SOM_PROJINIMIGO), ("DASH", SOM_DASH), ("ESCUDO", SOM_ESCUDO),
    ("ORB", SOM_ORB),
]
for _nome, _som in _nomes_sons:
    print(f"[SOM] {_nome}: {'OK' if _som else 'FALHOU (numpy ausente ou erro)'}")

def tocar(som):
    if som:
        try:
            som.play()
        except Exception as e:
            print(f"[SOM] Erro ao tocar: {e}")

# ============================================================
# MÚSICA — helper com diagnóstico
# ============================================================
def tocar_musica(caminho, loop=-1):
    """Carrega e toca música. Retorna True se conseguiu."""
    path = resource_path(caminho) if not os.path.isabs(caminho) else caminho
    if not os.path.exists(path):
        print(f"[MÚSICA] Arquivo não encontrado: {path}")
        return False
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loop)
        print(f"[MÚSICA] Tocando: {path}")
        return True
    except Exception as e:
        print(f"[MÚSICA] Erro ao tocar {path}: {e}")
        return False

# ============================================================
# SAVE
# ============================================================
arquivo_save = "save_Note_Kingdom.json"

# ============================================================
# ESTADOS
# ============================================================
menu                    = True
menu_note               = False
confirmando_novo_jogo   = False
confirmando_voltar_menu = False
confirmando_sair_jogo   = False
confirmando_apagar      = False
morreu                  = False
mostrando_fim           = False
mostrando_autor         = False
fases_desbloqueadas     = [0]
colidindo_notebook      = False
aba_notebook            = "fases"
pagina_fases            = 0

save_notif_timer = 0
save_notif_ativo = False
save_notif_dur   = 2500
shake_fim        = 0
shake_mag        = 0

_btn_menu_cache  = None
_btn_morte_cache = None
_btn_conf_cache  = None

# ── Orbs e habilidades ───────────────────────────────────────
orbs                = 0
habilidades         = set()
grupos_comprados    = {0}
fases_completadas   = set()

# ── Dash ─────────────────────────────────────────────────────
dash_cooldown_fim = 0
dash_ativo        = False
dash_fim          = 0
dash_dx = dash_dy = 0.0

# ── Escudo ───────────────────────────────────────────────────
escudo_ativo       = False
escudo_fim         = 0
escudo_cooldown_fim= 0

# ============================================================
# JOGADOR
# ============================================================
largura_q, altura_q = 50, 50
x, y        = largura_tela // 2, altura_tela // 2
velocidade  = 10
hp          = 100
max_hp      = 100
cor_olho    = (255, 0, 255)
cor_jogador = (255, 255, 255)

notebook_rect = pygame.Rect(largura_tela//2-40, altura_tela//2-30, 80, 50)

# ── Projéteis ────────────────────────────────────────────────
projetil_velocidade    = 15
projetil_lista         = []
cooldown_tiro          = 600
ultimo_tiro            = 0
direcao_jogador        = "direita"
projetil_inimigo_lista = []
cooldown_tiro_inimigo  = 1200
dano_tiro_inimigo      = 5
cor_fundo              = (70, 30, 80)
cor_inimigo            = (255, 0, 0)
cor_guardiao           = (0,   0, 0)
ultimo_dano            = 0
intervalo_dano         = 1000

# ============================================================
# GERAÇÃO DE FASES 0-21
# ============================================================
def _inimigos_fase(n):
    random.seed(n * 137 + 42)

    def hp_escala(base):
        return max(1, int(base * (1 + n * 0.25)))

    def pos():
        return (random.randint(100, largura_tela-100),
                random.randint(100, altura_tela-100))

    inims = []

    if n == 0:
        posicoes = [
            (largura_tela*0.1, altura_tela*0.1),
            (largura_tela*0.5, altura_tela*0.3),
            (largura_tela*0.8, altura_tela*0.7),
            (largura_tela*0.2, altura_tela*0.8),
            (largura_tela*0.7, altura_tela*0.2),
        ]
        for px, py in posicoes:
            inims.append({"rect": [px, py, 50, 50], "hp": 3, "tipo": "morador"})
        random.seed()
        return inims

    if n <= 2:
        n_mor, n_gua = 3+n, 0;  tam_gua = 60
    elif n <= 5:
        n_mor, n_gua = 5, n-2;  tam_gua = 60
    elif n <= 8:
        n_mor, n_gua = 4, n-3;  tam_gua = 62
    elif n <= 11:
        n_mor, n_gua = 3, n-4;  tam_gua = 64
    elif n <= 14:
        n_mor, n_gua = 2, n-5;  tam_gua = 65
    elif n <= 17:
        n_mor, n_gua = 1, n-6;  tam_gua = 66
    elif n <= 20:
        n_mor, n_gua = 1, n-7;  tam_gua = 68
    else:
        n_mor, n_gua = 0, 8;    tam_gua = 70

    hp_mor = hp_escala(3)
    hp_gua = hp_escala(6)

    for _ in range(n_mor):
        px, py = pos()
        inims.append({"rect": [px, py, 50, 50], "hp": hp_mor, "tipo": "morador"})
    for _ in range(n_gua):
        px, py = pos()
        inims.append({"rect": [px, py, tam_gua, tam_gua], "hp": hp_gua,
                       "tipo": "guardiao", "ultimo_ataque": 0})

    random.seed()
    return inims

fases_originais = {n: _inimigos_fase(n) for n in range(22)}

fase_atual = 0
inimigos   = []

def resetar_inimigos_fase(f):
    global inimigos
    inimigos = []
    for i in fases_originais[f]:
        d = dict(i)
        d["rect"]           = pygame.Rect(i["rect"])
        d["max_hp"]         = i["hp"]
        d["fogo_ticks"]     = 0
        d["fogo_timer"]     = 0
        d["escudo_ativo"]   = False
        d["escudo_fim"]     = 0
        d["dash_cd_fim"]    = 0
        d.setdefault("ultimo_ataque", 0)
        inimigos.append(d)

resetar_inimigos_fase(fase_atual)

# ============================================================
# PARTÍCULAS
# ============================================================
particles      = []
bg_particles   = []
menu_particles = []

for _ in range(160):
    bg_particles.append({
        'x': random.randint(0, largura_tela), 'y': random.randint(0, altura_tela),
        'sz': random.uniform(0.8, 2.5), 'sp': random.uniform(0.15, 0.6),
        'base_alpha': random.randint(40, 180),
        'cor': random.choice([(255,255,255),(210,160,255),(130,80,220),(180,120,255)])
    })
for _ in range(70):
    menu_particles.append({
        'x': random.randint(0, largura_tela), 'y': random.randint(0, altura_tela),
        'dx': random.uniform(-0.4, 0.4), 'dy': random.uniform(-0.9, -0.2),
        'sz': random.uniform(1.0, 3.5),
        'cor': random.choice([(255,80,200),(180,40,255),(80,200,255),(255,180,80),(120,255,180)])
    })

def spawn_particulas_tiro(px, py, dx, dy):
    ab = math.atan2(dy, dx)
    particles.append({'x':px,'y':py,'dx':0,'dy':0,'life':6,'max_life':6,'sz':14,'cor':(255,255,200),'flash':True})
    for _ in range(10):
        a = ab + random.uniform(-0.45, 0.45)
        sp = random.uniform(3, 7)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp,
                          'life':random.randint(8,20),'max_life':20,'sz':random.uniform(2,5),
                          'cor':random.choice([(255,255,80),(255,200,40),(255,140,0)])})

def spawn_particulas_fogo(px, py):
    for _ in range(6):
        a = random.uniform(0, math.tau)
        sp = random.uniform(1, 4)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp-1,
                          'life':random.randint(8,18),'max_life':18,'sz':random.uniform(2,5),
                          'cor':random.choice([(255,80,0),(255,160,0),(255,40,0)])})

def spawn_particulas_impacto(px, py):
    for _ in range(14):
        a = random.uniform(0, math.tau)
        sp = random.uniform(1.5, 6)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp,
                          'life':random.randint(10,28),'max_life':28,'sz':random.uniform(2,6),
                          'cor':random.choice([(255,60,0),(255,120,30),(200,0,0)])})

def spawn_particulas_morte(px, py):
    for _ in range(30):
        a = random.uniform(0, math.tau)
        sp = random.uniform(2, 9)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp-1.5,
                          'life':random.randint(20,45),'max_life':45,'sz':random.uniform(3,9),
                          'cor':random.choice([(255,0,0),(200,0,0),(255,100,0),(130,0,0)])})

def spawn_particulas_dano_player(px, py):
    for _ in range(18):
        a = random.uniform(0, math.tau)
        sp = random.uniform(2, 7)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp,
                          'life':random.randint(12,22),'max_life':22,'sz':random.uniform(2,5),'cor':(255,50,50)})

def spawn_particulas_notebook(rx, ry, rw, rh):
    if random.random() < 0.35:
        particles.append({'x':rx+random.randint(0,rw),'y':ry+random.randint(0,rh),
                          'dx':random.uniform(-0.6,0.6),'dy':random.uniform(-1.8,-0.4),
                          'life':random.randint(18,35),'max_life':35,'sz':random.uniform(1.5,3.5),'cor':(0,255,100)})

def spawn_particulas_dash(px, py):
    for _ in range(12):
        a = random.uniform(0, math.tau)
        sp = random.uniform(3, 8)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp,
                          'life':random.randint(6,14),'max_life':14,'sz':random.uniform(3,7),
                          'cor':random.choice([(150,150,255),(100,100,255),(200,200,255)])})

def spawn_particulas_orb(px, py):
    for _ in range(8):
        a = random.uniform(0, math.tau)
        sp = random.uniform(1, 4)
        particles.append({'x':px,'y':py,'dx':math.cos(a)*sp,'dy':math.sin(a)*sp,
                          'life':random.randint(15,30),'max_life':30,'sz':random.uniform(3,6),
                          'cor':random.choice([(255,220,0),(255,180,0),(220,160,0)])})

def atualizar_particulas():
    global particles
    vivos = []
    for p in particles:
        p['x'] += p['dx']; p['y'] += p['dy']
        p['dy'] += 0.14;   p['dx'] *= 0.94
        p['life'] -= 1
        if p['life'] > 0:
            ratio = p['life'] / p['max_life']
            sz    = max(1, int(p['sz'] * ratio))
            r, g, b = p['cor']
            if p.get('flash'):
                sf = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
                pygame.draw.circle(sf, (255,255,220,int(ratio*220)), (sz+1,sz+1), sz)
                tela.blit(sf, (int(p['x'])-sz, int(p['y'])-sz))
            else:
                pygame.draw.circle(tela, (min(255,r),min(255,g),min(255,b)),
                                   (int(p['x']), int(p['y'])), sz)
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
        pulse = int(abs(math.sin(t*0.001+bp['x']*0.012))*90 + bp['base_alpha'] - 45)
        pulse = max(15, min(230, pulse))
        sz = max(1, int(bp['sz']))
        sf = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
        r, g, b = bp['cor']
        pygame.draw.circle(sf, (r,g,b,pulse), (sz+1,sz+1), sz)
        tela.blit(sf, (int(bp['x'])-sz, int(bp['y'])-sz))

def desenhar_fundo_menu():
    t = pygame.time.get_ticks()
    for mp in menu_particles:
        mp['x'] += mp['dx']; mp['y'] += mp['dy']
        if mp['y'] < -5:
            mp['y'] = altura_tela + 5
            mp['x'] = random.randint(0, largura_tela)
        if mp['x'] < -5 or mp['x'] > largura_tela+5:
            mp['x'] = random.randint(0, largura_tela)
        alpha = int(abs(math.sin(t*0.0025+mp['x']*0.01))*110+70)
        sz = max(1, int(mp['sz']))
        sf = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
        r, g, b = mp['cor']
        pygame.draw.circle(sf, (r,g,b,alpha), (sz+1,sz+1), sz)
        tela.blit(sf, (int(mp['x'])-sz, int(mp['y'])-sz))

# ============================================================
# HUD
# ============================================================
def desenhar_barra_hp_player(surf, bx, by, _hp, _max):
    larg, alt = 200, 25
    hv   = max(0, min(_hp, _max))
    prop = hv / _max
    pygame.draw.rect(surf, (50,50,50), (bx,by,larg,alt))
    if hv > 0:
        r = int(255*(1-prop)); g = int(255*prop)
        pygame.draw.rect(surf, (r,g,0), (bx,by,int(larg*prop),alt))
    if escudo_ativo:
        t = pygame.time.get_ticks()
        a = int(abs(math.sin(t*0.01))*150+105)
        sf = pygame.Surface((larg+6, alt+6), pygame.SRCALPHA)
        pygame.draw.rect(sf, (80,120,255,a), (0,0,larg+6,alt+6), 3, border_radius=4)
        tela.blit(sf, (bx-3, by-3))

def desenhar_barra_hp_inimigo(ini):
    r    = ini["rect"]
    prop = max(0.0, ini["hp"] / max(1, ini["max_hp"]))
    bx, by = r.x, r.y - 13
    larg, alt = r.width, 7
    pygame.draw.rect(tela, (40,10,10), (bx,by,larg,alt))
    if prop > 0:
        vr = int(255*(1-prop)); vg = int(200*prop)
        pygame.draw.rect(tela, (vr,vg,0), (bx,by,int(larg*prop),alt))
    pygame.draw.rect(tela, (180,180,180), (bx,by,larg,alt), 1)
    if ini.get("escudo_ativo"):
        sf = pygame.Surface((larg+4, alt+4), pygame.SRCALPHA)
        pygame.draw.rect(sf, (80,120,255,160), (0,0,larg+4,alt+4), 2, border_radius=3)
        tela.blit(sf, (bx-2, by-2))

def desenhar_cooldowns():
    agora = pygame.time.get_ticks()
    f = pygame.font.SysFont('Arial', 16, bold=True)
    cx = largura_tela//2 - 120
    if "dash" in habilidades:
        cd_r = max(0, (dash_cooldown_fim-agora)/DASH_COOLDOWN_MS)
        cor  = (100,100,255) if cd_r == 0 else (60,60,140)
        pygame.draw.rect(tela, cor, (cx, altura_tela-50, 80, 30), border_radius=6)
        txt = f.render("Q DASH" + (f" {cd_r:.1f}s" if cd_r > 0 else ""), True, (255,255,255))
        tela.blit(txt, (cx+40-txt.get_width()//2, altura_tela-43))
        cx += 100
    if "escudo" in habilidades:
        cd_r = max(0, (escudo_cooldown_fim-agora)/ESCUDO_COOLDOWN_MS)
        cor  = (80,180,255) if cd_r == 0 else (40,80,140)
        if escudo_ativo: cor = (0,150,255)
        pygame.draw.rect(tela, cor, (cx, altura_tela-50, 80, 30), border_radius=6)
        txt = f.render("E ESCUDO" + (f" {cd_r:.1f}s" if cd_r > 0 else ""), True, (255,255,255))
        tela.blit(txt, (cx+40-txt.get_width()//2, altura_tela-43))

def desenhar_orbs_hud():
    txt = pygame.font.SysFont('Arial', 22, bold=True).render(f"◈ {orbs}", True, (255,220,0))
    tela.blit(txt, (largura_tela - txt.get_width() - 20, 30))

def desenhar_hud_tab():
    if len(fases_desbloqueadas) > 1:
        t   = pygame.time.get_ticks()
        txt = pygame.font.SysFont('Arial', 22, bold=True).render(T("tab_nb"), True, (0,255,100))
        txt.set_alpha(int(abs(math.sin(t*0.005))*255))
        tela.blit(txt, (largura_tela-220, 55))

def desenhar_notificacao_save(agora):
    global save_notif_ativo
    if not save_notif_ativo: return
    elapsed = agora - save_notif_timer
    if elapsed >= save_notif_dur:
        save_notif_ativo = False; return
    alpha = 255
    fs    = save_notif_dur * 0.55
    if elapsed > fs:
        alpha = int(255 * (1 - (elapsed-fs)/(save_notif_dur-fs)))
    txt = pygame.font.SysFont('Arial', 30, bold=True).render(T("jogo_salvo"), True, (255,220,0))
    txt.set_alpha(max(0, alpha))
    tela.blit(txt, (largura_tela - txt.get_width() - 20, 65))

# ============================================================
# NOTEBOOK DESIGN
# ============================================================
def desenhar_design_notebook(surf, rect):
    pygame.draw.rect(surf, (40,40,40),
                     (rect.x, rect.y+rect.height//2, rect.width, rect.height//2),
                     border_bottom_left_radius=5, border_bottom_right_radius=5)
    pygame.draw.rect(surf, (20,20,20),
                     (rect.x+5, rect.y, rect.width-10, rect.height//2+5),
                     border_top_left_radius=5, border_top_right_radius=5)
    pygame.draw.rect(surf, (0,40,20),
                     (rect.x+10, rect.y+5, rect.width-20, rect.height//2-5))
    pygame.draw.line(surf, (0,255,100), (rect.x+15,rect.y+10), (rect.x+40,rect.y+10), 2)
    pygame.draw.line(surf, (0,255,100), (rect.x+15,rect.y+15), (rect.x+30,rect.y+15), 2)
    for i in range(3):
        pygame.draw.line(surf, (60,60,60),
                         (rect.x+10, rect.y+32+i*4), (rect.x+rect.width-10, rect.y+32+i*4), 1)

def desenhar_notebook_com_brilho(agora):
    pulse = abs(math.sin(agora*0.004))*35+8
    gw, gh = notebook_rect.width+24, notebook_rect.height+24
    gs = pygame.Surface((gw, gh), pygame.SRCALPHA)
    pygame.draw.rect(gs, (0,255,100,int(pulse)), (0,0,gw,gh), border_radius=12)
    tela.blit(gs, (notebook_rect.x-12, notebook_rect.y-12))
    spawn_particulas_notebook(notebook_rect.x, notebook_rect.y,
                              notebook_rect.width, notebook_rect.height)
    desenhar_design_notebook(tela, notebook_rect)

# ============================================================
# TRANSIÇÃO
# ============================================================
def fade(para_preto, duracao_ms=500):
    surf = pygame.Surface((largura_tela, altura_tela))
    surf.fill((0,0,0))
    passos = 20
    delay  = max(1, duracao_ms // passos)
    for i in range(passos+1):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        surf.set_alpha(int(255*i/passos) if para_preto else int(255*(1-i/passos)))
        tela.blit(surf, (0,0))
        pygame.display.flip()
        pygame.time.delay(delay)

# ============================================================
# TELAS
# ============================================================
def desenhar_caixa_confirmacao(texto):
    bx, by = largura_tela//2-200, altura_tela//2-100
    pygame.draw.rect(tela, (30,30,30),  (bx,by,400,200), border_radius=20)
    pygame.draw.rect(tela, (255,255,255),(bx,by,400,200), 2, border_radius=20)
    txt = pygame.font.SysFont('Arial', 25).render(texto, True, (255,255,255))
    tela.blit(txt, (largura_tela//2-txt.get_width()//2, by+40))
    bs = pygame.Rect(largura_tela//2-110, altura_tela//2+10, 100, 50)
    bn = pygame.Rect(largura_tela//2+10,  altura_tela//2+10, 100, 50)
    pygame.draw.rect(tela, (0,150,0),  bs, border_radius=10)
    pygame.draw.rect(tela, (150,0,0),  bn, border_radius=10)
    f = pygame.font.SysFont('Arial', 20, bold=True)
    tela.blit(f.render(T("sim"), True, (255,255,255)), (bs.centerx-18, bs.centery-12))
    tela.blit(f.render(T("nao"), True, (255,255,255)), (bn.centerx-18, bn.centery-12))
    return bs, bn

def desenhar_menu():
    global _btn_menu_cache
    tela.fill(cor_fundo)
    desenhar_fundo_menu()
    agora  = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()

    fb = pygame.font.SysFont('Arial', 18, bold=True).render(T("beta"), True, (180,180,100))
    tela.blit(fb, (largura_tela//2-fb.get_width()//2, altura_tela//5-40))

    ty_off = math.sin(agora*0.002)*8
    ft     = pygame.font.SysFont('Arial Black', 72)
    titulo = ft.render(T("titulo"), True, (255,255,255))
    glow   = ft.render(T("titulo"), True, (200,100,255))
    glow.set_alpha(int(abs(math.sin(agora*0.003))*60+25))
    tx = largura_tela//2 - titulo.get_width()//2
    ty = int(altura_tela//5 + ty_off)
    tela.blit(glow, (tx+3, ty+3))
    tela.blit(titulo, (tx, ty))

    btn_pt = pygame.Rect(largura_tela-130, 10, 55, 30)
    btn_en = pygame.Rect(largura_tela-70,  10, 55, 30)
    pygame.draw.rect(tela, (100,40,150) if idioma=="pt" else (50,50,50), btn_pt, border_radius=8)
    pygame.draw.rect(tela, (100,40,150) if idioma=="en" else (50,50,50), btn_en, border_radius=8)
    fi = pygame.font.SysFont('Arial', 16, bold=True)
    tela.blit(fi.render("PT BR", True, (255,255,255)), (btn_pt.x+5, btn_pt.y+7))
    tela.blit(fi.render("ENG",   True, (255,255,255)), (btn_en.x+8, btn_en.y+7))

    tem_save = os.path.exists(arquivo_save)
    bj = pygame.Rect(largura_tela//2-150, altura_tela//2-100, 300, 60)
    bn = pygame.Rect(largura_tela//2-150, altura_tela//2-20,  300, 60)
    bs = pygame.Rect(largura_tela//2-150, altura_tela//2+60,  300, 60)
    ba = pygame.Rect(largura_tela//2-150, altura_tela//2+140, 300, 50)

    for btn, hc, bc in [
        (bj, (140,60,200), (100,40,150) if tem_save else (30,30,30)),
        (bn, (200,60,60),  (150,40,40)),
        (bs, (80,80,80),   (50,50,50))
    ]:
        cor = hc if btn.collidepoint((mx,my)) and (btn!=bj or tem_save) else bc
        if btn.collidepoint((mx,my)) and (btn!=bj or tem_save):
            gs = pygame.Surface((btn.width+16, btn.height+16), pygame.SRCALPHA)
            r, g, b = hc
            pygame.draw.rect(gs, (r,g,b,50), (0,0,btn.width+16,btn.height+16), border_radius=18)
            tela.blit(gs, (btn.x-8, btn.y-8))
        pygame.draw.rect(tela, cor, btn, border_radius=15)

    cor_ap  = (60,60,60) if not tem_save else ((90,30,30) if ba.collidepoint((mx,my)) else (70,30,30))
    pygame.draw.rect(tela, cor_ap, ba, border_radius=12)
    cor_txt_ap = (80,80,80) if not tem_save else (200,100,100)
    tela.blit(pygame.font.SysFont('Arial',22,bold=True).render(T("apagar_save"),True,cor_txt_ap),
              (ba.centerx-70, ba.centery-11))

    f30 = pygame.font.SysFont('Arial', 30)
    ct  = (255,255,255) if tem_save else (100,100,100)
    tela.blit(f30.render(T("continuar"), True, ct),          (bj.centerx-80, bj.centery-15))
    tela.blit(f30.render(T("novo_jogo"), True, (255,255,255)),(bn.centerx-75, bn.centery-15))
    tela.blit(f30.render(T("fechar"),    True, (255,255,255)),(bs.centerx-85, bs.centery-15))

    bsb = bnb = None
    if   confirmando_novo_jogo: bsb, bnb = desenhar_caixa_confirmacao(T("tem_certeza"))
    elif confirmando_sair_jogo: bsb, bnb = desenhar_caixa_confirmacao(T("sair_jogo"))
    elif confirmando_apagar:    bsb, bnb = desenhar_caixa_confirmacao(T("apagar_conf"))

    desenhar_notificacao_save(agora)
    _btn_menu_cache = (bj,bn,bs,ba,btn_pt,btn_en,bsb,bnb,tem_save)
    return _btn_menu_cache

def desenhar_tela_morte():
    global _btn_morte_cache
    s = pygame.Surface((largura_tela, altura_tela))
    s.set_alpha(185); s.fill((0,0,0)); tela.blit(s, (0,0))
    agora = pygame.time.get_ticks()
    pulse = abs(math.sin(agora*0.004))*40
    txt   = pygame.font.SysFont('Arial Black', 80).render(T("voce_caiu"), True, (255,int(pulse),int(pulse)))
    tela.blit(txt, (largura_tela//2-txt.get_width()//2, altura_tela//3))
    btn = pygame.Rect(largura_tela//2-100, altura_tela//2, 200, 60)
    pygame.draw.rect(tela, (255,255,255), btn, border_radius=10)
    tela.blit(pygame.font.SysFont('Arial',30,bold=True).render(T("renascer"),True,(0,0,0)),
              (btn.centerx-70, btn.centery-15))
    _btn_morte_cache = btn
    return btn

def desenhar_tela_fim():
    tela.fill((10,5,20))
    desenhar_fundo_menu()
    agora = pygame.time.get_ticks()
    pulse = int(abs(math.sin(agora*0.003))*40+215)
    ft  = pygame.font.SysFont('Arial Black', 60)
    txt = ft.render(T("fim_titulo"), True, (pulse, pulse//2, 255))
    tela.blit(txt, (largura_tela//2-txt.get_width()//2, altura_tela//4))
    fm  = pygame.font.SysFont('Arial', 32)
    msg = fm.render(T("fim_msg"), True, (0,255,150))
    tela.blit(msg, (largura_tela//2-msg.get_width()//2, altura_tela//2-30))
    btn = pygame.Rect(largura_tela//2-100, altura_tela*2//3, 200, 60)
    pygame.draw.rect(tela, (0,150,100), btn, border_radius=12)
    tela.blit(pygame.font.SysFont('Arial',28,bold=True).render(T("continuar_btn"),True,(255,255,255)),
              (btn.centerx-60, btn.centery-14))
    return btn

def desenhar_tela_autor():
    tela.fill((5,5,15))
    desenhar_fundo_menu()
    ft     = pygame.font.SysFont('Arial Black', 38)
    titulo = ft.render(T("autor_titulo"), True, (255,220,0))
    tela.blit(titulo, (largura_tela//2-titulo.get_width()//2, 40))
    pygame.draw.line(tela, (255,220,0), (largura_tela//4,90), (largura_tela*3//4,90), 2)
    fl     = pygame.font.SysFont('Arial', 22)
    linhas = T("autor")
    for i, linha in enumerate(linhas):
        cor = (200,200,200) if linha else (100,100,100)
        txt = fl.render(linha, True, cor)
        tela.blit(txt, (largura_tela//2-txt.get_width()//2, 110+i*32))
    btn = pygame.Rect(largura_tela//2-80, altura_tela-80, 160, 50)
    pygame.draw.rect(tela, (80,80,80), btn, border_radius=10)
    tela.blit(pygame.font.SysFont('Arial',24,bold=True).render(T("fechar_btn"),True,(255,255,255)),
              (btn.centerx-35, btn.centery-12))
    return btn

def desenhar_menu_note():
    global aba_notebook, pagina_fases
    tela.fill((10,10,20))
    agora  = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()

    ba2 = int(abs(math.sin(agora*0.003))*100+155)
    bs2 = pygame.Surface((largura_tela*3//4, altura_tela-60), pygame.SRCALPHA)
    pygame.draw.rect(bs2, (0,255,100,ba2), (0,0,largura_tela*3//4,altura_tela-60), 3, border_radius=15)
    tela.blit(bs2, (largura_tela//8, 30))

    fo      = pygame.font.SysFont('Arial', 26, bold=True)
    orb_txt = fo.render(f"◈ {orbs} ORBS", True, (255,220,0))
    tela.blit(orb_txt, (largura_tela//2-orb_txt.get_width()//2, 50))

    aba_f_r = pygame.Rect(largura_tela//2-150, 90, 140, 40)
    aba_h_r = pygame.Rect(largura_tela//2+10,  90, 140, 40)
    pygame.draw.rect(tela, (0,150,80)  if aba_notebook=="fases"       else (30,80,50),  aba_f_r, border_radius=10)
    pygame.draw.rect(tela, (0,80,200)  if aba_notebook=="habilidades"  else (20,40,100), aba_h_r, border_radius=10)
    fa = pygame.font.SysFont('Arial', 20, bold=True)
    tela.blit(fa.render(T("aba_fases"), True, (255,255,255)), (aba_f_r.centerx-35, aba_f_r.centery-10))
    tela.blit(fa.render(T("aba_habs"),  True, (255,255,255)), (aba_h_r.centerx-50, aba_h_r.centery-10))

    btn_salvar = pygame.Rect(largura_tela-200, 50, 170, 40)
    pygame.draw.rect(tela,
                     (0,100,200) if btn_salvar.collidepoint((mx,my)) else (0,70,160),
                     btn_salvar, border_radius=10)
    tela.blit(fa.render(T("salvar_jogo"), True, (255,255,255)),
              (btn_salvar.centerx-60, btn_salvar.centery-10))

    resultados = {"salvar": btn_salvar, "aba_f": aba_f_r, "aba_h": aba_h_r}

    if aba_notebook == "fases":
        resultados.update(_desenhar_aba_fases(mx, my, agora))
    else:
        resultados.update(_desenhar_aba_habilidades(mx, my, agora))

    desenhar_notificacao_save(agora)
    return resultados

def _desenhar_aba_fases(mx, my, agora):
    res = {}
    f28 = pygame.font.SysFont('Arial', 24)
    fi  = pygame.font.SysFont('Arial', 18, bold=True)

    inicio         = pagina_fases * 6
    fim            = min(inicio + 6, 22)
    fases_na_pagina= list(range(inicio, fim))

    btn_ant  = pygame.Rect(largura_tela//8+10,    altura_tela//2-15, 50, 35)
    btn_prox = pygame.Rect(largura_tela*7//8-60,  altura_tela//2-15, 50, 35)
    pygame.draw.rect(tela, (50,50,80), btn_ant,  border_radius=8)
    pygame.draw.rect(tela, (50,50,80), btn_prox, border_radius=8)
    tela.blit(fi.render("<", True, (255,255,255)), (btn_ant.centerx-6,  btn_ant.centery-9))
    tela.blit(fi.render(">", True, (255,255,255)), (btn_prox.centerx-6, btn_prox.centery-9))
    res["ant"] = btn_ant; res["prox"] = btn_prox

    grupo_comprado = pagina_fases in grupos_comprados
    botoes_fases   = {}

    if not grupo_comprado and pagina_fases > 0:
        custos = [0, CUSTO_FASES_6_11, CUSTO_FASES_12_17, CUSTO_FASES_18_21]
        custo  = custos[pagina_fases]
        txt_g  = f"{T('comprar_grupo')}: {custo} ORBS"
        btn_g  = pygame.Rect(largura_tela//2-160, altura_tela//2-30, 320, 60)
        pode   = orbs >= custo
        pygame.draw.rect(tela, (0,120,60) if pode else (60,60,60), btn_g, border_radius=12)
        tela.blit(f28.render(txt_g, True, (255,255,255) if pode else (120,120,120)),
                  (btn_g.centerx-f28.size(txt_g)[0]//2, btn_g.centery-14))
        if pode:
            res["comprar_grupo"] = (btn_g, pagina_fases, custo)
    else:
        for idx, fase in enumerate(fases_na_pagina):
            lib = fase in fases_desbloqueadas
            rf  = pygame.Rect(largura_tela//2-180, 145+idx*52, 360, 40)
            cor = (0,255,150) if lib else (120,120,120)
            if lib and rf.collidepoint((mx,my)):
                pygame.draw.rect(tela, (20,60,40), rf, border_radius=5)
                cor = (150,255,200)
            label = f"{T('fase')} {fase}: {T('liberada') if lib else T('bloqueada')}"
            if fase in fases_completadas:
                label += " ✓"
            tela.blit(f28.render(label, True, cor), (largura_tela//2-170, 150+idx*52))
            if lib:
                botoes_fases[fase] = rf

    res["fases"] = botoes_fases
    return res

HABILIDADES_INFO = [
    ("dash",       "hab_dash",   "dash_desc",   CUSTO_DASH),
    ("escudo",     "hab_escudo", "escudo_desc",  CUSTO_ESCUDO),
    ("dano",       "hab_dano",   "dano_desc",    CUSTO_DANO_BOOST),
    ("vida",       "hab_vida",   "vida_desc",    CUSTO_VIDA_BOOST),
    ("tiro_maior", "hab_tiro_m", "tiro_m_desc",  CUSTO_TIRO_MAIOR),
    ("fogo",       "hab_fogo",   "fogo_desc",    CUSTO_TIRO_FOGO),
]

def _desenhar_aba_habilidades(mx, my, agora):
    res = {"habs": {}}
    f24 = pygame.font.SysFont('Arial', 22)
    fi  = pygame.font.SysFont('Arial', 17)

    for idx, (chave, nome_k, desc_k, custo) in enumerate(HABILIDADES_INFO):
        comprado = chave in habilidades
        pode     = orbs >= custo and not comprado
        rf       = pygame.Rect(largura_tela//2-210, 145+idx*50, 420, 42)
        hover    = rf.collidepoint((mx,my))

        cor_bg = (20,60,40) if comprado else ((30,50,70) if hover and pode else (25,25,40))
        pygame.draw.rect(tela, cor_bg, rf, border_radius=8)
        pygame.draw.rect(tela, (0,200,100) if comprado else (80,80,120), rf, 1, border_radius=8)

        nome = f24.render(T(nome_k), True, (0,255,150) if comprado else (200,200,200))
        tela.blit(nome, (rf.x+10, rf.y+5))
        desc = fi.render(T(desc_k), True, (150,150,150))
        tela.blit(desc, (rf.x+10, rf.y+26))

        if comprado:
            ct = f24.render(T("comprado"), True, (0,200,100))
            tela.blit(ct, (rf.right-ct.get_width()-10, rf.y+10))
        else:
            cor_btn = (0,100,50) if pode else (50,50,50)
            btn     = pygame.Rect(rf.right-110, rf.y+6, 105, 30)
            pygame.draw.rect(tela, cor_btn, btn, border_radius=8)
            bt = fi.render(f"{T('comprar')} {custo}◈", True, (255,255,255) if pode else (100,100,100))
            tela.blit(bt, (btn.centerx-bt.get_width()//2, btn.centery-bt.get_height()//2))
            if pode:
                res["habs"][chave] = (btn, custo)

    return res

# ============================================================
# LÓGICA
# ============================================================
def separar_inimigos():
    sep = 85; forca = 2.2; n = len(inimigos)
    for i in range(n):
        for j in range(i+1, n):
            a, b   = inimigos[i]["rect"], inimigos[j]["rect"]
            dx, dy = a.centerx-b.centerx, a.centery-b.centery
            d = math.hypot(dx, dy)
            if 0 < d < sep:
                f = (sep-d)/sep * forca
                nx, ny = dx/d, dy/d
                a.x = max(0, min(int(a.x+nx*f), largura_tela-a.width))
                a.y = max(0, min(int(a.y+ny*f), altura_tela-a.height))
                b.x = max(0, min(int(b.x-nx*f), largura_tela-b.width))
                b.y = max(0, min(int(b.y-ny*f), altura_tela-b.height))

def inimigo_seguir_jogador(rect, jx, jy, vel=2):
    dx, dy = jx-rect.x, jy-rect.y
    d = math.hypot(dx, dy)
    if d:
        rect.x += int(dx/d*vel)
        rect.y += int(dy/d*vel)

def atualizar_fogo_inimigos(agora):
    for ini in inimigos[:]:
        if ini["fogo_ticks"] > 0 and agora-ini["fogo_timer"] >= FOGO_INTERVALO_MS:
            ini["hp"]        -= FOGO_DANO_TICK
            ini["fogo_ticks"] -= 1
            ini["fogo_timer"]  = agora
            spawn_particulas_fogo(ini["rect"].centerx, ini["rect"].centery)
            if ini["hp"] <= 0:
                spawn_particulas_morte(ini["rect"].centerx, ini["rect"].centery)
                tocar(SOM_MORTE_INI)
                inimigos.remove(ini)

def atualizar_guardian_habilidades(agora):
    for ini in inimigos[:]:
        if ini["tipo"] != "guardiao": continue
        if "escudo" in habilidades:
            if not ini["escudo_ativo"] and agora-ini.get("escudo_cd",0) > ESCUDO_COOLDOWN_MS*2:
                if random.random() < 0.001:
                    ini["escudo_ativo"] = True
                    ini["escudo_fim"]   = agora + ESCUDO_DURACAO_MS//2
                    ini["escudo_cd"]    = agora
        if ini.get("escudo_ativo") and agora > ini.get("escudo_fim", 0):
            ini["escudo_ativo"] = False
        if "dash" in habilidades:
            if agora-ini.get("dash_cd",0) > DASH_COOLDOWN_MS*2 and random.random() < 0.0005:
                dx = ini["rect"].x - x; dy = ini["rect"].y - y
                d  = math.hypot(dx, dy)
                if d > 0:
                    ini["rect"].x = max(0, min(int(ini["rect"].x+dx/d*DASH_VELOCIDADE), largura_tela-ini["rect"].width))
                    ini["rect"].y = max(0, min(int(ini["rect"].y+dy/d*DASH_VELOCIDADE), altura_tela-ini["rect"].height))
                ini["dash_cd"] = agora

# ============================================================
# SAVE — SOMENTE MANUAL (botão Salvar Jogo)
# ============================================================
def salvar_jogo():
    """Salva o jogo. Chamado APENAS pelo botão — sem auto-save."""
    global save_notif_ativo, save_notif_timer
    if morreu: return
    ini_s = [{"rect":[i["rect"].x,i["rect"].y,i["rect"].width,i["rect"].height],
               "hp":i["hp"],"max_hp":i["max_hp"],"tipo":i["tipo"]} for i in inimigos]
    dados = {
        "fases_desbloqueadas": fases_desbloqueadas,
        "fase_atual":          fase_atual,
        "player_x":            x,
        "player_y":            y,
        "player_hp":           hp,
        "inimigos_vivos":      ini_s,
        "orbs":                orbs,
        "habilidades":         list(habilidades),
        "grupos_comprados":    list(grupos_comprados),
        "fases_completadas":   list(fases_completadas),
        "max_hp":              max_hp,
    }
    try:
        with open(arquivo_save, "w") as f:
            json.dump(dados, f)
        save_notif_ativo  = True
        save_notif_timer  = pygame.time.get_ticks()
        tocar(SOM_SAVE)
        print("[SAVE] Jogo salvo com sucesso.")
    except Exception as e:
        print(f"[SAVE] Erro ao salvar: {e}")

def carregar_jogo():
    global fases_desbloqueadas, fase_atual, inimigos, x, y, hp, orbs, habilidades
    global grupos_comprados, fases_completadas, max_hp
    if not os.path.exists(arquivo_save):
        print("[SAVE] Nenhum save encontrado.")
        return
    try:
        with open(arquivo_save, "r") as f:
            dados = json.load(f)
        fases_desbloqueadas = dados.get("fases_desbloqueadas", [0])
        fase_atual          = dados.get("fase_atual", 0)
        x                   = dados.get("player_x", largura_tela//2)
        y                   = dados.get("player_y", altura_tela//2)
        hp                  = dados.get("player_hp", 100)
        max_hp              = dados.get("max_hp", 100)
        orbs                = dados.get("orbs", 0)
        habilidades         = set(dados.get("habilidades", []))
        grupos_comprados    = set(dados.get("grupos_comprados", [0]))
        fases_completadas   = set(dados.get("fases_completadas", []))
        inimigos = []
        for i in dados.get("inimigos_vivos", []):
            d = {"rect":pygame.Rect(i["rect"]), "hp":i["hp"],
                 "max_hp":i.get("max_hp", i["hp"]), "tipo":i["tipo"],
                 "ultimo_ataque":0, "fogo_ticks":0, "fogo_timer":0,
                 "escudo_ativo":False, "escudo_fim":0, "dash_cd":0}
            inimigos.append(d)
        print(f"[SAVE] Jogo carregado. Fase {fase_atual}, HP {hp}/{max_hp}, Orbs {orbs}")
    except Exception as e:
        print(f"[SAVE] Save corrompido ou inválido: {e}")

# ============================================================
# CUTSCENE — corrigido: usa T("cutscene") corretamente
# ============================================================
def rodar_video():
    caminho = resource_path(T("cutscene"))   # ← CORRIGIDO
    print(f"[VIDEO] Tentando carregar: {caminho}")
    if not os.path.exists(caminho):
        print(f"[VIDEO] Arquivo não encontrado — pulando cutscene.")
        return
    fade(True, 500)
    tela.fill((0,0,0)); pygame.display.flip()
    # Pequena espera antes de abrir o vídeo
    inicio = pygame.time.get_ticks()
    while pygame.time.get_ticks() - inicio < 400:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        pygame.time.delay(10)

    cap = cv2.VideoCapture(caminho)
    if not cap.isOpened():
        print(f"[VIDEO] cv2 não conseguiu abrir: {caminho}")
        fade(False, 400)
        return

    fps_v = cap.get(cv2.CAP_PROP_FPS)
    if fps_v <= 0: fps_v = 30
    print(f"[VIDEO] FPS do vídeo: {fps_v:.1f}")

    # Áudio da cutscene
    if os.path.exists(SOM_VIDEO_PATH):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(SOM_VIDEO_PATH)
            pygame.mixer.music.play()
            print(f"[VIDEO] Áudio da cutscene: {SOM_VIDEO_PATH}")
        except Exception as e:
            print(f"[VIDEO] Erro ao tocar áudio da cutscene: {e}")
    else:
        print(f"[VIDEO] Áudio da cutscene não encontrado: {SOM_VIDEO_PATH}")

    clk_v = pygame.time.Clock()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                cap.release(); pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                print("[VIDEO] Cutscene pulada pelo jogador.")
                cap.release()
                pygame.mixer.music.stop()
                fade(False, 400)
                return
        frame = cv2.cvtColor(
            cv2.resize(frame, (largura_tela, altura_tela)),
            cv2.COLOR_BGR2RGB
        )
        tela.blit(pygame.surfarray.make_surface(frame.swapaxes(0,1)), (0,0))
        pygame.display.flip()
        clk_v.tick(fps_v)

    cap.release()
    pygame.mixer.music.stop()
    print("[VIDEO] Cutscene encerrada.")
    fade(False, 400)

def novo_jogo():
    global fases_desbloqueadas, fase_atual, x, y, hp, menu, ultimo_tiro, orbs, habilidades
    global grupos_comprados, fases_completadas, max_hp, escudo_ativo, dash_ativo
    pygame.mixer.music.stop()
    rodar_video()
    if os.path.exists(arquivo_save):
        os.remove(arquivo_save)
    fases_desbloqueadas = [0]; fase_atual = 0
    orbs = 0; habilidades = set(); grupos_comprados = {0}; fases_completadas = set()
    max_hp = 100; hp = 100; escudo_ativo = False; dash_ativo = False
    resetar_inimigos_fase(0)
    x, y = largura_tela//2, altura_tela//2
    particles.clear()
    tocar_musica(MUSICA_GAMEPLAY)
    ultimo_tiro = pygame.time.get_ticks() + 1000
    menu = False
    # SEM salvar automático aqui

def comprar_habilidade(chave, custo):
    global orbs, max_hp, hp
    if orbs < custo or chave in habilidades: return
    orbs -= custo
    habilidades.add(chave)
    if chave == "vida":
        max_hp += VIDA_BOOST_QTD
        hp = min(hp + VIDA_BOOST_QTD, max_hp)
    tocar(SOM_ORB)

# ============================================================
# ARRANQUE
# ============================================================
tocar_musica(MUSICA_MENU)
carregar_jogo()
fade(False, 500)

clock   = pygame.time.Clock()
rodando = True

# ============================================================
# LOOP PRINCIPAL
# ============================================================
while rodando:
    clock.tick(60)
    agora = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    clique_mouse = pygame.mouse.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            # SEM auto-save ao fechar
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if menu:
                    confirmando_sair_jogo = not confirmando_sair_jogo
                elif mostrando_autor:
                    mostrando_autor = False
                elif mostrando_fim:
                    pass
                elif not menu_note and not morreu:
                    confirmando_voltar_menu = not confirmando_voltar_menu

            if (evento.key == pygame.K_TAB and not menu and not morreu
                    and not mostrando_fim and not mostrando_autor):
                if len(fases_desbloqueadas) > 1:
                    menu_note = not menu_note
                    tocar(SOM_NOTEBOOK)

            # Dash
            if evento.key == pygame.K_q and "dash" in habilidades and not menu and not morreu:
                if agora >= dash_cooldown_fim and not dash_ativo:
                    dash_ativo        = True
                    dash_fim          = agora + DASH_DURACAO_MS
                    dash_cooldown_fim = agora + DASH_COOLDOWN_MS
                    teclas = pygame.key.get_pressed()
                    dx_d = (-1 if (teclas[pygame.K_a] or teclas[pygame.K_LEFT]) else
                             1 if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) else
                             (1 if direcao_jogador == "direita" else -1))
                    dy_d = (-1 if (teclas[pygame.K_w] or teclas[pygame.K_UP]) else
                             1 if (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) else 0)
                    d = math.hypot(dx_d, dy_d)
                    dash_dx = dx_d/d if d else 1
                    dash_dy = dy_d/d if d else 0
                    spawn_particulas_dash(x+25, y+25)
                    tocar(SOM_DASH)

            # Escudo
            if evento.key == pygame.K_e and "escudo" in habilidades and not menu and not morreu:
                if agora >= escudo_cooldown_fim and not escudo_ativo:
                    escudo_ativo        = True
                    escudo_fim          = agora + ESCUDO_DURACAO_MS
                    escudo_cooldown_fim = agora + ESCUDO_COOLDOWN_MS
                    tocar(SOM_ESCUDO)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

            # ── MENU ─────────────────────────────────────────
            if menu and not mostrando_fim and not mostrando_autor:
                cache = _btn_menu_cache
                if cache:
                    bj,bn,bs,ba,btn_pt,btn_en,bsb,bnb,tem_save = cache
                    if btn_pt.collidepoint((mx,my)):
                        idioma = "pt"
                    elif btn_en.collidepoint((mx,my)):
                        idioma = "en"
                    elif not any([confirmando_novo_jogo, confirmando_sair_jogo, confirmando_apagar]):
                        if bj.collidepoint((mx,my)) and tem_save:
                            fade(True, 350)
                            menu = False
                            ultimo_tiro = agora + 1000
                            tocar_musica(MUSICA_GAMEPLAY)
                            fade(False, 350)
                        elif bn.collidepoint((mx,my)):
                            confirmando_novo_jogo = True
                        elif bs.collidepoint((mx,my)):
                            confirmando_sair_jogo = True
                        elif ba.collidepoint((mx,my)) and tem_save:
                            confirmando_apagar = True
                    else:
                        if confirmando_novo_jogo:
                            if bsb and bsb.collidepoint((mx,my)):
                                confirmando_novo_jogo = False; novo_jogo()
                            elif bnb and bnb.collidepoint((mx,my)):
                                confirmando_novo_jogo = False
                        elif confirmando_sair_jogo:
                            if bsb and bsb.collidepoint((mx,my)):
                                rodando = False
                            elif bnb and bnb.collidepoint((mx,my)):
                                confirmando_sair_jogo = False
                        elif confirmando_apagar:
                            if bsb and bsb.collidepoint((mx,my)):
                                if os.path.exists(arquivo_save):
                                    os.remove(arquivo_save)
                                confirmando_apagar = False
                            elif bnb and bnb.collidepoint((mx,my)):
                                confirmando_apagar = False

            # ── FIM DE BETA ──────────────────────────────────
            elif mostrando_fim:
                btn_c = desenhar_tela_fim()
                if btn_c.collidepoint((mx,my)):
                    mostrando_fim  = False
                    mostrando_autor = True

            # ── AUTOR ────────────────────────────────────────
            elif mostrando_autor:
                btn_a = desenhar_tela_autor()
                if btn_a.collidepoint((mx,my)):
                    mostrando_autor = False
                    menu = True
                    tocar_musica(MUSICA_MENU)

            # ── MORTE ────────────────────────────────────────
            elif morreu:
                from contextlib import suppress
                with suppress(Exception):
                    btn_r = _btn_morte_cache
                    if btn_r and btn_r.collidepoint((mx,my)):
                        hp     = max_hp
                        morreu = False
                        x, y   = largura_tela//2, altura_tela//2
                        resetar_inimigos_fase(fase_atual)
                        projetil_lista.clear()
                        projetil_inimigo_lista.clear()
                        particles.clear()

            # ── CONFIRMAÇÃO VOLTAR ────────────────────────────
            elif confirmando_voltar_menu and _btn_conf_cache:
                bs_c, bn_c = _btn_conf_cache
                if bs_c.collidepoint((mx,my)):
                    # SEM auto-save aqui — o jogador decide salvar antes de sair
                    fade(True, 350)
                    confirmando_voltar_menu = False
                    menu = True
                    tocar_musica(MUSICA_MENU)
                    fade(False, 350)
                elif bn_c.collidepoint((mx,my)):
                    confirmando_voltar_menu = False

            # ── NOTEBOOK ─────────────────────────────────────
            elif menu_note:
                res = desenhar_menu_note()
                if res["salvar"].collidepoint((mx,my)):
                    salvar_jogo()   # ← único ponto de save manual
                if res["aba_f"].collidepoint((mx,my)):
                    aba_notebook = "fases"
                if res["aba_h"].collidepoint((mx,my)):
                    aba_notebook = "habilidades"
                if res.get("ant") and res["ant"].collidepoint((mx,my)):
                    pagina_fases = (pagina_fases-1) % 4
                if res.get("prox") and res["prox"].collidepoint((mx,my)):
                    pagina_fases = (pagina_fases+1) % 4
                if res.get("comprar_grupo"):
                    btn_g, grp, custo = res["comprar_grupo"]
                    if btn_g.collidepoint((mx,my)) and orbs >= custo:
                        orbs -= custo
                        grupos_comprados.add(grp)
                        primeira = grp * 6
                        if primeira not in fases_desbloqueadas:
                            fases_desbloqueadas.append(primeira)
                        tocar(SOM_ORB)
                for n, rf in res.get("fases", {}).items():
                    if rf.collidepoint((mx,my)):
                        fase_atual = n
                        resetar_inimigos_fase(n)
                        menu_note = False
                        x, y, hp  = largura_tela//2, altura_tela//2, max_hp
                        projetil_lista.clear()
                        projetil_inimigo_lista.clear()
                        particles.clear()
                for chave, (btn_h, custo) in res.get("habs", {}).items():
                    if btn_h.collidepoint((mx,my)):
                        comprar_habilidade(chave, custo)

    # ── ESTADOS ESPECIAIS ─────────────────────────────────────
    if menu:
        desenhar_menu(); pygame.display.flip(); continue
    if mostrando_fim:
        desenhar_tela_fim(); pygame.display.flip(); continue
    if mostrando_autor:
        desenhar_tela_autor(); pygame.display.flip(); continue
    if morreu:
        desenhar_tela_morte(); pygame.display.flip(); continue
    if confirmando_voltar_menu:
        tela.fill(cor_fundo); desenhar_fundo_jogo()
        _btn_conf_cache = desenhar_caixa_confirmacao(T("voltar_menu"))
        desenhar_notificacao_save(agora); pygame.display.flip(); continue
    if menu_note:
        desenhar_menu_note(); pygame.display.flip(); continue

    # ============================================================
    # LÓGICA DO JOGO
    # ============================================================
    if escudo_ativo and agora > escudo_fim:
        escudo_ativo = False
    if dash_ativo and agora > dash_fim:
        dash_ativo = False

    ox = oy = 0
    if agora < shake_fim:
        ox = random.randint(-shake_mag, shake_mag)
        oy = random.randint(-shake_mag, shake_mag)

    tela.fill(cor_fundo)
    desenhar_fundo_jogo()
    desenhar_hud_tab()

    teclas = pygame.key.get_pressed()
    dx_m = dy_m = 0
    if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
        dx_m = -velocidade; direcao_jogador = "esquerda"
    elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
        dx_m =  velocidade; direcao_jogador = "direita"
    if teclas[pygame.K_w] or teclas[pygame.K_UP]:
        dy_m = -velocidade; direcao_jogador = "cima"
    elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
        dy_m =  velocidade; direcao_jogador = "baixo"
    elif clique_mouse[2]:
        ddx, ddy = mx-(x+25), my-(y+25)
        dist = math.hypot(ddx, ddy)
        if dist > 5:
            dx_m, dy_m = int(ddx/dist*velocidade), int(ddy/dist*velocidade)
            direcao_jogador = (("direita" if ddx>0 else "esquerda") if abs(ddx)>abs(ddy)
                               else ("baixo" if ddy>0 else "cima"))

    if dash_ativo:
        dx_m += int(dash_dx * DASH_VELOCIDADE)
        dy_m += int(dash_dy * DASH_VELOCIDADE)

    x = max(0, min(x+dx_m, largura_tela-largura_q))
    y = max(0, min(y+dy_m, altura_tela-altura_q))

    # Tiro
    if (teclas[pygame.K_SPACE] or clique_mouse[0]) and agora >= ultimo_tiro:
        dx_t = dy_t = 0
        if clique_mouse[0]:
            ddx, ddy = mx-(x+25), my-(y+25)
            d = math.hypot(ddx, ddy)
            if d > 0:
                dx_t, dy_t = ddx/d*projetil_velocidade, ddy/d*projetil_velocidade
        else:
            mapa = {"direita": (projetil_velocidade,0), "esquerda":(-projetil_velocidade,0),
                    "cima":    (0,-projetil_velocidade),"baixo":   (0,projetil_velocidade)}
            dx_t, dy_t = mapa[direcao_jogador]

        tam_p   = (45,22) if "tiro_maior" in habilidades else (30,15)
        dano_p  = 2 if ("dano" in habilidades or "tiro_maior" in habilidades) else 1
        if "dano" in habilidades and "tiro_maior" in habilidades:
            dano_p = 3

        projetil_lista.append({
            "rect":  pygame.Rect(x+25, y+25, tam_p[0], tam_p[1]),
            "dx": dx_t, "dy": dy_t,
            "dano":  dano_p,
            "fogo":  "fogo" in habilidades
        })
        spawn_particulas_tiro(x+25, y+25, dx_t, dy_t)
        tocar(SOM_TIRO)
        ultimo_tiro = agora + cooldown_tiro

    # Desenhar jogador
    jogador_rect = pygame.Rect(x, y, largura_q, altura_q)
    pygame.draw.rect(tela, cor_jogador, (x+ox, y+oy, largura_q, altura_q))
    pygame.draw.circle(tela, cor_olho, (x+12+ox, y+18+oy), 8)
    pygame.draw.circle(tela, cor_olho, (x+38+ox, y+18+oy), 8)
    if escudo_ativo:
        prog = (escudo_fim-agora) / ESCUDO_DURACAO_MS
        a    = int(80 + prog*120)
        sf   = pygame.Surface((largura_q+20, altura_q+20), pygame.SRCALPHA)
        pygame.draw.ellipse(sf, (80,150,255,a), (0,0,largura_q+20,altura_q+20))
        tela.blit(sf, (x-10+ox, y-10+oy))

    # Notebook / inimigos
    if not inimigos:
        desenhar_notebook_com_brilho(agora)
        if jogador_rect.colliderect(notebook_rect):
            if not colidindo_notebook:
                prox = fase_atual + 1
                drop = ORBS_PRIMEIRA_VEZ if fase_atual not in fases_completadas else ORBS_REVISITA
                orbs += drop
                fases_completadas.add(fase_atual)
                spawn_particulas_orb(notebook_rect.centerx, notebook_rect.centery)
                tocar(SOM_ORB)
                if prox <= 21 and prox not in fases_desbloqueadas:
                    grp_prox = prox // 6
                    if grp_prox in grupos_comprados:
                        fases_desbloqueadas.append(prox)
                if fase_atual == 21:
                    mostrando_fim = True
                    # SEM auto-save aqui
                else:
                    tocar(SOM_NOTEBOOK)
                    menu_note = True
                colidindo_notebook = True
        else:
            colidindo_notebook = False
    else:
        separar_inimigos()
        atualizar_fogo_inimigos(agora)
        atualizar_guardian_habilidades(agora)

        for ini in inimigos[:]:
            inimigo_seguir_jogador(ini["rect"], x, y, 2)
            cb = cor_inimigo if ini["tipo"] == "morador" else cor_guardiao
            pygame.draw.rect(tela, cb,
                             (ini["rect"].x+ox, ini["rect"].y+oy,
                              ini["rect"].width, ini["rect"].height))
            if ini["fogo_ticks"] > 0 and random.random() < 0.4:
                spawn_particulas_fogo(ini["rect"].centerx+random.randint(-10,10), ini["rect"].y)
            ce = (0,0,0) if ini["tipo"] == "morador" else (255,0,255)
            pygame.draw.circle(tela, ce, (ini["rect"].x+12+ox, ini["rect"].y+18+oy), 8)
            pygame.draw.circle(tela, ce, (ini["rect"].x+38+ox, ini["rect"].y+18+oy), 8)
            desenhar_barra_hp_inimigo(ini)

            if ini["tipo"] == "guardiao" and agora-ini.get("ultimo_ataque",0) >= cooldown_tiro_inimigo:
                if not ini.get("escudo_ativo"):
                    ddx = x - ini["rect"].centerx
                    ddy = y - ini["rect"].centery
                    d   = math.hypot(ddx, ddy)
                    if d:
                        vel_proj = 4
                        dano_g   = int(dano_tiro_inimigo*GUARDIAN_DANO_MULT) if "dano" in habilidades else dano_tiro_inimigo
                        projetil_inimigo_lista.append({
                            "rect": pygame.Rect(ini["rect"].centerx, ini["rect"].centery, 15, 15),
                            "dx": ddx/d*vel_proj, "dy": ddy/d*vel_proj,
                            "dano": dano_g,
                            "fogo": "fogo" in habilidades and random.random() < 0.3
                        })
                        tocar(SOM_PROJINIMIGO)
                        ini["ultimo_ataque"] = agora

            if jogador_rect.colliderect(ini["rect"]) and agora-ultimo_dano >= intervalo_dano:
                if not escudo_ativo:
                    hp         -= 15
                    ultimo_dano = agora
                    spawn_particulas_dano_player(x+25, y+25)
                    tocar(SOM_DANO_PLAYER)
                    shake_fim = agora+320; shake_mag = 6
                else:
                    ultimo_dano = agora

    # Projéteis do jogador
    for p in projetil_lista[:]:
        p["rect"].x += p["dx"]; p["rect"].y += p["dy"]
        bx, by = p["rect"].x+ox, p["rect"].y+oy
        cor_proj = (255,120,0) if p.get("fogo") else (220,220,80)
        pygame.draw.rect(tela, cor_proj, (bx,by,p["rect"].width,p["rect"].height))
        pygame.draw.circle(tela, (255,255,200),
                           (int(bx+p["rect"].width//2), int(by+p["rect"].height//2)), 7)
        if (p["rect"].x < -50 or p["rect"].x > largura_tela+50 or
                p["rect"].y < -50 or p["rect"].y > altura_tela+50):
            if p in projetil_lista: projetil_lista.remove(p); continue
        for ini in inimigos[:]:
            if ini.get("escudo_ativo"): continue
            if p["rect"].colliderect(ini["rect"]):
                ini["hp"] -= p.get("dano", 1)
                if p.get("fogo") and ini["fogo_ticks"] == 0:
                    ini["fogo_ticks"] = FOGO_TICKS
                    ini["fogo_timer"] = agora
                spawn_particulas_impacto(p["rect"].centerx, p["rect"].centery)
                tocar(SOM_IMPACTO)
                if p in projetil_lista: projetil_lista.remove(p)
                if ini["hp"] <= 0:
                    spawn_particulas_morte(ini["rect"].centerx, ini["rect"].centery)
                    tocar(SOM_MORTE_INI)
                    inimigos.remove(ini)
                break

    # Projéteis inimigos
    for pi in projetil_inimigo_lista[:]:
        pi["rect"].x += pi["dx"]; pi["rect"].y += pi["dy"]
        cx, cy = pi["rect"].center
        cor_pi = (200,100,0) if pi.get("fogo") else (120,30,30)
        pygame.draw.circle(tela, cor_pi,      (cx+ox, cy+oy), 10)
        pygame.draw.circle(tela, (200,200,200),(cx+ox, cy+oy),  7)
        if (pi["rect"].x < -50 or pi["rect"].x > largura_tela+50 or
                pi["rect"].y < -50 or pi["rect"].y > altura_tela+50):
            if pi in projetil_inimigo_lista: projetil_inimigo_lista.remove(pi); continue
        if pi["rect"].colliderect(jogador_rect):
            if not escudo_ativo:
                hp -= pi.get("dano", 5)
                spawn_particulas_dano_player(x+25, y+25)
                tocar(SOM_DANO_PLAYER)
                shake_fim = agora+200; shake_mag = 4
            if pi in projetil_inimigo_lista: projetil_inimigo_lista.remove(pi)

    atualizar_particulas()
    desenhar_barra_hp_player(tela, 20, 20, hp, max_hp)
    desenhar_orbs_hud()
    desenhar_cooldowns()
    desenhar_notificacao_save(agora)
    pygame.display.flip()

    if hp <= 0:
        morreu = True

pygame.quit()
