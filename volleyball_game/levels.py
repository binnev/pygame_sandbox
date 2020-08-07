from base.groups import Level
from base.objects.entities import Platform


class VolleyballCourt(Level):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(
            Platform(-10, 480, 550, 30, can_fall_through=False),
            Platform(250, 250, 10, 200, can_fall_through=False),
            type="platform",
        )
