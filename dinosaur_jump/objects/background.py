from pygame import Surface

from base.objects import Entity


class ScrollingBackground(Entity):
    def __init__(self, x, y, image: Surface, speed: int):
        super().__init__()
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed
        self.progress = 0

    def draw(self, surface: Surface, debug: bool = False):
        surface.blit(self.image, (self.x - self.progress, self.y))
        surface.blit(self.image, (self.x - self.progress + self.image.get_width(), self.y))

    def update(self):
        self.progress = (self.progress + self.speed) % self.image.get_width()
