from unittest.mock import patch

from base.event import EventQueue


@patch("pygame.event.get")
def test_event_queue(mock):
    assert EventQueue.events == []

    mock.return_value = ["foo"]
    EventQueue.update()
    assert EventQueue.events == ["foo"]

    mock.return_value = ["bar"]
    EventQueue.update()
    assert EventQueue.events == ["bar"]
