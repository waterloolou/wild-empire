# ============================================================
# WILD EMPIRE — Entity Classes
# Player, Enemy, Civilian — all use PyGame Rects for hitboxes
# ============================================================

import pygame
import os
import math

# --------------- Sprite loader helper -----------------------
def loadSprite(path, fallbackColor, size):
    """
    Tries to load a sprite from disk.
    If missing, returns a colored placeholder surface.
    DROP YOUR ART in assets/sprites/ and it will auto-load.
    """
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    # Placeholder: solid color rectangle with an 'X'
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((*fallbackColor, 200))
    pygame.draw.line(surf, (255, 255, 255), (0, 0), size, 2)
    pygame.draw.line(surf, (255, 255, 255), (size[0], 0), (0, size[1]), 2)
    return surf


# ============================================================
# BASE ENTITY
# ============================================================
class Entity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.velX = 0.0
        self.velY = 0.0
        self.onGround = False
        self.alive = True
        self.facingRight = True
        self.sprite = None          # set by subclass
        self.spriteMirror = None    # cached flipped version
        self._prevBottom = y + height
        self._hurtFlash  = 0        # frames of red tint on damage

    def applyGravity(self, gravity, terminalVel):
        if not self.onGround:
            self.velY = min(self.velY + gravity, terminalVel)

    def move(self, platforms):
        """Move with gravity + platform collision."""
        self._prevBottom = self.rect.bottom
        self.rect.x += int(self.velX)
        self._resolveHorizontal(platforms)
        self.rect.y += int(self.velY)
        self._resolveVertical(platforms)

    def _resolveHorizontal(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat) and self._prevBottom <= plat.top:
                if self.velX > 0:
                    self.rect.right = plat.left
                elif self.velX < 0:
                    self.rect.left = plat.right
                self.velX = 0

    def _resolveVertical(self, platforms):
        self.onGround = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.velY >= 0:
                # Only land if the entity was at or above the platform top last frame.
                # This prevents corner-teleports when jumping up alongside a platform.
                if self._prevBottom <= plat.top:
                    self.rect.bottom = plat.top
                    self.onGround = True
                    self.velY = 0

    def draw(self, surface, camOffset):
        drawX = self.rect.x - camOffset[0]
        drawY = self.rect.y - camOffset[1]
        if self.sprite:
            img = self.sprite if self.facingRight else self.spriteMirror
            surface.blit(img, (drawX, drawY))
        else:
            pygame.draw.rect(surface, (200, 50, 200),
                             (drawX, drawY, self.rect.width, self.rect.height))
        # Hurt flash — red tint overlay
        if self._hurtFlash > 0:
            self._hurtFlash -= 1
            alpha = int(180 * self._hurtFlash / 8)
            hs = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            hs.fill((255, 40, 40, alpha))
            surface.blit(hs, (drawX, drawY))

    def setSprite(self, path, fallbackColor):
        size = (self.rect.width, self.rect.height)
        self.sprite = loadSprite(path, fallbackColor, size)
        self.spriteMirror = pygame.transform.flip(self.sprite, True, False)


