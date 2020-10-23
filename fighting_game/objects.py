from numpy.core._multiarray_umath import sign
import pygame
from pygame import Color, Surface
from pygame.rect import Rect
from pygame.sprite import Sprite

from base.animation import SpriteDict
from fighting_game.groups import Level
from fighting_game.inputs import FightingGameInput
from fighting_game.sprites.stickman import stickman_sprites


class Entity(Sprite):
    image: Surface
    debug_color = Color("red")
    rect: Rect
    game_tick = 0  # number of game ticks elapsed in the current state
    frame_duration: int  # higher = slower animation framerate

    def update(self):
        self.update_animation()

    def draw(self, surface: Surface, debug: bool = False):
        if hasattr(self, "image"):
            surface.blit(self.image, self.image_rect)
        if debug:
            pygame.draw.rect(surface, self.debug_color, self.rect, 1)
            pygame.draw.circle(surface, self.debug_color, self.rect.center, 2, 1)

    @property
    def image_rect(self):
        """ Default is to align the image with the center of the object """
        if self.image:
            image_rect = self.image.get_rect()
            image_rect.center = self.rect.center
            return image_rect
        else:
            return None

    @property
    def x(self):
        # todo: rethink this. Currently this clips off sub-pixel positions and speeds.
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

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        """ Reset animation counter when state changes """
        self._state = new_state
        self.game_tick = 0

    @property
    def animation_frame(self):
        """ Convert game ticks to animation frames. """
        return self.game_tick // self.frame_duration

    def update_animation(self):
        self.game_tick += 1


class Platform(Entity):
    color = Color("gray")

    def __init__(self, x, y, width, height, droppable=False):
        super().__init__()

        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.droppable = droppable
        self.color = Color("green") if droppable else self.color
        self.image = Surface((width, height))
        self.image.fill(self.color)


class Character(Entity):
    width: int
    height: int
    color: Color
    level: Level
    sprites: SpriteDict
    ground_acceleration: float
    ground_speed: float
    air_acceleration: float
    air_speed: float
    jump_power: float
    gravity: float
    friction: float
    air_resistance: float
    fall_speed: float
    fast_fall_speed: float

    touch_box_margin = 2
    frame_duration = 3

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__()

        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.u = 0
        self.v = 0
        self.input = input
        self.facing_right = facing_right

    def update(self):
        super().update()
        self.state()
        self.update_physics()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        if debug:
            # draw touchbox
            pygame.draw.rect(surface, Color("goldenrod"), self.touch_box, 1)

    @property
    def facing(self):
        return "right" if self.facing_right else "left"

    @property
    def touch_box(self):
        return self.rect.inflate(self.touch_box_margin, self.touch_box_margin)

    def touching(self, entity: Entity):
        return self.touch_box.colliderect(entity.rect)

    @property
    def airborne(self):
        for plat in self.level.platforms:
            # if standing on top of platform
            if self.touching(plat) and self.rect.bottom <= plat.rect.top:
                return False
        return True

    def update_physics(self):
        # modify speeds
        if self.airborne:
            # vertical
            self.v += self.gravity
            if self.v > self.fall_speed:
                self.v = self.fall_speed
            # horizontal
            magnitude = abs(self.u)
            direction = sign(self.u)
            speed = magnitude - self.air_resistance
            speed = max([0, speed])
            self.u = speed * direction
            if self.u > self.air_speed:
                self.u = self.air_speed
            if self.u < -self.air_speed:
                self.u = -self.air_speed
        else:
            magnitude = abs(self.u)
            direction = sign(self.u)
            speed = magnitude - self.friction
            speed = speed if speed > 0 else 0
            self.u = speed * direction
            if self.u > self.ground_speed:
                self.u = self.ground_speed
            if self.u < -self.ground_speed:
                self.u = -self.ground_speed

        # modify position
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
        self.image = self.sprites["jump_" + self.facing].get_frame(self.animation_frame)
        input = self.input
        if input.is_down(input.LEFT):
            self.u -= self.air_acceleration
        if input.is_down(input.RIGHT):
            self.u += self.air_acceleration
        if input.is_pressed(input.UP):
            self.v = -self.jump_power
        if not self.airborne:
            self.state = self.state_stand

    def state_stand(self):
        self.image = self.sprites["stand_" + self.facing].get_frame(self.animation_frame)
        input = self.input
        if input.is_down(input.DOWN):
            self.v = 1  # need this to drop through platforms
        if input.is_down(input.LEFT):
            self.u -= self.ground_acceleration
        if input.is_down(input.RIGHT):
            self.u += self.ground_acceleration
        if input.is_pressed(input.UP):
            self.v = -self.jump_power
            self.state = self.state_fall
        if self.airborne:
            self.state = self.state_fall


class Debugger(Character):
    width = 50
    height = 100
    color = Color("cyan")
    ground_acceleration = 99
    ground_speed = 7
    air_acceleration = 0.75
    air_speed = 5
    gravity = 0.3
    jump_power = 10
    air_resistance = 0.1
    friction = 1
    fall_speed = 7

    def __init__(self, x, y, input=FightingGameInput, facing_right=True):
        super().__init__(x, y, input, facing_right)
        self.state = self.state_fall
        self.sprites = stickman_sprites()

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
            f"state: {self.state.__name__}",
        ]
        line_spacing = 20
        for ii, thing in enumerate(things_to_print):
            tprint(surface, 0, ii * line_spacing, thing)

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
