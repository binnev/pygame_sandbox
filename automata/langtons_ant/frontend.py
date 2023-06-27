from pygame import Surface, Color

from automata.frontend import (
    DrawRectFrontend,
    Transform,
    draw_circle,
)
from automata.langtons_ant.automaton import LangtonsAntAutomaton
from automata.viewport_handler import FloatRect


class LangtonsAntFrontend(DrawRectFrontend):
    def draw(
        self,
        surface: Surface,
        automaton: LangtonsAntAutomaton,
        viewport: FloatRect,
        debug: bool = False,
    ):
        """Also draw ants"""
        super().draw(surface, automaton, viewport, debug)
        image_rect_uv = surface.get_rect()
        transform = Transform(viewport, image_rect_uv)
        for ant in automaton.ants:
            u, v = transform.point(ant.xy)
            self.draw_ant(surface, u, v, transform.scale)

    def draw_ant(self, surface: Surface, u: float, v: float, size: float):
        """Draw a white-black bullseye"""
        draw_circle(surface, Color("white"), u, v, size)
        draw_circle(surface, Color("black"), u, v, size * 0.75)
