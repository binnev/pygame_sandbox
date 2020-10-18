import pygame


class Group(pygame.sprite.Group):
    def draw(self, surface, debug=False):
        """ Draws all of the member sprites onto the given surface. """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface, debug)
        self.lostsprites = []

    def kill(self):
        """ Kill all the sprites in this group. This is different from .empty().
        empty() does not kill the sprites in other groups. """
        for sprite in self:
            sprite.kill()


class Level(Group):
    """ A Group representing a level of a game, with some special sub-groups. """

    def __init__(self, *args, game=None):
        super().__init__(*args)
        self.game = game
        self.platforms = Group()
        self.characters = Group()
        self.projectiles = Group()
        self.hitboxes = Group()
        self.particle_effects = Group()

    def add(self, *objects, type=None):
        # add to Level (similar to "all" group)
        super().add(*objects)

        if type == "platform":
            self.platforms.add(*objects)
        if type == "character":
            self.characters.add(*objects)
        if type == "projectile":
            self.projectiles.add(*objects)
        if type == "hitbox":
            self.hitboxes.add(*objects)
        if type == "particle_effect":
            self.particle_effects.add(*objects)
        # give the object a reference to this level
        for obj in objects:
            obj.level = self

    def add_platform(self, *objects):
        self.add(*objects, type="platform")

    def add_character(self, *objects):
        self.add(*objects, type="character")

    def add_projectile(self, *objects):
        self.add(*objects, type="projectile")

    def add_hitbox(self, *objects):
        self.add(*objects, type="hitbox")

    def add_particle_effect(self, *objects):
        self.add(*objects, type="particle_effect")