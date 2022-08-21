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


def test_add_event_pygame_style():
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


def test_add_custom_dataclass_event_is_converted_to_event():
    # in events.py
    @dataclass
    class MyCustomEvent:
        type = pygame.event.custom_type()
        foo: str
        bar: int = 0

    # somewhere in the code
    EventQueue.add(MyCustomEvent(foo="foo"))
    EventQueue.add(MyCustomEvent(foo="foo", bar=420))

    EventQueue.update()

    # dataclasses should be converted to Events by EventQueue
    assert len(EventQueue.filter(type=MyCustomEvent.type, foo="foo")) == 2
    result1 = EventQueue.get(type=MyCustomEvent.type, foo="foo", bar=0)
    assert isinstance(result1, EventType)
    assert result1.foo == "foo"
    assert result1.bar == 0
    result2 = EventQueue.get(type=MyCustomEvent.type, foo="foo", bar=420)
    assert isinstance(result2, EventType)
    assert result2.foo == "foo"
    assert result2.bar == 420
