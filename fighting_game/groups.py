import pygame
from pygame import Surface
from pygame.sprite import Sprite


class Group(pygame.sprite.Group):
    """ Container for multiple sprite objects. """

    def draw(self, surface, debug=False):
        """ Draws all of the member sprites onto the given surface. """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface, debug)
        self.lostsprites = []

    def kill(self):
        """Kill all the sprites in this group. This is different from .empty().
        empty() does not kill the sprites in other groups."""
        for sprite in self:
            sprite.kill()


class Scene(Sprite):
    """
    Finite State Machine with a .groups attribute. Generally used for objects that
    1) need to maintain state (e.g. menu screen with animate in/out states)
    2) have several groups of child objects (e.g. background, buttons)
    3) have no .image attribute
    Scenes can be added to Groups to create a hierarchical structure
    The order of groups in the .groups attribute determines the draw order; it's basically the
    layers
    """

    state: "method"
    groups: list
    parental_name = "parent_scene"

    def update(self):
        self.state()
        for group in self.groups:
            group.update()

    def draw(self, surface: Surface, debug=False):
        for group in self.groups:
            group.draw(surface, debug)

    def add_to_group(self, *objects, group: Group):
        """group should be one of self.groups. This method is intended to be used by more
        specific methods e.g.:
        def add_particle(*objects):
            self.add_to_group(*objects, self.particles)
        """
        group.add(*objects)
        # give the object a reference to this scene
        for obj in objects:
            setattr(obj, self.parental_name, self)


