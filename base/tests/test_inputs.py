from unittest.mock import patch

import pygame
import pytest

from base.input import gamecube
from base.input.gamecube import (
    GamecubeController,
    ButtonInput,
)
from base.input.queue import InputQueue


@patch("pygame.joystick.Joystick")
@patch("base.input.gamecube.GamecubeControllerReader.get_values")
def test_gamecube_controller_basic(mock_get_values, mock_joystick):
    mock_get_values.return_value = (1, 0)  # A down, B not down
    pygame.init()

    controller = GamecubeController(controller_id=0)
    controller.read_new_inputs()
    assert controller[0] == (1, 0)
    assert controller.is_down(gamecube.A) == 1
    assert controller.is_down(gamecube.B) == 0
    assert controller.A.is_down == 1
    assert controller.B.is_down == 0


@patch("pygame.joystick.Joystick")
@patch("base.input.gamecube.GamecubeControllerReader.get_values")
def test_gamecube_controller_subclasses(mock_get_values, mock_joystick):
    mock_get_values.return_value = (1, 0)  # A down, B not down
    pygame.init()

    class Subclass(GamecubeController):
        A2 = ButtonInput(gamecube.A)

    class Subclass2(Subclass):
        A3 = ButtonInput(gamecube.A)

    class Subclass3(GamecubeController):
        B2 = ButtonInput(gamecube.B)

    subclass = Subclass(controller_id=0)
    subclass.read_new_inputs()
    assert subclass[0] == (1, 0)
    assert subclass.is_down(gamecube.A) == 1
    assert subclass.is_down(gamecube.B) == 0
    assert subclass.A.is_down == 1
    assert subclass.A2.is_down == 1
    with pytest.raises(AttributeError):
        assert subclass.A3.is_down == 1
    with pytest.raises(AttributeError):
        assert subclass.B2.is_down == 1
    assert subclass.B.is_down == 0

    subclass2 = Subclass2(controller_id=0)
    subclass2.read_new_inputs()
    assert subclass2[0] == (1, 0)
    assert subclass2.is_down(gamecube.A) == 1
    assert subclass2.is_down(gamecube.B) == 0
    assert subclass2.A.is_down == 1
    assert subclass2.A2.is_down == 1
    assert subclass2.A3.is_down == 1
    with pytest.raises(AttributeError):
        assert subclass.B2.is_down == 1
    assert subclass2.B.is_down == 0

    subclass3 = Subclass3(controller_id=0)
    subclass3.read_new_inputs()
    assert subclass3[0] == (1, 0)
    assert subclass3.is_down(gamecube.A) == 1
    assert subclass3.is_down(gamecube.B) == 0
    assert subclass3.A.is_down == 1
    with pytest.raises(AttributeError):
        assert subclass3.A2.is_down == 1
    with pytest.raises(AttributeError):
        assert subclass3.A3.is_down == 1
    assert subclass3.B.is_down == 0
    assert subclass3.B2.is_down == 0


@pytest.mark.parametrize(
    "input, expected_rising_edges, expected_falling_edges",
    [
        ([], 0, 0),  # no buffered values shouldn't crash things
        ([0, 0, 0], 0, 0),  # some values but less than the buffer
        ([0, 0, 1], 1, 0),
        ([1, 0, 0], 0, 1),
        ([0, 1, 0], 1, 1),
        ([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 0, 0),  # too far in past
        ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 1, 0),
        ([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], 1, 1),
        ([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], 2, 1),
    ],
)
def test_buffered_inputs(input, expected_rising_edges, expected_falling_edges):
    BUFFER_LENGTH = 5
    queue = InputQueue(queue_length=100)
    for value in input:
        queue.append([value])

    rising, falling = queue.buffered_inputs(key=0, buffer_length=BUFFER_LENGTH)

    assert rising == queue.buffered_presses(0, BUFFER_LENGTH) == expected_rising_edges
    assert falling == queue.buffered_releases(0, BUFFER_LENGTH) == expected_falling_edges
