#!/usr/bin/env python3
"""
WILD EMPIRE — Alien Sprite Generator
Creates pixel-art PNG sprites for every character and pickup.

Run from the wild_empire/ game folder:
    python generate_sprites.py

Requires:
    pip install Pillow
"""

from PIL import Image, ImageDraw
import os, math

OUT = "assets/sprites"
os.makedirs(OUT, exist_ok=True)

# ─── Palette ──────────────────────────────────────────────────────────────────
T  = (0,   0,   0,   0)    # transparent
BK = (0,   0,   0, 255)    # black outline

# Alien skins
TEAL        = (50,  205, 185, 255)   # player
GRAY_BLUE   = (95,  110, 145, 255)   # L1 blackshirts
DARK_INDIGO = (45,  45,  80,  255)   # L1 captain
SANDY       = (205, 180, 135, 255)   # L1/L2 civilians
BROWN_TAN   = (155, 118, 75,  255)   # L2 soldiers
DEEP_AMBER  = (145, 80,  20,  255)   # L2 inquisitor
ORANGE_FAT  = (255, 118, 0,   255)   # L3 blobs
ORANGE_DARK = (210, 80,  0,   255)   # L3 blob shadow
ORANGE_HI   = (255, 175, 60,  255)   # L3 blob highlight
RED_ALIEN   = (195, 40,  25,  255)   # L3 fire agent
PALE_GREEN  = (150, 215, 155, 255)   # L3/L5 detained/imprisoned
CRIMSON     = (175, 20,  20,  255)   # L4 imperial
KHAKI       = (155, 138, 88,  255)   # L2/secret olive
OLIVE       = (98,  108, 58,  255)   # secret enforcer
CHITINBLK   = (28,  22,  35,  255)   # L5 arthropod carapace
CHITINHI    = (55,  48,  70,  255)   # L5 carapace highlight
CHITIN_RED  = (90,  10,  10,  255)   # L5 commander markings
DISPLACED   = (205, 190, 148, 255)   # secret civilian

# Uniforms / materials
BLACK_UNI   = (18,  18,  28,  255)
DARK_GREEN  = (32,  75,  42,  255)
STEEL       = (110, 115, 130, 255)
DARK_STEEL  = (60,  65,  75,  255)
GOLD        = (215, 175, 20,  255)
RED         = (215, 38,  38,  255)
BRIGHT_RED  = (255, 30,  30,  255)
MAGA_RED    = (198, 30,  30,  255)
MAGA_GOLD   = (210, 168, 0,   255)
WEB_TAN     = (200, 190, 155, 255)
BOOT        = (22,  38,  58,  255)
BELT        = (58,  48,  28,  255)

# Eyes
YELLOW_EYE  = (255, 220, 0,   255)
RED_EYE     = (255, 35,  35,  255)
GREEN_EYE   = (50,  220, 80,  255)
BLUE_EYE    = (60,  160, 255, 255)
ORANGE_EYE  = (255, 140, 0,   255)
GLOW_RED    = (255, 50,  50,  255)
PUPIL       = (5,   5,   5,   255)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def C(w, h):  return Image.new("RGBA", (w, h), T)
def D(im):    return ImageDraw.Draw(im)

def sv(im, name):
    im.save(os.path.join(OUT, name))
    print(f"  {name}")

def ell(d, cx, cy, rx, ry, fill, ol=None):
    d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=fill, outline=ol)

def box(d, x, y, w, h, fill, ol=None):
    d.rectangle([x, y, x+w-1, y+h-1], fill=fill, outline=ol)

def dot(d, x, y, fill):
    d.point([(x, y)], fill=fill)

