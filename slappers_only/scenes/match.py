import time

from robingame.input import EventQueue
from robingame.objects import Entity, Group
from robingame.text.font import fonts

from slappers_only import images, conf
from slappers_only.events import UpdateScore, GameOver, SlowMotion
from slappers_only.scenes.main import SlappersOnlyScene


class SlapMatch(Entity):
    slow_motion = 0

    def __init__(self):
        super().__init__()
        self.background = Group()
        self.foreground = Group()
        self.gui = Group()
        self.child_groups = [
            self.background,
            self.foreground,
            self.gui,
        ]
        self.slappers_only_scene = SlappersOnlyScene()
        self.background.add(Background())
        self.foreground.add(self.slappers_only_scene)
        self.gui.add(ScoreDisplay(y=50))
        self.state = self.state_main

    def update(self):
        super().update()
        if self.slow_motion:
            self.slow_motion -= 1
            time.sleep(0.1)

    def state_main(self):
        for event in EventQueue.filter(type=GameOver.type):
            self.end_game(event.winner)
        for event in EventQueue.filter(type=SlowMotion.type):
            self.slow_motion += event.duration

    def end_game(self, winner):
        self.gui.add(GameOverText(winner=winner))
        # self.slappers_only_scene.paused = True
        self.state = self.state_game_over

    def state_game_over(self):
        pass


class Background(Entity):
    def draw(self, surface, debug=False):
        img = images.background_desert.loop(self.tick // 10)
        surface.blit(img, img.get_rect())
        super().draw(surface, debug)


class ScoreDisplay(Entity):
    def __init__(self, y):
        super().__init__()
        self.p1 = 0
        self.p2 = 0
        self.y = y

    def update(self):
        super().update()
        for event in EventQueue.filter(type=UpdateScore.type):
            self.p1 = event.p1
            self.p2 = event.p2

    def draw(self, surface, debug=False):
        fonts.cellphone_black.render(
            surface,
            text=f"{self.p1}-{self.p2}",
            x=0,
            y=self.y,
            scale=5,
            wrap=conf.WINDOW_WIDTH,
            align=0,
        )


class GameOverText(Entity):
    def __init__(self, winner: str):
        super().__init__()
        self.winner = winner

    def draw(self, surface, debug=False):
        fonts.cellphone_black.render(
            surface,
            text=f"{self.winner} wins!",
            x=0,
            y=conf.WINDOW_HEIGHT // 2,
            scale=5,
            wrap=conf.WINDOW_WIDTH,
            align=0,
        )
