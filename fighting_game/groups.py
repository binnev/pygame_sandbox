import random

import pygame
from pygame import Surface
from pygame.sprite import Sprite

from fighting_game.objects import HitHandler


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


class Level(Scene):
    """ A Scene representing a level of a game. """

    parental_name = "level"
    screen_shake: int

    def __init__(self):
        super().__init__()
        self.background = Group()
        self.platforms = Group()
        self.characters = Group()
        self.projectiles = Group()
        self.particle_effects = Group()
        self.hitboxes = Group()
        self.groups = [
            self.background,
            self.platforms,
            self.characters,
            self.projectiles,
            self.particle_effects,
            self.hitboxes,
        ]
        self.state = self.main
        self.hit_handler = HitHandler()
        self.screen_shake = 0

    def add_background(self, *objects):
        self.add_to_group(*objects, group=self.background)

    def add_platform(self, *objects):
        self.add_to_group(*objects, group=self.platforms)

    def add_character(self, *objects):
        self.add_to_group(*objects, group=self.characters)

    def add_projectile(self, *objects):
        self.add_to_group(*objects, group=self.projectiles)

    def add_hitbox(self, *objects):
        self.add_to_group(*objects, group=self.hitboxes)

    def add_particle_effect(self, *objects):
        self.add_to_group(*objects, group=self.particle_effects)

    def main(self):
        self.hit_handler.handle_hits(self.hitboxes, [*self.characters, *self.projectiles])
        self.hitboxes.kill()
        if self.screen_shake:
            self.screen_shake -= 1

    def draw(self, surface: Surface, debug=False):
        if self.screen_shake:
            temp_surf = Surface(surface.get_size())
            temp_surf.fill((150, 150, 150))  # overwrite previous stuff on screen
            magnitude = 10
            rect = temp_surf.get_rect()
            rect.centerx += random.randrange(-magnitude, magnitude)
            rect.centery += random.randrange(-magnitude, magnitude)
            super().draw(temp_surf, debug)
            surface.blit(temp_surf, rect)
        else:
            surface.fill((150, 150, 150))  # overwrite previous stuff on screen
            super().draw(surface, debug)
