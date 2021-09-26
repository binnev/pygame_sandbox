import sys
import time

import pygame

from base.game import Game
from base.groups import EntityGroup
from base.objects.gui_elements import GuiButton


def allow_exit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()


def mouse_hovering_over(element):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return element.rect.collidepoint(mouse_x, mouse_y)


def mouse_clicking(element):
    mouse_buttons = pygame.mouse.get_pressed()
    return mouse_hovering_over(element) and any(mouse_buttons)


button_params = dict(
    width=200,
    height=100,
    color=pygame.color.THECOLORS["red"],
    text_color=(255, 255, 255, 255),
)


class GuiTestGround(Game):
    window_width = 500
    window_height = 500
    window_caption = "gui test ground"

    def __init__(self):
        super().__init__()

    def main(self):
        """ outermost game loop """
        self.window.fill((0, 0, 0))
        text = self.font.render("WELCOME SCREEN", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)
        pygame.display.flip()
        time.sleep(1)

        self.main_menu()

        self.window.fill((0, 0, 0))
        text = self.font.render("EXIT SCREEN", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)
        pygame.display.flip()
        time.sleep(1)

    def main_menu(self):
        run = True
        next_menu = None

        # animate menu in here
        self.window.fill((0, 100, 100))
        text = self.font.render("start animation main menu", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)
        pygame.display.flip()
        time.sleep(1)

        while run:
            allow_exit()
            self.window.fill((255, 255, 255))
            text = self.font.render("Main menu", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.midtop = (self.window_width // 2, 10)
            self.window.blit(text, textRect)

            game_button = GuiButton(x=250, y=100, text="game", **button_params)
            settings_button = GuiButton(x=250, y=250, text="settings", **button_params)
            quit_button = GuiButton(x=250, y=400, text="quit", **button_params)

            buttons = EntityGroup()
            buttons.add(game_button, settings_button, quit_button)
            for button in buttons:
                button.is_focused = mouse_hovering_over(button)
                button.is_pressed = mouse_clicking(button)

            buttons.update()
            buttons.draw(self.window, debug=False)

            if game_button.click:
                next_menu = self.game
                run = False
            if settings_button.click:
                next_menu = self.settings
                run = False
            if quit_button.click:
                pygame.quit()

            self.clock.tick(self.fps)
            pygame.display.flip()

        # animate menu out here
        self.window.fill((0, 100, 100))
        text = self.font.render("end animation main menu", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)
        pygame.display.flip()
        time.sleep(1)

        if next_menu:
            return next_menu()  # fixme: this doesn not prevent infinite recursion.

    def game(self):
        print("GAME")

    def settings(self):
        run = True
        next_menu = None

        # animate menu in here
        self.window.fill((100, 0, 100))
        text = self.font.render("start animation settings", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)
        pygame.display.flip()
        time.sleep(1)

        while run:
            allow_exit()
            self.window.fill((255, 255, 255))
            text = self.font.render("Settings", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.midtop = (self.window_width // 2, 10)
            self.window.blit(text, textRect)

            back_button = GuiButton(x=250, y=250, text="back", **button_params)
            buttons = EntityGroup()
            buttons.add(back_button)

            for thing in buttons:
                thing.is_focused = mouse_hovering_over(thing)
                thing.is_pressed = mouse_clicking(thing)

            buttons.update()
            buttons.draw(self.window, debug=False)

            if back_button.click:
                next_menu = self.main_menu
                run = False  # cascade back up the tree to the main menu

            self.clock.tick(self.fps)
            pygame.display.flip()

        # animate menu out here
        self.window.fill((100, 0, 100))
        text = self.font.render("end animation settings", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.window_width // 2, self.window_height // 2)
        self.window.blit(text, textRect)
        pygame.display.flip()
        time.sleep(1)

        if next_menu:
            return next_menu()  # fixme: this doesn not prevent infinite recursion.


def main():
    game = GuiTestGround()
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
