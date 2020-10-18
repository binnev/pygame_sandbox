import pygame
from pygame import Color, Surface
from pygame.rect import Rect
from pygame.sprite import Sprite

from fighting_game.groups import Level
from fighting_game.inputs import FightingGameInput


class Entity(Sprite):
    debug_color = Color("red")
    rect: Rect

    def update(self):
        pass

    def draw(self, surface: Surface, debug: bool = False):
        pass

    @property
    def x(self):
        return self.rect.centerx

    @x.setter
    def x(self, new_value):
        self.rect.centerx = new_value

    @property
    def y(self):
        return self.rect.centery

    @y.setter
    def y(self, new_value):
        self.rect.centery = new_value


class Platform(Entity):
    color = Color("gray")

    def __init__(self, x, y, width, height, droppable=False):
        super().__init__()

        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.droppable = droppable
        self.color = Color("green") if droppable else self.color

    def draw(self, surface, debug=False):
        pygame.draw.rect(surface, self.color, self.rect)
        if debug:
            pygame.draw.rect(surface, self.debug_color, self.rect, 1)
            pygame.draw.circle(surface, self.debug_color, self.rect.center, 2, 1)

    @property
    def width(self):
        return self.rect.width

    @width.setter
    def width(self, new_value):
        self.rect.width = new_value

    @property
    def height(self):
        return self.rect.height

    @height.setter
    def height(self, new_value):
        self.rect.height = new_value


class Character(Entity):
    width: int
    height: int
    color: Color
    level: Level

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__()

        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.u = 0
        self.v = 0
        self.input = input
        self.facing_right = facing_right

    def update(self):
        self.state()

    def draw(self, surface: Surface, debug: bool = False):
        # pygame.draw.rect(surface, self.color, self.rect)
        if debug:
            pygame.draw.rect(surface, self.debug_color, self.rect, 1)
            pygame.draw.circle(surface, self.debug_color, self.rect.center, 2, 1)


class Debugger(Character):
    width = 50
    height = 100
    color = Color("cyan")
    speed = 5

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__(x, y, input, facing_right)
        self.state = self.state_debug

    def update(self):
        self.state()

    def state_debug(self):
        if self.input.is_down(self.input.LEFT):
            self.x -= self.speed
            platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
            for plat in platforms:
                if plat.droppable:
                    pass
                else:
                    self.rect.left = max([self.rect.left, plat.rect.right])

        if self.input.is_down(self.input.RIGHT):
            self.x += self.speed
            platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
            for plat in platforms:
                if plat.droppable:
                    pass
                else:
                    self.rect.right = min([self.rect.right, plat.rect.left])

        if self.input.is_down(self.input.UP):
            self.y -= self.speed
            platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
            for plat in platforms:
                if plat.droppable:
                    pass
                else:
                    self.rect.top = max([self.rect.top, plat.rect.bottom])

        if self.input.is_down(self.input.DOWN):
            old_rect = Rect(self.rect)
            self.y += self.speed
            platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
            for plat in platforms:
                if plat.droppable:
                    # if character was above the platform, don't fall through
                    if old_rect.bottom <= plat.rect.top:
                        self.rect.bottom = min([self.rect.bottom, plat.rect.top])
                else:
                    self.rect.bottom = min([self.rect.bottom, plat.rect.top])
