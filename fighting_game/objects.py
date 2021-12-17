import pygame
from pygame import Color
from pygame import Surface
from pygame.rect import Rect

from base.objects import Entity


class PhysicalEntity(Entity):
    """
    attributes:
    - rect: used for collision detection and positioning
    - image: used for blitting to screen
    """

    level: Entity  # parent Entity
    image: Surface = None
    debug_color = Color("red")
    rect: Rect
    frame_duration: int  # higher = slower animation framerate

    def draw(self, surface: Surface, debug: bool = False):
        if self.image:
            surface.blit(self.image, self.image_rect)
        if debug:
            pygame.draw.rect(surface, self.debug_color, self.rect, 1)
            pygame.draw.circle(surface, self.debug_color, self.rect.center, 2, 1)
        super().draw(surface, debug)

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
    def animation_frame(self):
        """ Convert game ticks to animation frames. """
        return self.tick // self.frame_duration
