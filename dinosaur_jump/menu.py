from pygame import Surface

from base.animation import ease_in, ease_out
from base.gui.button import Button
from base.gui.menu import Menu
from base.objects import Entity, Group
from base.text.font import fonts
from dinosaur_jump import conf


class Toast(Entity):
    def __init__(self, text, y=10, **font_params):
        super().__init__()
        self.target_y = y
        self.y = -35
        self.text = text
        self.state = self.state_animate_in
        self.font_params = font_params

    def draw(self, surface: Surface, debug: bool = False):
        params = dict(wrap=conf.WINDOW_WIDTH, align=0, scale=5)
        params.update(self.font_params)
        fonts.cellphone_white.render(surface, text=self.text, x=0, y=self.y, **params)

    def state_animate_in(self):
        self.y = ease_out(start=-35, stop=self.target_y, num=15)[self.tick]
        if self.tick == 14:
            self.state = self.state_idle

    def state_animate_out(self):
        self.y = ease_in(start=self.target_y, stop=-35, num=15)[self.tick]
        if self.tick == 14:
            self.kill()

    def state_idle(self):
        pass

    def exit(self):
        self.state = self.state_animate_out


class DinoMenu(Menu):
    def exit(self):
        for group in self.child_groups:
            for entity in group:
                try:
                    entity.exit()
                except AttributeError:
                    pass
        self.state = self.state_exit

    def state_exit(self):
        """Die when all entities have finished animating out"""
        if not any(self.child_groups):
            self.kill()


class PauseMenu(DinoMenu):
    def __init__(self):
        super().__init__()
        self.entities = Group()
        self.child_groups += [self.entities]
        self.entities.add(Toast("PAUSED"))


class GameOverMenu(DinoMenu):
    def __init__(self, score: int):
        super().__init__()
        self.entities = Group()
        self.child_groups += [self.entities]
        self.entities.add(Toast("R.I.P.", scale=10))
        self.entities.add(Toast(f"Score: {score}", y=100))
        self.entities.add(Toast("PRESS SPACE TO CONTINUE", y=300))
