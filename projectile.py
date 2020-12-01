import pygame
import math
import settings


class Projectile(pygame.sprite.DirtySprite):
    def __init__(self, speed: float, angle: float, x: int, y: int, images: list, anim_delay: float = 0):
        # print(x, y)
        pygame.sprite.DirtySprite.__init__(self)
        self.speed = speed
        self.angle = angle
        self.x = x
        self.y = y
        self.images = images
        self.image = pygame.transform.rotate(self.images[0], self.angle)
        self.anim_delay = anim_delay
        self.anim_timer = 0
        self.image_index = 0
        self.rect = pygame.Rect(self.x, self.y,
                                self.image.get_width(),
                                self.image.get_height())
        self.rect.center = self.rect.x, self.rect.y

    def update(self):
        self.anim_timer += settings.DELTA_T * 1000
        if self.anim_timer >= self.anim_delay:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
            self.image = pygame.transform.rotate(self.images[self.image_index], self.angle)

        dx = math.cos(math.radians(self.angle)) * self.speed * settings.DELTA_T
        dy = -math.sin(math.radians(self.angle)) * self.speed * settings.DELTA_T
        # negative because of how x and y work
        self.x += dx
        self.y += dy
        if self.x < settings.LEFT_BOUND \
                or self.x > settings.RIGHT_BOUND \
                or self.y < settings.LOWER_BOUND \
                or self.y > settings.UPPER_BOUND:
            self.kill()
        self.rect.center = round(self.x), round(self.y)
        self.dirty = 1

    def draw(self, wn):
        wn.blit(self.images[self.image_index], (self.rect.x, self.rect.y))


class MultiProjectile:
    def __init__(self, speed: float, x: int, y: int, images: list, anim_delay: float = 0,
                 projectile_count: int = 1, centred_angle: float = 180, spread: float = 15):
        self.speed = speed
        self.x = x
        self.y = y
        self.images = images
        self.anim_delay = anim_delay
        self.projectile_count = projectile_count
        self.centred_angle = centred_angle
        self.spread = spread
        self.projectiles_group = self.create_projectiles()

    def create_projectiles(self):
        """
        the projectiles are created centred around the centre angle, with each
        spread apart by self.spread.

        for the angle calculation: take proj_count = 5, centred_angle = 180, spread = 15.
        Then i is from -5//2+1 to 5//2+1 = -2 to 3 = -2, -1, 0, 1, 2.
        Then you can multiply i by the spread factor and add the offset of centered_angle.

        If proj_count = 6, i is from -6//2+1 to 6//2+1 = -2 to 4 = -2, -1, 0, 1, 2, 3.
        But we want i to be centred about 0, so we subtract each i by 0.5 to get -2.5, -1.5, -0.5, 0.5, 1.5, 2.5.
        Then we multiply by spread factor and add the offset like before.

        returns a pygame.sprite.Group with the projectiles created.
        """

        projectiles_group = pygame.sprite.Group()
        for i in range(-self.projectile_count // 2 + 1, self.projectile_count // 2 + 1, 1):
            if self.projectile_count // 2 != 1:
                angle = i * self.spread + self.centred_angle
            else:
                angle = (i - 0.5) * self.spread + self.centred_angle
            projectiles_group.add(Projectile(
                self.speed, angle, self.x, self.y, self.images, self.anim_delay
            ))
        return projectiles_group

    '''
    def update(self):
        for projectile in self.projectiles_group:
            projectile.update()

        return self.projectiles_group

    def draw(self, wn):
        self.projectiles_group.draw(wn)
    '''


class Powerup(Projectile):
    def __init__(self, speed: float, x: int, y: int, image: pygame.Surface, powerup_type: str):
        super().__init__(speed, 270, x, y, [image])
        self.powerup_type = powerup_type
