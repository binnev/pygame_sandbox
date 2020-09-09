import pygame

from base.game import Game
from base.groups import EntityGroup
from base.objects.gui_elements import GuiButton


class GuiTestGround(Game):
    window_width = 500
    window_height = 500
    window_caption = "gui test ground"

    def __init__(self):
        super().__init__()
        self.gui_elements = EntityGroup()

    def main(self):
        """ Setup stuff before super().main() """
        self.window.fill((255, 255, 255))
        self.gui_elements.add(
            GuiButton(
                x=250,
                y=250,
                width=200,
                height=100,
                text="press me",
                text_color=(255, 255, 255, 255),
            )
        )
        super().main()

    def run(self):
        self.gui_elements.update()
        self.gui_elements.draw(self.window)


def main():
    game = GuiTestGround()
    game.main()
    pygame.quit()


if __name__ == "__main__":
    main()
