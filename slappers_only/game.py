from robingame.objects import Game

from slappers_only.objects import Character


class SlappersOnly(Game):
    window_width = 1000
    window_height = 500
    window_caption = "Slappers Only"
    screen_color = (255, 255, 255)
    fps=10

    def __init__(self):
        super().__init__()
        self.scenes.add(Character(x=100, y=100))


if __name__ == "__main__":
    SlappersOnly().main()
