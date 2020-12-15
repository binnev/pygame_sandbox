from fighting_game.levels import *
from fighting_game.characters import *
from fighting_game.game import *


class SandBox(Scene):
    """ Sandbox scene to try stuff out """

    game: FightingGame  # parent scene

    def __init__(self):
        super().__init__()
        self.levels = Group()
        self.gui_elements = Group()
        self.enemies = Group()
        self.players = Group()
        self.groups = [self.levels, self.gui_elements]
        self.state = self.setup

    def setup(self):
        self.level = Battlefield()
        self.levels.add(self.level)  # didn't pass a ref to self.
        self.players.add(Debugger(500, 500, input=self.game.controller0))
        self.enemies.add(Debugger(700, 500, input=Keyboard0()))
        self.level.add_character(*self.players, *self.enemies)
        self.state = lambda: None

    def update(self):
        super().update()
        if not self.enemies:
            self.enemies.add(Debugger(700, 500, input=Keyboard0()))
            self.level.add_character(*self.enemies)
        if not self.players:
            self.players.add(Debugger(500, 500, input=self.game.controller0))
            self.level.add_character(*self.players)

