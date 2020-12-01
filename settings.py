import pygame
import json

pygame.init()
WIDTH = 1280
HEIGHT = 900
LEFT_BOUND = 50
RIGHT_BOUND = WIDTH - 350
LOWER_BOUND = 50
UPPER_BOUND = HEIGHT-50
DISPLAY_WIDTH = RIGHT_BOUND-LEFT_BOUND
DISPLAY_HEIGHT = UPPER_BOUND-LOWER_BOUND

SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
FULLSCREEN = False
LOW_DETAIL_MODE = True&False
FPS = 60
DELTA_T = 1 / FPS
VOLUME = 1.00
TIMER = 0
LIVES = 0
SCORE = 0
LEVEL = 0
BUTTON_FONT = "Arial"
clock = pygame.time.Clock()
keys = {
    "UP": pygame.K_w,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "DOWN": pygame.K_s,
    "SHOOT": pygame.K_SPACE,
    "BOMB": pygame.K_b
}
wn = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN * FULLSCREEN)
defaults = dict((("VOLUME", 1.00),
                 ("keys", {
                     "UP": pygame.K_w,
                     "LEFT": pygame.K_a,
                     "RIGHT": pygame.K_d,
                     "DOWN": pygame.K_s,
                     "SHOOT": pygame.K_SPACE,
                     "BOMB": pygame.K_b
                 }),
                 ("FULLSCREEN", False)))


def init():
    global VOLUME, keys, FULLSCREEN
    f = open("settings.json", "r")

    # empty settings file: set it up with the defaults
    if not f.read(1):
        startup = defaults
        f.close()
        f = open("settings.json", "w")
        f.write(json.dumps(startup, indent=4))

    else:
        f.seek(0)
        startup = json.loads(f.read())
        VOLUME = startup["VOLUME"]
        keys = startup["keys"]
        FULLSCREEN = startup["FULLSCREEN"]

    f.close()


def change_settings(new_settings: dict):
    f = open("settings.json", "r")
    startup = json.loads(f.read())
    f.close()
    for key in new_settings:
        try:
            startup[key] = new_settings[key]
        except KeyError:
            print(f"key {key} does not exist in startup!")
            exit(1)
    f = open("settings.json", "w")
    f.write(json.dumps(startup, indent=4))

    f.close()
    update_settings_globals(new_settings)

def update_settings_globals(new_settings: dict):
    global VOLUME, keys, FULLSCREEN, wn
    VOLUME = new_settings["VOLUME"]
    keys = new_settings["keys"]
    FULLSCREEN = new_settings["FULLSCREEN"]
    wn = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN * FULLSCREEN)


def main():
    pygame.draw.line(wn, (255, 255, 255), (LEFT_BOUND, 0), (LEFT_BOUND, HEIGHT))
    pygame.draw.line(wn, (255, 255, 255), (RIGHT_BOUND, 0), (RIGHT_BOUND, HEIGHT))
    pygame.display.update()
    myfont = pygame.font.SysFont("Arial", 28)
    while True:
        # wn.fill((0,0,0))
        font = myfont.render("fwiefjwefjpokfosdkfksdflkwe", True, (255, 255, 255))
        font = myfont.render("fwiefjwefjpokfosdkfksdflkwe", True, (255, 255, 255))
        font = myfont.render("fwiefjwefjpokfosdkfksdflkwe", True, (255, 255, 255))
        font = myfont.render("fwiefjwefjpokfosdkfksdflkwe", True, (255, 255, 255))
        font = myfont.render("fwiefjwefjpokfosdkfksdflkwe", True, (255, 255, 255))
        wn.blit(font, (25, 25))
        wn.blit(font, (125, 125))
        wn.blit(font, (225, 225))
        wn.blit(font, (325, 325))
        wn.blit(font, (425, 425))
        # pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


if __name__ == '__main__':
    main()
