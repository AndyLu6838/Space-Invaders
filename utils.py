import pygame
import math
import settings
from pathlib import Path


def x_offset(src_rect: pygame.Rect, target_rect: pygame.Rect):
    src_rect = pygame.Rect(src_rect)
    if isinstance(target_rect, float) or isinstance(target_rect, int):
        target_rect = pygame.Rect(0, 0, target_rect, 0)
    else:
        target_rect = pygame.Rect(target_rect)
    return src_rect.x + (src_rect.w - target_rect.w) // 2


def y_offset(src_rect: pygame.Rect, target_rect: pygame.Rect):
    src_rect = pygame.Rect(src_rect)
    if isinstance(target_rect, float) or isinstance(target_rect, int):
        target_rect = pygame.Rect(0, 0, 0, target_rect)
    else:
        target_rect = pygame.Rect(target_rect)
    return src_rect.y + (src_rect.h - target_rect.h) // 2


def centre_offset(src_rect: pygame.Rect, target_rect: pygame.Rect):
    """
    returns the x and y coordinate where the target_rect should go
    inside src_rect
    returns (x, y)
    """
    return x_offset(src_rect, target_rect), y_offset(src_rect, target_rect)


# loads an image from the filename
# and converts it for faster use.
# raises an error if filename does not exist
# otherwise returns the Surface
def load_image(filename: str, newWidth: float, newHeight: float = None, alpha: bool = True):
    try:
        im = pygame.image.load(filename)
        if alpha:
            im = im.convert_alpha()
        else:
            im = im.convert()
        if newWidth is not None:
            scale = im.get_width() / newWidth
            if newHeight is None:
                im = pygame.transform.scale(im, (int(newWidth), int(im.get_height() / scale)))
            else:
                im = pygame.transform.scale(im, (int(newWidth), newHeight))

    except pygame.error:
        print("Cannot load image:", filename)
        raise SystemExit
    return im


def load_folder(foldername: str, newWidth: float, newHeight: float = None):
    p = Path.cwd()
    p = p / "images" / foldername
    res_ims = []
    try:
        img_list = list(p.glob("*.png"))
        for img in img_list:
            res_ims.append(load_image(str(img), newWidth, newHeight))
        # for path in p.iterdir():
        # if path.suffix == "png":
        # print(path)
    except FileNotFoundError:
        print("Cannot load folder:", foldername)
        raise SystemExit

    return res_ims


def attr_blit(Class):
    if Class is None:
        return
    x = 0
    y = 0
    myfont = pygame.font.SysFont("Arial", 28)
    d = vars(Class)
    for k in d:
        temp = d[k]
        if isinstance(temp, float):
            temp = round(temp, 3)
        text = myfont.render(k + f": {temp}", True, (255, 255, 255))
        h = myfont.get_height()
        settings.wn.blit(text, (x, y))
        y += h

    text = myfont.render(str(settings.clock.get_fps()), True, (255, 255, 255))
    settings.wn.blit(text, (x, y + myfont.get_height()))


def debug(player=None, angle_start=0, angle_end=0, angle_step=0, start=(settings.WIDTH / 2, settings.HEIGHT / 2),
          *groups):
    """
    Can show class attributes of player, show lines between angle_start and angle_end (starting at coord tuple start),
    and show all the rects of sprites in groups.
    Suggested to use pygame.display.update() to update the whole screen and blit/fill in the
    background after updating.

    :param player: Optional. Show the attributes of class member Player.
    :param angle_start: Optional, though needed with the other angle parameters. Start of the angle.
    :param angle_end: End of the angle.
    :param angle_step: Space between each line between angle_start and angle_end.
    :param start: Where to begin drawing the lines.
    :param groups: Groups to show rects of.
    :return: None.
    """
    attr_blit(player)
    for i in range(angle_start, angle_end + 1, angle_step):
        pygame.draw.line(settings.wn, (255, 0, 0), start,
                         (math.cos(math.radians(i)) * 700 + start[0], -math.sin(math.radians(i)) * 700 + start[1]))

    for group in groups:
        for p in group:
            pygame.draw.rect(settings.wn, (255, 255, 255), p.rect, 3)


def window_WriteLines(text_list, x=20, y=20, wn=settings.wn):
    myfont = pygame.font.SysFont("Arial", 28)
    for i, text in enumerate(text_list):
        rendered_text = myfont.render(text, True, (255, 255, 255))
        wn.blit(rendered_text, (x, y+i*myfont.get_linesize()))
        #myfont.get_linesize()