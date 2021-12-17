from random import random
from typing import Union

import numpy
import pygame
from pygame.color import Color
from pygame.rect import Rect

from base.animation import ease_in_out
from base.event import EventQueue
from base.objects.gui_test import mouse_hovering_over, mouse_clicking
from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.game import FightingGame
from fighting_game.objects import Entity, Group, PhysicalEntity
from fighting_game.particles import Plume
from fighting_game.scenes import SandBox
from fighting_game.utils import pulsing_value


class Menu(Entity):
    """ Base menu class. """

    game = FightingGame
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

    def state_idle(self):
        pass

    def update_buttons(self):
        """todo: if you wanted to make this really efficient, you could only perform updates if
        an event is detected."""
        mouse_click = any(event.type == pygame.MOUSEBUTTONDOWN for event in EventQueue.events)
        for button in self.buttons:
            button.is_focused = False
            button.is_pressed = False
            if mouse_hovering_over(button):
                if mouse_click:
                    button.is_pressed = True
                else:
                    button.is_focused = True


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
    button_width = 200
    button_height = 50
    button_size = (button_width, button_height)
    transition_length = 40

    def __init__(self, *groups):
        super().__init__(*groups)
        self.state = self.animate_in

    @property
    def game_rect(self):
        return self.game.window.get_rect()

    def arrange_buttons_vertically(self):
        num_buttons = len(self.buttons)
        top = self.game.window.get_rect().top + 150
        bottom = top + self.button_height * 1.5 * num_buttons
        ys = numpy.linspace(top, bottom, num=num_buttons)
        for button, y in zip(self.buttons, ys):
            button.y = y

    def animate_in(self):
        if self.tick == 0:
            self.arrange_buttons_vertically()
        try:
            # todo: maybe make these generators so that you're not generating the entire array
            #  each tick
            centerx = self.game_rect.centerx
            far_left = self.game_rect.left - self.button_width
            xs = ease_in_out(far_left, centerx, self.transition_length)
            for button in self.buttons:
                button.x = xs[self.tick]
        except IndexError:
            self.state = self.state_idle

    def animate_out(self, next_scene=None):
        def _animate_out():
            if next_scene:
                self.game.add_scene(next_scene)
            try:

                centerx = self.game_rect.centerx
                far_right = self.game_rect.right + self.button_width
                xs = ease_in_out(centerx, far_right, self.transition_length)
                for button in self.buttons:
                    button.x = xs[self.tick]
            except IndexError:
                self.kill()

        return _animate_out


class MainMenu(MyMenu):
    def __init__(self):
        super().__init__()
        self.explosion_button = ColoredButton(-999, 200, *self.button_size, text="random explosion")
        self.settings_button = ColoredButton(-999, 260, *self.button_size, text="settings")
        self.game_button = ColoredButton(-999, 330, *self.button_size, text="fighting game")
        self.quit_button = ColoredButton(-999, 400, *self.button_size, text="quit")
        self.add_button(
            self.explosion_button,
            self.settings_button,
            self.game_button,
            self.quit_button,
        )
        self.explosions = Group()
        self.child_groups.append(self.explosions)

    def state_idle(self):
        """
        Currently, having the menu check the button statuses and trigger an action in the idle
        state is more reliable than using the Button.on_press. This is because the menu sees a
        button press and immediately changes state. And once it's not in the idle state,
        the menu is no longer _reading_ button presses. This means we don't get double button
        clicks from a long mouse press. The Button.on_press route is more correct, but we need
        some additional logic to distinguish between _pressed_ and _down_.
        """
        if self.quit_button.is_pressed:
            self.state = self.animate_out()
        if self.settings_button.is_pressed:
            self.state = self.animate_out(next_scene=SettingsMenu())
        if self.game_button.is_pressed:
            self.state = self.animate_out(next_scene=SandBox())
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
        self.dummy_button1 = ColoredButton(-999, 200, 200, 50, text="1")
        self.dummy_button2 = ColoredButton(-999, 200, 200, 50, text="2")
        self.dummy_button3 = ColoredButton(-999, 200, 200, 50, text="3")
        self.dummy_button4 = ColoredButton(-999, 200, 200, 50, text="4")
        self.dummy_button5 = ColoredButton(-999, 200, 200, 50, text="5")
        self.dummy_button6 = ColoredButton(-999, 200, 200, 50, text="6")
        self.back_button = ColoredButton(-999, 200, 200, 50, text="back")
        self.buttons.add(
            self.dummy_button1,
            self.dummy_button2,
            self.dummy_button3,
            self.dummy_button4,
            self.dummy_button5,
            self.dummy_button6,
            self.back_button,
        )

    def state_idle(self):
        if self.back_button.is_pressed:
            self.state = self.animate_out(next_scene=MainMenu())
