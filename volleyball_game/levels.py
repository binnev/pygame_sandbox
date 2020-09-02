from base.groups import Level
from base.objects.entities import Platform
from volleyball_game import conf


class VolleyballCourt(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        COURT_WIDTH = 1100
        NET_HEIGHT = 250
        self.add(
            Platform(
                conf.SCREEN_WIDTH // 2 - COURT_WIDTH // 2,
                conf.SCREEN_HEIGHT - 20,
                COURT_WIDTH,
                30,
                can_fall_through=False,
            ),
            Platform(
                conf.SCREEN_WIDTH // 2,
                conf.SCREEN_HEIGHT - NET_HEIGHT - 50,
                10,
                NET_HEIGHT,
                can_fall_through=False,
            ),
            # Platform(260, 260, 50, 50, can_fall_through=False),
            type="platform",
        )
