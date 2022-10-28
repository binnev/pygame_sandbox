from robingame.input import EventQueue
from robingame.objects import Entity, Group

from slappers_only.events import SetValue
from slappers_only.scenes.character_select import CharacterSelectScreen
from slappers_only.scenes.match import SlapMatch


class Manager(Entity):
    p1: int
    p2: int

    def __init__(self):
        super().__init__()
        self.scenes = Group()
        self.child_groups = [self.scenes]
        # self.scenes.add(CharacterSelectScreen(callback=lambda: self.scenes.add(SlapMatch())))
        self.scenes.add(SlapMatch())

    def update(self):
        super().update()
        for event in EventQueue.filter(type=SetValue.type):
            self.p1 = event.p1
            self.p2 = event.p2
            print(f"{self.p1=}")
            print(f"{self.p2=}")
