# ============================================================
# WILD EMPIRE — Main Game
# Workers International League of Defense
# The Sewer Society Liberation Campaign
# ============================================================
# Run:   python main.py
# Deps:  pip install pygame
# ============================================================

import pygame
import sys
import random
import math
import os

# ── Local imports ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from levels.level_config import LEVEL_CONFIGS, SCORING, PICKUPS
from entities.entities import Player, Enemy, Civilian, Bullet, Pickup

# ============================================================
# CONSTANTS
# ============================================================
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "WILD EMPIRE — Sewer Society"

# Level order (use 1-5 then "secret" unlocks after 5)
LEVEL_ORDER = [1, 2, 3, 4, 5]

# Colors
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (220, 40, 40)
GREEN   = (0, 200, 80)
YELLOW  = (255, 220, 0)
GRAY    = (80, 80, 80)
DARK    = (15, 12, 20)


# ============================================================
# SPACE BACKGROUND EFFECTS
# ============================================================
class StarField:
    """Three-layer parallax star field."""
    def __init__(self, seed=0):
        rng = random.Random(seed)
        # (x, y, layer)  — layer 0=far 1=mid 2=near
        self.stars = [
            (rng.randint(0, SCREEN_W * 4), rng.randint(0, SCREEN_H), 0)
            for _ in range(200)
        ] + [
            (rng.randint(0, SCREEN_W * 4), rng.randint(0, SCREEN_H), 1)
            for _ in range(80)
        ] + [
            (rng.randint(0, SCREEN_W * 4), rng.randint(0, SCREEN_H), 2)
            for _ in range(25)
        ]
        self.parallax = [0.04, 0.12, 0.25]
        self.sizes    = [1, 1, 2]
        self.brights  = [(140, 160, 200), (180, 200, 230), (255, 255, 255)]
        # Twinkling: random phase per star
        self._phases  = [rng.uniform(0, math.pi * 2) for _ in self.stars]

    def draw(self, surface, camera, tick):
        for i, (sx, sy, layer) in enumerate(self.stars):
            par = self.parallax[layer]
            px  = int(sx - camera[0] * par) % SCREEN_W
            py  = int(sy - camera[1] * par * 0.2) % SCREEN_H
            # Gentle twinkle
            t   = 0.7 + 0.3 * math.sin(tick * 0.002 + self._phases[i])
            r, g, b = self.brights[layer]
            col = (int(r * t), int(g * t), int(b * t))
            sz  = self.sizes[layer]
            if sz == 1:
                surface.set_at((px, py), col)
            else:
                pygame.draw.circle(surface, col, (px, py), sz)


class Asteroid:
    """Slow-drifting background rock with parallax."""
    def __init__(self, seed):
        rng = random.Random(seed)
        self.x      = float(rng.randint(0, 4000))
        self.y      = float(rng.randint(30, SCREEN_H - 80))
        self.speed  = rng.uniform(0.25, 0.9) * rng.choice([-1, 1])
        self.par    = rng.uniform(0.35, 0.65)   # parallax factor
        size        = rng.randint(14, 40)
        # Pre-compute irregular polygon
        n = rng.randint(6, 9)
        self.verts  = []
        for i in range(n):
            ang = math.radians(i * 360 / n + rng.uniform(-18, 18))
            r   = size * rng.uniform(0.65, 1.0)
            self.verts.append((r * math.cos(ang), r * math.sin(ang)))
        base        = rng.randint(55, 95)
        self.color  = (base, int(base * 0.92), int(base * 0.82))
        self.rim    = (max(0, base - 22), max(0, int(base * 0.9) - 18), max(0, int(base * 0.8) - 16))

    def update(self):
        self.x += self.speed
        if self.x >  4200: self.x = -150.0
        if self.x < -150:  self.x =  4200.0

    def draw(self, surface, camera):
        sx = int(self.x - camera[0] * self.par)
        sy = int(self.y - camera[1] * self.par * 0.1)
        if -80 < sx < SCREEN_W + 80:
            pts = [(int(sx + vx), int(sy + vy)) for vx, vy in self.verts]
            pygame.draw.polygon(surface, self.color, pts)
            pygame.draw.polygon(surface, self.rim,   pts, 2)


