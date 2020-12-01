import pygame
import settings


class Button:
    def __init__(self, rect: pygame.Rect, col: tuple, hover_col: tuple,
                 text: str, font_size: int, font_col: tuple,
                 function: callable, *function_args):
        if not isinstance(rect, pygame.Rect):
            self.rect = pygame.Rect(rect)
        else:
            self.rect = rect
        self.col = col
        self.hover_col = hover_col
        self.text = text
        self.font_size = font_size
        self.font_col = font_col
        self.function = function
        self.function_args = function_args

        self.button_font = pygame.font.SysFont(settings.BUTTON_FONT, self.font_size)

    def draw(self, wn: pygame.Surface):
        if self.is_hovering():
            pygame.draw.rect(wn, self.hover_col, self.rect)
            font = self.button_font.render(self.text, True, self.font_col, self.hover_col)
        else:
            pygame.draw.rect(wn, self.col, self.rect)
            font = self.button_font.render(self.text, True, self.font_col, self.col)

        # calculate where the font should be blitted
        font_rect = self.button_font.size(self.text)
        offset_x = (self.rect.w - font_rect[0])//2
        offset_y = (self.rect.h - font_rect[1])//2
        wn.blit(font, (self.rect.x + offset_x, self.rect.y + offset_y))

    def is_hovering(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        return self.rect.left <= mouse_x <= self.rect.right and self.rect.top <= mouse_y <= self.rect.bottom

    def update(self):
        if self.is_hovering() and pygame.mouse.get_pressed()[0] and self.function is not None:
            return self.function(*self.function_args)


class BorderButton(Button):
    def __init__(self, rect: pygame.Rect, col: tuple, hover_col: tuple,
                 text: str, font_size: int, font_col: tuple, width: int,
                 function: callable, *function_args):
        super().__init__(rect, col, hover_col, text, font_size, font_col, function, *function_args)
        self.width = width

    def draw(self, wn: pygame.Surface):
        if self.is_hovering():
            pygame.draw.rect(wn, self.hover_col, self.rect)
            pygame.draw.rect(wn, self.col, (self.rect.x+self.width, self.rect.y+self.width,
                                            self.rect.w-2*self.width, self.rect.h-2*self.width))
            font = self.button_font.render(self.text, True, self.font_col, self.col)
        else:
            pygame.draw.rect(wn, self.col, self.rect)
            font = self.button_font.render(self.text, True, self.font_col, self.col)

        # calculate where the font should be blitted
        font_rect = self.button_font.size(self.text)
        offset_x = (self.rect.w - font_rect[0])//2
        offset_y = (self.rect.h - font_rect[1])//2
        wn.blit(font, (self.rect.x + offset_x, self.rect.y + offset_y))