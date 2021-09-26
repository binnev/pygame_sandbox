from random import random
from typing import Union

import pygame
from pygame.color import Color
from pygame.rect import Rect

from base.animation import ease_in_out
from base.objects.gui_test import mouse_hovering_over, mouse_clicking
from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.objects import Entity, Group, PhysicalEntity
from fighting_game.particles import Plume
from fighting_game.utils import pulsing_value


class Menu(Entity):
    """ Base menu class. """

    parental_name = "menu"

    def __init__(self, *groups):
        super().__init__(*groups)
        self.buttons = Group()
        self.child_groups = [self.buttons]

    def add_button(self, *objects):
        self.add_to_group(*objects, group=self.buttons)

    def update(self):
        self.update_buttons()
        super().update()

    def update_buttons(self):
        for element in self.buttons:
            element.is_focused = mouse_hovering_over(element)
            element.is_pressed = mouse_clicking(element)

    def animate_to(self, animation_function, next_scene_callable):
        """Partial execution. State functions are called without any arguments, so if I want the
        animation function to know what state is next, I need to create this wrapper"""

        def wrapped():
            return animation_function(next_scene_callable)

        return wrapped


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

    text_color: Union[Color, tuple]
    idle_color: Union[Color, tuple]
    focus_color: Union[Color, tuple]
    press_color: Union[Color, tuple]

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


class MyMenu(Menu):
    button_size = (200, 50)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.state = self.animate_in

    def animate_in(self):
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            xs = ease_in_out(-250, 250, 20)
            for button in self.buttons:
                button.x = xs[self.tick]
        except IndexError:
            self.state = self.idle

    def animate_out(self, next_scene):
        if next_scene:
            self.game.add_scene(next_scene)
        try:
            xs = ease_in_out(250, 750, 20)
            for button in self.buttons:
                button.x = xs[self.tick]
        except IndexError:
            self.kill()


class MainMenu(MyMenu):
    def __init__(self):
        super().__init__()
        self.explosion_button = ColoredButton(-999, 200, *self.button_size, text="random explosion")
        self.quit_button = ColoredButton(-999, 400, *self.button_size, text="quit")
        self.settings_button = ColoredButton(-999, 300, *self.button_size, text="settings")
        self.add_button(self.explosion_button, self.quit_button, self.settings_button)
        self.explosions = Group()
        self.child_groups.append(self.explosions)

    def idle(self):
        if self.quit_button.is_pressed:
            self.state = self.animate_to(self.animate_out, None)
        if self.settings_button.is_pressed:
            self.state = self.animate_to(self.animate_out, SettingsMenu())
        if self.explosion_button.is_pressed:
            self.explosions.add(
                Plume(
                    x=random() * SCREEN_WIDTH,
                    y=random() * SCREEN_HEIGHT,
                    angle_deg=random() * 360,
                )
            ),


class SettingsMenu(MyMenu):
    def __init__(self):
        super().__init__()
        self.back_button = ColoredButton(-999, 200, 200, 50, text="back")
        self.buttons.add(self.back_button)

    def idle(self):
        if self.back_button.is_pressed:
            self.state = self.animate_to(self.animate_out, MainMenu())