class Crater:
    """Scorched ellipse left on the ground when a heavy enemy dies."""
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.r = radius

    def draw(self, surface, camera):
        sx = int(self.x - camera[0])
        sy = int(self.y - camera[1])
        rw, rh = self.r * 2, max(4, self.r // 2)
        pygame.draw.ellipse(surface, (12, 8, 5),
                            (sx - self.r, sy - rh // 2, rw, rh))
        pygame.draw.ellipse(surface, (45, 30, 18),
                            (sx - self.r, sy - rh // 2, rw, rh), 2)


class Meteor:
    """Flaming rock falling from the sky — damages entities on impact."""
    def __init__(self, worldX):
        self.x      = float(worldX)
        self.y      = -50.0
        self.velY   = random.uniform(4.5, 8.0)
        self.radius = random.randint(8, 16)
        self.alive  = True
        self._trail = []

    def update(self, platforms):
        self._trail.append((self.x, self.y))
        if len(self._trail) > 7:
            self._trail.pop(0)
        self.y += self.velY
        for plat in platforms:
            if plat.left - self.radius < self.x < plat.right + self.radius:
                if plat.top - self.velY - 4 <= self.y <= plat.top + self.radius:
                    self.y = plat.top
                    self.alive = False
                    return True   # landed — caller handles impact
        if self.y > 720:
            self.alive = False
        return False

    def draw(self, surface, camera):
        sx = int(self.x - camera[0])
        sy = int(self.y - camera[1])
        if sx < -60 or sx > SCREEN_W + 60:
            return
        # Fire trail (fading circles)
        for i, (tx, ty) in enumerate(self._trail):
            frac  = (i + 1) / len(self._trail) if self._trail else 1
            alpha = int(160 * frac)
            tr    = max(2, int(self.radius * frac * 0.7))
            ts = pygame.Surface((tr * 2 + 1, tr * 2 + 1), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 100, 10, alpha), (tr, tr), tr)
            surface.blit(ts, (int(tx - camera[0]) - tr, int(ty - camera[1]) - tr))
        # Core
        pygame.draw.circle(surface, (255, 80, 10), (sx, sy), self.radius)
        pygame.draw.circle(surface, (255, 230, 80), (sx, sy), max(2, self.radius // 3))


# ============================================================
# HUD
# ============================================================
class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.fontLg = pygame.font.SysFont("monospace", 22, bold=True)
        self.fontSm = pygame.font.SysFont("monospace", 15)

    def draw(self, player, levelName, score, totalEnemies, deadEnemies,
             totalCivs, rescuedCivs, deadCivs):
        sw = SCREEN_W

        # ── Health bar ─────────────────────────────────────
        pct = player.health / player.MAX_HEALTH
        pygame.draw.rect(self.screen, (80, 0, 0),      (20, 20, 200, 18))
        pygame.draw.rect(self.screen, (220, 40, 40),   (20, 20, int(200 * pct), 18))
        self._label(f"HP {player.health}/{player.MAX_HEALTH}", 20, 40, self.fontSm, WHITE)

        # ── Ammo ───────────────────────────────────────────
        ammoTxt = "RELOADING..." if player.reloading else f"AMMO {player.ammo}/{player.MAX_AMMO}"
        self._label(ammoTxt, 20, 58, self.fontSm, YELLOW)

        # ── Score (top center) ─────────────────────────────
        scoreTxt = f"SCORE  {score:+d}"
        col = GREEN if score >= 0 else RED
        self._label(scoreTxt, sw // 2, 20, self.fontLg, col, center=True)

        # ── Level name ─────────────────────────────────────
        self._label(levelName, sw // 2, 46, self.fontSm, WHITE, center=True)

        # ── Enemy counter ──────────────────────────────────
        self._label(f"FASCISTS  {deadEnemies}/{totalEnemies} eliminated",
                    sw - 20, 20, self.fontSm, RED, right=True)

        # ── Civilian counter ───────────────────────────────
        civCol = (220, 80, 80) if deadCivs > 0 else GREEN
        self._label(f"WORKERS  {rescuedCivs}/{totalCivs} rescued  |  {deadCivs} dead",
                    sw - 20, 40, self.fontSm, civCol, right=True)

        # ── Shield indicator ───────────────────────────────
        if player.shieldActive:
            self._label("[ SHIELD ACTIVE ]", sw // 2, 70, self.fontSm, (100, 180, 255), center=True)

        # ── Webbed indicator ───────────────────────────────
        if player.webbed:
            self._label("[ WEBBED — slowed ]", sw // 2, 88, self.fontSm, (200, 200, 80), center=True)

    def _label(self, text, x, y, font, color, center=False, right=False):
        surf = font.render(text, True, color)
        if center:
            self.screen.blit(surf, (x - surf.get_width() // 2, y))
        elif right:
            self.screen.blit(surf, (x - surf.get_width(), y))
        else:
            self.screen.blit(surf, (x, y))


# ============================================================
# PLATFORM / TILEMAP
# Four tiers above ground (y=680):
#   Low  y≈560  (~120px above ground — one jump)
#   Mid  y≈440  (~120px above Low)
#   High y≈320  (~120px above Mid)
#   Top  y≈200  (~120px above High)
# ============================================================
def buildPlatforms(levelId):
    # Tier heights — 102px gaps so enemies (jump force -12, max gravity 0.65)
    # can reach every tier.  Ground=680, Low=578, Mid=476, High=374, Top=272.
    R = pygame.Rect
    G = [R(0, 680, 4000, 40)]   # ground

    if levelId == 1:    # Korrith-7 — open ruins
        return G + [
            # Low  (y=578)
            R( 180, 578, 240, 20), R( 650, 578, 220, 20), R(1150, 578, 240, 20),
            R(1700, 578, 220, 20), R(2250, 578, 240, 20), R(2800, 578, 220, 20),
            R(3350, 578, 240, 20),
            # Mid  (y=476)
            R( 420, 476, 220, 20), R( 950, 476, 240, 20), R(1490, 476, 220, 20),
            R(2020, 476, 240, 20), R(2560, 476, 220, 20), R(3100, 476, 240, 20),
            # High (y=374)
            R( 180, 374, 220, 20), R( 700, 374, 240, 20), R(1250, 374, 220, 20),
            R(1800, 374, 240, 20), R(2380, 374, 220, 20), R(2960, 374, 240, 20),
            # Top  (y=272)
            R( 430, 272, 220, 20), R(1000, 272, 240, 20), R(1700, 272, 220, 20),
            R(2420, 272, 240, 20), R(3150, 272, 220, 20),
        ]

    elif levelId == 2:  # Vael-4 — cliff plateaus, wider platforms
        return G + [
            # Low  (y=578)
            R(   0, 578, 320, 20), R( 550, 578, 280, 20), R(1100, 578, 300, 20),
            R(1700, 578, 280, 20), R(2300, 578, 300, 20), R(2950, 578, 280, 20),
            # Mid  (y=476)
            R( 200, 476, 260, 20), R( 750, 476, 280, 20), R(1300, 476, 260, 20),
            R(1900, 476, 280, 20), R(2500, 476, 260, 20), R(3100, 476, 280, 20),
            # High (y=374)
            R( 400, 374, 250, 20), R(1000, 374, 270, 20), R(1600, 374, 250, 20),
            R(2200, 374, 270, 20), R(2850, 374, 250, 20), R(3450, 374, 220, 20),
            # Top  (y=272)
            R( 600, 272, 240, 20), R(1250, 272, 260, 20), R(1950, 272, 240, 20),
            R(2650, 272, 260, 20), R(3350, 272, 220, 20),
        ]

    elif levelId == 3:  # Glorbax-3 — blob-friendly, wider surfaces
        return G + [
            # Low  (y=578)
            R( 200, 578, 300, 20), R( 700, 578, 280, 20), R(1250, 578, 300, 20),
            R(1820, 578, 280, 20), R(2380, 578, 300, 20), R(2940, 578, 280, 20),
            R(3500, 578, 260, 20),
            # Mid  (y=476)
            R( 450, 476, 260, 20), R(1000, 476, 280, 20), R(1550, 476, 260, 20),
            R(2100, 476, 280, 20), R(2670, 476, 260, 20), R(3250, 476, 260, 20),
            # High (y=374)
            R( 650, 374, 250, 20), R(1350, 374, 270, 20), R(2050, 374, 250, 20),
            R(2750, 374, 270, 20), R(3400, 374, 220, 20),
            # Top  (y=272) — fewer: blobs are heavy
            R( 900, 272, 240, 20), R(1900, 272, 260, 20),
            R(2900, 272, 240, 20), R(3650, 272, 200, 20),
        ]

    elif levelId == 4:  # Nexar-9 — tight staggered grid
        return G + [
            # Low  (y=578)
            R( 100, 578, 180, 20), R( 480, 578, 160, 20), R( 850, 578, 180, 20),
            R(1300, 578, 160, 20), R(1750, 578, 180, 20), R(2250, 578, 160, 20),
            R(2750, 578, 180, 20),
            # Mid  (y=476)
            R( 280, 476, 160, 20), R( 680, 476, 180, 20), R(1100, 476, 160, 20),
            R(1550, 476, 180, 20), R(2050, 476, 160, 20), R(2580, 476, 180, 20),
            # High (y=374)
            R( 430, 374, 160, 20), R( 870, 374, 180, 20), R(1350, 374, 160, 20),
            R(1850, 374, 180, 20), R(2380, 374, 160, 20), R(2900, 374, 180, 20),
            # Top  (y=272)
            R( 650, 272, 160, 20), R(1150, 272, 180, 20), R(1700, 272, 160, 20),
            R(2250, 272, 180, 20), R(2900, 272, 160, 20),
        ]

    elif levelId == 5:  # Arachnos — irregular web-like network
        return G + [
            # Low  (y≈578, slight variation for spider feel)
            R( 150, 575, 200, 20), R( 520, 582, 180, 20), R( 900, 572, 220, 20),
            R(1350, 580, 180, 20), R(1800, 570, 200, 20), R(2280, 580, 180, 20),
            R(2750, 575, 200, 20),
            # Mid  (y≈476)
            R( 320, 476, 180, 20), R( 730, 470, 200, 20), R(1160, 478, 180, 20),
            R(1620, 468, 200, 20), R(2110, 476, 180, 20), R(2600, 472, 200, 20),
            # High (y≈374)
            R( 500, 372, 180, 20), R( 960, 378, 200, 20), R(1440, 370, 180, 20),
            R(1960, 378, 200, 20), R(2500, 372, 180, 20), R(3050, 378, 200, 20),
            # Top  (y≈272)
            R( 700, 270, 180, 20), R(1300, 276, 200, 20), R(1950, 270, 180, 20),
            R(2600, 276, 200, 20), R(3300, 270, 180, 20),
        ]

    else:               # Secret / fallback
        return G + [
            # Low  (y=578)
            R( 200, 578, 220, 20), R( 650, 578, 200, 20), R(1150, 578, 220, 20),
            R(1750, 578, 200, 20), R(2350, 578, 220, 20), R(2950, 578, 200, 20),
            # Mid  (y=476)
            R( 430, 476, 200, 20), R(1000, 476, 220, 20), R(1600, 476, 200, 20),
            R(2200, 476, 220, 20), R(2800, 476, 200, 20),
            # High (y=374)
            R( 650, 374, 200, 20), R(1350, 374, 220, 20),
            R(2050, 374, 200, 20), R(2800, 374, 220, 20),
            # Top  (y=272)
            R( 900, 272, 200, 20), R(1800, 272, 220, 20), R(2800, 272, 200, 20),
        ]


# ============================================================
# SPAWN HELPERS
# ============================================================
def spawnEnemies(cfg, platforms):
    enemies  = []
    spawnCfg  = cfg["spawn"]
    enemyCfgs = cfg["enemies"]
    groundY   = 679
    # Elevated platforms for stationary turrets
    elevated = [p for p in platforms if p.top < groundY - 20]

    for etype, count in spawnCfg.items():
        if etype not in enemyCfgs:
            continue
        ecfg = enemyCfgs[etype]
        for i in range(count):
            x = random.randint(400, 3500)
            if ecfg.get("is_stationary") and elevated:
                plat = random.choice(elevated)
                x = random.randint(plat.left, max(plat.left, plat.right - ecfg["hitbox"][0]))
                y = plat.top - ecfg["hitbox"][1]
            elif ecfg.get("flies"):
                y = random.randint(80, 420)
            else:
                y = groundY - ecfg["hitbox"][1]
            enemies.append(Enemy(x, y, ecfg))

    return enemies


def _pickGuardCfg(cfg):
    """Return the lightest ground-walking enemy config to use as civilian guards."""
    for ecfg in cfg["enemies"].values():
        if (ecfg.get("ai_type") in ("patrol", "chase")
                and not ecfg.get("is_boss")
                and not ecfg.get("flies")
                and not ecfg.get("is_stationary")):
            return ecfg
    return None


def spawnCivilians(cfg, platforms):
    civs        = []
    guard_pool  = []   # extra Enemy objects that guard workers
    spawnCfg    = cfg["spawn"]
    civCfgs     = cfg["civilians"]
    groundY     = 679
    guardCfg    = _pickGuardCfg(cfg)

    # Elevated platforms for distributing civilians vertically
    elevated = [p for p in platforms if p.top < groundY - 20]
    # On lava levels never put civilians on the burning ground
    if cfg.get("lava_floor") and elevated:
        spawn_pool = elevated
    else:
        spawn_pool = elevated * 3 + [p for p in platforms if p.top >= groundY - 20]

    for ctype, count in spawnCfg.items():
        if ctype not in civCfgs:
            continue
        ccfg = civCfgs[ctype]
        for i in range(count):
            # Prefer elevated platforms (3× weight) for dynamic placement
            plat = random.choice(spawn_pool)
            x = random.randint(plat.left + 4,
                               max(plat.left + 4, plat.right - ccfg["hitbox"][0] - 4))
            y = plat.top - ccfg["hitbox"][1]
            civ = Civilian(x, y, ccfg)
            # 2 guards spawn on the same platform
            if guardCfg:
                for offset in (-70, 70):
                    gx = max(plat.left + 2, min(plat.right - 2, x + offset))
                    gy = plat.top - guardCfg["hitbox"][1]
                    guard = Enemy(gx, gy, guardCfg)
                    civ.guards.append(guard)
                    guard_pool.append(guard)
            civs.append(civ)

    return civs, guard_pool


def spawnPickupsFromDrop(enemy, pickupTypes):
    """Called when an enemy dies. Returns a Pickup or None."""
    if random.random() > enemy.cfg.get("drop_chance", 0):
        return None
    validTypes = [t for t in pickupTypes if t in PICKUPS]
    if not validTypes:
        return None
    ptype = random.choice(validTypes)
    pdata = PICKUPS[ptype]
    return Pickup(enemy.rect.centerx, enemy.rect.top, ptype, pdata)


# ============================================================
# SCREEN OVERLAYS
# ============================================================
def drawTitleScreen(screen, font, smallFont):
    screen.fill(DARK)
    title = font.render("WILD EMPIRE", True, (0, 220, 120))
    sub   = smallFont.render("Sewer Society Liberation Campaign", True, (160, 220, 160))
    start = smallFont.render("Press ENTER to begin   |   ESC to quit", True, GRAY)
    w = SCREEN_W
    screen.blit(title, (w//2 - title.get_width()//2, 200))
    screen.blit(sub,   (w//2 - sub.get_width()//2,   280))
    screen.blit(start, (w//2 - start.get_width()//2, 420))

    # Controls
    controls = [
        "A/D  or  ←/→ : Move",
        "W / SPACE / ↑ : Jump",
        "Left Click     : Shoot",
        "R              : Reload",
        "E              : Rescue civilian",
    ]
    y = 490
    for line in controls:
        s = smallFont.render(line, True, (120, 180, 120))
        screen.blit(s, (w//2 - s.get_width()//2, y))
        y += 22


def drawPauseOverlay(screen, font, smallFont):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    t = font.render("PAUSED", True, WHITE)
    s = smallFont.render("Press P to resume  |  ESC for menu", True, GRAY)
    screen.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H//2 - 40))
    screen.blit(s, (SCREEN_W//2 - s.get_width()//2, SCREEN_H//2 + 20))


def drawLevelComplete(screen, font, smallFont, score, rescued, civDeaths):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 30, 0, 200))
    screen.blit(overlay, (0, 0))
    t  = font.render("PLANET LIBERATED!", True, GREEN)
    s1 = smallFont.render(f"Score: {score:+d}", True, YELLOW)
    s2 = smallFont.render(f"Workers rescued: {rescued}", True, WHITE)
    s3 = smallFont.render(f"Civilian deaths: {civDeaths}  ({civDeaths * SCORING['civilian_death_penalty']} pts)", True, RED)
    s4 = smallFont.render("Press ENTER for next level  |  ESC for menu", True, GRAY)
    cx = SCREEN_W // 2
    screen.blit(t,  (cx - t.get_width()//2,  200))
    screen.blit(s1, (cx - s1.get_width()//2, 290))
    screen.blit(s2, (cx - s2.get_width()//2, 325))
    screen.blit(s3, (cx - s3.get_width()//2, 358))
    screen.blit(s4, (cx - s4.get_width()//2, 440))


def drawGameOver(screen, font, smallFont, score):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((30, 0, 0, 210))
    screen.blit(overlay, (0, 0))
    t  = font.render("OPERATIVE DOWN", True, RED)
    s1 = smallFont.render(f"Final Score: {score:+d}", True, YELLOW)
    s2 = smallFont.render("Press ENTER to retry  |  ESC for menu", True, GRAY)
    cx = SCREEN_W // 2
    screen.blit(t,  (cx - t.get_width()//2, 260))
    screen.blit(s1, (cx - s1.get_width()//2, 340))
    screen.blit(s2, (cx - s2.get_width()//2, 420))


# ============================================================
# SOUND MANAGER
# ============================================================
class SoundManager:
    """Load and play WAV sound effects. Silently no-ops if files are missing."""

    _NAMES = [
        "shoot", "enemy_shoot", "melee", "jump",
        "hurt", "player_death", "enemy_death",
        "rescue", "civ_death", "pickup",
        "meteor", "level_complete", "game_over", "lava",
    ]

    def __init__(self, sounds_dir="assets/sounds"):
        self._sounds = {}
        self._loops  = {}
        if not pygame.mixer.get_init():
            return
        for name in self._NAMES:
            path = os.path.join(sounds_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    self._sounds[name] = pygame.mixer.Sound(path)
                except Exception:
                    pass

    def play(self, name, vol=0.70):
        s = self._sounds.get(name)
        if s:
            s.set_volume(vol)
            s.play()

    def loop(self, name, vol=0.20):
        if name in self._loops:
            return
        s = self._sounds.get(name)
        if s:
            s.set_volume(vol)
            ch = s.play(loops=-1)
            if ch:
                self._loops[name] = ch

    def stop_loop(self, name):
        ch = self._loops.pop(name, None)
        if ch:
            try: ch.stop()
            except Exception: pass

    def stop_all_loops(self):
        for ch in list(self._loops.values()):
            try: ch.stop()
            except Exception: pass
        self._loops.clear()


# ============================================================
# CAMERA
# ============================================================
def cameraOffset(player, levelW, levelH):
    cx = player.rect.centerx - SCREEN_W // 2
    cy = player.rect.centery - SCREEN_H // 2
    cx = max(0, min(cx, levelW - SCREEN_W))
    cy = max(0, min(cy, levelH - SCREEN_H))
    return (cx, cy)


# ============================================================
# MAIN GAME CLASS
# ============================================================
class Game:
    LEVEL_W = 4000
    LEVEL_H = 720   # matches SCREEN_H — no vertical camera scroll

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(44100, -16, 1, 512)
        except Exception:
            pass
        self.sounds = SoundManager()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.fontLg  = pygame.font.SysFont("monospace", 36, bold=True)
        self.fontSm  = pygame.font.SysFont("monospace", 18)
        self.hud     = HUD(self.screen)
        self.state   = "title"      # title | playing | paused | level_complete | game_over
        self.levelIdx = 0
        self.totalScore = 0
        self.secretUnlocked = False

        # Per-level state (set in loadLevel)
        self.player    = None
        self.enemies   = []
        self.civilians = []
        self.bullets   = []
        self.pickups   = []
        self.platforms = []
        self.cfg       = {}
        self.bgSurf    = None
        self.camera    = (0, 0)

        self.starField      = StarField(seed=0)
        self.asteroids      = []
        self.craters        = []
        self.meteors        = []
        self._tick          = 0
        self._meteorTimer   = 0
        self._lavaDmgTimer  = 0

        self.rescuedCount  = 0
        self.civDeathCount = 0
        self.enemyKillCount = 0

    # -------------------------------------------------------
    def loadLevel(self, levelId):
        self.cfg = LEVEL_CONFIGS[levelId]
        self.platforms = buildPlatforms(levelId)
        self.player    = Player(100, 600)
        self.enemies   = spawnEnemies(self.cfg, self.platforms)
        civs, guards   = spawnCivilians(self.cfg, self.platforms)
        self.civilians = civs
        self.enemies  += guards   # guards are tracked as regular enemies
        self.bullets        = []
        self.pickups        = []
        self.craters        = []
        self.meteors        = []
        self._meteorTimer   = 0
        self._lavaDmgTimer  = 0
        self.rescuedCount   = 0
        self.civDeathCount  = 0
        self.enemyKillCount = 0

        # Sounds — stop any loop from the previous level, start lava if needed
        self.sounds.stop_all_loops()
        if self.cfg.get("lava_floor"):
            self.sounds.loop("lava", vol=0.18)

        # Star field — new seed per level keeps each one feeling different
        self.starField = StarField(seed=hash(levelId) & 0xFFFF)

        # Asteroids — count driven by level config
        n = self.cfg.get("asteroids", 0)
        self.asteroids = [Asteroid(seed=i + hash(levelId)) for i in range(n)]

        # Background image
        bgPath = self.cfg.get("background", "")
        if os.path.exists(bgPath):
            raw = pygame.image.load(bgPath).convert()
            self.bgSurf = pygame.transform.scale(raw, (self.LEVEL_W, self.LEVEL_H))
        else:
            self.bgSurf = None

    # -------------------------------------------------------
    def currentLevelId(self):
        if self.levelIdx < len(LEVEL_ORDER):
            return LEVEL_ORDER[self.levelIdx]
        return "secret"

    # -------------------------------------------------------
    def checkWinCondition(self):
        allEnemiesDead = all(not e.alive for e in self.enemies)
        allCivsSaved   = all(c.rescued for c in self.civilians if c.alive)
        return allEnemiesDead or allCivsSaved

    # -------------------------------------------------------
    def run(self):
        while True:
            self.handleEvents()
            self.update()
            self.render()
            self.clock.tick(FPS)

    # -------------------------------------------------------
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_SPACE, pygame.K_UP):
                    if self.state == "playing" and self.player and self.player.onGround:
                        self.sounds.play("jump", vol=0.32)

                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "title"
                    else:
                        pygame.quit(); sys.exit()

                elif event.key == pygame.K_p and self.state == "playing":
                    self.state = "paused"
                elif event.key == pygame.K_p and self.state == "paused":
                    self.state = "playing"

                elif event.key == pygame.K_RETURN:
                    if self.state == "title":
                        self.levelIdx = 0
                        self.totalScore = 0
                        self.loadLevel(self.currentLevelId())
                        self.state = "playing"
                    elif self.state == "level_complete":
                        self.levelIdx += 1
                        if self.levelIdx >= len(LEVEL_ORDER):
                            if self.secretUnlocked:
                                self.loadLevel("secret")
                            else:
                                self.state = "title"
                                return
                        self.loadLevel(self.currentLevelId())
                        self.state = "playing"
                    elif self.state == "game_over":
                        self.loadLevel(self.currentLevelId())
                        self.state = "playing"

                elif event.key == pygame.K_r and self.state == "playing":
                    if self.player:
                        self.player.startReload()

                elif event.key == pygame.K_e and self.state == "playing":
                    self._tryRescue()

                elif event.key == pygame.K_f and self.state == "playing":
                    if self.player:
                        fired = self.player.tryMelee(pygame.time.get_ticks(), self.enemies)
                        if fired:
                            self.sounds.play("melee", vol=0.65)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.state == "playing":
                    now = pygame.time.get_ticks()
                    _bc = len(self.bullets)
                    self.player.tryShoot(now, self.bullets,
                                         pygame.mouse.get_pos(), self.camera)
                    if len(self.bullets) > _bc:
                        self.sounds.play("shoot", vol=0.42)

    def _tryRescue(self):
        if not self.player:
            return
        for c in self.civilians:
            if c.rescued or not c.alive:
                continue
            dist = ((self.player.rect.centerx - c.rect.centerx)**2 +
                    (self.player.rect.centery - c.rect.centery)**2)**0.5
            if dist <= Civilian.RESCUE_RANGE:
                if any(g.alive for g in c.guards):
                    continue  # guards still protecting this worker
                c.rescued = True
                self.rescuedCount += 1
                self.totalScore += SCORING["liberation_bonus"]
                self.sounds.play("rescue", vol=0.75)
                print(f"[RESCUE] Worker freed! +{SCORING['liberation_bonus']} pts")

    def _onEnemyKilled(self, enemy):
        self.sounds.play("enemy_death", vol=0.50)
        self.enemyKillCount += 1
        self.totalScore += SCORING["fascist_kill"]
        pk = spawnPickupsFromDrop(enemy, self.cfg.get("pickups", []))
        if pk:
            self.pickups.append(pk)
        # Crater on ground
        r = enemy.cfg.get("crater_radius", 0)
        if r > 0:
            self.craters.append(Crater(enemy.rect.centerx, 680, r))

    def _onCivilianDied(self):
        self.sounds.play("civ_death", vol=0.60)
        self.civDeathCount += 1
        self.totalScore += SCORING["civilian_death_penalty"]
        print(f"[TRAGEDY] Civilian killed! {SCORING['civilian_death_penalty']} pts")

    # -------------------------------------------------------
    def update(self):
        if self.state != "playing":
            return

        now  = pygame.time.get_ticks()
        cfg  = self.cfg
        grav = cfg["gravity"]
        term = cfg["terminal_velocity"]
        fric = cfg["friction"]

        # ── Player ─────────────────────────────────────────
        keys = pygame.key.get_pressed()
        self.player.handleInput(keys, None, fric)
        self.player.applyGravity(grav, term)
        self.player.move(self.platforms)
        # Clamp to level bounds so player can't walk/fall off the edges
        self.player.rect.x = max(0, min(self.player.rect.x, self.LEVEL_W - self.player.rect.width))
        if self.player.rect.top > self.LEVEL_H:   # fell through the floor somehow
            self.player.rect.bottom = 680
            self.player.velY = 0
        self.player.updateTimers(now)
        if not self.player.alive:
            self.sounds.stop_all_loops()
            self.sounds.play("player_death", vol=0.80)
            self.state = "game_over"
            return

        # ── Enemies ────────────────────────────────────────
        rescued_allies = [c for c in self.civilians if c.alive and c.rescued]
        _bc_before = len(self.bullets)
        for e in self.enemies:
            if not e.alive:
                continue
            e.update(self.player, now, grav, term, self.platforms, self.bullets,
                     allies=rescued_allies)
        if len(self.bullets) > _bc_before:
            self.sounds.play("enemy_shoot", vol=0.22)

        # ── Civilians ──────────────────────────────────────
        for c in self.civilians:
            if not c.alive:
                continue
            c.update(self.player, grav, term, self.platforms, self.enemies,
                     now=now, bullets=self.bullets)

        # ── Bullets ────────────────────────────────────────
        for b in self.bullets:
            b.update(self.platforms)
            if not b.alive:
                continue

            if b.owner == "player":
                for e in self.enemies:
                    if e.alive and b.rect.colliderect(e.rect):
                        killed = e.takeDamage(b.damage)
                        b.alive = False
                        if killed:
                            self._onEnemyKilled(e)
                        break
                # Friendly fire check
                for c in self.civilians:
                    if c.alive and not c.rescued and b.rect.colliderect(c.rect):
                        c.takeDamage(b.damage)
                        b.alive = False
                        if not c.alive:
                            self._onCivilianDied()
                        break

            elif b.owner == "enemy":
                if b.rect.colliderect(self.player.rect):
                    self.player.takeDamage(b.damage)
                    b.alive = False
                    self.sounds.play("hurt", vol=0.68)
                else:
                    for c in self.civilians:
                        if c.alive and c.rescued and b.rect.colliderect(c.rect):
                            c.takeDamage(b.damage)
                            b.alive = False
                            break

        # ── Pickups ────────────────────────────────────────
        for pk in self.pickups:
            if pk.alive and pk.rect.colliderect(self.player.rect):
                self.player.applyPickup(pk.ptype, pk.pdata)
                pk.alive = False
                self.sounds.play("pickup", vol=0.58)

        # ── Web slowdown (Level 5 turrets) ─────────────────
        # (Handled inside Enemy._snipe via bullet type; extend here if needed)

        # ── Cull dead objects ──────────────────────────────
        self.enemies   = [e for e in self.enemies   if e.alive]
        self.bullets   = [b for b in self.bullets   if b.alive]
        self.pickups   = [p for p in self.pickups   if p.alive]

        # ── Meteors ────────────────────────────────────────
        meteor_rate = self.cfg.get("meteor_rate", 0)
        if meteor_rate > 0 and now - self._meteorTimer >= meteor_rate:
            wx = self.camera[0] + random.randint(60, SCREEN_W - 60)
            self.meteors.append(Meteor(wx))
            self._meteorTimer = now
        for m in list(self.meteors):
            landed = m.update(self.platforms)
            if landed:
                self.sounds.play("meteor", vol=0.72)
                blast = m.radius + 35
                # Hurt nearby entities
                if (abs(self.player.rect.centerx - m.x) < blast and
                        abs(self.player.rect.bottom  - m.y) < 70):
                    self.player.takeDamage(m.radius * 2)
                for e in self.enemies:
                    if (e.alive and abs(e.rect.centerx - m.x) < blast and
                            abs(e.rect.bottom - m.y) < 70):
                        e.takeDamage(m.radius * 3)
                if m.y >= 660:
                    self.craters.append(Crater(int(m.x), 680, m.radius + 5))
            if not m.alive:
                self.meteors.remove(m)

        # ── Lava floor damage ──────────────────────────────
        if self.cfg.get("lava_floor"):
            if self.player.onGround and self.player.rect.bottom >= 678:
                lava_dmg = self.cfg.get("lava_damage", 3)
                if now - self._lavaDmgTimer >= 200:
                    self.player.takeDamage(lava_dmg)
                    self.sounds.play("hurt", vol=0.38)
                    self._lavaDmgTimer = now

        # ── Asteroids + tick ───────────────────────────────
        for ast in self.asteroids:
            ast.update()
        self._tick += 1

        # ── Camera ─────────────────────────────────────────
        self.camera = cameraOffset(self.player, self.LEVEL_W, self.LEVEL_H)

        # ── Win check ──────────────────────────────────────
        if self.checkWinCondition():
            bonus = SCORING["level_clear_bonus"]
            if self.civDeathCount == 0:
                bonus += SCORING["no_civilian_deaths_bonus"]
            self.totalScore += bonus
            if self.levelIdx == len(LEVEL_ORDER) - 1:
                self.secretUnlocked = True
            self.sounds.stop_all_loops()
            self.sounds.play("level_complete", vol=0.72)
            self.state = "level_complete"

    # -------------------------------------------------------
    def _drawWorld(self):
        # 1 — solid space background
        self.screen.fill(self.cfg.get("bg_color", DARK))

        # 2 — star field (parallax, behind everything)
        self.starField.draw(self.screen, self.camera, self._tick)

        # 3 — background image overlay (if present)
        if self.bgSurf:
            self.screen.blit(self.bgSurf, (-self.camera[0], -self.camera[1]))

        # 4 — asteroids (mid-parallax, above stars)
        for ast in self.asteroids:
            ast.draw(self.screen, self.camera)

        # 5 — craters (on ground surface, behind platforms visually)
        for crater in self.craters:
            crater.draw(self.screen, self.camera)

        # 6 — platforms (lava ground on volcanic levels, rock elsewhere)
        pc       = self.cfg.get("platform_color", (68, 58, 48))
        rim      = tuple(max(0, c - 26) for c in pc)
        lava_lvl = self.cfg.get("lava_floor", False)
        t        = self._tick
        for plat in self.platforms:
            drawR = pygame.Rect(plat.x - self.camera[0],
                                plat.y - self.camera[1],
                                plat.width, plat.height)
            if lava_lvl and plat.y >= 679:
                # Animated lava ground
                for lx in range(drawR.left, drawR.right, 3):
                    wave = int(3 * math.sin(lx * 0.05 + t * 0.10))
                    col  = (min(255, 195 + wave * 8), 55, 0)
                    pygame.draw.rect(self.screen, col,
                                     (lx, drawR.top - wave, 3, drawR.height + wave + 2))
                # Glow strip at lava surface
                gs = pygame.Surface((drawR.width, 12), pygame.SRCALPHA)
                pulse = int(55 + 30 * math.sin(t * 0.12))
                gs.fill((255, 140, 0, pulse))
                self.screen.blit(gs, (drawR.left, drawR.top - 6))
            else:
                pygame.draw.rect(self.screen, pc,  drawR)
                pygame.draw.rect(self.screen, rim, drawR, 2)

        for pk in self.pickups:
            pk.draw(self.screen, self.camera)
        for c in self.civilians:
            if c.alive:
                c.draw(self.screen, self.camera)
        for e in self.enemies:
            if e.alive:
                e.draw(self.screen, self.camera)
        for m in self.meteors:
            m.draw(self.screen, self.camera)
        for b in self.bullets:
            if b.alive:
                b.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        totalE = sum(self.cfg["spawn"].get(et, 0)
                     for et in self.cfg.get("enemies", {}))
        totalC = sum(self.cfg["spawn"].get(ct, 0)
                     for ct in self.cfg.get("civilians", {}))
        self.hud.draw(
            self.player,
            f"{self.cfg['name']} — {self.cfg['subtitle']}",
            self.totalScore,
            totalE, self.enemyKillCount,
            totalC, self.rescuedCount, self.civDeathCount,
        )

    # -------------------------------------------------------
    def render(self):
        if self.state == "title":
            drawTitleScreen(self.screen, self.fontLg, self.fontSm)
        elif self.state in ("playing", "paused", "level_complete"):
            self._drawWorld()
            if self.state == "paused":
                drawPauseOverlay(self.screen, self.fontLg, self.fontSm)
            elif self.state == "level_complete":
                drawLevelComplete(self.screen, self.fontLg, self.fontSm,
                                  self.totalScore, self.rescuedCount, self.civDeathCount)
        elif self.state == "game_over":
            drawGameOver(self.screen, self.fontLg, self.fontSm, self.totalScore)

        pygame.display.flip()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    Game().run()
