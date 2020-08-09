from base.groups import Level
from base.objects.entities import Platform
from volleyball_game import conf


class VolleyballCourt(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(
            Platform(-10, 480, conf.SCREEN_WIDTH * 1.1, 30, can_fall_through=False),
            Platform(conf.SCREEN_WIDTH // 2, 250, 10, 200, can_fall_through=False),
            # Platform(260, 260, 50, 50, can_fall_through=False),
            type="platform",
        )
