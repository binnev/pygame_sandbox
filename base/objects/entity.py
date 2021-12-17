import pygame
from pygame import Surface

from base.objects.group import Group


class Entity(pygame.sprite.Sprite):
    """
    Finite State Machine:
    - self.tick is incremented every time the main game loop executes
    - self.state is executed every tick
    - when self.state changes, self.tick is set to 0

    Hierarchical structure:
    - Entities can be added to Groups to create a hierarchical structure
    - The order of groups in the .groups attribute determines the draw order; it's basically the
    layers
    """

    _state: "method" = lambda *args, **kwargs: None
    child_groups: list = []  # groups of child Entities belonging to this entity
    parent_groups: list  # groups of which this Entity is a member
    tick: int = 0  # iterations of the main game loop
    parental_name = "parent"

    def update(self):
        self.state()
        for group in self.child_groups:
            group.update()
        self.tick += 1

    def draw(self, surface: Surface, debug: bool = False):
        for group in self.child_groups:
            group.draw(surface, debug)

    def kill(self):
        """ Removes self from all groups it is a member of. """
        for group in self.child_groups:
            group.kill()
        super().kill()

    def add_to_group(self, *objects, group: Group):
        """
        Add an object to one of self.child_groups and give the object a reference to self as parent.
        This method is intended to be used by more specific methods e.g.:
        def add_particle(*objects):
            self.add_to_group(*objects, self.particles)
        """
        group.add(*objects)
        # give the object a reference to this scene
        for obj in objects:
            setattr(obj, self.parental_name, self)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        """Reset self.tick when state changes so we know how long we've been in the current
        state."""
        self._state = new_state
        self.tick = 0

    @property
    def parent_groups(self):
        return super().groups()

    @property
    def groups(self):
        raise Exception("NO")
