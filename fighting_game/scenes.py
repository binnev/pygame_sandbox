import pygame

from base.event import EventQueue
from fighting_game.characters.hawko import Hawko
from fighting_game.objects import Entity, Group
from fighting_game.characters.debugger import Debugger
from fighting_game.levels import Battlefield


class SandBox(Entity):
    """ Sandbox scene to try stuff out """

    game: "FightingGame"  # parent scene

    def __init__(self):
        super().__init__()
        self.levels = Group()
        self.gui_elements = Group()
        self.enemies = Group()
        self.players = Group()
        self.child_groups = [self.levels, self.gui_elements]
        self.state = self.state_setup

    def state_setup(self):
        self.level = Battlefield()
        self.levels.add(self.level)  # didn't pass a ref to self.
        self.players.add(Hawko(600, 500, input=self.game.controller0))
        self.enemies.add(Debugger(1000, 500, facing_right=False, input=self.game.controller1))
        self.level.add_character(*self.players, *self.enemies)
        self.state = self.state_main

    def state_main(self):
        from fighting_game.menus.base import MainMenu

        if not self.enemies:
            self.enemies.add(Debugger(1000, 500, facing_right=False, input=self.game.controller1))
            self.level.add_character(*self.enemies)
        if not self.players:
            self.players.add(Hawko(600, 500, input=self.game.controller0))
            self.level.add_character(*self.players)
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.add_scene(MainMenu())
                self.kill()

    def update(self):
        super().update()
