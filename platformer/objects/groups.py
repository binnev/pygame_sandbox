import pygame


class EntityGroup(pygame.sprite.Group):
    """Extends pygame's sprite.Group class. Overrides the .draw() method."""

    def draw(self, surface, debug=False):
        """draw all sprites onto the surface
        Group.draw(surface): return None
        Draws all of the member sprites onto the given surface.
        """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface, debug)
        self.lostsprites = []


class Level(EntityGroup):
    """The Level class holds sprite lists of all the platforms, characters, etc---all
    the game objects that are currently "in play". Create a subclass to create a
    specific level e.g. one with platforms in certain positions. """

    def __init__(self):
        super().__init__()
        self.platforms = EntityGroup()
        self.characters = EntityGroup()
        self.projectiles = EntityGroup()

    def add(self, *objects, type=None):
        # add to Level spritegroup (similar to "all" group)
        super().add(*objects)

        # todo: allow multiple types?
        if type == "platform":
            self.platforms.add(*objects)
        if type == "character":
            self.characters.add(*objects)
        if type == "projectile":
            self.projectiles.add(*objects)
        # give the object a reference to this level
        for obj in objects:
            obj.level = self
