import pygame


class EntityGroup(pygame.sprite.Group):
    """Extends pygame's sprite.Group class. Overrides the .draw() method."""

    def __init__(self):
        """Keep a reference to the game class"""
        super().__init__()  # todo: delete

    def draw(self, surface, debug=False):
        """ Draws all of the member sprites onto the given surface. """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface, debug)
        self.lostsprites = []

    def kill(self):
        """ Kill all the sprites in this group. """
        for sprite in self:
            sprite.kill()


class Level(EntityGroup):
    """The Level class holds sprite lists of all the platforms, characters, etc---all
    the game objects that are currently "in play". Create a subclass to create a
    specific level e.g. one with platforms in certain positions. """

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        self.platforms = EntityGroup()
        self.characters = EntityGroup()
        self.projectiles = EntityGroup()
        self.hitboxes = EntityGroup()
        self.particle_effects = EntityGroup()

    def add(self, *objects, type=None):
        # add to Level spritegroup (similar to "all" group)
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