# ============================================================
# PLAYER — Sewer Society Operative
# ============================================================
class Player(Entity):
    """
    Controls:
        A / D  or  ← →  : move
        W / Space / ↑    : jump
        Left Click       : shoot
        R                : reload
        E                : rescue civilian
    """

    SPRITE_PATH = "assets/sprites/player.png"
    SPRITE_FALLBACK = (0, 180, 80)

    MAX_HEALTH     = 100
    MOVE_SPEED     = 3.8
    JUMP_FORCE     = -12.0
    MELEE_COOLDOWN = 700
    MELEE_DAMAGE   = 20
    MELEE_RANGE    = 58
    SKILL_SHIELD_COOLDOWN = 5000

    GUN_STATS = {
        "regular": {"cooldown": 700,  "max_ammo": 30, "reload": 2500,
                    "ammo_cost": 1,   "damage": 20,   "bullets": 1,
                    "spread": 0.0,    "knockback": 0, "label": "GUN"},
        "shotgun": {"cooldown": 1400, "max_ammo": 30, "reload": 3000,
                    "ammo_cost": 3,   "damage": 8,    "bullets": 5,
                    "spread": 0.30,   "knockback": 5, "label": "SHOTGUN"},
        "rpg":     {"cooldown": 0,    "max_ammo": 1,  "reload": 10000,
                    "ammo_cost": 1,   "damage": 80,   "bullets": 1,
                    "spread": 0.0,    "knockback": 0, "label": "RPG",
                    "explodes": True, "explode_radius": 100},
    }

    def __init__(self, x, y):
        super().__init__(x, y, 28, 44)
        self.health = self.MAX_HEALTH
        self.score = 0
        self.civilianDeaths = 0
        self.reloading = False
        self.shieldActive = False
        self.shieldTimer = 0
        self.shieldDuration = 0
        self.webbed = False
        self.webbedTimer = 0
        self._shootTimer = 0
        self._reloadTimer = 0
        self._meleeTimer  = 0
        self._meleeFlash  = 0
        self._shootFlash  = 0   # frames of muzzle flash

        # Gun system — set via setGunType() before play
        self.gunType = "regular"
        stats = self.GUN_STATS["regular"]
        self.MAX_AMMO    = stats["max_ammo"]
        self.SHOOT_COOLDOWN = stats["cooldown"]
        self.RELOAD_TIME = stats["reload"]
        self.ammo        = self.MAX_AMMO

        # Skill shield (Q key) — separate from pickup shield
        self._skillShield = False
        self._skillShieldCooldownEnd = -self.SKILL_SHIELD_COOLDOWN  # ready at start

        self.setSprite(self.SPRITE_PATH, self.SPRITE_FALLBACK)

    def setGunType(self, gtype):
        self.gunType = gtype
        stats = self.GUN_STATS[gtype]
        self.MAX_AMMO       = stats["max_ammo"]
        self.SHOOT_COOLDOWN = stats["cooldown"]
        self.RELOAD_TIME    = stats["reload"]
        self.ammo           = self.MAX_AMMO

    # -------------------------------------------------------
    def handleInput(self, keys, mouseButtons, friction):
        speed = self.MOVE_SPEED * (0.4 if self.webbed else 1.0)

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velX = -speed
            self.facingRight = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velX = speed
            self.facingRight = True
        else:
            self.velX *= friction   # decelerate

        if (keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.onGround:
            self.velY = self.JUMP_FORCE

    def activateSkillShield(self, now):
        if not self._skillShield and now >= self._skillShieldCooldownEnd:
            self._skillShield = True

    def tryShoot(self, now, bullets):
        """Call each frame; returns True if a shot was fired."""
        stats = self.GUN_STATS[self.gunType]
        cost = stats["ammo_cost"]
        if self.ammo < cost or self.reloading:
            return False
        if now - self._shootTimer < stats["cooldown"]:
            return False

        speed = 14
        cx, cy = self.rect.centerx, self.rect.centery
        base_vx = speed if self.facingRight else -speed

        for i in range(stats["bullets"]):
            spread = stats["spread"]
            angle = 0.0
            if spread > 0:
                # Distribute spread evenly across bullet count
                half = (stats["bullets"] - 1) / 2.0
                angle = (i - half) * spread / max(1, stats["bullets"] - 1)
            vx = base_vx * math.cos(angle) - 0 * math.sin(angle)
            vy = abs(base_vx) * math.sin(angle)
            explodes = stats.get("explodes", False)
            er = stats.get("explode_radius", 0)
            bullets.append(Bullet(cx, cy, vx, vy,
                                  damage=stats["damage"], owner="player",
                                  color=(255, 255, 80),
                                  explodes=explodes, explode_radius=er))

        # Shotgun knockback
        if stats["knockback"] > 0:
            self.velX += (-stats["knockback"]) if self.facingRight else stats["knockback"]

        self.ammo -= cost
        self._shootTimer = now
        self._shootFlash = 4
        return True

    def startReload(self):
        if not self.reloading and self.ammo < self.MAX_AMMO:
            self.reloading = True
            self._reloadTimer = pygame.time.get_ticks()

    def updateTimers(self, now):
        if self.reloading and now - self._reloadTimer >= self.RELOAD_TIME:
            self.ammo = self.MAX_AMMO
            self.reloading = False
        if self.webbed and now - self.webbedTimer >= 3000:
            self.webbed = False
        if self.shieldActive and now - self.shieldTimer >= self.shieldDuration:
            self.shieldActive = False

    def takeDamage(self, amount):
        if self.shieldActive or self._skillShield:
            if self._skillShield:
                self._skillShield = False
                self._skillShieldCooldownEnd = pygame.time.get_ticks() + self.SKILL_SHIELD_COOLDOWN
            return
        self.health = max(0, self.health - amount)
        self._hurtFlash = 8
        if self.health <= 0:
            self.alive = False

    def tryMelee(self, now, enemies):
        if now - self._meleeTimer < self.MELEE_COOLDOWN:
            return False
        self._meleeTimer = now
        self._meleeFlash = 8
        # Hitbox: covers the player's own body + MELEE_RANGE in front, slightly taller.
        # This catches enemies that are standing on/overlapping the player.
        if self.facingRight:
            hbox = pygame.Rect(self.rect.left, self.rect.top - 8,
                               self.rect.width + self.MELEE_RANGE, self.rect.height + 16)
        else:
            hbox = pygame.Rect(self.rect.left - self.MELEE_RANGE, self.rect.top - 8,
                               self.rect.width + self.MELEE_RANGE, self.rect.height + 16)
        for e in enemies:
            if e.alive and hbox.colliderect(e.rect):
                e.takeDamage(self.MELEE_DAMAGE)
        return True

    def applyPickup(self, ptype, pdata):
        if ptype == "health_pack":
            self.health = min(self.MAX_HEALTH, self.health + pdata["heal"])
        elif ptype == "ammo_crate":
            self.ammo = min(self.MAX_AMMO, self.ammo + pdata["ammo"])
        elif ptype == "shield_boost":
            self.shieldActive = True
            self.shieldTimer = pygame.time.get_ticks()
            self.shieldDuration = pdata["duration"]
        elif ptype == "emp_grenade":
            self.ammo = min(self.MAX_AMMO, self.ammo + 15)

    def draw(self, surface, camOffset):
        super().draw(surface, camOffset)
        drawX = self.rect.x - camOffset[0]
        drawY = self.rect.y - camOffset[1]
        # Pickup shield glow (blue)
        if self.shieldActive:
            s = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (80, 160, 255, 90), s.get_rect())
            surface.blit(s, (drawX - 6, drawY - 6))
        # Skill shield glow (gold)
        if self._skillShield:
            s = pygame.Surface((self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (255, 210, 0, 110), s.get_rect())
            surface.blit(s, (drawX - 8, drawY - 8))
        # Shoot flash — muzzle burst
        if self._shootFlash > 0:
            self._shootFlash -= 1
            alpha = int(220 * self._shootFlash / 4)
            mx = drawX + self.rect.width if self.facingRight else drawX - 10
            my = drawY + self.rect.height // 2 - 5
            fs = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(fs, (255, 240, 80, alpha), (9, 9), 9)
            surface.blit(fs, (mx - 4, my - 4))
        # Melee flash — matches the full hitbox (body + range in front)
        if self._meleeFlash > 0:
            self._meleeFlash -= 1
            alpha = int(200 * self._meleeFlash / 8)
            fw = self.rect.width + self.MELEE_RANGE
            fx = drawX if self.facingRight else drawX - self.MELEE_RANGE
            ms = pygame.Surface((fw, self.rect.height + 16), pygame.SRCALPHA)
            ms.fill((255, 220, 60, alpha))
            surface.blit(ms, (fx, drawY - 8))


# ============================================================
# ENEMY
# ============================================================
class Enemy(Entity):

    def __init__(self, x, y, cfg):
        w, h = cfg["hitbox"]
        super().__init__(x, y, w, h)
        self.cfg = cfg
        self.health = cfg["health"]
        self.maxHealth = cfg["health"]
        self.damage = cfg["damage"]
        self.speed = cfg["speed"]
        self.detectionRange = cfg["detection_range"]
        self.attackRange = cfg["attack_range"]
        self.aiType = cfg["ai_type"]
        self.scoreValue = cfg["score_value"]
        self.flies = cfg.get("flies", False)
        self.wallClimb = cfg.get("wall_climb", False)
        self.explodesOnDeath = cfg.get("explodes_on_death", False)
        self.explosionRadius = cfg.get("explosion_radius", 0)
        self.isBoss = cfg.get("is_boss", False)
        self.canJump = cfg.get("can_jump", True)
        self.spawnsCooldown = cfg.get("spawn_cooldown", 9999999)
        self._lastSpawn = 0
        self._patrolDir = 1
        self._patrolTimer = 0
        self._attackTimer = 0
        self._shootTimer  = 0
        self._jumpTimer   = 0
        self._gravity     = 0.5
        self._platforms   = []
        self._shootFlash  = 0   # muzzle flash frames
        self._attackFlash = 0   # melee flash frames

        # ── SPRITE: swap in your art ────────────────────────
        self.setSprite(cfg["sprite"], cfg["color_placeholder"])

    # -------------------------------------------------------
    def update(self, player, now, gravity, terminalVel, platforms, bullets, allies=None):
        self._platforms = platforms
        self._gravity   = gravity
        target = self._pickTarget(player, allies or [])
        dist   = self._distTo(target)

        # Always active — no detection gating
        if self.aiType == "patrol":
            self._patrol(target, now)
            self._rangedFallback(target, now, bullets)
        elif self.aiType in ("chase", "swarm"):
            self._chaseTarget(target)
            self._tryJump(target, now)
            self._rangedFallback(target, now, bullets)
        elif self.aiType == "sniper":
            self._snipe(target, now, bullets)

        if not self.flies:
            self.applyGravity(gravity, terminalVel)
        self.move(platforms)

        # Melee attack on nearest target (long-range attacks require LOS)
        if dist <= self.attackRange and now - self._attackTimer > 1000:
            if self.attackRange <= 70 or self._hasLOS(target):
                target.takeDamage(self.damage)
                self._attackTimer = now
                self._attackFlash = 5

    def _pickTarget(self, player, allies):
        candidates = [player] + [a for a in allies if a.alive]
        return min(candidates, key=lambda t: self._distTo(t))

    def _distTo(self, entity):
        dx = entity.rect.centerx - self.rect.centerx
        dy = entity.rect.centery - self.rect.centery
        return (dx**2 + dy**2) ** 0.5

    def _chaseTarget(self, target):
        dx = target.rect.centerx - self.rect.centerx
        if abs(dx) > 4:
            dir_ = 1 if dx > 0 else -1
            self.velX = dir_ * self.speed
            self.facingRight = dir_ > 0

    def _tryJump(self, target, now):
        if not self.canJump:
            return
        if not self.onGround or now - self._jumpTimer < 1500:
            return
        if target.rect.centery >= self.rect.centery - 40:
            return  # target not above us

        g          = max(0.15, self._gravity)
        jump_force = 12.0
        frames_air = (2.0 * jump_force) / g
        max_h      = (jump_force * jump_force) / (2.0 * g)
        # Cap to one platform tier (102 px gap) so low-gravity levels don't skip tiers.
        vert_max   = min(max_h, 120.0)

        # Use the velX that patrol/chase already set this frame — it's the actual
        # horizontal speed we'll have during the jump.
        vx = self.velX
        if abs(vx) < 0.1:
            vx = self.speed if target.rect.centerx > self.rect.centerx else -self.speed

        land_x = self.rect.centerx + vx * frames_air
        feet   = self.rect.bottom

        for plat in self._platforms:
            vert = feet - plat.top
            if not (8 <= vert <= vert_max):
                continue
            # Landing point must sit comfortably inside the platform, not just near the edge.
            if plat.left + 10 <= land_x <= plat.right - 10:
                self.velY = -jump_force
                self._jumpTimer = now
                return

    def _rangedFallback(self, target, now, bullets):
        """Lob a shot upward when the target is on a higher platform and can't be reached by melee."""
        if now - self._shootTimer < 3500:
            return
        dy = target.rect.centery - self.rect.centery
        if dy > -90:     # target not meaningfully above
            return
        if not self._hasLOS(target):
            return
        dx = target.rect.centerx - self.rect.centerx
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        bullets.append(Bullet(self.rect.centerx, self.rect.centery,
                              dx / dist * 7, dy / dist * 7,
                              damage=max(5, self.damage // 3),
                              owner="enemy", color=(255, 140, 60),
                              max_range=380))
        self._shootTimer = now
        self._shootFlash = 4

    def _patrol(self, target, now):
        """Always move toward the target — slow when far, full speed when close."""
        dx = target.rect.centerx - self.rect.centerx
        if abs(dx) > 4:
            dir_ = 1 if dx > 0 else -1
            mult = 1.0 if self._distTo(target) < self.detectionRange else 0.45
            self.velX = dir_ * self.speed * mult
            self.facingRight = dir_ > 0
        self._tryJump(target, now)

    def _hasLOS(self, target, steps=12):
        """Sample the line to target; return False if a platform blocks it."""
        x1, y1 = self.rect.centerx, self.rect.centery
        x2, y2 = target.rect.centerx, target.rect.centery
        for i in range(1, steps):
            t  = i / steps
            px = int(x1 + t * (x2 - x1))
            py = int(y1 + t * (y2 - y1))
            for plat in self._platforms:
                if plat.collidepoint(px, py):
                    return False
        return True

    def _snipe(self, target, now, bullets):
        if now - self._shootTimer < 3000:
            return
        if not self._hasLOS(target):
            return                          # wall in the way — wait for clear shot
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        b = Bullet(self.rect.centerx, self.rect.centery,
                   dx / dist * 10, dy / dist * 10,
                   damage=self.damage, owner="enemy", color=(255, 60, 60),
                   max_range=900)
        bullets.append(b)
        self._shootTimer = now
        self._shootFlash = 4

    def takeDamage(self, amount):
        self.health -= amount
        self._hurtFlash = 8
        if self.health <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface, camOffset):
        super().draw(surface, camOffset)
        drawX = self.rect.x - camOffset[0]
        drawY = self.rect.y - camOffset[1]
        # Health bar
        barW = self.rect.width
        barH = 5
        pct = max(0, self.health / self.maxHealth)
        pygame.draw.rect(surface, (180, 0, 0), (drawX, drawY - 8, barW, barH))
        pygame.draw.rect(surface, (0, 220, 0), (drawX, drawY - 8, int(barW * pct), barH))
        # Shoot flash — yellow muzzle burst
        if self._shootFlash > 0:
            self._shootFlash -= 1
            alpha = int(220 * self._shootFlash / 4)
            mx = drawX + self.rect.width if self.facingRight else drawX - 12
            my = drawY + self.rect.height // 2
            fs = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(fs, (255, 230, 60, alpha), (8, 8), 8)
            surface.blit(fs, (mx - 4, my - 8))
        # Attack flash — orange burst on melee
        if self._attackFlash > 0:
            self._attackFlash -= 1
            alpha = int(180 * self._attackFlash / 5)
            af = pygame.Surface((self.rect.width + 16, self.rect.height), pygame.SRCALPHA)
            af.fill((255, 100, 0, alpha))
            surface.blit(af, (drawX - 8, drawY))


# ============================================================
# CIVILIAN — oppressed worker / prisoner
# ============================================================
class Civilian(Entity):

    RESCUE_RANGE    = 50
    FOLLOW_DIST     = 60
    FOLLOW_SPEED    = 3.2
    ATTACK_RANGE    = 260
    ATTACK_DAMAGE   = 14
    ATTACK_COOLDOWN = 1800
    PROJECTILE_SPD  = 9
    PROJECTILE_COL  = (80, 220, 120)

    def __init__(self, x, y, cfg):
        w, h = cfg["hitbox"]
        super().__init__(x, y, w, h)
        self.cfg = cfg
        self.health = cfg["health"]
        self.rescued = False
        self.guards   = []   # Enemy refs — must all be dead before rescue
        self._atkTimer = 0
        self._minePhase = 0  # animation counter for pickaxe swing

        # ── SPRITE: swap in your art ────────────────────────
        self.setSprite(cfg["sprite"], cfg["color_placeholder"])

    # -------------------------------------------------------
    def update(self, player, gravity, terminalVel, platforms, enemies,
               now=0, bullets=None):
        if self.rescued:
            self._followPlayer(player)
            if bullets is not None and now:
                self._tryAttack(enemies, now, bullets)
            self.applyGravity(gravity, terminalVel)
            self.move(platforms)
            return

        # Un-rescued: stand still and mine
        self.velX = 0
        self._minePhase = (self._minePhase + 4) % 360
        self.applyGravity(gravity, terminalVel)
        self.move(platforms)

    # -------------------------------------------------------
    def _followPlayer(self, player):
        dx = player.rect.centerx - self.rect.centerx
        if abs(dx) > self.FOLLOW_DIST:
            dir_ = 1 if dx > 0 else -1
            self.velX = dir_ * self.FOLLOW_SPEED
            self.facingRight = dir_ > 0
        else:
            self.velX *= 0.7
        # Mirror the player's jump so allies climb platforms together
        if player.velY < -6 and self.onGround:
            self.velY = -12.0

    def _tryAttack(self, enemies, now, bullets):
        if now - self._atkTimer < self.ATTACK_COOLDOWN:
            return
        target = self._nearestInRange(enemies, self.ATTACK_RANGE)
        if target is None:
            return
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        vx = dx / dist * self.PROJECTILE_SPD
        vy = dy / dist * self.PROJECTILE_SPD
        bullets.append(Bullet(self.rect.centerx, self.rect.centery,
                               vx, vy,
                               damage=self.ATTACK_DAMAGE,
                               owner="player",          # same team as player
                               color=self.PROJECTILE_COL))
        self._atkTimer = now
        self.facingRight = dx > 0

    def _nearestInRange(self, enemies, max_dist):
        best, best_d = None, max_dist
        for e in enemies:
            if not e.alive:
                continue
            d = self._distTo(e)
            if d < best_d:
                best, best_d = e, d
        return best

    # -------------------------------------------------------
    def _distTo(self, other):
        dx = other.rect.centerx - self.rect.centerx
        dy = other.rect.centery - self.rect.centery
        return (dx**2 + dy**2) ** 0.5

    def _nearestEnemy(self, enemies):
        if not enemies:
            return None
        return min((e for e in enemies if e.alive), key=lambda e: self._distTo(e), default=None)

    def takeDamage(self, amount):
        self.health -= amount
        self._hurtFlash = 8
        if self.health <= 0:
            self.alive = False

    def draw(self, surface, camOffset):
        super().draw(surface, camOffset)
        cx   = self.rect.centerx - camOffset[0]
        topY = self.rect.top     - camOffset[1]
        midY = self.rect.centery - camOffset[1]
        font = pygame.font.SysFont("monospace", 11)

        if not self.rescued:
            # Pickaxe mining animation
            swing = math.sin(self._minePhase * math.pi / 180)  # -1..1
            side  = 1 if self.facingRight else -1
            hx, hy = cx + side * 7, midY + 4          # hand position
            angle  = math.radians(swing * 45)          # ±45° swing
            dx = int(math.cos(angle) * 16 * side)
            dy = int(math.sin(angle) * 16)
            tx, ty = hx + dx, hy + dy                  # tip of handle
            pygame.draw.line(surface, (139, 90, 43), (hx, hy), (tx, ty), 2)
            # Pickaxe head — perpendicular cross at tip
            px, py = int(-dy * 0.35), int(dx * 0.35)
            pygame.draw.line(surface, (170, 170, 195),
                             (tx - px, ty - py), (tx + px * 2, ty + py * 2), 3)

            # Guard warning
            alive_guards = sum(1 for g in self.guards if g.alive)
            if alive_guards > 0:
                warn = font.render(f"! {alive_guards} guards", True, (255, 120, 0))
                surface.blit(warn, (cx - warn.get_width() // 2, topY - 30))
                label = font.render("[E] Rescue", True, (100, 140, 100))
            else:
                label = font.render("[E] Rescue", True, (0, 255, 120))
            surface.blit(label, (cx - label.get_width() // 2, topY - 18))
        else:
            label = font.render("ALLY", True, (80, 220, 120))
            surface.blit(label, (cx - label.get_width() // 2, topY - 14))


# ============================================================
# BULLET
# ============================================================
class Bullet:
    RADIUS = 5

    def __init__(self, x, y, velX, velY, damage, owner, color=(255, 255, 80),
                 max_range=520, explodes=False, explode_radius=0):
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS,
                                self.RADIUS * 2, self.RADIUS * 2)
        self.velX = velX
        self.velY = velY
        self.damage = damage
        self.owner = owner      # "player" | "enemy"
        self.explodes = explodes
        self.explode_radius = explode_radius
        self.color = color
        self.alive = True
        self.max_range = max_range
        self._dist = 0.0

    def update(self, platforms):
        self.rect.x += int(self.velX)
        self.rect.y += int(self.velY)
        self._dist += (self.velX ** 2 + self.velY ** 2) ** 0.5
        if self._dist > self.max_range:
            self.alive = False
            return
        # Cull if it leaves the world entirely
        if self.rect.y < -120 or self.rect.y > 820 or self.rect.x < -120 or self.rect.x > 4120:
            self.alive = False
            return
        for plat in platforms:
            if self.rect.colliderect(plat):
                self.alive = False
                return

    def draw(self, surface, camOffset):
        pygame.draw.circle(surface, self.color,
                           (self.rect.centerx - camOffset[0],
                            self.rect.centery - camOffset[1]),
                           self.RADIUS)


# ============================================================
# PICKUP
# ============================================================
class Pickup:
    SIZE = 36

    def __init__(self, x, y, ptype, pdata):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.ptype = ptype
        self.pdata = pdata
        self.color = pdata["color"]
        self.alive = True
        self.sprite = loadSprite(pdata["sprite"], pdata["color"], (self.SIZE, self.SIZE))

    def draw(self, surface, camOffset):
        drawX = self.rect.x - camOffset[0]
        drawY = self.rect.y - camOffset[1]
        if self.sprite:
            surface.blit(self.sprite, (drawX, drawY))
        else:
            pygame.draw.rect(surface, self.color, (drawX, drawY, self.SIZE, self.SIZE))
