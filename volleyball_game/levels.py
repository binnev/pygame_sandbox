from base.groups import Level
from base.objects.entities import Platform
from volleyball_game import conf


class VolleyballCourt(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        COURT_WIDTH = 1300
        NET_HEIGHT = 250 - 120
        self.ground = Platform(
            conf.SCREEN_WIDTH // 2 - COURT_WIDTH // 2,
            conf.SCREEN_HEIGHT - 20,
            COURT_WIDTH,
            30,
            can_fall_through=False,
        )
        self.net = Platform(
            conf.SCREEN_WIDTH // 2,
            conf.SCREEN_HEIGHT - NET_HEIGHT - 50 - 120,
            10,
            NET_HEIGHT,
            can_fall_through=False,
        )
        self.add(self.ground, self.net, type="platform")
