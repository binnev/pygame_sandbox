from automata.advent_of_code.day11.classes import OctopusBoard
from automata.advent_of_code.day9.classes import Caverns
from fighting_game.menus import MyMenu, ColoredButton, Group


class MainMenu(MyMenu):
    def __init__(self):
        super().__init__()
        self.day9_button = ColoredButton(-999, 200, *self.button_size, text="Day 9 (smoke caverns)")
        self.day11_button = ColoredButton(-999, 260, *self.button_size, text="Day 11 (octopi)")
        self.day17_button = ColoredButton(-999, 260, *self.button_size, text="Day 17 (ballistics)")
        self.quit_button = ColoredButton(-999, 400, *self.button_size, text="quit")
        self.buttons.add(
            self.day9_button,
            self.day11_button,
            self.day17_button,
            self.quit_button,
        )
        self.explosions = Group()

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
        if self.day9_button.is_pressed:
            self.state = self.animate_out(next_scene=Caverns(self.game))
        if self.day11_button.is_pressed:
            self.state = self.animate_out(next_scene=OctopusBoard(self.game))
