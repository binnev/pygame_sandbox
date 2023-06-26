import random

from pygame import Color, Rect
from robingame.objects import Game, Group, Entity

from automata.automatons import GameOfLifeAutomaton, LangtonsAntAutomaton
from automata.backends import Backend
from automata.controllers import KeyboardController
from automata.frontends import BitmapFrontend, BitmapMinimap, DrawRectFrontend, DrawRectMinimap
from automata.game_of_life import threshold, patterns
from automata.game_of_life.patterns import load_pattern
from automata.viewers import Viewer


class GameOfLife2(Game):
    fps = 64
    window_width = 1200
    window_height = 600
    window_caption = "Conway's Game of Life"
    screen_color = Color("black")
    ticks_per_frame = 1
    debug_color = Color("white")
    debug = False

    def __init__(self):
        super().__init__()
        self.scenes.add(
            MainScene2(
                underpopulation_threshold=threshold.UNDERPOPULATION,
                overpopulation_threshold=threshold.OVERPOPULATION,
                reproduction_threshold=threshold.REPRODUCTION,
            )
        )


def random_ants(n: int):
    ants = []
    num_colours = 0
    for _ in range(n):
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)
        rule_length = random.randint(2, 32)
        ruleset = "".join(random.choice("rl") for _ in range(rule_length))
        num_colours = max(num_colours, len(ruleset))
        ants.append(((x, y), ruleset, 0))
    return ants, num_colours


class MainScene2(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.children = Group()
        self.child_groups += [self.children]

        game_of_life_backend = Backend(
            automaton=GameOfLifeAutomaton(
                contents={
                    **load_pattern(patterns.ACORN),
                    # **load_pattern(patterns.SPINNER, shift=(10000, 10000)),
                },
                **kwargs,
            )
        )
        for _ in range(500):
            game_of_life_backend.iterate()
        game_of_life_backend.paused = True
        langtons_ant_automaton = LangtonsAntAutomaton()
        ants, num_colours = random_ants(5)
        for ant in ants:
            langtons_ant_automaton.add_ant(*ant)
        langtons_ant_backend = Backend(automaton=langtons_ant_automaton)

        keyboard_controller = KeyboardController()
        game_of_life_main = Viewer(
            rect=Rect(10, 10, 500, 500),
            backend=game_of_life_backend,
            frontend=BitmapFrontend(),
            controller=keyboard_controller,
        )
        game_of_life_mini = Viewer(
            rect=Rect(500 - 100, 20, 100, 100),
            backend=game_of_life_backend,
            frontend=BitmapMinimap(),
        )
        game_of_life_second = Viewer(
            rect=Rect(600, 10, 500, 500),
            backend=game_of_life_backend,
            frontend=DrawRectFrontend(),
            controller=KeyboardController(),
        )
        game_of_life_second_mini = Viewer(
            rect=Rect(600 + 500 - 100 - 10, 10 + 10, 100, 100),
            backend=game_of_life_backend,
            frontend=DrawRectMinimap(),
        )

        self.children.add(
            game_of_life_backend,
            langtons_ant_backend,
            game_of_life_main,
            game_of_life_mini,
            game_of_life_second,
            game_of_life_second_mini,
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
