#!/usr/bin/env python3
"""
Generate synthesized 8-bit-style sound effects for WILD EMPIRE.
Run once from the game root:  python generate_sounds.py
Creates WAV files in assets/sounds/
No external libraries needed — uses only the Python standard library.
"""

import wave, math, os, random, array

RATE = 44100
OUT  = os.path.join("assets", "sounds")

# ──────────────────────────────────────────────────────────────
def save(filename, samples):
    os.makedirs(OUT, exist_ok=True)
    path  = os.path.join(OUT, filename)
    idata = array.array('h', [max(-32767, min(32767, int(s * 32767))) for s in samples])
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(idata.tobytes())
    print(f"  {filename}")

def normalize(samples, target=0.88):
    mx = max(abs(x) for x in samples) or 1.0
    if mx > target:
        k = target / mx
        return [x * k for x in samples]
    return list(samples)


# ──────────────────────────────────────────────────────────────
# SHOOT  — laser zap: swept sine 750→120 Hz in 0.14 s
# ──────────────────────────────────────────────────────────────
def make_shoot():
    n = int(RATE * 0.14)
    out, ph1, ph2 = [], 0.0, 0.0
    for i in range(n):
        t    = i / n
        f    = 750 - 630 * t
        ph1 += 2 * math.pi * f / RATE
        ph2 += 2 * math.pi * (f * 2) / RATE
        env  = math.exp(-t * 7) * 0.65
        s    = math.sin(ph1) * 0.7 + (1 if math.sin(ph2) > 0 else -1) * 0.3
        out.append(s * env)
    return out


# ──────────────────────────────────────────────────────────────
# ENEMY SHOOT  — deeper mechanical thup 400→80 Hz in 0.12 s
# ──────────────────────────────────────────────────────────────
def make_enemy_shoot():
    n   = int(RATE * 0.12)
    out, ph = [], 0.0
    rng = random.Random(7)
    for i in range(n):
        t    = i / n
        f    = 400 - 320 * t
        ph  += 2 * math.pi * max(20, f) / RATE
        env  = math.exp(-t * 10) * 0.55
        s    = math.sin(ph) * 0.6 + rng.uniform(-1, 1) * 0.25
        out.append(s * env)
    return out


# ──────────────────────────────────────────────────────────────
# MELEE  — meaty thud: noise burst + 70 Hz bass thump 0.13 s
# ──────────────────────────────────────────────────────────────
def make_melee():
    n   = int(RATE * 0.13)
    out, ph = [], 0.0
    rng = random.Random(42)
    for i in range(n):
        t    = i / n
        ph  += 2 * math.pi * 70 / RATE
        env  = math.exp(-t * 16) * 0.85
        s    = math.sin(ph) * 0.45 + rng.uniform(-1, 1) * 0.55
        out.append(s * env)
    return out


# ──────────────────────────────────────────────────────────────
# JUMP  — upward whoosh: 160→540 Hz in 0.11 s
# ──────────────────────────────────────────────────────────────
def make_jump():
    n = int(RATE * 0.11)
    out, ph = [], 0.0
    for i in range(n):
        t    = i / n
        f    = 160 + 380 * t
        ph  += 2 * math.pi * f / RATE
        env  = min(t / 0.05, 1.0) * max(0.0, 1.0 - (t - 0.05) / 0.06)
        out.append(math.sin(ph) * env * 0.42)
    return out


# ──────────────────────────────────────────────────────────────
# HURT  — electric jolt: buzz + white noise 0.17 s
# ──────────────────────────────────────────────────────────────
def make_hurt():
    n   = int(RATE * 0.17)
    out, ph = [], 0.0
    rng = random.Random(55)
    for i in range(n):
        t    = i / n
        ph  += 2 * math.pi * 220 / RATE
        env  = math.exp(-t * 7) * 0.8
        buzz = (1 if math.sin(ph) > 0 else -1) * 0.4
        nse  = rng.uniform(-1, 1) * 0.5
        out.append((buzz + nse) * env)
    return out


