from platformer.objects.entities import Platform
from platformer.objects.groups import Level


class TestLevel(Level):
    def __init__(self, game):
        super().__init__(game)
        self.add(
            Platform(50, 100, 200, 30, can_fall_through=True),
            Platform(50, 300, 50, 30, can_fall_through=True),
            Platform(150, 310, 50, 30, can_fall_through=True),
            Platform(250, 290, 50, 30, can_fall_through=True),
            Platform(300, 200, 50, 30, can_fall_through=False),
            Platform(200, 400, 150, 30, can_fall_through=False),
            Platform(-10, 480, 550, 30, can_fall_through=False),
            type="platform",
        )


class FinalDestination(Level):
    def __init__(self, game):
        super().__init__(game)
        self.add(
            Platform(-10, 480, 550, 30, can_fall_through=False), type="platform",
        )


class VolleyballCourt(Level):
    def __init__(self, game):
        super().__init__(game)
        self.add(
            Platform(-10, 480, 550, 30, can_fall_through=False),
            Platform(250, 250, 10, 200, can_fall_through=False),
            type="platform",
        )
