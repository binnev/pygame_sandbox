import pygame.key
from pygame import Surface

from base.input import EventQueue
from base.objects import Entity, Group
from base.text.font import fonts
from dinosaur_jump import images, conf
from dinosaur_jump.objects.background import ScrollingBackground
from dinosaur_jump.objects.characters import Dino, Ptero


class DinoJumpScene(Entity):
    """The actual game with the running dino. Doesn't include any menus etc."""

    def __init__(self):
        super().__init__()
        self.paused = False
        self.entities = Group()
        self.background = Group()
        self.child_groups = [
            self.background,
            self.entities,
        ]
        self.entities.add(Dino(x=100, y=450))
        self.entities.add(Ptero(x=conf.WINDOW_WIDTH + 16 - 100, y=150))
        self.background.add(ScrollingBackground(0, 250, images.mountains2, speed=5))
        self.background.add(ScrollingBackground(0, 250, images.mountains1, speed=10))
        self.background.add(ScrollingBackground(0, 250, images.grass, speed=20))

    def update(self):
        if not self.paused:
            super().update()


class DinoJumpManager(Entity):
    """Handles playing the game and the pause menus etc."""

    def __init__(self):
        super().__init__()
        self.scenes = Group()
        self.menus = Group()
        self.child_groups = [
            self.scenes,
            self.menus,
        ]
        self.dino_scene = DinoJumpScene()
        self.scenes.add(self.dino_scene)
        self.state = self.state_play

    def state_play(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_ESCAPE):
            self.dino_scene.paused = True
            self.state = self.state_pause

    def state_pause(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_ESCAPE):
            self.dino_scene.paused = False
            self.state = self.state_play

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        if self.dino_scene.paused:
            fonts.cellphone_white.render(
                surface, "PAUSED", x=0, y=0, wrap=conf.WINDOW_WIDTH, align=0, scale=5
            )
