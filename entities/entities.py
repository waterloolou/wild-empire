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

    def applyGravity(self, gravity, terminalVel):
        if not self.onGround:
            self.velY = min(self.velY + gravity, terminalVel)

    def move(self, platforms):
        """Move with gravity + platform collision."""
        self.rect.x += int(self.velX)
        self._resolveHorizontal(platforms)
        self.rect.y += int(self.velY)
        self._resolveVertical(platforms)

    def _resolveHorizontal(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.velX > 0:
                    self.rect.right = plat.left
                elif self.velX < 0:
                    self.rect.left = plat.right
                self.velX = 0

    def _resolveVertical(self, platforms):
        self.onGround = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.velY > 0:
                    self.rect.bottom = plat.top
                    self.onGround = True
                elif self.velY < 0:
                    self.rect.top = plat.bottom
                self.velY = 0

    def draw(self, surface, camOffset):
        drawX = self.rect.x - camOffset[0]
        drawY = self.rect.y - camOffset[1]
        if self.sprite:
            img = self.sprite if self.facingRight else self.spriteMirror
            surface.blit(img, (drawX, drawY))
        else:
            # Raw fallback rectangle
            pygame.draw.rect(surface, (200, 50, 200),
                             (drawX, drawY, self.rect.width, self.rect.height))

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
    SHOOT_COOLDOWN = 2000   # 2 s between shots
    RELOAD_TIME    = 1500
    MAX_AMMO       = 30
    MELEE_COOLDOWN = 700
    MELEE_DAMAGE   = 20
    MELEE_RANGE    = 58

    def __init__(self, x, y):
        super().__init__(x, y, 28, 44)
        self.health = self.MAX_HEALTH
        self.ammo = self.MAX_AMMO
        self.score = 0
        self.civilianDeaths = 0
        self.reloading = False
        self.shieldActive = False
        self.shieldTimer = 0
        self.webbed = False
        self.webbedTimer = 0
        self._shootTimer = 0
        self._reloadTimer = 0
        self._meleeTimer  = 0
        self._meleeFlash  = 0   # frames remaining for melee visual

        # ── SPRITE: swap in your art file ──────────────────
        self.setSprite(self.SPRITE_PATH, self.SPRITE_FALLBACK)

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

    def tryShoot(self, now, bullets, mousePos, camOffset):
        """Call each frame; returns True if shot was fired."""
        if self.ammo <= 0 or self.reloading:
            return False
        if now - self._shootTimer < self.SHOOT_COOLDOWN:
            return False
        # Direction to mouse
        worldMX = mousePos[0] + camOffset[0]
        worldMY = mousePos[1] + camOffset[1]
        cx = self.rect.centerx
        cy = self.rect.centery
        dx = worldMX - cx
        dy = worldMY - cy
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        speed = 14
        b = Bullet(cx, cy, dx / dist * speed, dy / dist * speed,
                   damage=20, owner="player", color=(255, 255, 80))
        bullets.append(b)
        self.ammo -= 1
        self._shootTimer = now
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
        if self.shieldActive:
            return
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.alive = False

    def tryMelee(self, now, enemies):
        if now - self._meleeTimer < self.MELEE_COOLDOWN:
            return False
        self._meleeTimer = now
        self._meleeFlash = 8
        # Hitbox extends in front of the player
        if self.facingRight:
            hbox = pygame.Rect(self.rect.right, self.rect.top,
                               self.MELEE_RANGE, self.rect.height)
        else:
            hbox = pygame.Rect(self.rect.left - self.MELEE_RANGE, self.rect.top,
                               self.MELEE_RANGE, self.rect.height)
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
        # Shield glow
        if self.shieldActive:
            s = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (80, 160, 255, 80), s.get_rect())
            surface.blit(s, (drawX - 6, drawY - 6))
        # Melee flash
        if self._meleeFlash > 0:
            self._meleeFlash -= 1
            alpha = int(200 * self._meleeFlash / 8)
            fx = drawX + (self.rect.width if self.facingRight else -self.MELEE_RANGE)
            ms = pygame.Surface((self.MELEE_RANGE, self.rect.height), pygame.SRCALPHA)
            ms.fill((255, 220, 60, alpha))
            surface.blit(ms, (fx, drawY))


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
        self._jumpTimer   = 0
        self._platforms   = []   # cached each frame for sub-methods

        # ── SPRITE: swap in your art ────────────────────────
        self.setSprite(cfg["sprite"], cfg["color_placeholder"])

    # -------------------------------------------------------
    def update(self, player, now, gravity, terminalVel, platforms, bullets, allies=None):
        self._platforms = platforms
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

        # Melee attack on nearest target
        if dist <= self.attackRange and now - self._attackTimer > 1000:
            target.takeDamage(self.damage)
            self._attackTimer = now

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
        if not self.onGround or now - self._jumpTimer < 300:
            return
        if not target.onGround:
            return  # don't mirror player's jump
        if target.rect.centery >= self.rect.centery - 50:
            return  # target not above us
        if self._platformInJumpRange():
            self.velY = -12.0
            self._jumpTimer = now

    def _rangedFallback(self, target, now, bullets):
        """Lob a shot upward when the target is on a higher platform and can't be reached by melee."""
        if now - self._attackTimer < 2500:
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
                              owner="enemy", color=(255, 140, 60)))
        self._attackTimer = now

    def _platformInJumpRange(self):
        """True if there's a platform above that a single jump can reach."""
        MAX_H = 110   # conservative max jump height in pixels
        feet = self.rect.bottom
        for plat in self._platforms:
            vert = feet - plat.top
            if 15 <= vert <= MAX_H:
                if plat.right > self.rect.left - 60 and plat.left < self.rect.right + 60:
                    return True
        return False

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
        if now - self._attackTimer < 2000:
            return
        if not self._hasLOS(target):
            return                          # wall in the way — wait for clear shot
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        b = Bullet(self.rect.centerx, self.rect.centery,
                   dx / dist * 10, dy / dist * 10,
                   damage=self.damage, owner="enemy", color=(255, 60, 60))
        bullets.append(b)
        self._attackTimer = now

    def takeDamage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface, camOffset):
        super().draw(surface, camOffset)
        # Health bar
        drawX = self.rect.x - camOffset[0]
        drawY = self.rect.y - camOffset[1]
        barW = self.rect.width
        barH = 5
        pct = max(0, self.health / self.maxHealth)
        pygame.draw.rect(surface, (180, 0, 0), (drawX, drawY - 8, barW, barH))
        pygame.draw.rect(surface, (0, 220, 0), (drawX, drawY - 8, int(barW * pct), barH))


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

    def __init__(self, x, y, velX, velY, damage, owner, color=(255, 255, 80)):
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS,
                                self.RADIUS * 2, self.RADIUS * 2)
        self.velX = velX
        self.velY = velY
        self.damage = damage
        self.owner = owner      # "player" | "enemy"
        self.color = color
        self.alive = True

    def update(self, platforms):
        self.rect.x += int(self.velX)
        self.rect.y += int(self.velY)
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
    SIZE = 20

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
