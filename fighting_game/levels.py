from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.groups import Level
from fighting_game.objects import Platform


class DefaultLevel(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        COURT_WIDTH = 1300
        NET_HEIGHT = 250 - 120

        self.ground = Platform(0, 0, COURT_WIDTH, 30)
        self.ground.x = SCREEN_WIDTH // 2
        self.ground.y = SCREEN_HEIGHT - 50

        self.net = Platform(0, 0, 10, NET_HEIGHT)
        self.net.x = SCREEN_WIDTH // 2
        self.net.y = SCREEN_HEIGHT - 300

        self.droppable = Platform(500, 500, 300, 40, droppable=True)

        self.add(self.ground, self.net, self.droppable, type="platform")
