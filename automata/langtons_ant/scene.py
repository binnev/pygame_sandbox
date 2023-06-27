from pygame import Rect, Surface
from robingame.objects import Group, Entity
from robingame.text.font import fonts

from automata.backend import Backend
from automata.frontend import DrawRectFrontend, DrawRectMinimap
from automata.input_handler import KeyboardHandler
from automata.langtons_ant.utils import random_ants
from automata.viewer import Viewer
from .automaton import LangtonsAntAutomaton
from .frontend import LangtonsAntFrontend, LangtonsAntMinimap


class LangtonsAntScene(Entity):
    def __init__(self):
        super().__init__()
        self.children = Group()
        self.child_groups += [self.children]

        langtons_ant_automaton = LangtonsAntAutomaton()
        # ants, num_colours = random_ants(15)
        # for ant in ants:
        #     langtons_ant_automaton.add_ant(*ant)
        langtons_ant_automaton.add_ant((0, 0), "rl", 0)
        langtons_ant_backend = Backend(automaton=langtons_ant_automaton)
        main_rect = Rect(10, 100, 500, 500)
        mini_rect = Rect(0, 0, 100, 100)
        mini_rect.topright = (main_rect.right - 10, main_rect.top + 10)
        main_map = Viewer(
            rect=main_rect,
            backend=langtons_ant_backend,
            frontend=LangtonsAntFrontend(),
            controller=KeyboardHandler(),
        )
        mini_map = Viewer(
            rect=mini_rect,
            backend=langtons_ant_backend,
            frontend=LangtonsAntMinimap(),
            viewport_handler=main_map.viewport_handler,
        )

        self.children.add(
            langtons_ant_backend,
            main_map,
            mini_map,
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        fonts.cellphone_white.render(
            surface,
            text="Langton's Ant",
            x=0,
            y=10,
            scale=4,
            wrap=surface.get_width(),
            align=0,
        )
