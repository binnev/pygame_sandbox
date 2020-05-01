from platformer.levels import Level
from platformer.objects import Platform


class TestLevel(Level):

    def __init__(self):
        super().__init__()
        self.add(
            Platform(50, 100, 200, 30, can_fall_through=True),
            Platform(300, 200, 50, 30, can_fall_through=False),
            Platform(200, 400, 150, 30, can_fall_through=False),
            Platform(-10, 480, 550, 30, can_fall_through=False),
            type="platform",
        )


class FinalDestination(Level):

    def __init__(self):
        super().__init__()
        self.add(
            Platform(-10, 480, 550, 30, can_fall_through=False),
            type="platform",
        )
