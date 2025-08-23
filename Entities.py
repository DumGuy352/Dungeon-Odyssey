import pygame
import math

# Colors
WHITE = (255,255,255)
YELLOW = (200,200,0)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32,32))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4
        self.hp = 100
        self.name = "Player1"

    # Movement
    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_a] and not keys[pygame.K_d]:
            dx -= 1
        elif keys[pygame.K_d] and not keys[pygame.K_a]:
            dx += 1
        else:
            dx = 0
        if keys[pygame.K_w] and not keys[pygame.K_s]:
            dy -= 1
        elif keys[pygame.K_s] and not keys[pygame.K_w]:
            dy += 1
        else:
            dy = 0

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)
        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)

    def clamp_to_game_area(self, width, height):
        self.rect.left = max(self.rect.left, 0)
        self.rect.top = max(self.rect.top, 0)
        self.rect.right = min(self.rect.right, width)
        self.rect.bottom = min(self.rect.bottom, height)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color, hp, speed, chase_range=200):
        super().__init__()
        self.image = pygame.Surface((28,28))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = hp
        self.speed = speed
        self.knockback = [0, 0]
        self.chase_range = chase_range

    def ai(self, player):
        # Simple chase AI
        if self.knockback != [0, 0]:
            self.rect.x += int(self.knockback[0])
            self.rect.y += int(self.knockback[1])
            self.knockback[0] *= 0.7
            self.knockback[1] *= 0.7
            if abs(self.knockback[0]) < 0.5: 
                self.knockback[0] = 0
            if abs(self.knockback[1]) < 0.5: 
                self.knockback[1] = 0
            return 
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if 0 < dist <= self.chase_range:  # Use chase_range attribute
            dx, dy = dx/dist, dy/dist
            self.rect.x += int(dx * self.speed)
            self.rect.y += int(dy * self.speed)

    def clamp_to_game_area(self, width, height):
        self.rect.left = max(self.rect.left, 0)
        self.rect.top = max(self.rect.top, 0)
        self.rect.right = min(self.rect.right, width)
        self.rect.bottom = min(self.rect.bottom, height)

class RangedEnemy(Enemy):
    def __init__(self, x, y, hp, speed, attack_range=250, shoot_cooldown=60):
        super().__init__(x, y, (0,200,0), hp, speed)
        self.attack_range = attack_range
        self.shoot_cooldown = shoot_cooldown
        self.last_shot = 0

    def ai(self, player, projectiles, frame_count):
        if self.knockback != [0, 0]:
            self.rect.x += int(self.knockback[0])
            self.rect.y += int(self.knockback[1])
            self.knockback[0] *= 0.7
            self.knockback[1] *= 0.7
            if abs(self.knockback[0]) < 0.5: self.knockback[0] = 0
            if abs(self.knockback[1]) < 0.5: self.knockback[1] = 0
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        # If not in range, chase
        if dist > self.attack_range:
            super().ai(player)
        else:
            # In range: shoot at intervals
            if frame_count - self.last_shot > self.shoot_cooldown:
                if dist != 0:
                    dx_norm, dy_norm = dx/dist, dy/dist
                    proj = Projectile(self.rect.centerx, self.rect.centery, dx_norm, dy_norm)
                    projectiles.add(proj)
                    self.last_shot = frame_count

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW, 50, 2)
        self.image = pygame.Surface((48,48))
        self.image.fill(YELLOW)
        self.mode = "normal"  # "normal" or "projectile"
        self.mode_timer = 0
        self.shoot_cooldown = 60
        self.last_shot = 0

    def ai(self, player, projectiles=None, frame_count=0):
        # Switch mode every 3 seconds (180 frames at 60 FPS)
        if not hasattr(self, "mode"):
            self.mode = "normal"
            self.mode_timer = 0
            self.shoot_cooldown = 60
            self.last_shot = 0

        if frame_count - self.mode_timer > 180:
            self.mode = "projectile" if self.mode == "normal" else "normal"
            self.mode_timer = frame_count

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if hasattr(self, "knockback") and self.knockback != [0, 0]:
            self.rect.x += int(self.knockback[0])
            self.rect.y += int(self.knockback[1])
            self.knockback[0] *= 0.7
            self.knockback[1] *= 0.7
            if abs(self.knockback[0]) < 0.5: self.knockback[0] = 0
            if abs(self.knockback[1]) < 0.5: self.knockback[1] = 0
            return

        if self.mode == "normal":
            # Chase player
            if dist > 0:
                dx, dy = dx/dist, dy/dist
                self.rect.x += int(dx * self.speed)
                self.rect.y += int(dy * self.speed)
        elif self.mode == "projectile" and projectiles is not None:
            # Shoot at player if cooldown allows
            if frame_count - self.last_shot > self.shoot_cooldown:
                if dist != 0:
                    dx_norm, dy_norm = dx/dist, dy/dist
                    proj = Projectile(self.rect.centerx, self.rect.centery, dx_norm, dy_norm, color=YELLOW, speed=7)
                    projectiles.add(proj)
                    self.last_shot = frame_count


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, color=(0,255,0), speed=6):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self):
        self.rect.x += int(self.dx * self.speed)
        self.rect.y += int(self.dy * self.speed)
        # Remove if out of bounds
        if (self.rect.right < 0 or self.rect.left > 800 or
            self.rect.bottom < 0 or self.rect.top > 600):
            self.kill()