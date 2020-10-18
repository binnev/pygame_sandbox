from numpy.core._multiarray_umath import sign
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
    touch_box_margin = 1

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
            # draw touchbox
            pygame.draw.rect(surface, Color("goldenrod"), self.touch_box, 1)

    @property
    def touch_box(self):
        return self.rect.inflate(self.touch_box_margin, self.touch_box_margin)

    def touching(self, entity: Entity):
        return self.touch_box.colliderect(entity.rect)


class Debugger(Character):
    width = 50
    height = 100
    color = Color("cyan")
    speed = 5

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__(x, y, input, facing_right)
        self.state = self.state_fall
        self.gravity = 0.3
        self.jump_power = 20
        self.air_resistance = 0.5

    def update(self):
        self.state()
        self.update_physics()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)

        def tprint(surface, x, y, textString):
            font = pygame.font.Font(None, 30)
            textBitmap = font.render(textString, True, Color("black"))
            surface.blit(textBitmap, (x, y))

        colliding = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        touching = [plat for plat in self.level.platforms if self.touching(plat)]

        things_to_print = [
            f"u = {self.u}",
            f"v = {self.v}",
            f"airborne = {self.airborne}",
            f"touching: {touching}",
            f"colliding: {colliding}",
        ]
        line_spacing = 20
        for ii, thing in enumerate(things_to_print):
            tprint(surface, 0, ii * line_spacing, thing)

    @property
    def airborne(self):
        return True

    def update_physics(self):
        if self.airborne:
            self.v += self.gravity
            magnitude = abs(self.u)
            direction = sign(self.u)
            speed = magnitude - self.air_resistance
            speed = speed if speed > 0 else 0
            self.u = speed * direction

        # update horizontal position and handle platform collisions
        self.x += self.u
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        moving_right = self.u > 0
        for plat in platforms:
            if plat.droppable:
                pass  # you can move horizontally through droppable platforms
            else:
                if moving_right:
                    self.rect.right = min([self.rect.right, plat.rect.left])
                else:
                    self.rect.left = max([self.rect.left, plat.rect.right])
                self.u = 0

        # update vertical position and handle platform collisions
        old_rect = Rect(self.rect)  # remember previous position
        self.y += self.v
        platforms = pygame.sprite.spritecollide(self, self.level.platforms, dokill=False)
        moving_down = self.v > 0
        for plat in platforms:
            # droppable platforms
            if plat.droppable:
                if moving_down:
                    # if character was already inside the platform, or player is holding down
                    if (old_rect.bottom > plat.rect.top) or self.input.is_down(self.input.DOWN):
                        pass
                    # if character was above the platform and not holding down
                    else:
                        # don't go through the platform
                        self.rect.bottom = min([self.rect.bottom, plat.rect.top])
                        self.v = 0
                else:  # if travelling up
                    pass  # you can go upwards through droppable platforms

            # solid platforms
            else:
                if moving_down:
                    self.rect.bottom = min([self.rect.bottom, plat.rect.top])
                    self.v = 0
                else:
                    self.rect.top = max([self.rect.top, plat.rect.bottom])
                    self.v = 0

    def state_fall(self):
        # jump
        if self.input.is_down(self.input.Y):
            self.v = -self.jump_power

        if self.input.is_down(self.input.LEFT):
            self.u = -self.speed

        if self.input.is_down(self.input.RIGHT):
            self.u = self.speed

        if self.input.is_down(self.input.UP):
            self.v = -self.speed

        if self.input.is_down(self.input.DOWN):
            self.v = self.speed

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
