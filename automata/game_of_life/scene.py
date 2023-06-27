from pygame import Rect
from pygame import Surface
from robingame.objects import Group, Entity
from robingame.text.font import fonts

from automata.backend import Backend
from automata.frontend import DrawRectFrontend, DrawRectMinimap
from automata.input_handler import KeyboardHandler
from automata.viewer import Viewer
from . import patterns
from .automaton import GameOfLifeAutomaton


class GameOfLifeScene(Entity):
    """
    Interesting ones:
    (u, o, r)
    351 lots of squares
    042 static crystal
    142 static crystal 2
    242 crystal with marching ants
    332 lots of glider like things
    342 lots of glider like things
    032 constant activity; slow growing (133, 243)
    043 maze-like circle (143)
    053 fungal with staircase features
    064 fungal with vertical highways (163, 263, 373)
    073 fungal with horizontal highways (173, 183, 273, 283, 383)
    153 eye of sauron, staircase features
    253 self-similar fractal growth
    363 snowflake like growth
    353 extremely slow growing, rippling edges (483)
    """

    def __init__(self):
        super().__init__()
        self.children = Group()
        self.child_groups += [self.children]

        game_of_life_backend = Backend(
            automaton=GameOfLifeAutomaton(
                underpopulation_threshold=3,
                overpopulation_threshold=5,
                reproduction_threshold=3,
                contents={
                    **patterns.load(patterns.BLOCK),
                },
            )
        )
        main_rect = Rect(10, 100, 500, 500)
        mini_rect = Rect(0, 0, 100, 100)
        mini_rect.topright = (main_rect.right - 10, main_rect.top + 10)
        main_map = Viewer(
            rect=main_rect,
            backend=game_of_life_backend,
            frontend=DrawRectFrontend(),
            controller=KeyboardHandler(),
        )
        mini_map = Viewer(
            rect=mini_rect,
            backend=game_of_life_backend,
            frontend=DrawRectMinimap(),
            viewport_handler=main_map.viewport_handler,
        )

        self.children.add(
            game_of_life_backend,
            main_map,
            mini_map,
        )

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        fonts.cellphone_white.render(
            surface,
            text="Conway's Game of Life",
            x=0,
            y=10,
            scale=4,
            wrap=surface.get_width(),
            align=0,
        )
