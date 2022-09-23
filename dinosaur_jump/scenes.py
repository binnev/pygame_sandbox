import pygame.key
from pygame import Surface
from pygame.event import Event
from pygame.sprite import groupcollide

from base.input import EventQueue
from base.objects import Entity, Group
from base.text.font import fonts
from dinosaur_jump import images, conf, sounds, events
from dinosaur_jump.menu import PauseMenu, GameOverMenu, TextField
from dinosaur_jump.objects import ScrollingBackground, Dino, Ptero, Cactus
from dinosaur_jump.score import Score
from dinosaur_jump.utils import should_spawn


class DinoJumpScene(Entity):
    """The actual game with the running dino. Doesn't include any menus etc."""

    cactus_timer = cactus_cooldown = 5000
    ptero_timer = ptero_cooldown = 5000

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
        self.score = 0

    def update(self):
        if not self.paused:
            super().update()
        if self.tick % 10 == 0:
            self.score += 1

    def state_day(self):
        self.ptero_timer += 1
        self.cactus_timer += 1

        if should_spawn(self.cactus_cooldown, self.cactus_timer):
            self.spawn_cactus()

        if should_spawn(self.ptero_cooldown, self.ptero_timer):
            self.spawn_ptero()

        self.check_collisions()

    def spawn_cactus(self):
        self.cactus_timer = 0
        self.obstacles.add(Cactus(x=conf.WINDOW_WIDTH + 50, y=475))

    def spawn_ptero(self):
        self.ptero_timer = 0
        self.obstacles.add(Ptero(x=conf.WINDOW_WIDTH + 16, y=150))

    def check_collisions(self):
        if groupcollide(self.players, self.obstacles, False, False):
            sounds.hit.play()
            sounds.crowd_ohh.play()
            self.paused = True
            EventQueue.add(Event(events.game_over))

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        fonts.cellphone_white.render(
            surface, text=f"score: {self.score}", wrap=conf.WINDOW_WIDTH, align=1, scale=2
        )


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
        self.start_new_game()

    def start_new_game(self):
        self.dino_scene = DinoJumpScene()
        self.scenes.add(self.dino_scene)
        self.state = self.state_play

    def state_play(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_ESCAPE):
            self.dino_scene.paused = True
            self.state = self.state_pause
            self.menu = PauseMenu()
            self.menus.add(self.menu)
        if EventQueue.filter(type=events.game_over):
            self.state = self.state_game_over
            self.menu = GameOverMenu(score=self.dino_scene.score)
            self.menus.add(self.menu)

    def state_pause(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_ESCAPE):
            self.dino_scene.paused = False
            self.state = self.state_play
            self.menu.exit()

    def state_game_over(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_SPACE):
            self.menu.exit()
            self.scenes.kill()
            self.start_new_game()
