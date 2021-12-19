import pygame
from pygame import Color
from pygame.rect import Rect

from base.objects import PhysicalEntity
from base.utils import pulsing_value


class Button(PhysicalEntity):
    # These attributes are set by whatever is managing the buttons. The button itself doesn't
    # check these. This allows the menu to use keyboard/controller inputs to shift focus,
    # as well as the mouse.
    is_focused: bool  # is the button currently selected?
    is_pressed: bool  # is the button currently being clicked?
    font_name = "ubuntu"
    font_size = 20
    # callable hooks passed by the creator/owner of the Button that trigger some external
    # functionality.
    on_press: callable
    on_focus: callable

    text_color: Color
    idle_color: Color
    focus_color: Color
    press_color: Color

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text=None,
        on_press: callable = None,
        on_focus: callable = None,
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
        self.font = pygame.font.Font(pygame.font.get_default_font(), self.font_size)
        self.color = self.idle_color
        self.state = self.state_idle
        super().__init__()

    @property
    def image(self):
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.fill(self.color)
        if self.text:
            text = self.font.render(self.text, True, self.text_color)
            textRect = text.get_rect()
            textRect.center = image.get_rect().center
            image.blit(text, textRect)
        return image

    def draw(self, surface, debug=False):
        super().draw(surface, debug)

    def update(self):
        self.color = self.idle_color
        super().update()

    def state_idle(self):
        if self.is_focused:
            self.state = self.state_focus
        if self.is_pressed:
            self.state = self.state_press

    def state_focus(self):
        self.on_focus()
        if not self.is_focused:
            self.state = self.state_idle
        if self.is_pressed:
            self.state = self.state_press

    def state_press(self):
        self.on_press()
        if not self.is_pressed:
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
