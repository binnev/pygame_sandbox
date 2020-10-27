from collections import deque
from copy import copy

import numpy
from numpy.core._multiarray_umath import sign
import pygame
from pygame import Color, Surface
from pygame.rect import Rect
from pygame.sprite import Sprite

from base.animation import SpriteDict
from base.utils import draw_arrow
from fighting_game.groups import Level
from fighting_game.inputs import FightingGameInput
from fighting_game.sprites.stickman import stickman_sprites


class Entity(Sprite):
    image: Surface = None
    debug_color = Color("red")
    rect: Rect
    game_tick = 0  # number of game ticks elapsed in the current state
    frame_duration: int  # higher = slower animation framerate

    def update(self):
        self.update_animation()

    def draw(self, surface: Surface, debug: bool = False):
        if self.image:
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
        return self.rect.centerx

    @x.setter
    def x(self, new_value):
        new_value = round(new_value)
        self.rect.centerx = new_value

    @property
    def y(self):
        return self.rect.centery

    @y.setter
    def y(self, new_value):
        new_value = round(new_value)
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


class Move:
    """ E.g. an attack """
    hitbox_mapping: dict

    def __init__(self, character: "Character"):
        # todo flip hitboxes based on character orientation
        self.character = character
        self.hitbox_lookup = {
            frame: hitboxes
            for frames, hitboxes in self.hitbox_mapping.items()
            for frame in ([frames] if isinstance(frames, int) else range(frames[0], frames[-1] + 1))
        }

    def __call__(self, *args, **kwargs):
        n = self.character.animation_frame
        active_hitboxes = self.hitbox_lookup.get(n, [])
        for hitbox in active_hitboxes:
            self.character.level.add_hitbox(hitbox)


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

    class AttackMove(Move):

        def __init__(self, character: "Character"):
            super().__init__(character)

            self.sweet_spot = sweet_spot = Hitbox(
                owner=character,
                width=50,
                height=50,
            )
            self.sour_spot = sour_spot = Hitbox(
                owner=character,
                width=100,
                height=100,
                higher_priority_sibling=sweet_spot,
            )
            assert sour_spot.higher_priority_sibling is sweet_spot
            assert sweet_spot.lower_priority_sibling is sour_spot
            self.hitbox_mapping = {
                10: [sweet_spot],
                11: [sweet_spot],
                12: [sweet_spot],
                13: [sweet_spot],
                14: [sweet_spot],
                15: [sweet_spot],
                (16, 30): [sweet_spot, sour_spot],
                (31, 40): [sour_spot],
            }


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