def eye(d, cx, cy, r, iris, bg=(240,240,240,255)):
    """White sclera + iris + black pupil."""
    ell(d, cx, cy, r+1, r+1, bg)
    ell(d, cx, cy, r, r, iris)
    pr = max(1, r//2)
    ell(d, cx, cy, pr, pr, PUPIL)

def angry_brow(d, cx, cy, r, side=1):
    """Angled brow above eye. side=1 right, side=-1 left."""
    bx = cx + side * r
    d.line([cx-r, cy-r-1, bx, cy-r-3], fill=BK, width=2)

def legs_spider(d, cx, cy, rx, ry, n_pairs, color, thickness=2):
    """Draw n_pairs pairs of arthropod legs from the body ellipse."""
    for i in range(n_pairs):
        t = (i + 0.5) / n_pairs
        # Attachment point on body edge
        ax = cx + rx * math.cos(math.pi * t)
        ay = cy + ry * math.sin(math.pi * t)
        # Leg bends outward then downward
        mx = ax + (ax - cx) * 0.6
        my = ay + ry * 0.5
        ex = mx + (ax - cx) * 0.4
        ey = my + ry * 0.7
        # Left side
        d.line([int(ax), int(ay), int(mx), int(my)], fill=color, width=thickness)
        d.line([int(mx), int(my), int(ex), int(ey)], fill=color, width=thickness)
        # Mirror right side
        rax = cx - (ax - cx)
        ray = ay
        rmx = cx - (mx - cx)
        rmy = my
        rex = cx - (ex - cx)
        rey = ey
        d.line([int(rax), int(ray), int(rmx), int(rmy)], fill=color, width=thickness)
        d.line([int(rmx), int(rmy), int(rex), int(rey)], fill=color, width=thickness)


# ─── PLAYER (28×44) ──────────────────────────────────────────────────────────
def player():
    W, H = 28, 44
    im = C(W, H); d = D(im)

    # Boots
    box(d,  7, 39, 7, 5, BOOT)
    box(d, 15, 39, 7, 5, BOOT)
    # Legs
    box(d,  8, 28, 5, 13, DARK_GREEN)
    box(d, 15, 28, 5, 13, DARK_GREEN)
    # Body
    box(d,  7, 16, 14, 14, DARK_GREEN)
    # Belt
    box(d,  7, 27, 14, 3, BELT)
    box(d, 12, 27, 4, 3, GOLD)   # buckle
    # Arms
    box(d,  2, 17, 5, 12, TEAL)  # left — gun arm
    box(d, 21, 17, 5, 10, TEAL)  # right
    # Gun (left side)
    box(d,  0, 22, 4, 3, DARK_STEEL)
    box(d,  1, 20, 4, 5, STEEL)
    # Collar
    box(d,  9, 15, 10, 3, (40, 100, 60, 255))
    # Head — slightly wide alien
    ell(d, 14, 10, 9, 9, TEAL)
    # Beret
    box(d,  5,  4, 18, 5, (22, 42, 125, 255))
    ell(d, 14,  4, 9, 3, (22, 42, 125, 255))
    # Red star on beret
    box(d, 11,  2, 6, 6, RED)
    ell(d, 14,  5, 3, 3, RED)
    # Eyes (alien yellow)
    eye(d, 10, 10, 2, YELLOW_EYE)
    eye(d, 18, 10, 2, YELLOW_EYE)
    # Mouth — determined line
    d.line([11, 15, 17, 15], fill=(30, 140, 90, 255), width=1)
    # Antennae
    d.line([10, 2,  8,  0], fill=TEAL, width=1)
    d.line([18, 2, 20,  0], fill=TEAL, width=1)
    dot(d,  8,  0, YELLOW_EYE)
    dot(d, 20,  0, YELLOW_EYE)

    sv(im, "player.png")


# ─── L1: BLACKSHIRT GRUNT (28×42) ────────────────────────────────────────────
def l1_grunt():
    W, H = 28, 42
    im = C(W, H); d = D(im)

    # Boots
    box(d,  7, 38, 6, 4, BK)
    box(d, 15, 38, 6, 4, BK)
    # Legs
    box(d,  8, 28, 5, 12, BLACK_UNI)
    box(d, 15, 28, 5, 12, BLACK_UNI)
    # Body — black uniform
    box(d,  7, 16, 14, 14, BLACK_UNI)
    # Silver buttons
    for by in [20, 24, 28]:
        dot(d, 14, by, (180, 180, 190, 255))
    # Red armband
    box(d,  2, 22, 5, 3, RED)
    # Arms
    box(d,  2, 17, 5, 12, GRAY_BLUE)
    box(d, 21, 17, 5, 12, GRAY_BLUE)
    # Hands
    ell(d,  4, 30, 3, 3, GRAY_BLUE)
    ell(d, 24, 30, 3, 3, GRAY_BLUE)
    # Head
    ell(d, 14, 10, 8, 8, GRAY_BLUE)
    # Steel helmet
    ell(d, 14,  7, 9, 7, (35, 38, 55, 255))
    box(d,  5,  9, 18, 4, (35, 38, 55, 255))  # brim
    # Glowing red eyes
    eye(d, 10, 11, 2, RED_EYE, (80, 10, 10, 255))
    eye(d, 18, 11, 2, RED_EYE, (80, 10, 10, 255))
    # Alien mouth slit
    d.line([11, 15, 17, 15], fill=(60, 60, 80, 255), width=1)

    sv(im, "l1_blackshirt_grunt.png")


# ─── L1: BLACKSHIRT CAPTAIN (32×48) ─────────────────────────────────────────
def l1_captain():
    W, H = 32, 48
    im = C(W, H); d = D(im)

    # Boots
    box(d,  8, 43, 7, 5, BK)
    box(d, 17, 43, 7, 5, BK)
    # Legs
    box(d,  9, 32, 6, 13, BLACK_UNI)
    box(d, 17, 32, 6, 13, BLACK_UNI)
    # Body
    box(d,  8, 18, 16, 16, BLACK_UNI)
    # Gold trim
    box(d,  8, 18, 16, 2, GOLD)   # top collar
    box(d,  8, 30, 16, 2, GOLD)   # belt
    # Epaulettes
    box(d,  5, 18, 4, 6, GOLD)
    box(d, 23, 18, 4, 6, GOLD)
    # Medal
    ell(d, 16, 24, 3, 3, GOLD)
    # Arms
    box(d,  3, 19, 5, 14, DARK_INDIGO)
    box(d, 24, 19, 5, 14, DARK_INDIGO)
    # Gloves
    ell(d,  5, 34, 4, 4, BK)
    ell(d, 27, 34, 4, 4, BK)
    # Head
    ell(d, 16, 12, 9, 9, DARK_INDIGO)
    # Officer cap
    ell(d, 16,  8, 10, 6, (22, 22, 40, 255))
    box(d,  6, 12, 20, 4, (22, 22, 40, 255))  # brim
    box(d, 10,  8, 12, 3, (22, 22, 40, 255))
    # Gold cap badge
    box(d, 13,  9, 6, 4, GOLD)
    # Eyes — larger, more intense
    eye(d, 11, 13, 3, RED_EYE, (60, 8, 8, 255))
    eye(d, 21, 13, 3, RED_EYE, (60, 8, 8, 255))
    angry_brow(d, 11, 13, 3, -1)
    angry_brow(d, 21, 13, 3,  1)

    sv(im, "l1_blackshirt_captain.png")


# ─── L1: FASCIST TANK / ARMORED CRAWLER (64×40) ──────────────────────────────
def l1_tank():
    W, H = 64, 40
    im = C(W, H); d = D(im)

    # Treads
    box(d,  2, 28, 60, 10, BK)
    box(d,  2, 28, 60, 10, (35, 35, 40, 255))
    for tx in range(4, 62, 8):
        box(d, tx, 28, 6, 10, (55, 55, 60, 255))
    # Hull body
    box(d,  6, 14, 52, 16, STEEL)
    box(d,  8, 12, 48, 18, STEEL)
    # Hull highlight
    box(d,  8, 12, 48, 4, (145, 150, 165, 255))
    # Alien emblem on side — black X in red circle
    ell(d, 16, 21, 7, 7, RED)
    d.line([11, 16, 21, 26], fill=BK, width=2)
    d.line([11, 26, 21, 16], fill=BK, width=2)
    # Turret base
    box(d, 22,  8, 20, 8, DARK_STEEL)
    ell(d, 32,  8, 11, 8, DARK_STEEL)
    # Gun barrel
    box(d, 40,  9,  18, 5, DARK_STEEL)
    box(d, 56,  10, 6,  3, BK)
    # Vision slits (alien eyes on turret)
    box(d, 24, 10, 6, 3, (200, 30, 30, 255))
    box(d, 32, 10, 6, 3, (200, 30, 30, 255))
    # Rivets
    for rx in [10, 54]:
        for ry in [16, 24]:
            ell(d, rx, ry, 2, 2, DARK_STEEL)

    sv(im, "l1_tank.png")


# ─── L1: CIVILIAN — OPPRESSED WORKER (24×40) ─────────────────────────────────
def l1_civilian():
    W, H = 24, 40
    im = C(W, H); d = D(im)

    # Feet
    box(d,  4, 36, 6, 4, (88, 68, 40, 255))
    box(d, 13, 36, 6, 4, (88, 68, 40, 255))
    # Legs — ragged trousers
    box(d,  5, 26, 5, 12, (105, 95, 80, 255))
    box(d, 13, 26, 5, 12, (105, 95, 80, 255))
    # Tunic / rags
    box(d,  5, 14, 14, 14, (130, 115, 90, 255))
    box(d,  5, 20, 14,  2, (115, 100, 78, 255))  # belt
    # Arms (reaching outward — pleading)
    box(d,  1, 15, 4, 10, SANDY)
    box(d, 19, 15, 4, 10, SANDY)
    ell(d,  2, 26, 3, 3, SANDY)
    ell(d, 22, 26, 3, 3, SANDY)
    # Head — slightly small (hunched)
    ell(d, 12, 10, 7, 8, SANDY)
    # Three eyes — scared/wide
    eye(d,  8, 9, 2, GREEN_EYE)
    eye(d, 12, 8, 2, GREEN_EYE)
    eye(d, 16, 9, 2, GREEN_EYE)
    # Open mouth — frightened O
    ell(d, 12, 14, 2, 2, BK)

    sv(im, "l1_civilian.png")


# ─── L2: FALANGIST SOLDIER (28×44) ───────────────────────────────────────────
def l2_falangist():
    W, H = 28, 44
    im = C(W, H); d = D(im)

    # Boots
    box(d,  7, 39, 6, 5, (60, 42, 22, 255))
    box(d, 15, 39, 6, 5, (60, 42, 22, 255))
    # Legs
    box(d,  8, 28, 5, 13, KHAKI)
    box(d, 15, 28, 5, 13, KHAKI)
    # Body — khaki uniform
    box(d,  7, 16, 14, 14, KHAKI)
    # Eagle badge (simplified wing shape)
    box(d,  9, 18, 10, 4, (100, 88, 50, 255))
    ell(d, 14, 18, 5, 3, (130, 110, 60, 255))
    # Arms
    box(d,  2, 17, 5, 12, BROWN_TAN)
    box(d, 21, 17, 5, 12, BROWN_TAN)
    # Rifle
    box(d, 21, 16, 3, 18, DARK_STEEL)
    box(d, 21, 14, 2, 4,  (88, 68, 40, 255))
    # Head
    ell(d, 14, 10, 8, 8, BROWN_TAN)
    # Field cap
    box(d,  7,  6, 14, 6, KHAKI)
    ell(d, 14,  6, 7, 4, (148, 130, 82, 255))
    box(d,  6,  9, 16, 3, KHAKI)  # brim
    # Eyes
    eye(d, 10, 10, 2, ORANGE_EYE)
    eye(d, 18, 10, 2, ORANGE_EYE)
    # Mouth — grim set
    d.line([11, 15, 17, 15], fill=(90, 65, 40, 255), width=1)

    sv(im, "l2_falangist.png")


# ─── L2: INQUISITOR ELITE (30×50) ────────────────────────────────────────────
def l2_inquisitor():
    W, H = 30, 50
    im = C(W, H); d = D(im)

    # Robe (floor-length)
    box(d,  5, 18, 20, 32, (40, 28, 18, 255))
    # Robe hem detail
    box(d,  5, 46, 20, 4, (28, 18, 10, 255))
    # Sash / belt
    box(d,  5, 32, 20, 4, DEEP_AMBER)
    # Body under hood
    box(d,  8, 16, 14, 6, (50, 35, 20, 255))
    # Arms — hidden in robe sleeves
    box(d,  2, 20, 6, 18, (40, 28, 18, 255))
    box(d, 22, 20, 6, 18, (40, 28, 18, 255))
    # Clawed hands
    ell(d,  4, 38, 4, 4, DEEP_AMBER)
    d.line([2, 42, 0, 46], fill=DEEP_AMBER, width=1)
    d.line([4, 43, 3, 47], fill=DEEP_AMBER, width=1)
    d.line([6, 42, 6, 46], fill=DEEP_AMBER, width=1)
    ell(d, 26, 38, 4, 4, DEEP_AMBER)
    d.line([24, 42, 22, 46], fill=DEEP_AMBER, width=1)
    d.line([26, 43, 25, 47], fill=DEEP_AMBER, width=1)
    d.line([28, 42, 28, 46], fill=DEEP_AMBER, width=1)
    # Head under pointed hood
    ell(d, 15, 13, 8, 9, DEEP_AMBER)
    # Hood (pointed)
    d.polygon([(6,14),(24,14),(22,2),(15,0),(8,2)], fill=(25,16,8,255))
    box(d,  6, 12, 18, 5, (25, 16, 8, 255))
    # Glowing eyes (two large ones, deeply shadowed)
    eye(d, 11, 13, 3, (220, 120, 0, 255), (10,5,0,255))
    eye(d, 19, 13, 3, (220, 120, 0, 255), (10,5,0,255))
    # Symbol on chest (ornate dot pattern)
    ell(d, 15, 27, 3, 3, DEEP_AMBER)
    for ang in range(0, 360, 60):
        ex = int(15 + 5 * math.cos(math.radians(ang)))
        ey = int(27 + 5 * math.sin(math.radians(ang)))
        dot(d, ex, ey, GOLD)

    sv(im, "l2_inquisitor.png")


# ─── L2: CONDOR DRONE (40×20) ────────────────────────────────────────────────
def l2_condor_drone():
    W, H = 40, 20
    im = C(W, H); d = D(im)

    # Wings — swept eagle-like
    d.polygon([(0,15),(18,8),(20,10),(2,18)], fill=DARK_STEEL)
    d.polygon([(40,15),(22,8),(20,10),(38,18)], fill=DARK_STEEL)
    # Wing highlight (leading edge)
    d.line([0,15, 18,8], fill=STEEL, width=1)
    d.line([40,15, 22,8], fill=STEEL, width=1)
    # Fuselage body
    ell(d, 20, 10, 8, 6, STEEL)
    ell(d, 20, 10, 5, 4, DARK_STEEL)
    # Camera eye (alien sensor)
    ell(d, 20, 10, 3, 3, (200, 30, 30, 255))
    ell(d, 20, 10, 1, 1, PUPIL)
    # Tail fins
    d.polygon([(16,18),(24,18),(22,20),(18,20)], fill=DARK_STEEL)
    # Exhaust nozzle
    box(d, 17, 16, 6, 2, (255,160,40,255))

    sv(im, "l2_condor_drone.png")


# ─── L2: CIVILIAN — BASQUE WORKER (24×40) ────────────────────────────────────
def l2_civilian():
    W, H = 24, 40
    im = C(W, H); d = D(im)

    # Feet
    box(d,  4, 36, 6, 4, (80, 60, 35, 255))
    box(d, 13, 36, 6, 4, (80, 60, 35, 255))
    # Legs
    box(d,  5, 26, 5, 12, (110, 95, 72, 255))
    box(d, 13, 26, 5, 12, (110, 95, 72, 255))
    # Work shirt
    box(d,  5, 14, 14, 14, (88, 115, 135, 255))
    # Suspenders
    d.line([ 9, 14,  8, 26], fill=(55, 68, 80, 255), width=1)
    d.line([15, 14, 16, 26], fill=(55, 68, 80, 255), width=1)
    # Arms (one raised — waving for help)
    box(d,  1, 14, 4, 10, SANDY)
    box(d, 19, 14, 4, 14, SANDY)
    box(d, 19,  8, 4, 8,  SANDY)   # raised arm
    ell(d, 21,  8, 4, 4,  SANDY)   # raised hand
    ell(d,  2, 25, 3, 3,  SANDY)
    # Head
    ell(d, 12, 10, 7, 8, SANDY)
    # Flat cap
    box(d,  6,  6, 12, 4, (55, 48, 35, 255))
    box(d,  5,  8, 14, 3, (55, 48, 35, 255))
    # Eyes — two large worried
    eye(d,  9, 10, 2, BLUE_EYE)
    eye(d, 15, 10, 2, BLUE_EYE)
    # Worried mouth
    d.arc([9, 14, 15, 18], start=0, end=180, fill=BK, width=1)

    sv(im, "l2_civilian.png")


# ─── L3: ORANGE BLOB (52×52) — MAGA DRONE ────────────────────────────────────
def l3_orange_blob():
    W, H = 52, 52
    im = C(W, H); d = D(im)

    # Shadow blob at bottom
    ell(d, 26, 42, 20, 8, (160, 70, 0, 120))
    # Main fat blob body
    ell(d, 26, 28, 22, 22, ORANGE_DARK)
    ell(d, 26, 26, 22, 22, ORANGE_FAT)
    # Highlight
    ell(d, 20, 18, 8, 6, ORANGE_HI)
    # MAGA hat (red trapezoid)
    d.polygon([(14,12),(38,12),(36,4),(16,4)], fill=MAGA_RED)
    box(d, 12, 10, 28, 4, MAGA_RED)  # brim
    # Hat band + text area
    box(d, 14,  5, 24, 5, (170, 22, 22, 255))
    # Tiny fat arms
    ell(d,  6, 30, 5, 4, ORANGE_FAT)   # left stumpy arm
    ell(d, 46, 30, 5, 4, ORANGE_FAT)   # right stumpy arm
    # Tiny hands (useless)
    ell(d,  3, 33, 3, 3, ORANGE_DARK)
    ell(d, 49, 33, 3, 3, ORANGE_DARK)
    # Eyes — beady
    ell(d, 20, 24, 3, 3, BK)
    ell(d, 32, 24, 3, 3, BK)
    dot(d, 21, 23, (255,255,255,180))  # glint
    dot(d, 33, 23, (255,255,255,180))
    # Pursed angry mouth
    d.arc([20, 30, 32, 36], start=180, end=0, fill=BK, width=2)
    # Chins (multiple)
    ell(d, 26, 40, 14, 5, ORANGE_DARK)

    sv(im, "l3_orange_blob.png")


# ─── L3: FIRE AGENT (26×44) ──────────────────────────────────────────────────
def l3_fire_agent():
    W, H = 26, 44
    im = C(W, H); d = D(im)

    # Feet
    box(d,  4, 39, 6, 5, (100, 20, 5, 255))
    box(d, 15, 39, 6, 5, (100, 20, 5, 255))
    # Legs
    box(d,  5, 28, 5, 13, (160, 38, 15, 255))
    box(d, 14, 28, 5, 13, (160, 38, 15, 255))
    # Body — lean, aggressive
    box(d,  5, 15, 16, 15, RED_ALIEN)
    # Chest symbol (flame)
    d.polygon([(13,16),(10,22),(13,20),(11,26),(16,20),(13,22)], fill=(255,160,0,255))
    # Arms — angled forward
    box(d,  1, 16, 4, 13, RED_ALIEN)
    box(d, 21, 14, 4, 13, RED_ALIEN)
    # Fists
    ell(d,  2, 30, 4, 4, (155, 30, 12, 255))
    ell(d, 23, 28, 4, 4, (155, 30, 12, 255))
    # Head
    ell(d, 13,  9, 8, 8, RED_ALIEN)
    # Flame crest on head
    d.polygon([(9,2),(11,8),(13,4),(15,8),(17,2),(13,6)], fill=(255,180,0,255))
    # Eyes — white + slit pupils (reptilian)
    eye(d,  9,  9, 2, (255,60,0,255))
    eye(d, 17,  9, 2, (255,60,0,255))
    # Fanged mouth
    d.line([9, 14, 17, 14], fill=BK, width=1)
    for fx in [10, 13, 16]:
        d.line([fx, 14, fx, 16], fill=(255,255,255,200), width=1)

    sv(im, "l3_fire_agent.png")


# ─── L3: BLOB OVERLORD — TRUMP BOSS (80×80) ──────────────────────────────────
def l3_blob_overlord():
    W, H = 80, 80
    im = C(W, H); d = D(im)

    # Shadow
    ell(d, 40, 72, 32, 8, (160, 70, 0, 100))
    # Massive blob body (slightly egg-shaped, wide)
    ell(d, 40, 45, 36, 32, ORANGE_DARK)
    ell(d, 40, 43, 36, 32, ORANGE_FAT)
    # Body highlight
    ell(d, 30, 28, 12, 9, ORANGE_HI)

    # Enormous belly bulge
    ell(d, 40, 62, 28, 14, ORANGE_DARK)

    # Tiny arms (laughably small)
    ell(d,  8, 48,  8,  6, ORANGE_FAT)   # left arm
    ell(d,  3, 52,  5,  4, ORANGE_DARK)  # left hand
    d.line([2, 50, 0, 54], fill=ORANGE_DARK, width=1)  # stubby fingers
    d.line([4, 52, 3, 56], fill=ORANGE_DARK, width=1)
    ell(d, 72, 48,  8,  6, ORANGE_FAT)   # right arm
    ell(d, 77, 52,  5,  4, ORANGE_DARK)  # right hand
    d.line([76, 50, 79, 54], fill=ORANGE_DARK, width=1)
    d.line([77, 52, 79, 56], fill=ORANGE_DARK, width=1)

    # Red power-tie (long, drooping)
    d.polygon([(37,42),(43,42),(46,74),(40,78),(34,74)], fill=MAGA_RED)
    box(d, 37, 40, 6, 4, MAGA_RED)  # tie knot
    # Gold tie pin
    box(d, 38, 58, 4, 2, GOLD)

    # Head — large round orange
    ell(d, 40, 20, 26, 22, ORANGE_DARK)
    ell(d, 40, 18, 26, 22, ORANGE_FAT)
    ell(d, 34, 10, 8, 6, ORANGE_HI)  # highlight

    # MAGA hat
    d.polygon([(16,8),(64,8),(62,-2),(18,-2)], fill=MAGA_RED)
    box(d, 14, 5, 52, 5, MAGA_RED)  # brim
    box(d, 18,-2, 44, 7, (170,22,22,255))  # crown
    # Gold text block on hat
    box(d, 22, 0, 36, 5, MAGA_GOLD)

    # The legendary toupee swirl
    ell(d, 40, 1, 20, 8, MAGA_GOLD)
    ell(d, 30, 3, 10, 6, MAGA_GOLD)
    ell(d, 48, 2,  8, 5, MAGA_GOLD)
    ell(d, 40, 1, 20, 5, (245, 208, 40, 255))   # swirl highlight
    d.arc([26, -2, 54, 10], start=200, end=340, fill=(200,155,0,255), width=2)

    # Eyes — tiny beady, wide set
    ell(d, 28, 20, 5, 4, BK)
    ell(d, 52, 20, 5, 4, BK)
    dot(d, 29, 19, (255,255,255,200))
    dot(d, 53, 19, (255,255,255,200))
    # Angry brows
    d.line([22, 14, 33, 16], fill=MAGA_GOLD, width=3)
    d.line([47, 16, 58, 14], fill=MAGA_GOLD, width=3)

    # Pursed mouth
    d.arc([30, 28, 50, 38], start=180, end=0, fill=BK, width=3)
    # Multiple chins
    ell(d, 40, 36, 18, 7, ORANGE_DARK)
    ell(d, 40, 41, 16, 5, (195, 75, 0, 255))

    sv(im, "l3_blob_overlord.png")


# ─── L3: DETAINED ALIEN (24×38) ──────────────────────────────────────────────
def l3_detained():
    W, H = 24, 38
    im = C(W, H); d = D(im)

    # Cage bars (behind character)
    for bx in [2, 8, 14, 20]:
        box(d, bx, 0, 2, 38, (80, 80, 90, 180))
    # Horizontal bars
    box(d, 0,  0, 24, 2, (80, 80, 90, 255))
    box(d, 0, 18, 24, 2, (80, 80, 90, 255))
    box(d, 0, 36, 24, 2, (80, 80, 90, 255))

    # Small alien inside
    box(d,  6, 26, 5, 10, (80, 130, 80, 255))   # legs
    box(d, 12, 26, 5, 10, (80, 130, 80, 255))
    box(d,  6, 16, 12, 12, (80, 145, 85, 255))  # body (hugging knees)
    ell(d, 12, 12, 6, 7, PALE_GREEN)             # head
    # Three small eyes — wide and frightened
    eye(d,  8, 11, 1, GREEN_EYE)
    eye(d, 12, 10, 1, GREEN_EYE)
    eye(d, 16, 11, 1, GREEN_EYE)
    # Hands on bars
    ell(d,  5, 20, 3, 3, PALE_GREEN)
    ell(d, 19, 20, 3, 3, PALE_GREEN)

    sv(im, "l3_detained.png")


# ─── L4: IMPERIAL SOLDIER (26×44) ─────────────────────────────────────────────
def l4_imperial():
    W, H = 26, 44
    im = C(W, H); d = D(im)

    ARMOUR = (185, 18, 18, 255)   # crimson armour
    UNDER  = (220, 215, 200, 255) # white undershirt

    # Boots
    box(d,  4, 39, 6, 5, (28, 22, 18, 255))
    box(d, 14, 39, 6, 5, (28, 22, 18, 255))
    # Legs
    box(d,  5, 27, 5, 14, UNDER)
    box(d, 14, 27, 5, 14, UNDER)
    # Leg armour plates
    box(d,  5, 31, 5, 7, ARMOUR)
    box(d, 14, 31, 5, 7, ARMOUR)
    # Body
    box(d,  5, 15, 16, 14, UNDER)
    box(d,  5, 15, 16, 14, ARMOUR)  # chest plate
    # Rising sun on chest
    ell(d, 13, 22, 4, 4, (255,220,0,255))
    for ang in range(0, 360, 45):
        ex = int(13 + 6 * math.cos(math.radians(ang)))
        ey = int(22 + 6 * math.sin(math.radians(ang)))
        d.line([13, 22, ex, ey], fill=(255,200,0,200), width=1)
    # Arms
    box(d,  1, 16, 4, 13, ARMOUR)
    box(d, 21, 16, 4, 13, ARMOUR)
    # Hands
    ell(d,  2, 30, 3, 3, CRIMSON)
    ell(d, 23, 30, 3, 3, CRIMSON)
    # Spear / naginata
    d.line([22, 0, 22, 40], fill=STEEL, width=2)
    d.polygon([(20,-1),(24,-1),(22,-5)], fill=(220,215,200,255))  # blade
    # Head
    ell(d, 13, 10, 8, 8, CRIMSON)
    # Horned helmet
    box(d,  5,  6, 16, 7, ARMOUR)
    d.polygon([(5,10),(2,3),(7,8)], fill=ARMOUR)    # left horn
    d.polygon([(21,10),(24,3),(19,8)], fill=ARMOUR)  # right horn
    ell(d, 13,  6, 8, 5, ARMOUR)
    # Eyes
    eye(d,  9, 10, 2, RED_EYE, (40,5,5,255))
    eye(d, 17, 10, 2, RED_EYE, (40,5,5,255))

    sv(im, "l4_imperial_soldier.png")


# ─── L4: MECHANIZED SAMURAI (36×54) ──────────────────────────────────────────
def l4_mech_samurai():
    W, H = 36, 54
    im = C(W, H); d = D(im)

    MECH   = (60, 60, 75, 255)
    MECH_H = (95, 95, 115, 255)
    ACC    = (200, 20, 20, 255)

    # Foot plates
    box(d,  6, 49, 10, 5, MECH)
    box(d, 20, 49, 10, 5, MECH)
    # Leg armour (segmented)
    box(d,  7, 34, 9, 17, MECH)
    box(d, 20, 34, 9, 17, MECH)
    for sy in range(37, 50, 5):
        box(d, 7, sy, 9, 2, MECH_H)
        box(d, 20, sy, 9, 2, MECH_H)
    # Hip plate
    box(d,  5, 30, 26, 6, MECH)
    box(d,  5, 30, 26, 2, MECH_H)
    # Torso — boxy samurai chest
    box(d,  7, 14, 22, 18, MECH)
    box(d,  7, 14, 22,  3, MECH_H)
    # Rising sun on chest
    ell(d, 18, 23, 5, 5, ACC)
    for ang in range(0,360,45):
        ex = int(18 + 8 * math.cos(math.radians(ang)))
        ey = int(23 + 8 * math.sin(math.radians(ang)))
        d.line([18, 23, ex, ey], fill=(200,10,10,180), width=1)
    # Shoulder guards
    box(d,  1, 14, 7, 10, MECH)
    box(d, 28, 14, 7, 10, MECH)
    # Arms (mechanical)
    box(d,  2, 23, 5, 16, MECH)
    box(d, 29, 23, 5, 16, MECH)
    for sy in range(26, 38, 5):
        box(d, 2, sy, 5, 2, MECH_H)
        box(d, 29, sy, 5, 2, MECH_H)
    # Katana (long diagonal)
    d.line([30, 0, 35, 40], fill=STEEL, width=3)
    d.line([30, 0, 33, 0], fill=(220,215,200,255), width=2)
    # Head — oni helmet
    ell(d, 18,  9, 11, 11, MECH)
    ell(d, 18,  8, 11,  8, MECH)
    box(d,  7,  6, 22,  8, MECH)  # face plate
    # Crest / kawari-kabuto
    d.polygon([(12,0),(24,0),(26,6),(10,6)], fill=ACC)
    # Visor slit — glowing eyes
    box(d, 10, 10, 16, 4, BK)
    box(d, 11, 10, 6, 4, (255, 30, 30, 255))   # left eye glow
    box(d, 19, 10, 6, 4, (255, 30, 30, 255))   # right eye glow

    sv(im, "l4_mech_samurai.png")


# ─── L4: KAMIKAZE DRONE (22×22) ──────────────────────────────────────────────
def l4_kamikaze_drone():
    W, H = 22, 22
    im = C(W, H); d = D(im)

    # Spinning blade arms (4-way cross)
    box(d,  0,  9, 22, 4, DARK_STEEL)
    box(d,  9,  0, 4, 22, DARK_STEEL)
    # Blade tips
    ell(d,  2, 11, 3, 2, STEEL)
    ell(d, 20, 11, 3, 2, STEEL)
    ell(d, 11,  2, 2, 3, STEEL)
    ell(d, 11, 20, 2, 3, STEEL)
    # Core
    ell(d, 11, 11, 5, 5, (180,145,0,255))
    ell(d, 11, 11, 3, 3, (255,200,0,255))
    # Kamikaze symbol — red dot
    ell(d, 11, 11, 2, 2, RED)
    # Glow
    ell(d, 11, 11, 6, 6, (255,200,0,60))

    sv(im, "l4_kamikaze_drone.png")


# ─── L4: CIVILIAN — CONQUERED WORKER (24×40) ─────────────────────────────────
def l4_civilian():
    W, H = 24, 40
    im = C(W, H); d = D(im)

    skin = (185, 155, 115, 255)

    # Feet
    box(d,  4, 36, 6, 4, (65, 50, 30, 255))
    box(d, 13, 36, 6, 4, (65, 50, 30, 255))
    # Legs
    box(d,  5, 26, 5, 12, (95, 115, 140, 255))
    box(d, 13, 26, 5, 12, (95, 115, 140, 255))
    # Robe/kimono
    box(d,  4, 13, 16, 15, (210, 205, 190, 255))
    box(d,  4, 20,  2, 8, (180, 175, 158, 255))  # left fold
    box(d, 18, 20,  2, 8, (180, 175, 158, 255))  # right fold
    # Sash
    box(d,  4, 25, 16, 3, (155, 38, 38, 255))
    # Arms (bowed — submissive)
    box(d,  1, 16, 4, 10, skin)
    box(d, 19, 16, 4, 10, skin)
    # Hands together (bowing)
    ell(d, 12, 26, 5, 4, skin)
    # Head
    ell(d, 12, 10, 7, 8, skin)
    # Hair bun
    ell(d, 12,  4, 4, 4, (40, 32, 22, 255))
    # Eyes (downcast)
    eye(d,  9, 10, 2, (80,160,200,255))
    eye(d, 15, 10, 2, (80,160,200,255))
    # Mouth — sad downward arc
    d.arc([8, 14, 16, 18], start=0, end=180, fill=BK, width=1)

    sv(im, "l4_civilian.png")


# ─── L5: SPIDER GRUNT (34×26) — ARTHROPOD ────────────────────────────────────
def l5_spider_grunt():
    W, H = 34, 26
    im = C(W, H); d = D(im)

    # Leg pairs (3 per side)
    # Left legs
    d.line([14, 14,  6,  8], fill=CHITINBLK, width=2)
    d.line([ 6,  8,  0,  4], fill=CHITINBLK, width=2)
    d.line([14, 16,  5, 15], fill=CHITINBLK, width=2)
    d.line([ 5, 15,  0, 18], fill=CHITINBLK, width=2)
    d.line([14, 18,  6, 22], fill=CHITINBLK, width=2)
    d.line([ 6, 22,  0, 26], fill=CHITINBLK, width=2)
    # Right legs
    d.line([20, 14, 28,  8], fill=CHITINBLK, width=2)
    d.line([28,  8, 34,  4], fill=CHITINBLK, width=2)
    d.line([20, 16, 29, 15], fill=CHITINBLK, width=2)
    d.line([29, 15, 34, 18], fill=CHITINBLK, width=2)
    d.line([20, 18, 28, 22], fill=CHITINBLK, width=2)
    d.line([28, 22, 34, 26], fill=CHITINBLK, width=2)
    # Abdomen (rear egg-shape)
    ell(d, 22, 18, 10, 8, CHITINBLK)
    ell(d, 22, 17, 10, 8, CHITINHI)
    # Cephalothorax (front body — bigger)
    ell(d, 15, 14, 11, 10, CHITINBLK)
    ell(d, 15, 13, 11, 10, CHITINHI)
    # Carapace detail lines
    d.arc([7, 6, 23, 18], start=210, end=330, fill=CHITINBLK, width=1)
    # Eyes (4 glowing red in a row)
    for ex in [9, 12, 15, 18]:
        ell(d, ex, 10, 2, 2, GLOW_RED)
        dot(d, ex, 10, (255,180,180,255))
    # Chelicerae (fangs)
    d.line([12, 18, 9, 22], fill=CHITINBLK, width=2)
    d.line([18, 18, 21, 22], fill=CHITINBLK, width=2)
    ell(d,  9, 22, 2, 2, (60,0,0,255))
    ell(d, 21, 22, 2, 2, (60,0,0,255))

    sv(im, "l5_spider_grunt.png")


# ─── L5: SPIDER COMMANDER (44×36) — ARTHROPOD ────────────────────────────────
def l5_spider_commander():
    W, H = 44, 36
    im = C(W, H); d = D(im)

    # 4 leg pairs per side
    for side, ox in [(-1, 18), (1, 26)]:
        for i, (ly, ldy) in enumerate([(10,4),(16,14),(20,22),(24,30)]):
            ex = ox + side * (18 + i*2)
            d.line([ox, ly, ox + side*10, (ly+ldy)//2], fill=CHITINBLK, width=2)
            d.line([ox + side*10, (ly+ldy)//2, ex, ldy], fill=CHITINBLK, width=2)

    # Abdomen — larger, has red stripe
    ell(d, 30, 24, 13, 12, CHITINBLK)
    ell(d, 30, 23, 13, 12, CHITINHI)
    # Commander red marking on abdomen (hour-glass)
    ell(d, 30, 21, 5, 8, CHITIN_RED)
    ell(d, 30, 29, 3, 4, CHITIN_RED)

    # Cephalothorax (head+chest)
    ell(d, 18, 18, 14, 12, CHITINBLK)
    ell(d, 18, 17, 14, 12, CHITINHI)
    # Carapace grooves
    d.arc([7, 8, 29, 26], start=210, end=330, fill=CHITINBLK, width=1)
    d.arc([10, 11, 26, 23], start=210, end=330, fill=(42,35,55,255), width=1)

    # Eyes — 6 glowing, in 2 rows
    for ex in [11, 16, 21]:
        ell(d, ex, 12, 2, 2, GLOW_RED)
    for ex in [12, 18]:
        ell(d, ex, 17, 2, 2, GLOW_RED)

    # Chelicerae (longer fang arms)
    d.line([13, 26, 8, 34], fill=CHITINBLK, width=3)
    d.line([23, 26, 28, 34], fill=CHITINBLK, width=3)
    ell(d,  7, 34, 3, 2, (90,0,0,255))
    ell(d, 29, 34, 3, 2, (90,0,0,255))
    # Pedipalps
    d.line([11, 16,  5, 10], fill=CHITINHI, width=2)
    d.line([25, 16, 31, 10], fill=CHITINHI, width=2)

    sv(im, "l5_spider_commander.png")


# ─── L5: WEB TURRET (30×30) ──────────────────────────────────────────────────
def l5_web_turret():
    W, H = 30, 30
    im = C(W, H); d = D(im)

    cx, cy = 15, 15
    # Web rings
    for r in [14, 10, 6, 3]:
        ell(d, cx, cy, r, r, T)
        ell(d, cx, cy, r, r, T, ol=(100, 90, 130, 180))
    # Web radial lines
    for ang in range(0, 360, 45):
        ex = int(cx + 14 * math.cos(math.radians(ang)))
        ey = int(cy + 14 * math.sin(math.radians(ang)))
        d.line([cx, cy, ex, ey], fill=(100, 90, 130, 160), width=1)
    # Turret base
    ell(d, cx, cy, 8, 8, CHITINBLK)
    ell(d, cx, cy, 6, 6, CHITINHI)
    # Central eye / barrel
    ell(d, cx, cy, 4, 4, (80,0,0,255))
    ell(d, cx, cy, 2, 2, GLOW_RED)
    dot(d, cx, cy, (255,200,200,255))
    # Mount legs (4 anchors)
    for ang in [45, 135, 225, 315]:
        ax = int(cx + 10 * math.cos(math.radians(ang)))
        ay = int(cy + 10 * math.sin(math.radians(ang)))
        d.line([cx, cy, ax, ay], fill=CHITINBLK, width=2)
        ell(d, ax, ay, 2, 2, CHITINHI)

    sv(im, "l5_web_turret.png")


# ─── L5: ARACHNOS FÜHRER (100×80) — ARTHROPOD BOSS ──────────────────────────
def l5_arachnos_fuhrer():
    W, H = 100, 80
    im = C(W, H); d = D(im)

    # 8 massive legs (4 per side) — they're long and reach to edges
    leg_data_left = [
        ((40,35),(18,18),(0, 8)),
        ((38,42),(16,30),(0,35)),
        ((38,50),(16,55),(0,62)),
        ((40,58),(20,68),(2,78)),
    ]
    leg_data_right = [
        ((60,35),(82,18),(100, 8)),
        ((62,42),(84,30),(100,35)),
        ((62,50),(84,55),(100,62)),
        ((60,58),(80,68),(98, 78)),
    ]
    for (ax,ay),(mx,my),(ex,ey) in leg_data_left + leg_data_right:
        d.line([ax,ay, mx,my], fill=CHITINBLK, width=5)
        d.line([mx,my, ex,ey], fill=CHITINBLK, width=4)
        # Joint knob
        ell(d, mx, my, 4, 4, CHITINHI)
        # Spine / claw tip
        ell(d, ex, ey, 3, 3, (45,30,55,255))

    # Abdomen (large rear body)
    ell(d, 65, 52, 28, 24, CHITINBLK)
    ell(d, 65, 50, 28, 24, CHITINHI)
    # Abdomen web pattern (geometric, not swastika)
    for ang in range(0,360,60):
        eax = int(65 + 22 * math.cos(math.radians(ang)))
        eay = int(50 + 20 * math.sin(math.radians(ang)))
        d.line([65, 50, eax, eay], fill=(45,35,60,200), width=1)
    for r in [8,15,22]:
        ell(d, 65, 50, r, int(r*0.85), T, ol=(45,35,60,200))
    # Red hourglass marking
    d.polygon([(60,44),(70,44),(67,50),(70,56),(60,56),(63,50)], fill=CHITIN_RED)

    # Cephalothorax (massive head section)
    ell(d, 40, 40, 30, 26, CHITINBLK)
    ell(d, 40, 38, 30, 26, CHITINHI)
    # Carapace groove lines
    d.arc([15, 16, 65, 60], start=210, end=330, fill=(35,28,48,255), width=2)
    d.arc([20, 20, 60, 56], start=210, end=330, fill=(35,28,48,255), width=1)

    # Eyes — 8 glowing red eyes in two arcs
    for i, ex in enumerate([20, 26, 32, 38]):
        ell(d, ex, 32, 4, 4, (90, 0, 0, 255))
        ell(d, ex, 32, 2, 2, GLOW_RED)
        dot(d, ex, 31, (255,180,180,255))
    for i, ex in enumerate([24, 30, 36, 42]):
        ell(d, ex, 40, 3, 3, (90, 0, 0, 255))
        ell(d, ex, 40, 1, 1, GLOW_RED)

    # Mandibles — enormous
    d.line([28, 58, 12, 76], fill=CHITINBLK, width=6)
    d.line([52, 58, 68, 76], fill=CHITINBLK, width=6)
    ell(d, 10, 76, 6, 5, (70,0,0,255))   # fang tips
    ell(d, 70, 76, 6, 5, (70,0,0,255))
    # Pedipalps
    d.line([22, 38,  5, 22], fill=CHITINHI, width=3)
    d.line([58, 38, 72, 22], fill=CHITINHI, width=3)
    ell(d,  4, 21, 4, 4, CHITINHI)
    ell(d, 73, 21, 4, 4, CHITINHI)
    # Web spray nozzle (abdomen tip)
    ell(d, 88, 64, 4, 4, (80,70,100,255))
    d.line([89, 62, 96, 56], fill=WEB_TAN, width=1)

    sv(im, "l5_arachnos_fuhrer.png")


# ─── L5: IMPRISONED ALIEN (22×38) ────────────────────────────────────────────
def l5_imprisoned():
    W, H = 22, 38
    im = C(W, H); d = D(im)

    # Web cocoon (wraps most of body)
    ell(d, 11, 22, 10, 16, (185, 175, 148, 255))
    # Web strands
    d.line([ 2, 14, 20, 30], fill=WEB_TAN, width=1)
    d.line([ 2, 22, 20, 22], fill=WEB_TAN, width=1)
    d.line([ 4, 36, 18,  8], fill=WEB_TAN, width=1)
    d.line([ 1, 30, 21, 14], fill=WEB_TAN, width=1)
    # Alien head peeking out top
    ell(d, 11,  9, 8, 8, PALE_GREEN)
    # Three eyes — wide and terrified
    eye(d,  7,  8, 2, GREEN_EYE)
    eye(d, 11,  7, 2, GREEN_EYE)
    eye(d, 15,  8, 2, GREEN_EYE)
    # Screaming mouth
    ell(d, 11, 13, 3, 3, BK)
    # One arm struggling free
    box(d, 18, 16, 4, 8, PALE_GREEN)
    ell(d, 20, 24, 3, 3, PALE_GREEN)
    # Tear / drop
    ell(d, 8, 6, 1, 2, (100,180,255,200))

    sv(im, "l5_imprisoned.png")


# ─── SECRET: SETTLER ENFORCER (28×44) ────────────────────────────────────────
def ls_enforcer():
    W, H = 28, 44
    im = C(W, H); d = D(im)

    skin = (145, 175, 120, 255)  # olive-green alien skin

    # Boots
    box(d,  7, 39, 6, 5, (40,35,20,255))
    box(d, 15, 39, 6, 5, (40,35,20,255))
    # Legs
    box(d,  8, 28, 5, 13, OLIVE)
    box(d, 15, 28, 5, 13, OLIVE)
    # Tactical vest / body armour
    box(d,  7, 15, 14, 15, OLIVE)
    box(d,  5, 17,  3, 10, (80,90,50,255))  # side plate L
    box(d, 20, 17,  3, 10, (80,90,50,255))  # side plate R
    # Pouches
    box(d,  9, 24, 4, 4, (65,75,40,255))
    box(d, 15, 24, 4, 4, (65,75,40,255))
    # Arms
    box(d,  2, 16, 5, 13, skin)
    box(d, 21, 16, 5, 13, skin)
    # Rifle (held right side)
    box(d, 22, 10, 3, 20, DARK_STEEL)
    box(d, 20,  8, 3, 5,  (75,58,35,255))
    box(d, 24, 16, 3, 8,  DARK_STEEL)   # mag
    # Head
    ell(d, 14, 10, 8, 8, skin)
    # Tactical helmet
    box(d,  6,  6, 16, 7, OLIVE)
    ell(d, 14,  6, 8, 5, (75,85,45,255))
    box(d,  5,  9, 18, 3, OLIVE)  # brim
    # Visor
    box(d,  8, 10, 12, 3, (50,180,200,150))
    # Eyes behind visor
    eye(d, 10, 11, 2, BLUE_EYE)
    eye(d, 18, 11, 2, BLUE_EYE)

    sv(im, "ls_enforcer.png")


# ─── SECRET: PROPAGANDA DRONE (30×18) ────────────────────────────────────────
def ls_prop_drone():
    W, H = 30, 18
    im = C(W, H); d = D(im)

    # Main disc body
    ell(d, 15, 9, 13, 6, DARK_STEEL)
    ell(d, 15, 8, 13, 6, STEEL)
    # Camera lens (under)
    ell(d, 15, 11, 4, 3, BK)
    ell(d, 15, 11, 2, 2, (50,100,200,255))
    dot(d, 15, 11, (200,220,255,255))
    # Antenna
    d.line([15, 2, 15, -1], fill=STEEL, width=1)
    ell(d, 15, 1, 2, 2, (200,80,80,255))
    # Speaker grille
    for sx in [7, 10, 13, 16, 19, 22]:
        d.line([sx, 7, sx, 5], fill=(80,85,98,255), width=1)
    # Hover fans (both sides)
    ell(d,  3, 9, 4, 3, (60,65,78,255))
    ell(d, 27, 9, 4, 3, (60,65,78,255))
    d.line([0, 9, 6, 9], fill=STEEL, width=1)
    d.line([24, 9, 30, 9], fill=STEEL, width=1)

    sv(im, "ls_prop_drone.png")


# ─── SECRET: DISPLACED RESIDENT (24×40) ──────────────────────────────────────
def ls_civilian():
    W, H = 24, 40
    im = C(W, H); d = D(im)

    # Feet
    box(d,  4, 36, 6, 4, (88, 70, 45, 255))
    box(d, 13, 36, 6, 4, (88, 70, 45, 255))
    # Legs
    box(d,  5, 26, 5, 12, (155, 138, 108, 255))
    box(d, 13, 26, 5, 12, (155, 138, 108, 255))
    # Long robe / thawb
    box(d,  4, 14, 16, 14, (225, 218, 200, 255))
    # Robe fold
    d.line([12, 14, 12, 28], fill=(205,198,180,255), width=1)
    # Arms
    box(d,  1, 15, 4, 12, DISPLACED)
    box(d, 19, 15, 4, 12, DISPLACED)
    # Hands holding child/bundle
    ell(d,  2, 28, 3, 3, DISPLACED)
    ell(d, 22, 28, 3, 3, DISPLACED)
    # Small child form at chest
    ell(d, 12, 24, 5, 5, (200,185,158,255))
    eye(d, 10, 23, 1, (80,150,80,255))
    eye(d, 14, 23, 1, (80,150,80,255))
    # Head
    ell(d, 12, 10, 7, 8, DISPLACED)
    # Keffiyeh / head covering
    box(d,  5,  4, 14, 8, (245, 242, 235, 255))
    ell(d, 12,  4, 8, 6, (245, 242, 235, 255))
    # Band
    box(d,  5,  9, 14, 3, (50, 50, 50, 220))
    # Eyes — sorrowful
    eye(d,  9, 10, 2, (100,160,100,255))
    eye(d, 15, 10, 2, (100,160,100,255))
    # Downward mouth
    d.arc([8, 14, 16, 18], start=0, end=180, fill=BK, width=1)

    sv(im, "ls_civilian.png")


# ─── PICKUPS (all 20×20) ─────────────────────────────────────────────────────
def pickup_health():
    im = C(20, 20); d = D(im)
    ell(d, 10, 10, 9, 9, (180, 20, 20, 255))
    box(d,  7,  6, 6, 8, (240,240,240,255))  # vertical bar
    box(d,  4,  9, 12, 3, (240,240,240,255)) # horizontal bar
    sv(im, "pickup_health.png")

def pickup_ammo():
    im = C(20, 20); d = D(im)
    box(d, 2, 2, 16, 16, (55, 50, 30, 255), ol=(30,25,10,255))
    for bx in range(5, 15, 4):
        ell(d, bx, 10, 2, 5, (220, 195, 30, 255))
    d.line([2,6,18,6], fill=(80,75,45,255), width=1)
    d.line([2,14,18,14], fill=(80,75,45,255), width=1)
    sv(im, "pickup_ammo.png")

def pickup_shield():
    im = C(20, 20); d = D(im)
    d.polygon([(10,1),(18,5),(18,13),(10,19),(2,13),(2,5)], fill=(30,80,200,255))
    d.polygon([(10,3),(16,6),(16,12),(10,17),(4,12),(4,6)],  fill=(60,130,255,255))
    d.polygon([(10,5),(14,8),(10,15),(6,8)], fill=(130,185,255,180))
    sv(im, "pickup_shield.png")

def pickup_emp():
    im = C(20, 20); d = D(im)
    ell(d, 10, 10, 9, 9, (20,160,175,255))
    # Lightning bolt
    d.polygon([(12,2),(8,10),(11,10),(8,18),(14,9),(10,9)], fill=(255,255,100,255))
    sv(im, "pickup_emp.png")

def pickup_webcutter():
    im = C(20, 20); d = D(im)
    ell(d, 10, 10, 9, 9, (50,170,60,255))
    # Scissors blades
    d.line([ 4, 4, 16, 16], fill=(220,220,220,255), width=3)
    d.line([ 4,16, 16, 4],  fill=(220,220,220,255), width=3)
    ell(d, 10, 10, 3, 3, (50,170,60,255))
    # Rings
    ell(d,  5,  5, 3, 3, T, ol=(220,220,220,255))
    ell(d, 15,  5, 3, 3, T, ol=(220,220,220,255))
    ell(d,  5, 15, 3, 3, T, ol=(220,220,220,255))
    ell(d, 15, 15, 3, 3, T, ol=(220,220,220,255))
    sv(im, "pickup_webcutter.png")


# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating WILD EMPIRE sprites...\n")

    print("[ Player ]")
    player()

    print("\n[ Level 1 — Planet Roma-7 ]")
    l1_grunt()
    l1_captain()
    l1_tank()
    l1_civilian()

    print("\n[ Level 2 — Planet Iberia-4 ]")
    l2_falangist()
    l2_inquisitor()
    l2_condor_drone()
    l2_civilian()

    print("\n[ Level 3 — Planet MAGA-3  (orange blobs) ]")
    l3_orange_blob()
    l3_fire_agent()
    l3_blob_overlord()
    l3_detained()

    print("\n[ Level 4 — Planet Yamato-9 ]")
    l4_imperial()
    l4_mech_samurai()
    l4_kamikaze_drone()
    l4_civilian()

    print("\n[ Level 5 — Planet Arachnos  (arthropods) ]")
    l5_spider_grunt()
    l5_spider_commander()
    l5_web_turret()
    l5_arachnos_fuhrer()
    l5_imprisoned()

    print("\n[ Secret Level — Planet Bibi ]")
    ls_enforcer()
    ls_prop_drone()
    ls_civilian()

    print("\n[ Pickups ]")
    pickup_health()
    pickup_ammo()
    pickup_shield()
    pickup_emp()
    pickup_webcutter()

    print(f"\nDone — {len(os.listdir(OUT))} sprites written to {OUT}/")
