import sys

import numpy
import pygame

from base.groups import EntityGroup
from base.objects.gui_elements import GuiButton
from base.objects.gui_test import mouse_hovering_over, mouse_clicking
from base.objects.mixins import AnimationMixin

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("Game base")
screen = pygame.display.set_mode((500, 500), 0, 32)
font = pygame.font.SysFont(None, 50)


def animate_ease(start, stop, num, function):
    distance = stop - start
    ease = numpy.array(list(map(function, numpy.linspace(0, 1, num))))
    output = start + ease * distance
    return output


def ease_in(start, stop, num, power=3):
    return animate_ease(start, stop, num, function=lambda x: x ** power)


def ease_out(start, stop, num, power=3):
    return animate_ease(start, stop, num, function=lambda x: 1 - (1 - x) ** power)


class Menu(EntityGroup, AnimationMixin):
    def update(self, *args):
        super().update()  # call .update() on all children objects in self
        self.ticks_elapsed += 1
        self.state()
        self.check_children_status()

    def check_children_status(self):
        for element in self:
            element.focus = mouse_hovering_over(element)
            element.click = mouse_clicking(element)


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = self.animate_in
        self.button1 = GuiButton(0, 0, 200, 50)
        self.button2 = GuiButton(0, 0, 200, 50)
        self.add(self.button1, self.button2)

    def animate_in(self):
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            xs = ease_out(0, 250, 30)
            ys = ease_out(0, 200, 30)
            self.button1.x = xs[self.ticks_elapsed]
            self.button1.y = ys[self.ticks_elapsed]

            ys = ease_out(0, 300, 30)
            self.button2.x = xs[self.ticks_elapsed]
            self.button2.y = ys[self.ticks_elapsed]
        except IndexError:
            self.state = self.idle

    def idle(self):
        pass  # waiting for user input here.


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
