import math

import pygame
import time
import settings
import utils
import random
from Enemy import StaticEnemy, MovingEnemy
from button import Button, BorderButton
from player import Player, SpriteGlow

next_spawn = 0

pygame.init()
pygame.mixer.init()

enemy_ims = {"enemy1": utils.load_image("assets/images/alien1.png", 48)}
enemy_proj_ims = {"proj1": utils.load_image("assets/images/proj1.png", 16)}
enemy_glow_ims = {"glow1": utils.load_image("assets/images/alien1_glow.png", 54)}
powerup_ims = {"heart": utils.load_image("assets/images/heart.png", 32),
               "speed": utils.load_image("assets/images/fast_projectiles.png", 34),
               "firerate": utils.load_image("assets/images/faster_fire.png", 34),
               "count": utils.load_image("assets/images/more_rockets.png", 34),
               "spread": utils.load_image("assets/images/less_spread.png", 34),
               "invuln": utils.load_image("assets/images/more_invuln.png", 34)}


def blit_ui(player: Player, update_all: bool = True, update_lives: bool = False, update_score: bool = False,
            update_p_speed: bool = False, update_p_spread: bool = False, update_p_firerate: bool = False,
            update_p_count: bool = False, update_invuln: bool = False, update_level: bool = False,
            update_bomb: bool = False, bg: pygame.Surface = settings.wn) -> list:
    gap = 20
    right_offset = 20 + 50 + 20
    update_rects = []

    # background of the settings
    pygame.draw.rect(bg, (55, 55, 55),
                     (settings.RIGHT_BOUND, 0, settings.WIDTH - settings.RIGHT_BOUND, settings.HEIGHT))
    pygame.draw.rect(bg, (155, 155, 155),
                     (
                         settings.RIGHT_BOUND + 50, 50, settings.WIDTH - settings.RIGHT_BOUND - 100,
                         settings.HEIGHT - 100))

    font = pygame.font.SysFont("Arial", 28)

    # Preliminary when blitting the UI for the first time

    if update_all:
        lives_text = font.render("Lives", True, (255, 255, 255))

        score_text = font.render("Score", True, (255, 255, 255))

        powerup_text = pygame.font.SysFont("Arial", 32).render("Powerup Levels", True, (255, 255, 255))
        speed_im = pygame.transform.scale2x(powerup_ims["speed"])
        firerate_im = pygame.transform.scale2x(powerup_ims["firerate"])
        count_im = pygame.transform.scale2x(powerup_ims["count"])
        spread_im = pygame.transform.scale2x(powerup_ims["spread"])
        invuln_im = pygame.transform.scale2x(powerup_ims["invuln"])

        level_text = font.render("Level", True, (255, 255, 255))

        bomb_text = font.render("Bomb", True, (255, 255, 255))

        bg.blit(lives_text, (settings.RIGHT_BOUND + right_offset, 20 + 50))

        bg.blit(score_text, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50))

        bg.blit(powerup_text, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50))

        bg.blit(speed_im, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50))

        bg.blit(firerate_im, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50 + 68 + 20))

        bg.blit(count_im, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50 + 2 * 68 + 2 * 20))

        bg.blit(spread_im, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50 + 3 * 68 + 3 * 20))

        bg.blit(invuln_im, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50 + 4 * 68 + 4 * 20))

        bg.blit(level_text, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50 + 5 * 68 + 5 * 20))

        bg.blit(bomb_text, (settings.RIGHT_BOUND + right_offset, 20 + 50 + 50 + 50 + 50 + 50 + 5 * 68 + 5 * 20))

        update_rects += [pygame.Rect(settings.RIGHT_BOUND, 0, settings.WIDTH - settings.RIGHT_BOUND, settings.HEIGHT),
                         pygame.Rect(
                             settings.RIGHT_BOUND + 50, 50, settings.WIDTH - settings.RIGHT_BOUND - 100,
                             settings.HEIGHT - 100)]

    heart = powerup_ims["heart"]

    # Lives and hearts
    if update_lives or update_all:
        for i in range(player.health):
            bg.blit(heart, (settings.RIGHT_BOUND + 32 + (2 + i) * gap + right_offset, 20 + 50))

        update_rects += [pygame.Rect(settings.RIGHT_BOUND + 32 + 2 * gap + right_offset,
                                     20 + 50, 32 + settings.LIVES * 20, 32)]

    # Score
    if update_score or update_all:
        score = font.render(str(min(player.score, 999999999)), True, (255, 255, 255))
        bg.blit(score, (settings.RIGHT_BOUND + right_offset + gap + font.size("Score")[0], 20 + 50 + 50))
        update_rects += [pygame.Rect(settings.RIGHT_BOUND + right_offset + gap + font.size("Score")[0], 20 + 50 + 50,
                                     font.size(str(min(player.score, 999999999)))[0], font.size(str(1234567890))[1])]
    # Level
    if update_level or update_all:
        print("upd", settings.LEVEL)
        level_number_text = font.render(str(settings.LEVEL), True, (255, 255, 255))
        bg.blit(level_number_text,
                (settings.RIGHT_BOUND + right_offset + font.size("Level")[0] + gap, 20 + 50 + 50 + 50 + 50 + 5 * 68 + 5 * 20))
        update_rects += [pygame.Rect((settings.RIGHT_BOUND + right_offset + font.size("Level")[0] + gap,
                                     20 + 50 + 50 + 50 + 50 + 5 * 68 + 5 * 20), font.size(str(settings.LEVEL)))]
    # Powerups

    # Subroutine to blit the levels
    def blit_levels(level, x, y):
        width = 5
        rect_width = 25
        for i in range(level):
            # outer rect
            pygame.draw.rect(bg, (55, 55, 55), (x + i * (rect_width - width), y + 9, rect_width, 50))
            # inner rect
            pygame.draw.rect(bg, (0, 199, 0),
                             (x + i * (rect_width - width) + width, y + 9 + width, rect_width - 2 * width,
                              50 - 2 * width))
        for i in range(level, 5):
            # outer rect
            pygame.draw.rect(bg, (55, 55, 55), (x + i * (rect_width - width), y + 9, rect_width, 50))
            # inner rect
            pygame.draw.rect(bg, (199, 199, 199),
                             (x + i * (rect_width - width) + width, y + 9 + width, rect_width - 2 * width,
                              50 - 2 * width))

        return [pygame.Rect(x, y, rect_width * 5, 50)]

    # Powerups - Speed
    if update_p_speed or update_all:
        update_rects += blit_levels(player.p_speed_count, settings.RIGHT_BOUND + right_offset + 68 + gap,
                                    20 + 50 + 50 + 50 + 50)
    # Fire rate
    if update_p_firerate or update_all:
        update_rects += blit_levels(player.p_firerate_count, settings.RIGHT_BOUND + right_offset + 68 + gap,
                                    20 + 50 + 50 + 50 + 50 + 68 + 20)
    # Count
    if update_p_count or update_all:
        update_rects += blit_levels(player.p_count_count, settings.RIGHT_BOUND + right_offset + 68 + gap,
                                    20 + 50 + 50 + 50 + 50 + 2 * 68 + 2 * 20)
    # Spread
    if update_p_spread or update_all:
        update_rects += blit_levels(player.p_spread_count, settings.RIGHT_BOUND + right_offset + 68 + gap,
                                    20 + 50 + 50 + 50 + 50 + 3 * 68 + 3 * 20)

    # Invuln
    if update_invuln or update_all:
        update_rects += blit_levels(player.invuln_count, settings.RIGHT_BOUND + right_offset + 68 + gap,
                                    20 + 50 + 50 + 50 + 50 + 4 * 68 + 4 * 20)

    if update_bomb or update_all:
        cooldown_text = font.render(f"CD: {'Ready!' if player.bomb_timer < 0 else max(0, int(player.bomb_timer/1000))}",
                                    True, (255, 255, 255))
        bg.blit(cooldown_text, (settings.RIGHT_BOUND + right_offset + font.size("Bombs")[0],
                                20 + 50 + 50 + 50 + 50 + 50 + 5 * 68 + 5 * 20))
        update_rects += [pygame.Rect((settings.RIGHT_BOUND + right_offset + font.size("Bomb")[0] + gap,
                                    20 + 50 + 50 + 50 + 50 + 50 + 5 * 68 + 5 * 20),
                                    font.size(f"Cooldown: {max(0, int(player.bomb_timer/1000))}"))]

    return update_rects


