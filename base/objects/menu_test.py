import sys
from random import random

import numpy
import pygame
from pygame import Color

from base.animation import ease_in_out
from base.groups import EntityGroup
from base.objects.entities import Entity
from base.objects.gui_elements import GuiButton
from base.objects.gui_test import mouse_hovering_over, mouse_clicking
from base.objects.mixins import AnimationMixin
from volleyball_game.objects import ParticleEffect

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("Game base")
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
font = pygame.font.SysFont(None, 50)


class Menu(EntityGroup, AnimationMixin):
    def __init__(self):
        super().__init__()
        self.next_scene = self

    def update(self, *args):
        super().update()  # calls .update() on all children objects in self
        self.update_animation()
        self.state()
        self.check_children_status()
        return self.next_scene

    def check_children_status(self):
        for element in self:
            element.focus = mouse_hovering_over(element)
            element.click = mouse_clicking(element)

    def set_state(self, new_state):
        """ This setter is necessary because the lambdas used for button on_press callbacks don't
        allow us to assign to attributes. """
        self.state = new_state

    def set_next_scene(self, next_scene):
        self.next_scene = next_scene

    def animate_to(self, animation_function, next_scene_callable):
        """ Partial execution. State functions are called without any arguments, so if I want the
        animation function to know what state is next, I need to create this wrapper """

        def wrapped():
            return animation_function(next_scene_callable)

        return wrapped

    def animate(self, next_scene):
        """ dummy. Delete me """
        try:
            xs = ease_in_out(250, 750, 60)
            for button in self:
                button.x = xs[self.game_tick]
        except IndexError:
            self.next_scene = next_scene


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.explosion_button = GuiButton(
            0,
            200,
            200,
            50,
            text="random explosion",
            text_color=Color("white"),
            color=(100, 0, 100),
        )
        self.quit_button = GuiButton(
            0, 400, 200, 50, text="quit", text_color=Color("white"), color=(100, 0, 100),
        )
        self.settings_button = GuiButton(
            0, 300, 200, 50, text="settings", text_color=Color("white"), color=(100, 0, 100),
        )
        self.add(self.explosion_button, self.quit_button, self.settings_button)

    def animate_in(self):
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            xs = ease_in_out(-250, 250, 20)
            for button in self:
                button.x = xs[self.game_tick]
        except IndexError:
            self.state = self.idle

    def idle(self):
        if self.quit_button.click:
            self.state = self.animate_to(self.animate_out, None)
        if self.settings_button.click:
            self.state = self.animate_to(self.animate_out, SettingsMenu())
        if self.explosion_button.click:
            self.add(ParticleEffect(x=random() * SCREEN_WIDTH, y=random() * SCREEN_HEIGHT)),

    def animate_out(self, next_scene):
        try:
            xs = ease_in_out(250, 750, 20)
            for button in self:
                button.x = xs[self.game_tick]
        except IndexError:
            self.next_scene = next_scene
            self.kill()


class SettingsMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.back_button = GuiButton(
            0, 200, 200, 50, text="back", text_color=Color("white"), color=(100, 0, 100),
        )
        self.add(self.back_button)

    def animate_in(self):
        try:
            xs = ease_in_out(-250, 250, 20)
            self.back_button.x = xs[self.game_tick]
        except IndexError:
            self.state = self.idle

    def idle(self):
        if self.back_button.click:
            self.state = self.animate_to(self.animate_out, MainMenu())

    def animate_out(self, next_scene):
        try:
            xs = ease_in_out(250, 750, 20)
            self.back_button.x = xs[self.game_tick]
        except IndexError:
            self.next_scene = next_scene
            self.kill()


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def main():
    scene = MainMenu()

    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        scene.draw(screen)
        # scenes can return the next scene
        scene = scene.update()

        mainClock.tick(60)
        pygame.display.update()
        if scene is None:
            running = False


if __name__ == "__main__":
    main()
