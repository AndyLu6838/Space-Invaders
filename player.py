import pygame
import math
import settings
import utils
from projectile import MultiProjectile


class Player(pygame.sprite.DirtySprite):
    def __init__(self, speed: float, x: int, y: int, health: int, fire_delay: float, projectile_speed: float,
                 image: pygame.Surface, attack_imgs: list, anim_delay: int = 0,
                 projectile_count: int = 1, projectile_spread: float = 15):
        pygame.sprite.DirtySprite.__init__(self)
        self.speed = speed
        self.x = x
        self.y = y
        self.image = image
        self.attack_imgs = attack_imgs
        self.anim_delay = anim_delay
        self.fire_delay = fire_delay
        self.projectile_speed = projectile_speed
        self.projectile_count = projectile_count
        self.projectile_spread = projectile_spread
        self.timer = 0
        self.hit_timer = 9999
        self.bomb_timer = 10000
        self.invuln_delay = 200  # invincibility time after getting hit, in milliseconds
        self.health = health
        self.rect = pygame.Rect(x, y,
                                self.image.get_width(),
                                self.image.get_height())
        hitbox_width = self.rect.w/3
        hitbox_height = self.rect.h/3
        hitbox_x = utils.x_offset(self.rect, hitbox_width)
        hitbox_y = utils.y_offset(self.rect, hitbox_height)
        self.hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

        # game stats
        self.score = 0
        self.p_speed_count = 0
        self.p_spread_count = 0
        self.p_firerate_count = 0
        self.p_count_count = 0
        self.invuln_count = 0

        self.p_speed_incrs = [0, 50, 50, 50, 60, 75, 0]
        self.p_spread_incrs = [0, -1, -1, -2, -2, -3, 0]
        self.p_firerate_incrs = [0, -50, -50, -100, -200, -300, 0]
        self.p_count_incrs = [0, 1, 1, 1, 1, 2, 0]
        self.invuln_incrs = [0, 50, 50, 100, 100, 150, 0]


    def update(self, friendly_projectiles_group: pygame.sprite.Group,
               enemy_projectiles_group: pygame.sprite.Group,
               enemy_group: pygame.sprite.Group) -> bool:
        """
        returns True if still alive, False if health <= 0
        """
        self.timer += settings.DELTA_T * 1000
        self.hit_timer += settings.DELTA_T * 1000
        self.bomb_timer -= settings.DELTA_T * 1000
        self.update_keys(friendly_projectiles_group, enemy_projectiles_group)

        # test if collides with another group
        if self.collide(enemy_projectiles_group):
            self.health -= 1
            self.hit_timer = 0
            if self.health <= 0:
                return False

        hit_anim = 500

        if self.hit_timer <= hit_anim/4 or hit_anim/2 < self.hit_timer <= hit_anim*3/4:
            self.image.set_alpha(127)
            self.dirty = 1
        else:
            self.image.set_alpha(255)
            self.dirty = 1

        if pygame.sprite.spritecollide(self, enemy_group, False):
            self.dirty = 1

        if self.rect.right <= settings.LEFT_BOUND or self.rect.x >= settings.RIGHT_BOUND or \
            self.rect.bottom <= settings.LOWER_BOUND or self.rect.y >= settings.UPPER_BOUND:
            self.dirty = 0

        return True

    def collide(self, enemy_projectiles_group):
        # acts as pygame.sprite.spritecollide(self, enemy_projectiles_group, True)
        # but only tests for collision between player hitbox and projectiles

        collided = False

        for projectile in enemy_projectiles_group:
            if pygame.Rect.colliderect(self.hitbox, projectile.rect):
                self.dirty = 1
                if self.hit_timer > self.invuln_delay:
                    projectile.kill()
                    collided = True

            elif pygame.Rect.colliderect(self.rect, projectile.rect):
                self.dirty = 1

        return collided

    def update_keys(self, projectiles_group: pygame.sprite.Group, enemy_projectiles_group: pygame.sprite.Group):
        keys = pygame.key.get_pressed()
        # math.ceil to avoid integer truncation
        if keys[settings.keys["UP"]]:
            #print(self.rect.y)
            self.y -= (self.speed * settings.DELTA_T)
            #print(self.rect.y)
            self.dirty = 1

        if keys[settings.keys["DOWN"]]:
            self.y += (self.speed * settings.DELTA_T)
            self.dirty = 1

        if keys[settings.keys["LEFT"]]:
            self.x -= (self.speed * settings.DELTA_T)
            self.dirty = 1

        if keys[settings.keys["RIGHT"]]:
            self.x += (self.speed * settings.DELTA_T)
            self.dirty = 1

        if keys[settings.keys["BOMB"]]:
            if self.bomb_timer <= 0:
                enemy_projectiles_group.empty()
                self.bomb_timer = 10000

        self.x = max(self.x, settings.LEFT_BOUND)
        self.x = min(self.x+self.rect.w, settings.RIGHT_BOUND)-self.rect.w
        self.y = max(self.y, settings.LOWER_BOUND)
        self.y = min(self.y+self.rect.h, settings.UPPER_BOUND)-self.rect.h

        self.rect.topleft = round(self.x), round(self.y)
        self.hitbox.topleft = utils.x_offset(self.rect, self.hitbox.w), utils.y_offset(self.rect, self.hitbox.h)

        if keys[settings.keys["SHOOT"]]:
            if self.timer > self.fire_delay:
                settings.sounds["effects"]["shoot"].play()
                self.fire(projectiles_group)
                self.timer = 0
            self.dirty = 1

    def fire(self, projectiles_group: pygame.sprite.Group):
        # swap get_height and get_width because of rotation
        projectile = MultiProjectile(self.projectile_speed,
                                     self.x + self.rect.w / 2,
                                     self.y,
                                     self.attack_imgs,
                                     self.anim_delay,
                                     self.projectile_count,
                                     90,
                                     self.projectile_spread)
        projectiles_group.add(projectile.projectiles_group)

    def is_hit(self):
        return self.hit_timer <= self.invuln_delay


class SpriteGlow(pygame.sprite.DirtySprite):
    def __init__(self, sprite: pygame.sprite.DirtySprite, image: pygame.Surface):
        pygame.sprite.DirtySprite.__init__(self)
        self.sprite = sprite
        self.image = image
        self.rect = pygame.Rect(self.sprite.rect.x - (self.image.get_width() - self.sprite.rect.w) / 2,
                                self.sprite.rect.y - (self.image.get_height() - self.sprite.rect.h) / 2,
                                self.image.get_width(),
                                self.image.get_height())
        self.old_sprite_rect = pygame.Rect(self.sprite.rect)

    def update(self):
        if self.old_sprite_rect != self.sprite.rect:
            self.rect.topleft = (self.sprite.rect.x - (self.image.get_width() - self.sprite.rect.w) / 2,
                                 self.sprite.rect.y - (self.image.get_height() - self.sprite.rect.h) / 2)
        if self.sprite.image.get_alpha() != self.image.get_alpha():
            self.image.set_alpha(self.sprite.image.get_alpha())
            print(self.image.get_alpha())
        self.dirty = self.sprite.dirty
        self.old_sprite_rect = pygame.Rect(self.sprite.rect)
        # if the sprite is at or below 0 hp, stop blitting the glow
        if self.sprite.health <= 0:
            self.kill()
            #self.dirty = 0