def load_enemy(enemy_group, enemy_glow_group):
    global next_spawn
    # Spawn an enemy every 120/(12+level) seconds
    # with deviation +/- 3 seconds
    # level 1-3: hp = 5, count = 1, spr = 15, fr = 2-1.5 s, p_speed = 200-300
    # level 4-6: hp = 10, count = 1-3, spr = 10-15, fr = 2-1.2 s, p_speed = 200-500
    # level 7-10: hp = 15, count = 1-6, spr = 7-22, fr = 1.7-0.7 s, p_speed = 100-700
    # level 10-14: hp = 20, count = 1-10, spr = 5-25, fr = 2-0.3 s, p_speed = 100-900
    # level 15+: hp = 20+(level-15)^2, count = 1-level, spr = 3-25, fr = 1.7-0.2 s, p_speed = 100-900
    # speed is 200-500
    # score is hp*10+count*100+spread*10+firerate*100+speed

    if settings.TIMER >= next_spawn:
        next_spawn = settings.TIMER + 1000 * random.randint(120 // (12 + settings.LEVEL) - 3,
                                                            120 // (12 + settings.LEVEL) + 3)

        if settings.LEVEL <= 3:
            hp = 5
            count = 1
            spread = 15
            firerate = random.randint(15, 20) / 10
            p_speed = random.randint(200, 300)

        elif settings.LEVEL <= 6:
            hp = 10
            count = random.randint(1, 3)
            spread = random.randint(10, 14)
            firerate = random.randint(12, 20) / 10
            p_speed = random.randint(200, 500)

        elif settings.LEVEL <= 10:
            hp = 15
            count = random.randint(1, 6)
            spread = random.randint(7, 22)
            firerate = random.randint(7, 17) / 10
            p_speed = random.randint(100, 700)

        elif settings.LEVEL <= 14:
            hp = 20
            count = random.randint(1, 10)
            spread = random.randint(5, 25)
            firerate = random.randint(3, 20) / 10
            p_speed = random.randint(100, 900)

        else:
            hp = 20 + (settings.LEVEL - 15) ** 2
            count = random.randint(1, settings.LEVEL)
            spread = random.randint(3, 25)
            firerate = random.randint(2, 17) / 10
            p_speed = random.randint(100, 900)

        score = int(hp * 10 + count * 100 + spread * 10 + firerate * 100 + p_speed)
        firerate *= 1000  # (for conversion into milliseconds)
        # stx = random.randint(-100, settings.RIGHT_BOUND+100)
        stx = random.randint(settings.RIGHT_BOUND, settings.RIGHT_BOUND + 100)
        if stx < 0 or stx > settings.RIGHT_BOUND:
            sty = random.randint(0, 300)
        else:
            sty = -100
        endx = random.randint(settings.LEFT_BOUND + 100, settings.RIGHT_BOUND - 100)
        endy = random.randint(settings.LOWER_BOUND + 100, settings.UPPER_BOUND - 400)
        speed = random.randint(200, 500)
        if random.randint(0, 1) == 0:
            e = MovingEnemy(x=stx, y=sty, end_x=endx, end_y=endy,
                            image=random.choice(list(enemy_ims.values())), fire_delay=firerate,
                            speed=speed, health=hp, movement_delay=1000, score=score, p_speed=p_speed,
                            p_im=random.choice(list(enemy_proj_ims.values())), p_count=count,
                            p_fire_angle=270 + random.randint(-15, 15), p_spread=spread)
        else:
            e = StaticEnemy(x=stx, y=sty, end_x=endx, end_y=endy,
                            image=random.choice(list(enemy_ims.values())), fire_delay=firerate,
                            speed=speed, health=hp, score=score, p_speed=p_speed,
                            p_im=random.choice(list(enemy_proj_ims.values())), p_count=count,
                            p_fire_angle=270 + random.randint(-15, 15), p_spread=spread)

        enemy_group.add(e)
        # yeah...
        enemy_glow_group.add(
            SpriteGlow(e, enemy_glow_ims["glow" + list(enemy_ims.keys())[list(enemy_ims.values()).index(e.image)][-1]]))

    # e1 = MovingEnemy(200, 200, 300, 200, enemy_ims["enemy1"], 400, 100,
    #                 10, 5000, 200, 200, enemy_proj_ims["proj1"], 1)
    # enemy_group.add(e1)
    # enemy_glow_group.add(SpriteGlow(e1, enemy_glow_ims["glow1"]))


# get the projectiles over the player
def make_dirty(*groups: pygame.sprite.LayeredDirty):
    for group in groups:
        for sprite in group:
            sprite.dirty = 1


def draw_border(bg: pygame.Surface = settings.wn) -> list:
    res = []
    # upper line
    res.append(pygame.draw.line(bg, (55, 55, 55), (0, 25), (settings.RIGHT_BOUND + 50, 25), 50))
    # left line
    res.append(pygame.draw.line(bg, (55, 55, 55), (25, 50), (25, settings.HEIGHT), 50))
    # bottom line
    res.append(pygame.draw.line(bg, (55, 55, 55), (0, settings.HEIGHT - 25),
                                (settings.RIGHT_BOUND + 50, settings.HEIGHT - 25), 50))
    # right line
    res.append(pygame.draw.line(bg, (55, 55, 55), (settings.RIGHT_BOUND + 25, 50),
                                (settings.RIGHT_BOUND + 25, settings.HEIGHT - 25), 50))

    return res


def play():
    print("In play")
    done = False
    update_level = False

    background = utils.load_image("assets/images/galaxy.png", 1280, alpha=False)
    background = background.convert()
    # background.fill((5, 5, 155))
    update_rects = []

    player_group = pygame.sprite.LayeredDirty()
    glow_group = pygame.sprite.LayeredDirty()
    player_proj_group = pygame.sprite.LayeredDirty()
    enemy_group = pygame.sprite.LayeredDirty()
    enemy_glow_group = pygame.sprite.LayeredDirty()
    enemy_proj_group = pygame.sprite.LayeredDirty()
    powerup_group = pygame.sprite.LayeredDirty()

    player_proj_im_list = []
    player_im = utils.load_image("assets/images/spaceship.png", 48)
    player_glow = utils.load_image("assets/images/spaceship_glow.png", 54)

    player_proj_im_list.append(utils.load_image("assets/images/front_rocket.png", 44))
    # player_proj_im_list.append(utils.load_image("assets/images/rocket_im1.png", 64))
    # player_proj_im_list.append(utils.load_image("assets/images/rocket_im2.png", 64))

    p = Player(500, settings.WIDTH / 2, settings.HEIGHT / 2, settings.LIVES,
               300, 500, player_im, player_proj_im_list, 500, 1, 15)

    settings.wn.blit(background, (0, 0))
    p_glow = SpriteGlow(p, player_glow)
    player_group.add(p)
    glow_group.add(p_glow)

    # player_group.clear(settings.wn)
    # glow_group.clear(settings.wn, background)
    # player_proj_group.clear(settings.wn, background)
    # enemy_group.clear(settings.wn, background)
    # enemy_glow_group.clear(settings.wn, background)s
    # enemy_proj_group.clear(settings.wn, background)

    # pygame.draw.rect(background, (55, 55, 55), (25, 25, settings.RIGHT_BOUND - 25, settings.UPPER_BOUND - 25), 50)
    draw_border(background)
    blit_ui(p, bg=background)
    pygame.display.flip()

    #load_enemy(enemy_group, enemy_glow_group)
    while not done:
        #print(powerup_group)
        settings.clock.tick(settings.FPS)
        settings.TIMER += settings.DELTA_T * 1000
        # every 10 seconds s, the difficulty increases
        # 10 sec = 10000 milliseconds
        if settings.TIMER > settings.LEVEL * 10000:
            settings.LEVEL += 1
            update_level = True
        load_enemy(enemy_group, enemy_glow_group)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_menu()
                    settings.wn.blit(background, (0, 0))
                    draw_border()
                    blit_ui(p)
                    make_dirty(glow_group, player_group, enemy_group, player_proj_group, enemy_proj_group)
                    update_rects += [settings.SCREEN_RECT]

        # update the rects for enemy glow group before it gets taken out
        update_rects += [pygame.Rect(glow_im.rect.x - 10, glow_im.rect.y - 10, glow_im.rect.w + 20, glow_im.rect.h + 20)
                         for glow_im in enemy_glow_group]

        # Update player and enemy projectiles
        # Update enemy and borders of enemy
        # Update player and borders of player
        player_group.update(player_proj_group, enemy_proj_group, enemy_group)
        enemy_group.update(player_proj_group, enemy_proj_group, player_group, powerup_group)
        player_proj_group.update()
        enemy_proj_group.update()
        glow_group.update()
        enemy_glow_group.update()
        powerup_group.update()

        if not settings.LOW_DETAIL_MODE:
            settings.wn.blit(background, (0, 0))

            # draw player and enemy
            enemy_glow_group.draw(settings.wn)
            update_rects += enemy_group.draw(settings.wn)
            glow_group.draw(settings.wn)
            update_rects += [
                pygame.Rect(glow_im.rect.x - 10, glow_im.rect.y - 10, glow_im.rect.w + 20, glow_im.rect.h + 20)
                for glow_im in glow_group]
            player_group.draw(settings.wn)

            # Draw enemy and player projectiles
            update_rects += player_proj_group.draw(settings.wn)
            update_rects += enemy_proj_group.draw(settings.wn)
            update_rects += powerup_group.draw(settings.wn)
            update_rects += draw_border()

        else:
            # Draw enemy and player projectiles
            update_rects += player_proj_group.draw(settings.wn, background)
            update_rects += enemy_proj_group.draw(settings.wn, background)
            update_rects += powerup_group.draw(settings.wn, background)
            # draw player and enemy
            enemy_glow_group.draw(settings.wn, background)
            update_rects += enemy_group.draw(settings.wn)
            glow_group.draw(settings.wn, background)
            update_rects += [
                pygame.Rect(glow_im.rect.x - 10, glow_im.rect.y - 10, glow_im.rect.w + 20, glow_im.rect.h + 20)
                for glow_im in glow_group]
            player_group.draw(settings.wn)

        if p.health <= 0:
            done = True

        # check for player collision, important to put this after updating player
        # TODO: make into a subroutine?
        if p.is_hit():
            update_rects += blit_ui(p, update_all=False, update_lives=True)
        if p.score != settings.SCORE:
            settings.SCORE = p.score
            update_rects += blit_ui(p, update_all=False, update_score=True)
        coll = pygame.sprite.spritecollide(p, powerup_group, True)
        for powerup in coll:
            settings.sounds["effects"]["get_item"].play()
            if powerup.powerup_type == "heart":
                p.health += 1
                #update_rects += blit_ui(p, update_all=False, update_lives=True)
            elif powerup.powerup_type == "speed":
                p.p_speed_count += 1
                p.projectile_speed += p.p_speed_incrs[p.p_speed_count]
                p.p_speed_count = min(5, p.p_speed_count)
                #update_rects += blit_ui(p, update_all=False, update_p_speed=True)
            elif powerup.powerup_type == "firerate":
                p.p_firerate_count += 1
                p.fire_delay += p.p_firerate_incrs[p.p_firerate_count]
                p.p_firerate_count = min(5, p.p_firerate_count)
                #update_rects += blit_ui(p, update_all=False, update_p_firerate=True)
            elif powerup.powerup_type == "count":
                p.p_count_count += 1
                p.projectile_count += p.p_count_incrs[p.p_count_count]
                p.p_count_count = min(5, p.p_count_count)
                #update_rects += blit_ui(p, update_all=False, update_p_count=True)
            elif powerup.powerup_type == "spread":
                p.p_spread_count += 1
                p.projectile_spread += p.p_spread_incrs[p.p_spread_count]
                p.p_spread_count = min(5, p.p_spread_count)
                #update_rects += blit_ui(p, update_all=False, update_p_spread=True)
            elif powerup.powerup_type == "invuln":
                p.invuln_count += 1
                p.invuln_delay += p.invuln_incrs[p.invuln_count]
                p.invuln_count = min(5, p.invuln_count)
                #update_rects += blit_ui(p, update_all=False, update_invuln=True)
            p.score += 300*settings.LEVEL
            update_rects += blit_ui(p)

        if update_level:
            update_level = False
            update_rects += blit_ui(p)

        if p.bomb_timer > 0 and ((1-((p.bomb_timer/1000) % 1)) <= settings.DELTA_T):
            update_rects += blit_ui(p, update_all=True)

        # debug([p for p in player_group][0], 60, 121, 15, (663, 440), player_proj_group)
        # utils.window_WriteLines([str(p_glow.rect), str(update_rects)])
        # utils.attr_blit([e for e in enemy_group][0])
        #print(update_rects)
        pygame.display.update(update_rects)
        # settings.wn.fill((0,0,0))
        update_rects = []

    game_over()


def game_over():
    pygame.mixer.stop()
    settings.wn.fill((0,0,0))
    game_over_rect = pygame.Rect(utils.centre_offset(settings.SCREEN_RECT, (0, 0, settings.DISPLAY_WIDTH//2, settings.DISPLAY_HEIGHT//2)), (settings.DISPLAY_WIDTH//2, settings.DISPLAY_HEIGHT//2))
    pygame.draw.rect(settings.wn, (127, 127, 127), game_over_rect)
    done = False
    font = pygame.font.SysFont("Arial", 64)
    game_over_text = font.render("Game Over", True, (255, 255, 255))
    score_text = pygame.font.SysFont("Arial", 48).render(f"Score: {settings.SCORE}", True, (255, 255, 255))
    restart_button = BorderButton(pygame.Rect(game_over_rect.x+20, game_over_rect.bottom-80, 150, 60), (0, 128, 0),
                                  (0, 192, 0), "restart", 28, (255, 255, 255), 2, None)
    exit_to_menu_button = BorderButton(pygame.Rect(game_over_rect.right-170, game_over_rect.bottom-80, 150, 60), (128, 0, 0),
                                  (192, 0, 0), "Exit to Menu", 28, (255, 255, 255), 2, None)
    while not done:
        settings.clock.tick(settings.FPS)
        pygame.draw.rect(settings.wn, (127, 127, 127), game_over_rect)
        restart_button.update()
        restart_button.draw(settings.wn)
        exit_to_menu_button.update()
        exit_to_menu_button.draw(settings.wn)
        settings.wn.blit(game_over_text, (utils.x_offset(game_over_rect, game_over_text.get_size()[0]), game_over_rect.y+20))
        settings.wn.blit(score_text, (utils.x_offset(game_over_rect, score_text.get_size()[0]), game_over_rect.y+120))
        if restart_button.is_hovering() and pygame.mouse.get_pressed()[0]:
            done = True
            settings.wn.fill((0, 0, 0))
            settings.LEVEL = 0
            settings.SCORE = 0
            settings.TIMER = 0
        elif exit_to_menu_button.is_hovering() and pygame.mouse.get_pressed()[0]:
            settings.LEVEL = 0
            settings.SCORE = 0
            settings.TIMER = 0
            menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        pygame.display.flip()


def settings_menu():
    """
    Let the user change volume, keybinds and fullscreen
    """
    print("In settings")
    update_rects = [settings.SCREEN_RECT]
    buttons = []
    key_boxes = []
    key_buttons = []

    settings.wn.fill((0, 0, 0))

    volume = settings.VOLUME
    keys = settings.keys
    fullscreen = settings.FULLSCREEN

    # this is spaghetti code
    def seek_key(button):
        temp_hover_col = button.hover_col
        button.hover_col = button.col
        while True:
            settings.clock.tick(settings.FPS)
            pressed = pygame.key.get_pressed()
            count = 0
            for val in pressed:
                if val != 0:
                    button.hover_col = temp_hover_col
                    return count
                count += 1

            for event2 in pygame.event.get():
                if event2.type == pygame.QUIT:

                    pygame.quit()
                    exit()
            button.draw(settings.wn)
            pygame.display.update(button.rect)

    def save(button):
        button.text = "Saved!"
        res = dict((("VOLUME", volume), ("keys", keys), ("FULLSCREEN", fullscreen)))
        settings.change_settings(res)
        for key10 in settings.sounds:
            for key20 in settings.sounds[key10]:
                settings.sounds[key10][key20].set_volume(settings.VOLUME)

    settings_rect = pygame.Rect(utils.x_offset(settings.SCREEN_RECT, pygame.Rect(0, 0, 400, 100)),
                                25, 400, 100)
    settings_box = Button(settings_rect, (128, 128, 0), (128, 128, 0), "Settings", 56, (255, 255, 255), None)

    volume_str = f"Volume: {round(volume * 100)}%"
    volume_box_rect = pygame.Rect(utils.x_offset(settings.SCREEN_RECT, (0, 0, 200, 75)), 175, 200, 75)
    volume_box = Button(volume_box_rect, (128, 128, 128), (128, 128, 128),
                        volume_str, 32, (255, 255, 255), None)

    volume_button_minus_rect = pygame.Rect(volume_box_rect.x - volume_box_rect.h * 2, volume_box_rect.y,
                                           volume_box_rect.h, volume_box_rect.h)
    volume_button_minus = Button(volume_button_minus_rect, (128, 128, 128), (192, 192, 192),
                                 "-", 32, (255, 255, 255), None)

    volume_button_plus_rect = pygame.Rect(volume_box_rect.right + volume_box_rect.h, volume_box_rect.y,
                                          volume_box_rect.h, volume_box_rect.h)
    volume_button_plus = Button(volume_button_plus_rect, (128, 128, 128), (192, 192, 192),
                                "+", 32, (255, 255, 255), None)

    fullscreen_str = "Fullscreen: On" if fullscreen else "Fullscreen: Off"
    fullscreen_on_col = (0, 175, 0)
    fullscreen_on_hover_col = (0, 225, 0)
    fullscreen_off_col = (175, 0, 0)
    fullscreen_off_hover_col = (225, 0, 0)
    fullscreen_rect = pygame.Rect(utils.x_offset(settings.SCREEN_RECT, (0, 0, 300, 75)), 300, 300, 75)
    fullscreen_box = Button((fullscreen_rect.x, fullscreen_rect.y, 200, 75), (128, 128, 128), (128, 128, 128),
                            fullscreen_str, 32, (255, 255, 255), None)
    fullscreen_button_rect = pygame.Rect(fullscreen_rect.right + (300 - fullscreen_rect.w - fullscreen_rect.h),
                                         fullscreen_rect.y, fullscreen_rect.h, fullscreen_rect.h)
    if fullscreen:
        fullscreen_button = Button(fullscreen_button_rect, fullscreen_on_col, fullscreen_on_hover_col,
                                   "On", 32, (255, 255, 255), None)
    else:
        fullscreen_button = Button(fullscreen_button_rect, fullscreen_off_col, fullscreen_off_hover_col,
                                   "Off", 32, (255, 255, 255), None)

    bounding_key_rect = pygame.Rect(utils.x_offset(settings.SCREEN_RECT, (0, 0, 450, 300)), 460, 780, 360)
    elems = len(keys) + 1
    space = bounding_key_rect.h // elems
    gap = 20
    for i, key in enumerate({**{"Keybinds (click to change):": 0}, **keys}):
        if i == 0:
            key_rect = pygame.Rect(bounding_key_rect.x, bounding_key_rect.y - (80 - (space - gap)) + i * space, 450,
                                   60)
            key_box = Button(key_rect, (127, 127, 127), (127, 127, 127), key, 36, (255, 255, 255), None)
        else:
            key_rect = pygame.Rect(bounding_key_rect.x, bounding_key_rect.y + i * space, 200, space - gap)
            key_box = Button(key_rect, (127, 127, 127), (127, 127, 127), key, 24, (255, 255, 255), None)
            key_boxes.append(key_box)
        key_button_rect = pygame.Rect(bounding_key_rect.x + 200 + 50, bounding_key_rect.y + i * space, 200, space - gap)
        if i != 0:
            key_button = Button(key_button_rect, (127, 127, 127), (192, 192, 192),
                                pygame.key.name(keys[key]), 24, (255, 255, 255), None)
            buttons.append(key_button)
            key_buttons.append(key_button)
        update_rects.append(key_rect)
        buttons.append(key_box)

    cancel_rect = pygame.Rect(utils.x_offset(settings.SCREEN_RECT, (0, 0, 650, 25)), 825, 150, 50)
    save_rect = pygame.Rect(cancel_rect.right + 100, 825, 150, 50)
    reset_defaults_rect = pygame.Rect(save_rect.right + 100, 825, 150, 50)
    cancel_box = Button(cancel_rect, (127, 0, 0), (192, 0, 0), "Cancel", 28, (255, 255, 255), None)
    save_box = Button(save_rect, (0, 127, 0), (0, 192, 0), "Save", 28, (255, 255, 255), None)
    reset_defaults_box = Button(reset_defaults_rect, (127, 0, 127), (192, 0, 192),
                                "Reset", 28, (255, 255, 255), None)

    update_rects.append(settings_rect)
    update_rects.append(volume_box_rect)
    update_rects.append(volume_button_minus_rect)
    update_rects.append(volume_button_plus_rect)
    update_rects.append(fullscreen_rect)
    update_rects.append(fullscreen_button_rect)
    update_rects.append(cancel_rect)
    update_rects.append(save_rect)
    update_rects.append(reset_defaults_rect)

    buttons.append(settings_box)
    buttons.append(volume_box)
    buttons.append(volume_button_minus)
    buttons.append(volume_button_plus)
    buttons.append(fullscreen_box)
    buttons.append(fullscreen_button)
    buttons.append(cancel_box)
    buttons.append(save_box)
    buttons.append(reset_defaults_box)

    while True:
        settings.clock.tick(settings.FPS)
        for button in buttons:
            button.draw(settings.wn)
            update_rects.append(button.rect)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if volume_button_plus.is_hovering():
                        save_box.text = "Save"
                        volume += 0.05
                    elif volume_button_minus.is_hovering():
                        save_box.text = "Save"
                        volume -= 0.05
                        volume = round(volume, 2)
                    volume = min(max(0, volume), 1)
                    volume_box.text = f"Volume: {round(volume * 100)}%"

                    if fullscreen_button.is_hovering():
                        save_box.text = "Save"
                        fullscreen = not fullscreen
                        if fullscreen:
                            fullscreen_button.col = fullscreen_on_col
                            fullscreen_button.hover_col = fullscreen_on_hover_col
                            fullscreen_button.text = "On"
                            fullscreen_box.text = "Fullscreen: On"
                        else:
                            fullscreen_button.col = fullscreen_off_col
                            fullscreen_button.hover_col = fullscreen_off_hover_col
                            fullscreen_button.text = "Off"
                            fullscreen_box.text = "Fullscreen: Off"

                    for i, button in enumerate(key_buttons):
                        if button.is_hovering():
                            save_box.text = "Save"
                            temp_key_text = key_buttons[i].text
                            key_buttons[i].text = "Press a key to record"
                            new = seek_key(button)

                            # check if new is in the keybinds
                            if new not in keys.values():
                                key_buttons[i].text = pygame.key.name(new)
                                keys[key_boxes[i].text] = new

                            else:
                                key_buttons[i].text = temp_key_text

                    if cancel_box.is_hovering():
                        settings.wn.fill((0, 0, 0))
                        myfont = pygame.font.SysFont("Arial", 70)
                        title_font = myfont.render("Space Game", True, (255, 255, 255))
                        title_rect = pygame.Rect((0, 0), myfont.size("Space Game"))
                        settings.wn.blit(title_font, (utils.x_offset(settings.SCREEN_RECT, title_rect), 100))
                        pygame.display.flip()
                        return

                    if save_box.is_hovering():
                        save(save_box)

                    if reset_defaults_box.is_hovering():
                        save_box.text = "Save"
                        volume = settings.defaults["VOLUME"]
                        keys = settings.defaults["keys"]
                        fullscreen = settings.defaults["FULLSCREEN"]
                        volume_box.text = f"Volume: {round(volume * 100)}%"
                        for i, button in enumerate(key_buttons):
                            key_buttons[i].text = pygame.key.name(keys[key_boxes[i].text])
                        if fullscreen:
                            fullscreen_button.col = fullscreen_on_col
                            fullscreen_button.hover_col = fullscreen_on_hover_col
                            fullscreen_button.text = "On"
                            fullscreen_box.text = "Fullscreen: On"
                        else:
                            fullscreen_button.col = fullscreen_off_col
                            fullscreen_button.hover_col = fullscreen_off_hover_col
                            fullscreen_button.text = "Off"
                            fullscreen_box.text = "Fullscreen: Off"

            if event.type == pygame.QUIT:
                print(volume, keys, fullscreen)
                for key in keys:
                    print(key, pygame.key.name(keys[key]))
                pygame.quit()
                exit()

        pygame.display.update(update_rects)
        update_rects = []


def difficulty_menu():
    settings.wn.fill((0, 0, 0))
    update_rects = []
    buttons = []

    myfont = pygame.font.SysFont("Arial", 70)
    text_font = pygame.font.SysFont("Arial", 48)
    diff_text = myfont.render("Select Difficulty", True, (255, 255, 255))
    diff_rect = pygame.Rect((0, 0), myfont.size("Select Difficulty"))
    settings.wn.blit(diff_text, (utils.x_offset(settings.SCREEN_RECT, diff_rect), 50))

    easy_im = utils.load_image("assets/images/easy_button.png", 75)
    medium_im = utils.load_image("assets/images/medium_button.png", 75)
    hard_im = utils.load_image("assets/images/hard_button.png", 75)
    extreme_im = utils.load_image("assets/images/extreme_button.png", 75)

    easy_text = text_font.render("Easy difficulty. 5 lives.", True, (255, 255, 255))
    medium_text = text_font.render("Medium difficulty. 3 lives.", True, (255, 255, 255))
    hard_text = text_font.render("Hard difficulty. 2 lives.", True, (255, 255, 255))
    extreme_text = text_font.render("Extreme difficulty. 1 life.", True, (255, 255, 255))

    rect_width = 600
    rect_height = 100
    rect_gap = 50
    rect_x = utils.x_offset(settings.SCREEN_RECT, rect_width)

    easy_button = BorderButton((rect_x, 150 + rect_gap, rect_width, rect_height), (0, 127, 0), (0, 192, 0), "",
                               40, (255, 255, 255), 5, None)
    medium_button = BorderButton((rect_x, 250 + 2 * rect_gap, rect_width, rect_height), (176, 176, 0), (225, 225, 0),
                                 "",
                                 40, (255, 255, 255), 5, None)
    hard_button = BorderButton((rect_x, 350 + 3 * rect_gap, rect_width, rect_height), (127, 0, 0), (192, 0, 0), "",
                               40, (255, 255, 255), 5, None)
    extreme_button = BorderButton((rect_x, 450 + 4 * rect_gap, rect_width, rect_height), (76, 0, 76), (127, 0, 127), "",
                                  40, (255, 255, 255), 5, None)

    back_button = BorderButton((utils.x_offset(settings.SCREEN_RECT, 200), 800, 200, 50), (127, 127, 127),
                               (192, 192, 192),
                               "Back To Menu", 36, (255, 255, 255), 3, menu)

    '''
    for i, tup in enumerate(zip([easy_im, medium_im, hard_im, extreme_im],
                       [easy_text, medium_text, hard_text, extreme_text])):
        y_offset = utils.y_offset((rect_x, 150 + 100 * i + (i + 1) * rect_gap, rect_width, rect_height),
                                  text_font.get_linesize())
        settings.wn.blit(tup[0], (rect_x+12, 150+100*i+(i+1)*rect_gap+12))
        settings.wn.blit(tup[1], (rect_x+112, 150+100*i+(i+1)*rect_gap+y_offset))

    for i in range(1, 5, 1):
        pygame.draw.rect(settings.wn, (192, 192, 192), (rect_x+7, 150+(i-1)*100+i*rect_gap+7, 85, 85))
    '''

    buttons.append(easy_button)
    buttons.append(medium_button)
    buttons.append(hard_button)
    buttons.append(extreme_button)
    buttons.append(back_button)

    pygame.display.update()
    while True:
        settings.clock.tick(settings.FPS)
        for button in buttons:
            update_rects.append(button.rect)
            button.draw(settings.wn)
        back_button.update()
        for i in range(1, 5, 1):
            pygame.draw.rect(settings.wn, (192, 192, 192), (rect_x + 7, 150 + (i - 1) * 100 + i * rect_gap + 7, 85, 85))

        for i, tup in enumerate(zip([easy_im, medium_im, hard_im, extreme_im],
                                    [easy_text, medium_text, hard_text, extreme_text])):
            y_offset = utils.y_offset((rect_x, 150 + 100 * i + (i + 1) * rect_gap, rect_width, rect_height),
                                      text_font.get_linesize())
            settings.wn.blit(tup[0], (rect_x + 12, 150 + 100 * i + (i + 1) * rect_gap + 12))
            settings.wn.blit(tup[1], (rect_x + 112, y_offset))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.is_hovering():
                    settings.LIVES = 5
                    pygame.mixer.stop()
                    settings.sounds["music"]["easy_level_music"].play(loops=-1)
                    play()
                elif medium_button.is_hovering():
                    settings.LIVES = 3
                    pygame.mixer.stop()
                    settings.sounds["music"]["medium_level_music"].play(loops=-1)
                    play()
                elif hard_button.is_hovering():
                    settings.LIVES = 2
                    pygame.mixer.stop()
                    settings.sounds["music"]["hard_level_music"].play(loops=-1)
                    play()
                elif extreme_button.is_hovering():
                    settings.LIVES = 1
                    pygame.mixer.stop()
                    settings.sounds["music"]["extreme_level_music"].play(loops=-1)
                    play()

        pygame.display.update(update_rects)
        update_rects = []


def how_to_play():
    settings.wn.fill((0, 0, 0))
    header_font = pygame.font.SysFont("Arial", 70)
    body_font = pygame.font.SysFont("Arial", 28)
    how_to_play_text = header_font.render("How to Play", True, (255, 255, 255))
    settings.wn.blit(how_to_play_text, (utils.x_offset(settings.SCREEN_RECT, how_to_play_text.get_size()[0]), 100))
    body_text = []
    body_text.append(body_font.render(f"Press {pygame.key.name(settings.keys['UP'])} to move up, "
                                      f"press {pygame.key.name(settings.keys['LEFT'])} to move left, "
                                      f"press {pygame.key.name(settings.keys['DOWN'])} to move down, "
                                      f"and press {pygame.key.name(settings.keys['RIGHT'])} to move right.",
                                      True, (255, 255, 255)))
    body_text.append(body_font.render(f"Press {pygame.key.name(settings.keys['SHOOT'])} to fire a projectile.",
                                      True, (255, 255, 255)))
    body_text.append(body_font.render(f"Press {pygame.key.name(settings.keys['BOMB'])} to clear all enemy projectiles. "
                                      f"There is a cooldown of 10 seconds between each use.", True, (255, 255, 255)))
    body_text.append(body_font.render(f"Killing an enemy grants score and has a chance to drop a powerup.",
                                      True, (255, 255, 255)))
    back_to_menu_rect = pygame.Rect(settings.WIDTH-300, 100, 200, 100)
    back_to_menu_button = Button(back_to_menu_rect,
                                 (0, 0, 127), (0, 0, 192), "Back To Menu", 28, (255, 255, 255), None)
    for i, text in enumerate(body_text):
        settings.wn.blit(text, (50, 300+body_font.get_height()*i))
    pygame.display.flip()
    while True:
        back_to_menu_button.update()
        back_to_menu_button.draw(settings.wn)
        settings.clock.tick(settings.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_to_menu_button.is_hovering():
                    settings.wn.fill((0, 0, 0))
                    myfont = pygame.font.SysFont("Arial", 70)
                    title_font = myfont.render("Space Game", True, (255, 255, 255))
                    title_rect = pygame.Rect((0, 0), myfont.size("Space Game"))
                    settings.wn.blit(title_font, (utils.x_offset(settings.SCREEN_RECT, title_rect), 100))
                    pygame.display.flip()
                    return
        pygame.display.update(back_to_menu_rect)

def menu():
    settings.init()
    settings.wn.fill((0, 0, 0))
    update_rects = []
    buttons = []
    myfont = pygame.font.SysFont("Arial", 70)
    title_font = myfont.render("Space Game", True, (255, 255, 255))
    title_rect = pygame.Rect((0, 0), myfont.size("Space Game"))
    settings.wn.blit(title_font, (utils.x_offset(settings.SCREEN_RECT, title_rect), 100))
    update_rects.append(pygame.Rect((utils.x_offset(settings.SCREEN_RECT, title_rect), 100),
                                    myfont.size("Space Game")))

    b_width = 200
    b_height = 100
    b_x = utils.x_offset(settings.SCREEN_RECT, pygame.Rect(0, 0, b_width, b_height))
    buttons.append(Button(pygame.Rect(b_x, 300, b_width, b_height), (0, 127, 127), (0, 192, 192),
                          "Play", 40, (255, 255, 255), difficulty_menu))
    buttons.append(Button(pygame.Rect(b_x, 500, b_width, b_height), (127, 127, 127), (192, 192, 192),
                          "Settings", 40, (255, 255, 255), settings_menu))
    buttons.append(Button(pygame.Rect(b_x, 700, b_width, b_height), (127, 127, 0), (192, 192, 0),
                          "How to Play", 40, (255, 255, 255), how_to_play))

    pygame.mixer.stop()
    settings.sounds["music"]["menu_music"].play(loops=-1)
    for button in buttons:
        button.draw(settings.wn)
        update_rects.append(button.rect)

    pygame.display.update()
    while True:
        settings.clock.tick(settings.FPS)
        for button in buttons:
            button.update()
            button.draw(settings.wn)
            update_rects.append(button.rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(1)

        pygame.display.update(update_rects)
        update_rects = []


def main():
    scene = menu  # Set the current scene.
    while scene is not None:
        # Execute the current scene function. When it's done
        # it returns either the next scene or None which we
        # assign to the scene variable.

        scene = scene()
        print(scene)


if __name__ == '__main__':
    main()
