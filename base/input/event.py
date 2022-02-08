import pygame


class EventQueue:
    """Pygame's pygame.event.get() gets the events in the queue, but also empties the queue. This
    class solves that"""

    # this is intentional. I want to store the events on the class. Only one game will be active
    # at once, so we'll never need more than one instance of this class.
    events = []

    @classmethod
    def update(cls):
        events = pygame.event.get()
        cls.events = events

    @classmethod
    def filter(cls, event_type: int):
        return [event for event in cls.events if event.type == event_type]
