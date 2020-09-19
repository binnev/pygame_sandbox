import functools

import pygame

# todo: I suspect this is slow because it is blitting the entire "screen" to the screen every
#  tick. So stuff like hitboxes slows it down very quickly. As an optimisation, how about making
#  a Canvas singleton which respects alpha, drawing everything onto that using normal
#  Pygame.draw, and then blitting that canvas to screen once per tick?
from base.singleton import Singleton


class Canvas(pygame.Surface, Singleton):
    # todo: I don't think this should be a singleton. What if I want to have several canvases;
    #  one for the background, one for the foreground, etc?
    def __init__(self):
        """ This method is used by Singleton to create an instance of pygame.Surface which is
        stored as Canvas.instance. This surface has the same dimensions as the game
        window """
        display = pygame.display.get_surface()
        width = display.get_width()
        height = display.get_height()
        # create self; a pygame.Surface which respects transparency
        super().__init__((width, height))

    @classmethod
    def initialise(cls, *args, **kwargs):
        """ Need to wrap Singleton.initialise because we need to do some setup that involves
        mutating the instance object. Perhaps this is an indication that my current singleton
        implementation is not optimal... """
        super().initialise(*args, **kwargs)
        # this is not possible inside Canvas.__init__
        cls.instance = cls.instance.convert_alpha()
        return cls.instance

    @classmethod
    def blit_to_window(cls):
        window = pygame.display.get_surface()
        window.blit(cls.instance, (0, 0))


def get_it_together_pygame(func):
    @functools.wraps(func)
    def wrapper(screen, *args, **kwargs):
        # make a surface which does respect alpha values with the same dimensions as the screen
        dimensions = (screen.get_width(), screen.get_height())
        surface = pygame.Surface(dimensions).convert_alpha()
        surface.fill((0, 0, 0, 0))

        # pygame.draw *does* respect alpha values when you're not plotting to screen
        func(surface, *args, **kwargs)

        # now blit the whole surface to the screen
        screen.blit(surface, (0, 0))

    return wrapper


@get_it_together_pygame
def aaline(Surface, color, startpos, endpos, blend=1):
    return pygame.draw.aaline(Surface, color, startpos, endpos, blend)


@get_it_together_pygame
def aalines(Surface, color, closed, pointlist, blend=1):
    return pygame.draw.aalines(Surface, color, closed, pointlist, blend)


@get_it_together_pygame
def arc(Surface, color, Rect, start_angle, stop_angle, width=1):
    return pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width)


@get_it_together_pygame
def circle(Surface, color, pos, radius, width=0):
    return pygame.draw.circle(Surface, color, pos, radius, width)


@get_it_together_pygame
def ellipse(Surface, color, Rect, width=0):
    return pygame.draw.ellipse(Surface, color, Rect, width)


@get_it_together_pygame
def line(Surface, color, start_pos, end_pos, width=1):
    return pygame.draw.line(Surface, color, start_pos, end_pos, width)


@get_it_together_pygame
def lines(Surface, color, closed, pointlist, width=1):
    return pygame.draw.lines(Surface, color, closed, pointlist, width)


@get_it_together_pygame
def polygon(Surface, color, pointlist, width=0):
    return pygame.draw.polygon(Surface, color, pointlist, width)


@get_it_together_pygame
def rect(Surface, color, Rect, width=0):
    return pygame.draw.rect(Surface, color, Rect, width)
