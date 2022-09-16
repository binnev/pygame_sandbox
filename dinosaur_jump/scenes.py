import pygame.key
from pygame.sprite import groupcollide

from base.input import EventQueue
from base.objects import Entity, Group
from dinosaur_jump import images, conf
from dinosaur_jump.menu import PauseMenu
from dinosaur_jump.objects import ScrollingBackground, Dino, Ptero, Cactus


class DinoJumpScene(Entity):
    """The actual game with the running dino. Doesn't include any menus etc."""

    cactus_timer = cactus_cooldown = 120
    ptero_timer = ptero_cooldown = 360

    def __init__(self):
        super().__init__()
        self.paused = False
        self.players = Group()
        self.obstacles = Group()
        self.background = Group()
        self.child_groups = [
            self.background,
            self.obstacles,
            self.players,
        ]
        self.players.add(Dino(x=100, y=475))
        self.background.add(ScrollingBackground(0, 250, images.mountains2, speed=2))
        self.background.add(ScrollingBackground(0, 250, images.mountains1, speed=5))
        self.background.add(ScrollingBackground(0, 250, images.grass, speed=10))
        self.state = self.state_day

    def update(self):
        if not self.paused:
            super().update()

    def state_day(self):
        self.ptero_timer -= 1
        self.cactus_timer -= 1

        if self.cactus_timer == 0:
            self.spawn_cactus()

        if self.ptero_timer == 0:
            self.spawn_ptero()

        self.check_collisions()

    def spawn_cactus(self):
        self.cactus_timer = self.cactus_cooldown
        self.obstacles.add(Cactus(x=conf.WINDOW_WIDTH + 50, y=475))

    def spawn_ptero(self):
        self.ptero_timer = self.ptero_cooldown
        self.obstacles.add(Ptero(x=conf.WINDOW_WIDTH + 16, y=150))

    def check_collisions(self):
        if groupcollide(self.players, self.obstacles, False, False):
            self.paused = True


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
