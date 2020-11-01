



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

        self.net2 = Platform(0, 0, 10, NET_HEIGHT // 4)
        self.net2.x = SCREEN_WIDTH // 2
        self.net2.y = SCREEN_HEIGHT - 75

        self.droppable = Platform(SCREEN_WIDTH // 4, 500, 300, 40, droppable=True)
        self.droppable2 = Platform(SCREEN_WIDTH // 4, 400, 300, 20, droppable=True)
        self.droppable3 = Platform(SCREEN_WIDTH * 3 // 4 - 120, 400, 100, 20, droppable=True)
        self.droppable4 = Platform(SCREEN_WIDTH * 3 // 4, 400, 100, 20, droppable=True)

        self.add(
            self.ground,
            self.net,
            self.net2,
            self.droppable,
            self.droppable2,
            self.droppable3,
            self.droppable4,
            type="platform",
        )