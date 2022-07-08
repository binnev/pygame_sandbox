from unittest.mock import MagicMock, patch

import pytest
from pygame import Color

from base.gui.button import Button


def test_button_instantiation_default_values(font_init):
    button = Button(x=0, y=0, width=100, height=50)
    assert button.is_pressed == False
    assert button.is_focused == False
    assert button.rect == (-50, -25, 100, 50)
    assert button.image.get_at((0, 0)) == Color("red")
    assert button.state.__name__ == "state_idle"


def test_default_empty_hooks_dont_break_anything(font_init):
    button = Button(x=0, y=0, width=100, height=50)
    button.on_focus()
    button.on_unfocus()
    button.on_press()
    button.on_release()


@pytest.mark.parametrize("hook_name", ["on_press", "on_release", "on_focus", "on_unfocus"])
def test_button_state_switching_calls_hooks_passing_button_instance(hook_name, font_init):
    """
    If we pass `on_press=our_hook` to Button, and we call button.on_press, we expect our hook to
    be called as well
    """
    mock = MagicMock()
    button = Button(x=0, y=0, width=100, height=50, **{hook_name: mock})
    method = getattr(button, hook_name)
    method.__call__()
    mock.assert_called_with(button)


def test_button_with_overridden_method_still_calls_hook(font_init):
    """
    If we override Button.on_press, the super().on_press() call should still hit our hook.
    """

    class TestButton(Button):
        def on_press(self):
            print("custom behaviour yay")
            super().on_press()
            print("more custom behaviour yay")

    mock = MagicMock()
    button = TestButton(x=0, y=0, width=100, height=50, on_press=mock)
    button.on_press()
    mock.assert_called_with(button)


@patch("base.gui.button.Button.on_unfocus")
@patch("base.gui.button.Button.on_focus")
@patch("base.gui.button.Button.on_release")
@patch("base.gui.button.Button.on_press")
def test_updating_is_pressed_and_is_focused_correctly_updates_state(
    mock_on_press,
    mock_on_release,
    mock_on_focus,
    mock_on_unfocus,
    font_init,
):
    # tick: initial state
    button = Button(x=0, y=0, width=100, height=50)
    assert button.state.__name__ == "state_idle"

    # tick: mouse hovers over button
    button.is_focused = True
    button.update()
    assert button.state.__name__ == "state_focus"
    assert mock_on_press.call_count == 0
    assert mock_on_release.call_count == 0
    assert mock_on_focus.call_count == 1
    assert mock_on_unfocus.call_count == 0

    # tick: mouse presses button
    button.is_pressed = True
    button.update()
    assert button.state.__name__ == "state_press"
    assert mock_on_press.call_count == 1
    assert mock_on_release.call_count == 0
    assert mock_on_focus.call_count == 1
    assert mock_on_unfocus.call_count == 0

    # tick: mouse releases button; should go back to state_focus
    button.is_pressed = False
    button.update()
    assert button.state.__name__ == "state_focus"
    assert mock_on_press.call_count == 1
    assert mock_on_release.call_count == 1
    assert mock_on_focus.call_count == 1
    assert mock_on_unfocus.call_count == 0

    # tick: mouse stops hovering
    button.is_focused = False
    button.update()
    assert button.state.__name__ == "state_idle"
    assert mock_on_press.call_count == 1
    assert mock_on_release.call_count == 1
    assert mock_on_focus.call_count == 1
    assert mock_on_unfocus.call_count == 1

    # tick: instantly clicked without hovering
    button.is_pressed = True
    button.update()
    assert button.state.__name__ == "state_press"
    assert mock_on_press.call_count == 2
    assert mock_on_release.call_count == 1
    assert mock_on_focus.call_count == 1
    assert mock_on_unfocus.call_count == 1

    # tick: releasing when is_focused=False should return it to state_idle
    button.is_pressed = False
    button.update()
    assert button.state.__name__ == "state_idle"
    assert mock_on_press.call_count == 2
    assert mock_on_release.call_count == 2
    assert mock_on_focus.call_count == 1
    assert mock_on_unfocus.call_count == 1
