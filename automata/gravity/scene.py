from pygame import Rect
from robingame.objects import Entity, Group

from automata.backend import Backend
from automata.gravity.automaton import GravityAutomaton
from automata.gravity.body import Body
from automata.gravity.frontend import GravityFrontend
from automata.input_handler import KeyboardHandler
from automata.viewer import Viewer
from automata.viewport_handler import DefaultViewportHandler


class GravityScene(Entity):
    def __init__(self):
        super().__init__()

        automaton = GravityAutomaton()
        sun = Body(mass=99999999999999, radius=100)
        automaton.add_body(x=0, y=0, body=sun)
        for x in range(200, 400, 7):
            automaton.add_body(
                x=x,
                y=0,
                body=Body(mass=sun.mass / 100000, radius=5, v=7),
            )

        backend = Backend(automaton=automaton)
        rect = Rect(0, 0, 1000, 1000)
        viewer = Viewer(
            rect=rect,
            backend=backend,
            frontend=GravityFrontend(),
            controller=KeyboardHandler(),
            viewport_handler=DefaultViewportHandler(
                x=0,
                y=0,
                width=rect.width,
                height=rect.height,
            ),
        )

        self.children = Group()
        self.child_groups += [self.children]
        self.children.add(
            backend,
            viewer,
        )
