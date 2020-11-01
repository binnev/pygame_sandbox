from fighting_game.groups import Group, Scene


class SandBox(Scene):
    """ Sandbox scene to try stuff out """

    def __init__(self, game: FightingGame):
        super().__init__()
        self.game = game
        self.level = DefaultLevel()
        self.groups = [self.level]
        self.player1 = Debugger(500, 500, input=self.game.keyboard)
        self.level.add_character(self.player1)
        self.state = self.main

    def main(self):
        pass

    def update(self):
        super().update()
        self.level.hitboxes.empty()


