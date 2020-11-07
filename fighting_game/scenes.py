from fighting_game.groups import Scene, Group
from fighting_game.inputs import KeyboardInput
from fighting_game.levels import DefaultLevel
from fighting_game.objects import Debugger, Debugger2


class SandBox(Scene):
    """ Sandbox scene to try stuff out """

    game: "FightingGame"  # parent scene

    def __init__(self):
        super().__init__()
        self.levels = Group()
        self.gui_elements = Group()
        self.groups = [self.levels, self.gui_elements]
        self.state = self.setup

    def setup(self):
        self.level = DefaultLevel()
        self.levels.add(self.level)  # didn't pass a ref to self.
        self.player1 = Debugger(500, 500, input=self.game.keyboard)
        self.player2 = Debugger(600, 500, input=KeyboardInput())
        self.player3 = Debugger2(600, 500, input=KeyboardInput())
        self.level.add_character(self.player1, self.player2, self.player3)
        self.state = lambda: None

    def update(self):
        super().update()
