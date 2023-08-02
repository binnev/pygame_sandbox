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
        automaton.bodies.append(
            Body(
                x=500,
                y=500,
                mass=99999999999999,
                radius=100,
            ),
        )
        for x in range(0, 1000, 10):
            automaton.bodies.append(Body(x=x, y=0, mass=1000, radius=5, v=10))

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
