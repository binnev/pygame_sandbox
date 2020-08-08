import pygame

from base.game import Game
from volleyball_game import conf
from volleyball_game.keys import Player1, Player2
from volleyball_game.levels import VolleyballCourt
from volleyball_game.objects import Stickman


class VolleyballGame(Game):
    fps = conf.FPS
    window_width = conf.SCREEN_WIDTH
    window_height = conf.SCREEN_HEIGHT
    window_caption = "LAG SPIKE"

    def run(self):
        self.window.fill((255, 255, 255))
        level = VolleyballCourt(game=self)
        player1 = Stickman(
                conf.SCREEN_WIDTH // 4,
                3 * conf.SCREEN_HEIGHT // 4,
                keymap=Player1,
                facing_right=True,
            )
        level.add(
            player1,
            type="character",
        )
        level.add(
            Stickman(
                3 * conf.SCREEN_WIDTH // 4,
                3 * conf.SCREEN_HEIGHT // 4,
                keymap=Player2,
                facing_right=False,
            ),
            type="character",
        )

        run = True
        debug = False
        ii = 0
        while run:
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
            print(player1.u)

            # draw stuff
            self.window.fill((255, 255, 255))
            level.draw(
                self.window, debug=debug,
            )
            pygame.display.flip()
            self.clock.tick(self.fps)
