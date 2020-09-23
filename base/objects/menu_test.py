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

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("Game base")
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
font = pygame.font.SysFont(None, 50)


class Menu(EntityGroup, AnimationMixin):
    def update(self, *args):
        super().update()  # call .update() on all children objects in self
        self.update_animation()
        self.state()
        self.check_children_status()

    def check_children_status(self):
        for element in self:
            element.focus = mouse_hovering_over(element)
            element.click = mouse_clicking(element)


class Explosion(Entity, AnimationMixin):
    def __init__(self, x, y):
        self.original_position = x, y
        size = 5
        super().__init__(x, y, size, size)

    def update(self):
        self.update_animation()
        self.rect.height *= 2
        self.rect.width *= 2
        self.xy = self.original_position
        if self.ticks_elapsed == 6:
            self.kill()

    def draw(self, surface, debug=False):
        pygame.draw.ellipse(surface, Color("orange"), self.rect)


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.button1 = GuiButton(
            0,
            200,
            200,
            50,
            text="random explosion",
            text_color=Color("white"),
            on_click=lambda: self.add(
                Explosion(x=random() * SCREEN_WIDTH, y=random() * SCREEN_HEIGHT)
            ),
        )

        def goto_state(new_state):
            self.state = new_state

        self.button2 = GuiButton(
            0,
            300,
            200,
            50,
            text="quit",
            text_color=Color("white"),
            on_click=lambda: goto_state(self.animate_out),
        )
        self.add(self.button1, self.button2)

    def animate_in(self):
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            xs = ease_in_out(-250, 250, 60)
            self.button1.x = xs[self.ticks_elapsed]
            self.button2.x = xs[self.ticks_elapsed]
        except IndexError:
            self.state = self.idle

    def idle(self):
        pass  # waiting for user input here.

    def animate_out(self):
        try:
            xs = ease_in_out(250, 750, 60)
            self.button1.x = xs[self.ticks_elapsed]
            self.button2.x = xs[self.ticks_elapsed]
        except IndexError:
            pygame.quit()
            sys.exit()


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def main():
    menu = MainMenu()

    while True:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        menu.update()
        menu.draw(screen)

        mainClock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    main()
