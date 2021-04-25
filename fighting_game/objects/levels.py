import random

import pygame
from pygame import Color, Surface
from pygame.rect import Rect

from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.objects.base import Group, Entity, PhysicalEntity
from fighting_game.objects.characters import Platform
from fighting_game.objects.hitbox import HitHandler
from fighting_game.objects.particles import Plume


class BlastZone(PhysicalEntity):
    debug_color = Color("blue")

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)


class Level(Entity):
    """ A Scene representing a level of a game. """

    parental_name = "level"
    screen_shake: int
    blast_zone: BlastZone

    def __init__(self):
        super().__init__()
        self.background = Group()
        self.platforms = Group()
        self.characters = Group()
        self.projectiles = Group()
        self.particle_effects = Group()
        self.hitboxes = Group()
        self.invisible_elements = Group()
        self.child_groups = [
            self.background,
            self.platforms,
            self.characters,
            self.projectiles,
            self.particle_effects,
            self.hitboxes,
            self.invisible_elements,
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

    def add_invisible_element(self, *objects):
        self.add_to_group(*objects, group=self.invisible_elements)

    def main(self):
        self.hit_handler.handle_hits(self.hitboxes, [*self.characters, *self.projectiles])
        self.handle_blast_zone_collisions()
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

    def handle_blast_zone_collisions(self):
        objects = [*self.characters, *self.projectiles]
        for object in objects:
            if not pygame.sprite.collide_rect(self.blast_zone, object):
                object.kill()
                # todo: logic for keeping track of stocks
                # todo: add particle effect, screen shake, etc
                self.screen_shake = 20
                angle = self.calculate_plume_angle(object)
                self.add_particle_effect(Plume(object.x, object.y, angle))

    def calculate_plume_angle(self, object):
        """ Object has just entered the blastzone """
        if object.x < self.blast_zone.rect.left:
            angle = 0
        elif object.x > self.blast_zone.rect.right:
            angle = 180
        elif object.y > self.blast_zone.rect.bottom:
            angle = 90
        else:
            angle = 270
        return angle


class Battlefield(Level):
    def __init__(self):
        super().__init__()

        ground = Platform(0, 0, 800, 1000)
        ground.x = SCREEN_WIDTH // 2
        ground.rect.top = SCREEN_HEIGHT - 300

        wall = Platform(0, 0, 20, 300)
        wall.x = SCREEN_WIDTH // 2
        wall.rect.bottom = SCREEN_HEIGHT - 150

        left_platform = Platform(0, 0, 100, 20, droppable=True)
        left_platform.x = ground.x - 200
        left_platform.y = ground.rect.top - 100

        right_platform = Platform(0, 0, 100, 20, droppable=True)
        right_platform.x = ground.x + 200
        right_platform.y = ground.rect.top - 100

        top_platform = Platform(0, 0, 100, 20, droppable=True)
        top_platform.x = ground.x
        top_platform.y = ground.rect.top - 200

        self.add_platform(
            ground,
            left_platform,
            right_platform,
            top_platform,
            # wall
        )

        self.blast_zone = BlastZone(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.blast_zone.x = SCREEN_WIDTH // 2
        self.blast_zone.y = SCREEN_HEIGHT // 2
        self.add_invisible_element(self.blast_zone)
