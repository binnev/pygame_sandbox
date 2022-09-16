import pygame.key

from base.input import EventQueue
from base.objects import Entity, Group
from dinosaur_jump import images, conf
from dinosaur_jump.menu import PauseMenu
from dinosaur_jump.objects import ScrollingBackground, Dino, Ptero, Cactus


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
        self.entities.add(Ptero(x=conf.WINDOW_WIDTH + 16, y=150))
        self.entities.add(Cactus(x=conf.WINDOW_WIDTH + 50, y=450))
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
            self.menus.add(PauseMenu())

    def state_pause(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_ESCAPE):
            self.dino_scene.paused = False
            self.state = self.state_play
