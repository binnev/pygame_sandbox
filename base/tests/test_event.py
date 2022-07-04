from dataclasses import dataclass
from unittest.mock import patch

import pygame.event
from pygame.event import EventType, Event
from base.input.event import EventQueue


@patch("pygame.event.get")
def test_update(mock):
    assert EventQueue.events == []

    mock.return_value = ["foo"]
    EventQueue.update()
    assert EventQueue.events == ["foo"]

    mock.return_value = ["bar"]
    EventQueue.update()
    assert EventQueue.events == ["bar"]


def test_add_event_pygame_style(display_init):
    # in events.py we store an int representing the event type
    TEST_EVENT = pygame.event.custom_type()

    # event is created in the bowels of the code and we can pass any old stuff to the event __init__
    EventQueue.add(Event(TEST_EVENT, foo="foo", bar=69))

    # it shouldn't appear on the EventQueue.events list yet
    assert EventQueue.events == []

    # but after update, it should
    EventQueue.update()
    event = EventQueue.get(type=TEST_EVENT, foo="foo", bar=69)
    assert isinstance(event, EventType)

    # we trust that the event listener knows what attributes to look for
    assert event.foo == "foo"
    assert event.bar == 69
    assert event.type == TEST_EVENT

