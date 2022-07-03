from collections import deque

import pygame
from pygame.rect import Rect

from base.objects import PhysicalEntity
from base.utils import draw_arrow
from fighting_game import sounds
from fighting_game.conf import HITSTUN_CONSTANT, HITPAUSE_CONSTANT
from fighting_game.projectiles import Projectile


class Hitbox(PhysicalEntity):
    """
    A hitbox always has an owner. It follows its owner's x/y position. The x/y_offset attributes
    allow us to position the hitbox relative to its owner.
    """

    debug_color = (60, 0, 0)
    sound = sounds.hit
    owner: PhysicalEntity

    def __init__(
        self,
        owner: PhysicalEntity,
        width: int,
        height: int,
        x_offset: int = 0,
        y_offset: int = 0,
        rotation: float = 0,
        base_knockback: float = 0,
        fixed_knockback: float = 0,
        knockback_growth: float = 0,
        knockback_angle: float = 0,
        damage: float = 0,
        higher_priority_sibling: PhysicalEntity = None,
        lower_priority_sibling: PhysicalEntity = None,
        sound=None,
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
        self.base_knockback = base_knockback
        self.fixed_knockback = fixed_knockback
        self.knockback_angle = knockback_angle
        self.knockback_growth = knockback_growth
        self.higher_priority_sibling = higher_priority_sibling
        self.lower_priority_sibling = lower_priority_sibling
        if sound:
            self.sound = sound

        self.image = self.create_image()

    def create_image(self):
        image = pygame.Surface((self.width, self.height))
        pygame.draw.ellipse(image, self.debug_color, (0, 0, self.width, self.height))
        image.set_colorkey((0, 0, 0))
        image = pygame.transform.rotate(image, self.rotation)
        return image

    def __repr__(self):
        return f"Hitbox with id {id(self)}"

    def handle_hit(self, object):
        """Object is the entity hit by this hitbox. I've passed it here so that hitboxes can do
        context specific stuff e.g. trigger the object's "electrocute" animation if the hitbox is
        electric"""
        self.level.screen_shake += 10
        self.sound.play()
        self.owner.handle_land_hit(hitbox=self)

    @property
    def hitpause_duration(self):
        return round(
            (self.fixed_knockback + self.base_knockback + self.knockback_growth) * HITPAUSE_CONSTANT
        )

    def hitstun_duration(self, knockback):
        return round(knockback * HITSTUN_CONSTANT)

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
            image_rect = self.image.get_rect()
            image_rect.center = self.rect.center
            surface.blit(self.image, image_rect, special_flags=pygame.BLEND_RGB_ADD)
            if self.knockback_angle is not None:
                draw_arrow(surface, self.rect.center, self.knockback_angle, (255, 0, 0), 100)

    def flip_x(self):
        self.knockback_angle = 180 - self.knockback_angle
        self.rotation = 180 - self.rotation
        self.x_offset = -self.x_offset
        self.image = self.create_image()

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


class HitHandler:
    def __init__(self):
        # queue for storing
        self.handled = deque(maxlen=200)

    def handle_hits(self, hitboxes: [Hitbox], objects: [PhysicalEntity]):
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
                hitbox: Hitbox
                # hitboxes should never hit their owner
                if hitbox.owner == object:
                    continue

                if isinstance(hitbox.owner, Projectile) and hitbox.owner.owner == object:
                    continue

                # if this hitbox has already affected the object, don't repeat the interaction
                if (hitbox, object) in self.handled:
                    continue

                # if the hitbox has higher-priority siblings that are also colliding, skip and
                # let the higher-priority hitbox collide instead
                if any(s in colliding_hitboxes for s in hitbox.higher_priority_siblings):
                    continue

                object.handle_get_hit(hitbox)
                hitbox.handle_hit(object)
                self.handled.append((hitbox, object))
                # if the hitbox has lower priority sibling hitboxes, add those to the handled
                # list so that they don't also hit the object
                for sibling in hitbox.siblings:
                    self.handled.append((sibling, object))
