import random

import numpy
from pygame import Rect
from robingame.objects import Entity, Group
from robingame.utils import random_float

from automata.backend import Backend
from automata.gravity.automaton import GravityAutomaton
from automata.gravity.body import Body
from automata.gravity.frontend import GravityFrontend, GravityMinimap
from automata.input_handler import KeyboardHandler
from automata.viewer import Viewer
from automata.viewport_handler import DefaultViewportHandler


class GravityScene(Entity):
    def __init__(self):
        super().__init__()

        automaton = GravityAutomaton()
        for _ in range(200):
            x = random_float(-500, 500)
            y = random_float(-500, 500)
            u = random_float(-2, 2)
            v = random_float(-2, 2)
            radius = random_float(1, 10)
            mass = radius * 9999999999
            automaton.add_body(x, y, body=Body(radius=radius, mass=mass, u=u, v=v))

        backend = Backend(automaton=automaton)
        main_rect = Rect(0, 0, 1000, 1000)
        main_map = Viewer(
            rect=main_rect,
            backend=backend,
            frontend=GravityFrontend(),
            controller=KeyboardHandler(),
            viewport_handler=DefaultViewportHandler(
                x=0,
                y=0,
                width=main_rect.width,
                height=main_rect.height,
            ),
        )
        mini_rect = Rect(0, 0, 200, 200)
        mini_rect.topright = (main_rect.right - 10, main_rect.top + 100)
        mini_map = Viewer(
            rect=mini_rect,
            backend=backend,
            frontend=GravityMinimap(),
            viewport_handler=main_map.viewport_handler,
        )

        self.children = Group()
        self.child_groups += [self.children]
        self.children.add(
            backend,
            main_map,
            mini_map,
        )