class Hitbox(Entity):
    """
    A hitbox always has an owner. It follows its owner's x/y position. The x/y_offset attributes
    allow us to position the hitbox relative to its owner.
    """

    debug_color = (*Color("red")[:3], 150)

    def __init__(
        self,
        owner: Entity,
        width: int,
        height: int,
        x_offset: int = 0,
        y_offset: int = 0,
        rotation: float = 0,
        knockback: float = 0,
        knockback_angle: float = 0,
        damage: float = 0,
        higher_priority_sibling: Entity = None,
        lower_priority_sibling: Entity = None,
    ):
        super().__init__()
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.owner = owner
        self.width = width
        self.height = height
        self.rect = Rect(0, 0, self.width, self.height)
        self.rotation = rotation
        self.damage = damage
        self.knockback = knockback
        self.knockback_angle = knockback_angle
        self.higher_priority_sibling = higher_priority_sibling
        self.lower_priority_sibling = lower_priority_sibling

    @property
    def image(self) -> Surface:
        # todo optimise this
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.fill((0, 0, 0, 0))
        pygame.draw.ellipse(image, self.debug_color, (0, 0, self.width, self.height))
        colorkey = image.get_at((0, 0))  # todo
        image.set_colorkey(colorkey)
        image = pygame.transform.rotate(image, self.rotation)
        return image

    def __repr__(self):
        return f"Hitbox with id {id(self)}"

    def handle_hit(self, object):
        """Object is the entity hit by this hitbox. I've passed it here so that hitboxes can do
        context specific stuff e.g. trigger the object's "electrocute" animation if the hitbox is
        electric"""
        pass

    @property
    def rect(self):
        """If the hitbox has an owner, it will follow its owner's x and y (offset by x_offset
        and y_offset)."""
        self.align_to_owner()
        return self._rect

    @rect.setter
    def rect(self, new_rect):
        self._rect = new_rect
        self.align_to_owner()

    def align_to_owner(self):
        self._rect.center = (
            self.owner.x + self.x_offset,
            self.owner.y + self.y_offset,
        )

    def draw(self, surface, debug=False):
        if debug:
            super().draw(surface, debug)
            if self.knockback_angle is not None:
                draw_arrow(surface, self.rect.center, self.knockback_angle, color=self.debug_color)

    def flip_x(self):
        new_hitbox = copy(self)
        new_hitbox.knockback_angle = 180 - self.knockback_angle
        new_hitbox.rotation = 180 - self.rotation
        new_hitbox.x = -self.x
        # todo; flip image?
        return new_hitbox

    @property
    def lower_priority_sibling(self):
        return self._lower_priority_sibling

    @lower_priority_sibling.setter
    def lower_priority_sibling(self, hitbox):
        self._lower_priority_sibling = hitbox
        if hitbox:
            hitbox._higher_priority_sibling = self

    @property
    def higher_priority_sibling(self):
        return self._higher_priority_sibling

    @higher_priority_sibling.setter
    def higher_priority_sibling(self, hitbox):
        self._higher_priority_sibling = hitbox
        if hitbox:
            hitbox._lower_priority_sibling = self

    @property
    def lower_priority_siblings(self) -> {"Hitbox"}:
        sibling = self.lower_priority_sibling
        return {sibling} | sibling.lower_priority_siblings if sibling else set()

    @property
    def higher_priority_siblings(self) -> {"Hitbox"}:
        sibling = self.higher_priority_sibling
        return {sibling} | sibling.higher_priority_siblings if sibling else set()

    @property
    def siblings(self):
        return self.higher_priority_siblings | self.lower_priority_siblings


def handle_hitbox_collision(hitbox, object):
    # todo: apply hitbox damage?
    # here's where we calculate how far/fast the object gets knocked
    magnitude = hitbox.knockback / object.mass
    u = magnitude * numpy.cos(numpy.deg2rad(hitbox.knockback_angle))
    v = -magnitude * numpy.sin(numpy.deg2rad(hitbox.knockback_angle))
    object.u = u
    object.v = v
    object.x += u
    object.y += v
    object.handle_hit(hitbox)
    hitbox.handle_hit(object)


class HitHandler:
    def __init__(self):
        # queue for storing
        self.handled = deque(maxlen=200)

    def handle_hits(self, hitboxes: [Hitbox], objects: [Entity]):
        """
        Manage the effects of hitboxes hitting other entities.

        This function shouldn't know the details of how each object reacts to getting hit. That
        is the responsibility of the object to define those methods. This function's
        responsibility is to ensure no object instance is hit more than once by the same hitbox
        instance.
        """

        for object in objects:
            colliding_hitboxes = pygame.sprite.spritecollide(object, hitboxes, dokill=False)
            for hitbox in colliding_hitboxes:
                # hitboxes should never hit their owner
                if hitbox.owner == object:
                    continue

                # if this hitbox has already affected the object, don't repeat the interaction
                if (hitbox, object) in self.handled:
                    continue

                # if the hitbox has higher-priority siblings that are also colliding, skip and
                # let the higher-priority hitbox collide instead
                if any(s in colliding_hitboxes for s in hitbox.higher_priority_siblings):
                    continue

                handle_hitbox_collision(hitbox, object)
                self.handled.append((hitbox, object))
                # if the hitbox has lower priority sibling hitboxes, add those to the handled list so
                # that they don't also hit the object
                for sibling in hitbox.siblings:
                    self.handled.append((sibling, object))
