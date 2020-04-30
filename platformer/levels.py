from platformer.objects import Platform
from platformer.sprites import SpriteGroup


class Level(SpriteGroup):
    """The Level class holds sprite lists of all the platforms, characters, etc---all
    the game objects that are currently "in play". Create a subclass to create a
    specific level e.g. one with platforms in certain positions. """

    def __init__(self):
        super().__init__()
        self.platforms = SpriteGroup()
        self.characters = SpriteGroup()
        self.projectiles = SpriteGroup()

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


class TestLevel(Level):

    def __init__(self):
        super().__init__()
        self.add(
            Platform(50, 100, 200, 30, can_fall_through=True),
            Platform(300, 200, 50, 30, can_fall_through=False),
            Platform(200, 400, 150, 30, can_fall_through=False),
            Platform(-10, 480, 550, 30, can_fall_through=False),
            type="platform",
        )


class FinalDestination(Level):

    def __init__(self):
        super().__init__()
        self.add(
            Platform(-10, 480, 550, 30, can_fall_through=False),
            type="platform",
        )