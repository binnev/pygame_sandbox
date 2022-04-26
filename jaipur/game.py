from base.objects import Game


class Jaipur(Game):
    fps = 60
    window_width = 1000
    window_height = 1000
    window_caption = "Jaipur"
    font_name = "ubuntu"
    font_size = 50

    def __init__(self):
        super().__init__()
        self.add_scene(JaipurMatch())
