import sys

import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.sprite import Sprite

from fighting_game.inputs import KeyboardInput


class Group(pygame.sprite.Group):
    def draw(self, surface, debug=False):
        """ Draws all of the member sprites onto the given surface. """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface, debug)
        self.lostsprites = []

    def kill(self):
        """Kill all the sprites in this group. This is different from .empty().
        empty() does not kill the sprites in other groups."""
        for sprite in self:
            sprite.kill()


class Player(Sprite):
    color = Color("red")
    size = 10

    def __init__(self, x, y, input: KeyboardInput):
        super().__init__()
        self.input = input
        self.rect = Rect(0, 0, self.size, self.size)  # start in upright position
        self.rect.centerx = x
        self.rect.centery = y
        self.state = self.upright

    def draw(self, surface, debug=False):
        pygame.draw.rect(surface, self.color, self.rect)

    def update(self):
        self.state()

    def upright(self):
        """ Standing on end """
        input = self.input
        if input.is_pressed(input.LEFT):
            new_rect = Rect(0, 0, self.size * 2, self.size)
            new_rect.midright = self.rect.midleft
            self.rect = new_rect
            self.state = self.horizontal
        if input.is_pressed(input.RIGHT):
            new_rect = Rect(0, 0, self.size * 2, self.size)
            new_rect.midleft = self.rect.midright
            self.rect = new_rect
            self.state = self.horizontal
        if input.is_pressed(input.UP):
            new_rect = Rect(0, 0, self.size, self.size * 2)
            new_rect.midbottom = self.rect.midtop
            self.rect = new_rect
            self.state = self.vertical
        if input.is_pressed(input.DOWN):
            new_rect = Rect(0, 0, self.size, self.size * 2)
            new_rect.midtop = self.rect.midbottom
            self.rect = new_rect
            self.state = self.vertical

    def horizontal(self):
        """ Lying horizontally """
        input = self.input
        if input.is_pressed(input.LEFT):
            new_rect = Rect(0, 0, self.size, self.size)
            new_rect.midright = self.rect.midleft
            self.rect = new_rect
            self.state = self.upright
        if input.is_pressed(input.RIGHT):
            new_rect = Rect(0, 0, self.size, self.size)
            new_rect.midleft = self.rect.midright
            self.rect = new_rect
            self.state = self.upright
        if input.is_pressed(input.UP):
            self.rect.midbottom = self.rect.midtop
            self.state = self.horizontal
        if input.is_pressed(input.DOWN):
            self.rect.midtop = self.rect.midbottom
            self.state = self.horizontal

    def vertical(self):
        """ Lying vertically """
        input = self.input
        if input.is_pressed(input.LEFT):
            self.rect.midright = self.rect.midleft
            self.state = self.vertical
        if input.is_pressed(input.RIGHT):
            self.rect.midleft = self.rect.midright
            self.state = self.vertical
        if input.is_pressed(input.UP):
            new_rect = Rect(0, 0, self.size, self.size)
            new_rect.midbottom = self.rect.midtop
            self.rect = new_rect
            self.state = self.upright
        if input.is_pressed(input.DOWN):
            new_rect = Rect(0, 0, self.size, self.size)
            new_rect.midtop = self.rect.midbottom
            self.rect = new_rect
            self.state = self.upright


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.match_font("ubuntu"), 30)
        self.window = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("block_n_roll")
        self.clock = pygame.time.Clock()

        # input devices
        self.keyboard = KeyboardInput()
        self.input_devices = [self.keyboard]

        self.players = Group()
        self.groups = [
            self.players,
        ]

    def main(self):
        # setup here

        player = Player(50, 50, input=self.keyboard)
        self.players.add(player)
        run = True
        self.tick = 0
        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            for device in self.input_devices:
                device.read_new_inputs()

            for group in self.groups:
                group.update()

            self.window.fill(Color("black"))
            for group in self.groups:
                group.draw(self.window, debug=False)

            pygame.display.update()
            self.clock.tick(60)
            self.tick += 1

        pygame.quit()
        sys.exit()