# ──────────────────────────────────────────────────────────────
# PLAYER DEATH  — descending wail with harmonics 1.0 s
# ──────────────────────────────────────────────────────────────
def make_player_death():
    n = int(RATE * 1.0)
    out = []
    ph1 = ph2 = ph3 = 0.0
    for i in range(n):
        t    = i / n
        f1   = 440 * math.exp(-t * 1.5)
        f2   = f1 * 0.5
        f3   = f1 * 1.5
        ph1 += 2 * math.pi * f1 / RATE
        ph2 += 2 * math.pi * f2 / RATE
        ph3 += 2 * math.pi * f3 / RATE
        att  = min(1.0, t / 0.04)
        dec  = max(0.0, 1.0 - (t - 0.1) * 1.1) if t > 0.1 else 1.0
        env  = att * dec * 0.75
        s    = math.sin(ph1) * 0.5 + math.sin(ph2) * 0.3 + math.sin(ph3) * 0.2
        out.append(s * env)
    return out


# ──────────────────────────────────────────────────────────────
# ENEMY DEATH  — pop + burst: noise + sweep 300→80 Hz 0.15 s
# ──────────────────────────────────────────────────────────────
def make_enemy_death():
    n   = int(RATE * 0.15)
    out, ph = [], 0.0
    rng = random.Random(13)
    for i in range(n):
        t    = i / n
        f    = 300 - 220 * t
        ph  += 2 * math.pi * f / RATE
        env  = math.exp(-t * 10) * 0.7
        s    = math.sin(ph) * 0.5 + rng.uniform(-1, 1) * 0.4
        out.append(s * env)
    return out


# ──────────────────────────────────────────────────────────────
# RESCUE  — ascending major arpeggio C5 E5 G5 C6
# ──────────────────────────────────────────────────────────────
def make_rescue():
    out = []
    for freq, dur in [(523, 0.09), (659, 0.09), (784, 0.09), (1047, 0.22)]:
        n  = int(RATE * dur)
        ph = 0.0
        for i in range(n):
            t   = i / n
            ph += 2 * math.pi * freq / RATE
            att = min(1.0, t / 0.03)
            dec = max(0.0, 1.0 - (t - 0.05) / max(0.01, dur - 0.05)) if t > 0.05 else 1.0
            out.append(math.sin(ph) * att * dec * 0.55)
    return out


# ──────────────────────────────────────────────────────────────
# CIV DEATH  — sad two-note descent A4 → E4
# ──────────────────────────────────────────────────────────────
def make_civ_death():
    out = []
    for freq, dur in [(440, 0.18), (330, 0.28)]:
        n  = int(RATE * dur)
        ph = 0.0
        for i in range(n):
            t   = i / n
            ph += 2 * math.pi * freq / RATE
            att = min(1.0, t / 0.02)
            dec = max(0.0, 1.0 - (t - 0.1) / max(0.01, dur - 0.1)) if t > 0.1 else 1.0
            out.append(math.sin(ph) * att * dec * 0.50)
    return out


# ──────────────────────────────────────────────────────────────
# PICKUP  — bright double ding G5 then C6
# ──────────────────────────────────────────────────────────────
def make_pickup():
    out = []
    for freq, dur in [(784, 0.09), (1047, 0.14)]:
        n  = int(RATE * dur)
        ph = 0.0
        for i in range(n):
            t   = i / n
            ph += 2 * math.pi * freq / RATE
            att = min(1.0, t / 0.01)
            dec = max(0.0, 1.0 - t / dur * 1.05)
            out.append(math.sin(ph) * att * dec * 0.52)
    return out


# ──────────────────────────────────────────────────────────────
# METEOR IMPACT  — deep boom: sweeping bass + noise 0.55 s
# ──────────────────────────────────────────────────────────────
def make_meteor():
    n   = int(RATE * 0.55)
    out = []
    ph1 = ph2 = 0.0
    rng = random.Random(99)
    for i in range(n):
        t    = i / n
        f1   = 80 * math.exp(-t * 2)
        f2   = f1 * 2
        ph1 += 2 * math.pi * max(5, f1) / RATE
        ph2 += 2 * math.pi * max(10, f2) / RATE
        att  = min(1.0, t / 0.01)
        env  = att * math.exp(-t * 5) * 0.9
        nse  = rng.uniform(-1, 1) * 0.35
        s    = math.sin(ph1) * 0.55 + math.sin(ph2) * 0.25 + nse
        out.append(s * env)
    return out


