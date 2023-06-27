import matplotlib
from pygame import Surface, Color

from automata.automaton import Automaton
from automata.frontend import (
    DrawRectFrontend,
    Transform,
    draw_circle,
    linspace_colors,
    DrawRectMinimap,
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
        num_colors = max(len(ant.ruleset) for ant in automaton.ants)
        self.colors = linspace_colors(num_colors, self.colormap)
        super().draw(surface, automaton, viewport, debug)
        # also draw ants
        image_rect_uv = surface.get_rect()
        transform = Transform(viewport, image_rect_uv)
        for ant in automaton.ants:
            u, v = transform.point(ant.xy)
            self.draw_ant(surface, u, v, transform.scale)

    def draw_ant(self, surface: Surface, u: float, v: float, size: float):
        """Draw a white-black bullseye"""
        draw_circle(surface, Color("white"), u, v, size)
        draw_circle(surface, Color("black"), u, v, size * 0.75)


class LangtonsAntMinimap(DrawRectMinimap):
    colormap = LangtonsAntFrontend.colormap

    def draw(
        self, surface: Surface, automaton: Automaton, viewport: FloatRect, debug: bool = False
    ):
        num_colors = max(len(ant.ruleset) for ant in automaton.ants)
        self.colors = linspace_colors(num_colors, self.colormap)
        super().draw(surface, automaton, viewport, debug)
