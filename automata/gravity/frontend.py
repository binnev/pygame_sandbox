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
        for body in automaton.bodies:
            pygame.draw.circle(surface, Color("red"), center=(body.x, body.y), radius=body.radius)
