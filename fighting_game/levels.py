from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.groups import Level
from fighting_game.objects import Platform, BlastZone


class DefaultLevel(Level):
    def __init__(self):
        super().__init__()
        COURT_WIDTH = 1300
        NET_HEIGHT = 250 - 120

        self.ground = Platform(0, 0, COURT_WIDTH, 30)
        self.ground.x = SCREEN_WIDTH // 2
        self.ground.y = SCREEN_HEIGHT - 50

        self.net = Platform(0, 0, 10, NET_HEIGHT)
        self.net.x = SCREEN_WIDTH // 2
        self.net.y = SCREEN_HEIGHT - 300

        self.net2 = Platform(0, 0, 10, NET_HEIGHT // 4)
        self.net2.x = SCREEN_WIDTH // 2
        self.net2.y = SCREEN_HEIGHT - 75

        self.droppable = Platform(SCREEN_WIDTH // 4, 500, 300, 40, droppable=True)
        self.droppable2 = Platform(SCREEN_WIDTH // 4, 400, 300, 20, droppable=True)
        self.droppable3 = Platform(SCREEN_WIDTH * 3 // 4 - 120, 400, 100, 20, droppable=True)
        self.droppable4 = Platform(SCREEN_WIDTH * 3 // 4, 400, 100, 20, droppable=True)

        self.add_platform(
            self.ground,
            self.net,
            self.net2,
            self.droppable,
            self.droppable2,
            self.droppable3,
            self.droppable4,
        )


class Battlefield(Level):
    def __init__(self):
        super().__init__()

        ground = Platform(0, 0, 800, 1000)
        ground.x = SCREEN_WIDTH // 2
        ground.rect.top = SCREEN_HEIGHT - 150

        left_platform = Platform(0, 0, 100, 20, droppable=True)
        left_platform.x = ground.x - 200
        left_platform.y = ground.rect.top - 100

        right_platform = Platform(0, 0, 100, 20, droppable=True)
        right_platform.x = ground.x + 200
        right_platform.y = ground.rect.top - 100

        top_platform = Platform(0, 0, 100, 20, droppable=True)
        top_platform.x = ground.x
        top_platform.y = ground.rect.top - 200

        self.add_platform(
            ground,
            left_platform,
            right_platform,
            top_platform,
        )

        self.blast_zone = BlastZone(0, 0, 1200, 800)
        self.blast_zone.x = ground.x
        self.blast_zone.y = ground.rect.top - 300
        self.add_invisible_element(self.blast_zone)
