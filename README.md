# WILD EMPIRE — Sewer Society Liberation Campaign
### PyGame Platformer Starter — Full Architecture

---

## Setup

```bash
pip install pygame
cd wild_empire
python main.py
```

---

## Controls

| Key | Action |
|-----|--------|
| A / D  or  ← → | Move |
| W / SPACE / ↑ | Jump |
| Left Click | Shoot |
| R | Reload |
| G | Throw grenade (splash damage) |
| E | Rescue nearby civilian |
| P | Pause |
| ESC | Back to menu |

---

## Project Structure

```
wild_empire/
├── main.py                   ← game loop, rendering, input
├── levels/
│   └── level_config.py       ← ALL level data dictionaries
├── entities/
│   └── entities.py           ← Player, Enemy, Civilian, Bullet, Pickup
└── assets/
    ├── sprites/              ← DROP YOUR ART HERE (PNG, alpha OK)
    │   ├── player.png
    │   ├── l1_blackshirt_grunt.png
    │   ├── l1_blackshirt_captain.png
    │   ├── l1_tank.png
    │   ├── l1_civilian.png
    │   ├── l2_falangist.png
    │   ├── l2_inquisitor.png
    │   ├── l2_condor_drone.png
    │   ├── l2_civilian.png
    │   ├── l3_orange_blob.png
    │   ├── l3_fire_agent.png
    │   ├── l3_blob_overlord.png
    │   ├── l3_detained.png
    │   ├── l4_imperial_soldier.png
    │   ├── l4_mech_samurai.png
    │   ├── l4_kamikaze_drone.png
    │   ├── l4_civilian.png
    │   ├── l5_spider_grunt.png
    │   ├── l5_spider_commander.png
    │   ├── l5_web_turret.png
    │   ├── l5_arachnos_fuhrer.png
    │   ├── l5_imprisoned.png
    │   ├── ls_enforcer.png
    │   ├── ls_prop_drone.png
    │   ├── ls_civilian.png
    │   └── pickup_*.png      ← health, ammo, shield, emp, webcutter
    └── backgrounds/
        ├── l1_roma7_bg.png   ← full level scrolling background (4000×800)
        ├── l1_tiles.png      ← tileset (currently drawn as solid rects)
        ├── l2_iberia4_bg.png
        ├── l3_maga3_bg.png
        ├── l4_yamato9_bg.png
        ├── l5_arachnos_bg.png
        └── ls_bibi_bg.png
```

Sprites that are **missing** auto-render as colored placeholder rectangles
with an X — so the game runs immediately even without any art.

---

## Customizing a Level

All game data lives in `levels/level_config.py` as a plain Python dict.

```python
LEVEL_CONFIGS[3]["enemies"]["orange_blob"]["health"] = 100   # make blobs tankier
LEVEL_CONFIGS[3]["gravity"] = 0.8                            # heavier world
LEVEL_CONFIGS[3]["spawn"]["orange_blob"] = 20                # more blobs
```

Each enemy entry has:

| Key | Effect |
|-----|--------|
| `health` | hit points |
| `damage` | damage per hit / bullet |
| `speed` | movement speed (px/frame) |
| `detection_range` | px radius before enemy alerts |
| `attack_range` | px radius for melee / snipe trigger |
| `ai_type` | `patrol` `chase` `sniper` `swarm` |
| `flies` | ignores gravity |
| `wall_climb` | (L5) can traverse walls |
| `explodes_on_death` | AOE on kill |
| `spawns_minions` | periodically spawns grunts |
| `is_boss` | larger health bar, special logic hook |
| `hitbox` | `(w, h)` tuple — also sets sprite scale |
| `sprite` | path to PNG |
| `color_placeholder` | fallback color if PNG missing |

---

## Scoring (SCORING dict in level_config.py)

| Event | Points |
|-------|--------|
| Fascist kill | +1 |
| Civilian/worker death | −5 |
| Civilian rescued | +50 |
| Level clear | +200 |
| No civilian deaths bonus | +100 |

---

## Adding Real Level Geometry

In `main.py`, find `buildPlatforms(levelId)` and replace the
placeholder `pygame.Rect` lists with your own level design.
You can also integrate **Tiled** maps (`.tmx`) via `pytmx`:

```bash
pip install pytmx
```

---

## Win Conditions

A level ends when **either**:
- All fascist enemies are eliminated, OR
- All civilians are rescued

Both are active simultaneously — the player chooses their strategy.

---

## Secret Level

The secret level (`"secret"` key in `LEVEL_CONFIGS`) unlocks automatically
after completing Level 5.

---

## TODO / Extension Hooks

- [ ] Animated sprite sheets (swap `loadSprite` for a sprite-sheet loader)
- [ ] Tiled map integration for real level geometry
- [ ] Web-slowing projectile (L5 turrets) — `bullet.webOnHit = True`
- [ ] Boss multi-phase logic (check `is_boss` + `phase_count` in enemy cfg)
- [ ] Sound effects (`pygame.mixer`)
- [ ] Main menu art / animated logo
- [ ] Save/load high scores
- [ ] Multiplayer co-op (second player on same keyboard)
