from pygame import Rect
from robingame.objects import Entity, Group

from automata.backend import Backend
from automata.gravity.automaton import GravityAutomaton
from automata.gravity.body import Body
from automata.gravity.frontend import GravityFrontend
from automata.input_handler import KeyboardHandler
from automata.viewer import Viewer


class GravityScene(Entity):
    def __init__(self):
        super().__init__()

        automaton = GravityAutomaton()
        sun = Body(mass=99999999999999, radius=100)
        automaton.add_body(x=500, y=500, body=sun)
        for x in range(0, 1000, 10):
            automaton.add_body(
                x=x,
                y=0,
                body=Body(mass=sun.mass / 1000, radius=5, v=10),
            )

        backend = Backend(automaton=automaton)
        viewer = Viewer(
            rect=Rect(0, 0, 1000, 1000),
            backend=backend,
            frontend=GravityFrontend(),
            controller=KeyboardHandler(),
        )

        self.children = Group()
        self.child_groups += [self.children]
        self.children.add(
            backend,
            viewer,
        )
