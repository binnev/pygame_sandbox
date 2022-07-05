from typing import Callable

import pygame
from pygame import Color
from pygame.rect import Rect

from base.objects import PhysicalEntity
from base.utils import pulsing_value


class Button(PhysicalEntity):
    # These attributes are set by whatever is managing the buttons. The button itself doesn't
    # check these. This allows the menu to use keyboard/controller inputs to shift focus,
    # as well as the mouse.
    is_focused: bool  # does the button have focus? (e.g. mouse hovering over)
    is_pressed: bool  # is the button down right now
    font_name = "ubuntu"
    font_size = 20

    # callable hooks passed by the creator/owner of the Button that trigger some external
    # functionality.
    on_press: Callable
    on_focus: Callable
    on_release: Callable
    on_unfocus: Callable

    text_color: Color

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text=None,
        on_press=None,
        on_focus=None,
        on_release=None,
        on_unfocus=None,
    ):
        self.width = width
        self.height = height
        self.text = text
        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.is_focused = False
        self.is_pressed = False
        self.on_press = on_press or (lambda: None)
        self.on_focus = on_focus or (lambda: None)
        self.on_release = on_release or (lambda: None)
        self.on_unfocus = on_unfocus or (lambda: None)
        self.font = pygame.font.Font(pygame.font.get_default_font(), self.font_size)
        self.state = self.state_idle
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(Color("red"))
        if self.text:
            text = self.font.render(self.text, True, Color("black"))
            textRect = text.get_rect()
            textRect.center = self.image.get_rect().center
            self.image.blit(text, textRect)
        super().__init__()

    def draw(self, surface, debug=False):
        super().draw(surface, debug)

    def update(self):
        super().update()

    def state_idle(self):
        if self.is_focused:
            self.focus()
        if self.is_pressed:
            self.press()
        # subclasses can override to provide additional functionality

    def state_focus(self):
        if not self.is_focused:
            self.unfocus()
        if self.is_pressed:
            self.press()
        # subclasses can override to provide additional functionality

    def state_press(self):
        if not self.is_pressed:
            self.release()
        # subclasses can override to provide additional functionality

    def press(self):
        self.on_press(self)
        self.state = self.state_press

    def focus(self):
        self.on_focus(self)
        self.state = self.state_focus

    def release(self):
        self.on_release(self)
        self.state = self.state_focus if self.is_focused else self.state_idle

    def unfocus(self):
        self.on_unfocus(self)
        self.state = self.state_idle


class ColoredButton(Button):
    idle_color = (100, 0, 100)  # Color("purple")
    focus_color = Color("orange")
    press_color = Color("red")
    text_color = Color("white")

    def state_idle(self):
        super().state_idle()
        self.color = (pulsing_value(self.tick, 80, 150, 0.03), 30, 75)

    def state_focus(self):
        super().state_focus()
        self.color = (
            pulsing_value(self.tick, 180, 255, 0.3),
            pulsing_value(self.tick, 100, 163, 0.3),
            0,
        )

    def state_press(self):
        super().state_press()
        self.color = self.press_color
