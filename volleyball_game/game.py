import pygame

from base.game import Game
from volleyball_game.keys import Player1, Player2
from volleyball_game.levels import VolleyballCourt
from volleyball_game.objects import Stickman


class VolleyballGame(Game):
    fps = 60
    window_height = 500
    window_width = 1000
    window_caption = "LAG SPIKE"

    def run(self):
        self.window.fill((255, 255, 255))
        level = VolleyballCourt(game=self)
        level.add(Stickman(100, 100, keymap=Player1, facing_right=True), type="character")
        level.add(Stickman(300, 100, keymap=Player2, facing_right=False), type="character")

        run = True
        debug = False
        ii = 0
        while run:
            print(f"inside VolleyballGame.run. ii={ii}")
            ii += 1
            keys = pygame.key.get_pressed()
            self.key_handler.update(keys)
            pressed = self.key_handler.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            if pressed[pygame.K_F1]:
                debug = not debug

            level.update(keys)

            # draw stuff
            self.window.fill((255, 255, 255))
            level.draw(
                self.window, debug=debug,
            )
            pygame.display.flip()
            self.clock.tick(self.fps)