# ──────────────────────────────────────────────────────────────
# LEVEL COMPLETE  — fanfare C5 E5 G5 → C6 sustained
# ──────────────────────────────────────────────────────────────
def make_level_complete():
    out = []
    for freq, dur in [(523, 0.10), (659, 0.10), (784, 0.10), (0, 0.05), (1047, 0.45)]:
        n  = int(RATE * dur)
        ph = 0.0
        for i in range(n):
            t = i / n
            if freq == 0:
                out.append(0.0)
                continue
            ph += 2 * math.pi * freq / RATE
            att = min(1.0, t / 0.02)
            if dur > 0.2:
                dec = max(0.0, 1.0 - (t - 0.2) / max(0.01, dur - 0.2)) if t > 0.2 else 1.0
            else:
                dec = max(0.0, 1.0 - (t - 0.05) / max(0.01, dur - 0.05)) if t > 0.05 else 1.0
            out.append(math.sin(ph) * att * dec * 0.55)
    return out


# ──────────────────────────────────────────────────────────────
# GAME OVER  — defeat stinger A4 F#4 D4 → A3 sustained
# ──────────────────────────────────────────────────────────────
def make_game_over():
    out = []
    for freq, dur in [(440, 0.15), (370, 0.15), (294, 0.15), (220, 0.65)]:
        n   = int(RATE * dur)
        ph1 = ph2 = 0.0
        for i in range(n):
            t    = i / n
            ph1 += 2 * math.pi * freq / RATE
            ph2 += 2 * math.pi * (freq * 0.5) / RATE
            att  = min(1.0, t / 0.02)
            if dur > 0.2:
                dec = max(0.0, 1.0 - (t - 0.3) / max(0.01, dur - 0.3)) if t > 0.3 else 1.0
            else:
                dec = max(0.0, 1.0 - t / dur * 1.1)
            s = math.sin(ph1) * 0.45 + math.sin(ph2) * 0.25
            out.append(s * att * dec * 0.72)
    return out


# ──────────────────────────────────────────────────────────────
# LAVA AMBIENT  — looping rumble + bubble pops 3.0 s
# ──────────────────────────────────────────────────────────────
def make_lava():
    dur = 3.0
    n   = int(RATE * dur)
    out = [0.0] * n
    rng = random.Random(77)
    ph50 = ph80 = ph110 = 0.0
    for i in range(n):
        ph50  += 2 * math.pi * 50  / RATE
        ph80  += 2 * math.pi * 80  / RATE
        ph110 += 2 * math.pi * 110 / RATE
        rumble = (math.sin(ph50)  * 0.12 +
                  math.sin(ph80)  * 0.08 +
                  math.sin(ph110) * 0.05 +
                  rng.uniform(-1, 1) * 0.06)
        out[i] += rumble
    rng2 = random.Random(33)
    for _ in range(18):
        pos      = rng2.randint(0, n - 4000)
        pop_len  = rng2.randint(600, 2800)
        pop_freq = rng2.uniform(120, 380)
        ph_p     = 0.0
        for j in range(min(pop_len, n - pos)):
            t_p   = j / pop_len
            ph_p += 2 * math.pi * pop_freq * (1 - t_p * 0.4) / RATE
            env_p = math.exp(-t_p * 8) * rng2.uniform(0.15, 0.35)
            out[pos + j] += math.sin(ph_p) * env_p
    return normalize(out, 0.72)


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating sound effects for WILD EMPIRE ...")
    save("shoot.wav",          normalize(make_shoot()))
    save("enemy_shoot.wav",    normalize(make_enemy_shoot()))
    save("melee.wav",          normalize(make_melee()))
    save("jump.wav",           normalize(make_jump()))
    save("hurt.wav",           normalize(make_hurt()))
    save("player_death.wav",   normalize(make_player_death()))
    save("enemy_death.wav",    normalize(make_enemy_death()))
    save("rescue.wav",         normalize(make_rescue()))
    save("civ_death.wav",      normalize(make_civ_death()))
    save("pickup.wav",         normalize(make_pickup()))
    save("meteor.wav",         normalize(make_meteor()))
    save("level_complete.wav", normalize(make_level_complete()))
    save("game_over.wav",      normalize(make_game_over()))
    save("lava.wav",           make_lava())
    print("Done! All sounds saved to assets/sounds/")
