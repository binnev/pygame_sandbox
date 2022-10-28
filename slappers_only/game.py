from robingame.objects import Game

from slappers_only.scenes import SlappersOnlyScene


class SlappersOnly(Game):
    window_width = 500
    window_height = 500
    window_caption = "Slappers Only"
    screen_color = (255, 255, 255)
    fps = 60

    def __init__(self):
        super().__init__()
        self.scenes.add(SlappersOnlyScene())


if __name__ == "__main__":
    SlappersOnly().main()
