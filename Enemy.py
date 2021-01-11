import math
import random

import pygame
import utils
import settings
from projectile import MultiProjectile, Powerup
powerup_ims = {"heart": utils.load_image("assets/images/heart.png", 32),
               "speed": utils.load_image("assets/images/fast_projectiles.png", 34),
               "firerate": utils.load_image("assets/images/faster_fire.png", 34),
               "count": utils.load_image("assets/images/more_rockets.png", 34),
               "spread": utils.load_image("assets/images/less_spread.png", 34),
               "invuln": utils.load_image("assets/images/more_invuln.png", 34)}

class BaseEnemy(pygame.sprite.DirtySprite):
    """
    A base class for a generic enemy object.
    Has all enemy-related features, just differs in movement.
    """

    def __init__(self, x: int, y: int, image: pygame.Surface,
                 fire_delay: float, speed: float, health: int, score: int,
                 p_speed: float, p_im: pygame.Surface, p_count: int,
                 p_fire_angle: float = 270, p_spread: float = 15):
        pygame.sprite.DirtySprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.fire_delay = fire_delay
        self.speed = speed
        self.health = health
        self.score = score

        # Projectile arguments
        self.p_speed = p_speed
        self.p_im = p_im
        self.p_count = p_count
        self.p_fire_angle = p_fire_angle
        self.p_spread = p_spread

        self.fire_timer = 0
        self.hit_timer = 9999999
        self.invuln_delay = 200

    def update(self, player_projectile_group: pygame.sprite.Group,
               enemy_projectile_group: pygame.sprite.Group,
               player_group: pygame.sprite.Group,
               powerup_group: pygame.sprite.Group):
        self.fire_timer += settings.DELTA_T * 1000
        self.hit_timer += settings.DELTA_T * 1000
        self.update_movement()
        self.update_fire(enemy_projectile_group)

        hit_count = len(pygame.sprite.spritecollide(self, player_projectile_group, False))
        if self.hit_timer > self.invuln_delay and pygame.sprite.spritecollide(self, player_projectile_group, True):
            self.health -= hit_count
            self.hit_timer = 0
            if self.health <= 0:
                self.kill()
                settings.sounds["effects"]["explode"].play()
                for p in player_group:
                    p.score += self.score
                    powerups = ["heart", "speed", "firerate", "count", "spread", "invuln"]
                    powerup = random.choices(powerups, weights=[settings.LIVES - p.health, 5 - p.p_speed_count,
                                                                5 - p.p_firerate_count, 5 - p.p_count_count,
                                                                5 - p.p_spread_count, 5 - p.invuln_count])
                    if random.randint(0,0) % 3 == 0:
                        powerup_group.add(Powerup(100, self.rect.x, self.rect.y, pygame.transform.rotate(powerup_ims[powerup[0]], 90), powerup[0]))

        if self.is_hit():
            self.image = self.image.copy()
            self.image.set_alpha(127)
        else:
            self.image = self.image.copy()
            self.image.set_alpha(255)

        if pygame.sprite.spritecollide(self, player_group, False):
            self.dirty = 1

        if self.rect.right <= settings.LEFT_BOUND or self.rect.x >= settings.RIGHT_BOUND or \
                self.rect.bottom <= settings.LOWER_BOUND or self.rect.y >= settings.UPPER_BOUND:
            self.dirty = 0

    def update_movement(self):
        pass

    def update_fire(self, projectile_group: pygame.sprite.Group):
        if self.fire_timer > self.fire_delay:
            projectile_group.add(
                MultiProjectile(self.p_speed, self.rect.x + self.rect.w / 2, self.rect.bottom, [self.p_im], 0,
                                self.p_count, self.p_fire_angle, self.p_spread).projectiles_group)
            self.fire_timer = 0
        self.dirty = 1

    def is_hit(self):
        return self.hit_timer <= self.invuln_delay


class StaticEnemy(BaseEnemy):
    """
    Moves to a fixed location (end_x, end_y), then doesn't move at all
    """

    def __init__(self, x: int, y: int, end_x: int, end_y: int, image: pygame.Surface,
                 fire_delay: float, speed: float, health: int, score: int,
                 p_speed: float, p_im: pygame.Surface, p_count: int, p_fire_angle: float = 270, p_spread: float = 15):
        super().__init__(x, y, image, fire_delay, speed, health, score, p_speed, p_im, p_count, p_fire_angle, p_spread)
        self.end_x = end_x
        self.end_y = end_y
        self.dx = self.end_x - self.x
        self.dy = self.end_y - self.y
        self.angle = math.atan2(self.dy, self.dx)
        self.angle = math.degrees(self.angle)
        if self.angle < 0:
            self.angle += 360

    def update_movement(self):
        if (abs(self.dx) ** 2 + abs(self.dy) ** 2) ** 0.5 < self.speed * settings.DELTA_T:
            return
        else:
            self.x += math.cos(math.radians(self.angle)) * self.speed * settings.DELTA_T
            self.y += math.sin(math.radians(self.angle)) * self.speed * settings.DELTA_T
            self.dx = self.end_x - self.x
            self.dy = self.end_y - self.y
            self.rect.topleft = self.x, self.y
            self.dirty = 1


class MovingEnemy(StaticEnemy):
    """
    Moves to a fixed location (end_x, end_y), then moves somewhat randomly
    """

    def __init__(self, x: int, y: int, end_x: int, end_y: int, image: pygame.Surface,
                 fire_delay: float, speed: float, health: int, movement_delay: float, score,
                 p_speed: float, p_im: pygame.Surface, p_count: int, p_fire_angle: float = 270, p_spread: float = 15):
        super().__init__(x, y, end_x, end_y, image, fire_delay, speed, health, score,
                         p_speed, p_im, p_count, p_fire_angle, p_spread)
        # delay in milliseconds until the next random movement (moves linearly during the delay)
        self.movement_delay = movement_delay
        self.done_moving = False
        self.movement_timer = 0

    def update(self, player_projectile_group: pygame.sprite.Group,
               enemy_projectile_group: pygame.sprite.Group,
               player_group: pygame.sprite.Group,
               powerup_group: pygame.sprite.Group):
        self.movement_timer += settings.DELTA_T * 1000
        super().update(player_projectile_group, enemy_projectile_group, player_group, powerup_group)

    def update_movement(self):
        if (abs(self.dx) ** 2 + abs(self.dy) ** 2) ** 0.5 < self.speed * settings.DELTA_T and not self.done_moving:
            self.done_moving = True
            self.angle = random.randint(0, 359)

        self.x += math.cos(math.radians(self.angle)) * self.speed * settings.DELTA_T
        self.y += math.sin(math.radians(self.angle)) * self.speed * settings.DELTA_T
        self.rect.topleft = self.x, self.y

        if not self.done_moving:
            self.dx = self.end_x - self.x
            self.dy = self.end_y - self.y

        elif self.done_moving:
            if self.movement_timer > self.movement_delay or \
                    self.rect.x <= settings.LEFT_BOUND or \
                    self.rect.right >= settings.RIGHT_BOUND or \
                    self.rect.bottom >= settings.UPPER_BOUND or \
                    self.rect.y <= settings.LOWER_BOUND:
                # print(self.rect)
                if self.movement_timer >= 2 * settings.DELTA_T:
                    # flip direction of movement, then add a random angle offset
                    self.angle = (self.angle + 180) % 360 + random.randint(-75, 75)
                self.movement_timer = 0

        self.dirty = 1
