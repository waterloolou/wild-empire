# ============================================================
# WILD EMPIRE — Level Configuration Dictionaries
# ============================================================

_CIV_SPRITE = "assets/sprites/l1_civilian.png"
_CIV_COLOR  = (220, 200, 160)

LEVEL_CONFIGS = {

    # ----------------------------------------------------------
    # LEVEL 1 — Planet Korrith-7
    # Standard alien world — medium gravity, iron platforms
    # ----------------------------------------------------------
    1: {
        "name": "Planet Korrith-7",
        "subtitle": "The Iron Decree",
        "theme_color": (180, 60, 20),
        "bg_color": (18, 10, 28),
        "platform_color": (55, 48, 68),     # dark purple-gray iron

        "gravity": 0.55,
        "terminal_velocity": 14,
        "friction": 0.82,

        "asteroids": 6,
        "rescue_all_civilians": True,
        "destroy_all_fascists": True,

        "enemies": {
            "korrith_trooper": {
                "display_name": "Korrith Trooper",
                "health": 40, "damage": 6, "speed": 2.2,
                "detection_range": 220, "attack_range": 35,
                "score_value": 1, "drop_chance": 0.15,
                "ai_type": "patrol",
                "sprite": "assets/sprites/l1_blackshirt_grunt.png",
                "hitbox": (28, 42), "color_placeholder": (60, 60, 160),
                "crater_radius": 0,
            },
            "korrith_commander": {
                "display_name": "Korrith Commander",
                "health": 90, "damage": 11, "speed": 1.8,
                "detection_range": 280, "attack_range": 45,
                "score_value": 1, "drop_chance": 0.40,
                "ai_type": "chase",
                "sprite": "assets/sprites/l1_blackshirt_captain.png",
                "hitbox": (32, 48), "color_placeholder": (30, 30, 120),
                "crater_radius": 0,
            },
            "korrith_crawler": {
                "display_name": "Korrith Siege Crawler",
                "health": 200, "damage": 35, "speed": 0.9,
                "detection_range": 420, "attack_range": 290,
                "score_value": 1, "drop_chance": 0.60,
                "ai_type": "patrol",
                "sprite": "assets/sprites/l1_tank.png",
                "hitbox": (64, 40), "color_placeholder": (80, 80, 40),
                "can_jump": False, "crater_radius": 28,
            },
        },
        "civilians": {
            "enslaved_worker": {
                "display_name": "Enslaved Worker",
                "health": 90, "speed": 1.2,
                "sprite": _CIV_SPRITE, "hitbox": (24, 40),
                "color_placeholder": _CIV_COLOR,
            },
        },
        "spawn": {
            "korrith_trooper": 4,
            "korrith_commander": 2,
            "korrith_crawler": 1,
            "enslaved_worker": 5,
        },
        "pickups": ["health_pack", "ammo_crate"],
        "background": "assets/backgrounds/l1_roma7_bg.png",
        "tileset": "assets/backgrounds/l1_tiles.png",
    },

    # ----------------------------------------------------------
    # LEVEL 2 — Planet Vael-4
    # Light atmosphere — low gravity, long floaty jumps, sandy rock
    # ----------------------------------------------------------
    2: {
        "name": "Planet Vael-4",
        "subtitle": "Wings of the Vael",
        "theme_color": (180, 140, 20),
        "bg_color": (8, 6, 2),
        "platform_color": (105, 88, 48),    # sandstone tan

        "gravity": 0.30,
        "terminal_velocity": 10,
        "friction": 0.72,

        "asteroids": 4,
        "meteor_rate": 6000,         # meteor every 6 s — barren exposed atmosphere
        "rescue_all_civilians": True,
        "destroy_all_fascists": True,

        "enemies": {
            "vael_soldier": {
                "display_name": "Vael Soldier",
                "health": 50, "damage": 7, "speed": 2.0,
                "detection_range": 240, "attack_range": 40,
                "score_value": 1, "drop_chance": 0.15,
                "ai_type": "patrol",
                "sprite": "assets/sprites/l2_falangist.png",
                "hitbox": (28, 44), "color_placeholder": (140, 100, 40),
                "crater_radius": 0,
            },
            "vael_hunter": {
                "display_name": "Vael Hunter",
                "health": 120, "damage": 12, "speed": 1.6,
                "detection_range": 300, "attack_range": 55,
                "score_value": 1, "drop_chance": 0.45,
                "ai_type": "chase",
                "sprite": "assets/sprites/l2_inquisitor.png",
                "hitbox": (30, 50), "color_placeholder": (100, 60, 20),
                "crater_radius": 0,
            },
            "vael_interceptor": {
                "display_name": "Vael Interceptor",
                "health": 60, "damage": 9, "speed": 3.5,
                "detection_range": 600, "attack_range": 300,
                "score_value": 1, "drop_chance": 0.30,
                "ai_type": "sniper", "flies": True,
                "sprite": "assets/sprites/l2_condor_drone.png",
                "hitbox": (40, 20), "color_placeholder": (80, 80, 80),
                "crater_radius": 0,
            },
        },
        "civilians": {
            "captive_worker": {
                "display_name": "Captive Worker",
                "health": 90, "speed": 1.3,
                "sprite": _CIV_SPRITE, "hitbox": (24, 40),
                "color_placeholder": _CIV_COLOR,
            },
        },
        "spawn": {
            "vael_soldier": 4,
            "vael_hunter": 2,
            "vael_interceptor": 2,
            "captive_worker": 5,
        },
        "pickups": ["health_pack", "ammo_crate", "shield_boost"],
        "background": "assets/backgrounds/l2_iberia4_bg.png",
        "tileset": "assets/backgrounds/l2_tiles.png",
    },

    # ----------------------------------------------------------
    # LEVEL 3 — Planet Glorbax-3
    # Dense heavy world — high gravity, short hops, orange mud platforms
    # ----------------------------------------------------------
    3: {
        "name": "Planet Glorbax-3",
        "subtitle": "The Bloated Empire",
        "theme_color": (255, 100, 0),
        "bg_color": (22, 8, 2),
        "platform_color": (88, 48, 14),     # dark orange-brown mud

        "gravity": 0.68,
        "terminal_velocity": 18,
        "friction": 0.60,

        "asteroids": 8,
        "lava_floor": True,          # ground is burning lava
        "lava_damage": 4,            # hp per 200 ms while standing on it
        "meteor_rate": 4000,         # heavy meteor bombardment
        "rescue_all_civilians": True,
        "destroy_all_fascists": True,

        "enemies": {
            "glorbax_drone": {
                "display_name": "Glorbax Drone",
                "health": 70, "damage": 8, "speed": 1.2,
                "detection_range": 180, "attack_range": 50,
                "score_value": 1, "drop_chance": 0.45,
                "ai_type": "patrol",
                "sprite": "assets/sprites/l3_orange_blob.png",
                "hitbox": (52, 52), "color_placeholder": (255, 120, 0),
                "crater_radius": 0,
            },
            "glorbax_stalker": {
                "display_name": "Glorbax Stalker",
                "health": 55, "damage": 10, "speed": 3.0,
                "detection_range": 320, "attack_range": 60,
                "score_value": 1, "drop_chance": 0.55,
                "ai_type": "chase",
                "sprite": "assets/sprites/l3_fire_agent.png",
                "hitbox": (26, 44), "color_placeholder": (200, 30, 0),
                "crater_radius": 0,
            },
            "glorbax_supreme": {
                "display_name": "Glorbax Supreme",
                "health": 350, "damage": 40, "speed": 0.7,
                "detection_range": 500, "attack_range": 250,
                "score_value": 1, "drop_chance": 0.80,
                "ai_type": "chase", "is_boss": True,
                "sprite": "assets/sprites/l3_blob_overlord.png",
                "hitbox": (80, 80), "color_placeholder": (255, 80, 0),
                "crater_radius": 42,
            },
        },
        "civilians": {
            "detained_worker": {
                "display_name": "Detained Worker",
                "health": 90, "speed": 1.0,
                "sprite": _CIV_SPRITE, "hitbox": (24, 40),
                "color_placeholder": _CIV_COLOR,
            },
        },
        "spawn": {
            "glorbax_drone": 5,
            "glorbax_stalker": 3,
            "glorbax_supreme": 1,
            "detained_worker": 6,
        },
        "pickups": ["health_pack", "ammo_crate", "emp_grenade"],
        "background": "assets/backgrounds/l3_maga3_bg.png",
        "tileset": "assets/backgrounds/l3_tiles.png",
    },

    # ----------------------------------------------------------
    # LEVEL 4 — Planet Nexar-9
    # Near-zero gravity station — floaty, slow falls, metallic blue
    # ----------------------------------------------------------
    4: {
        "name": "Planet Nexar-9",
        "subtitle": "The Steel Hegemony",
        "theme_color": (200, 20, 20),
        "bg_color": (4, 6, 20),
        "platform_color": (30, 50, 90),     # metallic steel blue

        "gravity": 0.20,
        "terminal_velocity": 8,
        "friction": 0.90,

        "asteroids": 10,
        "meteor_rate": 5000,         # space debris field — slow-falling meteors
        "rescue_all_civilians": True,
        "destroy_all_fascists": True,

        "enemies": {
            "nexar_grunt": {
                "display_name": "Nexar Grunt",
                "health": 60, "damage": 8, "speed": 2.4,
                "detection_range": 260, "attack_range": 45,
                "score_value": 1, "drop_chance": 0.15,
                "ai_type": "patrol",
                "sprite": "assets/sprites/l4_imperial_soldier.png",
                "hitbox": (26, 44), "color_placeholder": (60, 80, 30),
                "crater_radius": 0,
            },
            "nexar_warframe": {
                "display_name": "Nexar Warframe",
                "health": 150, "damage": 30, "speed": 2.8,
                "detection_range": 380, "attack_range": 220,
                "score_value": 1, "drop_chance": 0.50,
                "ai_type": "chase", "can_jump": False,
                "sprite": "assets/sprites/l4_mech_samurai.png",
                "hitbox": (36, 54), "color_placeholder": (100, 20, 20),
                "crater_radius": 18,
            },
            "nexar_seeker": {
                "display_name": "Nexar Seeker",
                "health": 30, "damage": 50, "speed": 4.5,
                "detection_range": 350, "attack_range": 20,
                "score_value": 1, "drop_chance": 0.05,
                "ai_type": "chase", "flies": True,
                "explodes_on_death": True, "explosion_radius": 80,
                "sprite": "assets/sprites/l4_kamikaze_drone.png",
                "hitbox": (22, 22), "color_placeholder": (200, 150, 0),
                "crater_radius": 22,
            },
        },
        "civilians": {
            "subjugated_worker": {
                "display_name": "Subjugated Worker",
                "health": 90, "speed": 1.1,
                "sprite": _CIV_SPRITE, "hitbox": (24, 40),
                "color_placeholder": _CIV_COLOR,
            },
        },
        "spawn": {
            "nexar_grunt": 5,
            "nexar_warframe": 2,
            "nexar_seeker": 3,
            "subjugated_worker": 5,
        },
        "pickups": ["health_pack", "ammo_crate", "shield_boost", "emp_grenade"],
        "background": "assets/backgrounds/l4_yamato9_bg.png",
        "tileset": "assets/backgrounds/l4_tiles.png",
    },

    # ----------------------------------------------------------
    # LEVEL 5 — Planet Arachnos  ★ FINAL ★
    # Web world — medium gravity, sticky, chitinous purple platforms
    # ----------------------------------------------------------
    5: {
        "name": "Planet Arachnos",
        "subtitle": "The Brood Dominion",
        "theme_color": (20, 20, 20),
        "bg_color": (4, 2, 10),
        "platform_color": (38, 18, 55),     # dark chitinous purple

        "gravity": 0.42,
        "terminal_velocity": 14,
        "friction": 0.76,

        "asteroids": 12,
        "lava_floor": True,          # hellish web world — lava ground
        "lava_damage": 3,
        "rescue_all_civilians": True,
        "destroy_all_fascists": True,

        "enemies": {
            "spider_grunt": {
                "display_name": "Spider Grunt",
                "health": 55, "damage": 7, "speed": 2.8,
                "detection_range": 220, "attack_range": 35,
                "score_value": 1, "drop_chance": 0.10,
                "ai_type": "swarm", "wall_climb": True,
                "sprite": "assets/sprites/l5_spider_grunt.png",
                "hitbox": (34, 26), "color_placeholder": (40, 40, 40),
                "crater_radius": 0,
            },
            "spider_commander": {
                "display_name": "Spider Commander",
                "health": 180, "damage": 14, "speed": 2.0,
                "detection_range": 360, "attack_range": 70,
                "score_value": 1, "drop_chance": 0.55,
                "ai_type": "chase", "wall_climb": True,
                "spawns_minions": True, "spawn_cooldown": 8000,
                "sprite": "assets/sprites/l5_spider_commander.png",
                "hitbox": (44, 36), "color_placeholder": (80, 0, 0),
                "crater_radius": 16,
            },
            "web_turret": {
                "display_name": "Web Turret",
                "health": 100, "damage": 10, "speed": 0,
                "detection_range": 600, "attack_range": 400,
                "score_value": 1, "drop_chance": 0.30,
                "ai_type": "sniper", "is_stationary": True,
                "fires_web": True, "can_jump": False,
                "sprite": "assets/sprites/l5_web_turret.png",
                "hitbox": (30, 30), "color_placeholder": (60, 60, 0),
                "crater_radius": 0,
            },
            "arachnos_prime": {
                "display_name": "The Grand Arachnid Prime",
                "health": 800, "damage": 60, "speed": 1.5,
                "detection_range": 999, "attack_range": 300,
                "score_value": 1, "drop_chance": 1.0,
                "ai_type": "chase", "is_boss": True,
                "wall_climb": True, "spawns_minions": True,
                "spawn_cooldown": 5000, "phase_count": 3,
                "sprite": "assets/sprites/l5_arachnos_fuhrer.png",
                "hitbox": (100, 80), "color_placeholder": (10, 0, 10),
                "crater_radius": 55,
            },
        },
        "civilians": {
            "imprisoned_worker": {
                "display_name": "Imprisoned Worker",
                "health": 90, "speed": 0.8,
                "sprite": _CIV_SPRITE, "hitbox": (24, 40),
                "color_placeholder": _CIV_COLOR,
            },
        },
        "spawn": {
            "spider_grunt": 6,
            "spider_commander": 2,
            "web_turret": 2,
            "arachnos_prime": 1,
            "imprisoned_worker": 6,
        },
        "pickups": ["health_pack", "ammo_crate", "shield_boost", "emp_grenade", "web_cutter"],
        "background": "assets/backgrounds/l5_arachnos_bg.png",
        "tileset": "assets/backgrounds/l5_tiles.png",
    },

    # ----------------------------------------------------------
    # SECRET LEVEL — Planet Zarak
    # ----------------------------------------------------------
    "secret": {
        "name": "Planet Zarak",
        "subtitle": "The Outer Enclave",
        "theme_color": (0, 100, 50),
        "bg_color": (6, 10, 4),
        "platform_color": (42, 62, 22),     # military olive

        "gravity": 0.55,
        "terminal_velocity": 13,
        "friction": 0.80,

        "asteroids": 5,
        "rescue_all_civilians": True,
        "destroy_all_fascists": True,

        "enemies": {
            "zarak_enforcer": {
                "display_name": "Zarak Enforcer",
                "health": 65, "damage": 15, "speed": 2.1,
                "detection_range": 240, "attack_range": 50,
                "score_value": 1, "drop_chance": 0.20,
                "ai_type": "patrol",
                "sprite": "assets/sprites/ls_enforcer.png",
                "hitbox": (28, 44), "color_placeholder": (100, 120, 60),
                "crater_radius": 0,
            },
            "zarak_drone": {
                "display_name": "Zarak Broadcast Drone",
                "health": 40, "damage": 8, "speed": 3.0,
                "detection_range": 600, "attack_range": 400,
                "score_value": 1, "drop_chance": 0.10,
                "ai_type": "sniper", "flies": True, "stuns_on_hit": True,
                "sprite": "assets/sprites/ls_prop_drone.png",
                "hitbox": (30, 18), "color_placeholder": (150, 150, 150),
                "crater_radius": 0,
            },
        },
        "civilians": {
            "displaced_worker": {
                "display_name": "Displaced Worker",
                "health": 90, "speed": 1.0,
                "sprite": _CIV_SPRITE, "hitbox": (24, 40),
                "color_placeholder": _CIV_COLOR,
            },
        },
        "spawn": {
            "zarak_enforcer": 5,
            "zarak_drone": 2,
            "displaced_worker": 6,
        },
        "pickups": ["health_pack", "ammo_crate", "shield_boost"],
        "background": "assets/backgrounds/ls_bibi_bg.png",
        "tileset": "assets/backgrounds/ls_tiles.png",
    },
}

SCORING = {
    "civilian_death_penalty": -5,
    "fascist_kill": 1,
    "liberation_bonus": 50,
    "level_clear_bonus": 200,
    "no_civilian_deaths_bonus": 100,
}

PICKUPS = {
    "health_pack":  {"heal": 30,  "sprite": "assets/sprites/pickup_health.png",    "color": (0, 220, 80)},
    "ammo_crate":   {"ammo": 30,  "sprite": "assets/sprites/pickup_ammo.png",       "color": (220, 180, 0)},
    "shield_boost": {"shield": 50, "duration": 8000, "sprite": "assets/sprites/pickup_shield.png", "color": (80, 160, 255)},
    "emp_grenade":  {"ammo": 15,  "sprite": "assets/sprites/pickup_emp.png",        "color": (0, 200, 200)},
    "web_cutter":   {"count": 3,  "sprite": "assets/sprites/pickup_webcutter.png",  "color": (220, 220, 80)},
}
