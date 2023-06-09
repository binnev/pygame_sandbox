from pygame import Color
from robingame.objects import Game, Group, Entity

from automata.automatons import GameOfLifeAutomaton
from automata.backends import Backend
from automata.controllers import KeyboardController
from automata.frontends import GameOfLifeFrontend, DeadSimpleFrontend, Minimap
from automata.game_of_life import threshold, patterns
from automata.game_of_life.patterns import load_pattern
from automata.viewers import Viewer


class GameOfLife2(Game):
    fps = 32
    window_width = 900
    window_height = 500
    window_caption = "Conway's Game of Life"
    screen_color = Color("black")
    ticks_per_frame = 1
    debug_color = Color("white")
    debug = True

    def __init__(self):
        super().__init__()
        self.scenes.add(
            MainScene2(
                underpopulation_threshold=threshold.UNDERPOPULATION,
                overpopulation_threshold=threshold.OVERPOPULATION,
                reproduction_threshold=threshold.REPRODUCTION,
            )
        )


class MainScene2(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.boards = Group()
        self.child_groups += [self.boards]

        backend = Backend(
            automaton=GameOfLifeAutomaton(
                contents=load_pattern(patterns.ACORN),
                **kwargs,
            )
        )
        keyboard_controller = KeyboardController()
        self.main_board = Viewer(
            rect=(10, 10, 1000, 500),
            backend=backend,
            frontend=DeadSimpleFrontend(),
            controller=keyboard_controller,
        )
        self.second_board = Viewer(
            rect=(20, 20, 100, 100),
            backend=backend,
            frontend=Minimap(),
        )
        self.boards.add(
            self.main_board,
            self.second_board,
        )


if __name__ == "__main__":
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
    GameOfLife2().main()
