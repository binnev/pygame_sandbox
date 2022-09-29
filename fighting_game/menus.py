from random import random

from robingame.gui.button import ColoredButton
from robingame.gui.menu import MyMenu
from robingame.objects import Group
from fighting_game.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from fighting_game.particles import Plume
from fighting_game.scenes import SandBox


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
