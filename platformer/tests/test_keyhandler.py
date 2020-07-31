import pygame
from pygame import constants
import pytest

from platformer.objects.keyhandlers import KeyHandler

key_numbers = {value for key, value in constants.__dict__.items() if key.startswith("K")}


@pytest.mark.parametrize("key_number", key_numbers)
def test_empty_keyhandler(key_number):
    """When the keyhandler is empty (i.e. no ticks of the game have elapsed) then it
    should always return an Empty object. The Empty object spoofs the "keys" tuple,
    but always returns zero no matter the index supplied. """

    kh = KeyHandler()

    pressed = kh.get_pressed()
    down = kh.get_down()
    released = kh.get_released()

    assert pressed[key_number] == 0
    assert down[key_number] == 0
    assert released[key_number] == 0


def test_single_entry_keyhandler():
    keys = (0, 1, 1, 0, 1)
    kh = KeyHandler()
    kh.enqueue(keys)  # keyhandler now has one entry

    pressed = kh.get_pressed()
    down = kh.get_down()
    released = kh.get_released()

    # down should be the same as the most recent entry (keys)
    assert down == keys
    # when there's a single entry, `released` and `pressed` should both be empty
    # because they require information about the previous keys state which we don't have.
    for key_number in range(len(keys)):
        assert pressed[key_number] == 0
        assert released[key_number] == 0


def test_populated_keyhandler():
    kh = KeyHandler()
    keys = (0, 1, 1, 0, 1)
    kh.enqueue(keys)
    keys = (1, 1, 1, 0, 0)
    kh.enqueue(keys)

    expected_pressed = (1, 0, 0, 0, 0)
    expected_released = (0, 0, 0, 0, 1)

    pressed = kh.get_pressed()
    down = kh.get_down()
    released = kh.get_released()

    assert down == keys
    assert pressed == expected_pressed
    assert released == expected_released


def test_keyhandler_length():
    """Make sure the keyhandler maintains the correct length queue of key tuples"""
    queue_length = 6
    kh = KeyHandler(queue_length)
    for ii in range(10):
        kh.update((1, 0, 1))
        assert len(kh) <= queue_length
    assert len(kh) == queue_length
