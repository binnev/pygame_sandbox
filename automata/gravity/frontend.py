import pygame.draw
from pygame import Surface, Color

from automata.gravity.automaton import GravityAutomaton
from automata.viewport_handler import FloatRect


class GravityFrontend:
    def draw(
        self,
        surface: Surface,
        automaton: GravityAutomaton,
        viewport: FloatRect,
        debug: bool = False,
    ):
        """
        For now just draw everything
        """
        surface.fill(Color("black"))
        for xy, body in automaton.contents.items():
            pygame.draw.circle(surface, Color("red"), center=xy, radius=body.radius)
