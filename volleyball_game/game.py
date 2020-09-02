import pygame

from base import draw
from base.game import Game
from base.keyhandler import KeyHandler
from volleyball_game import conf
from volleyball_game.keys import Player1, Player2
from volleyball_game.levels import VolleyballCourt
from volleyball_game.objects import Stickman, Volleyball, Bowlingball


class VolleyballGame(Game):
    fps = conf.FPS
    window_width = conf.SCREEN_WIDTH
    window_height = conf.SCREEN_HEIGHT
    window_caption = "LAG SPIKE"
    ticks_per_frame = conf.TICKS_PER_SPRITE_FRAME

    def run(self):
        self.window.fill((255, 255, 255))
        level = VolleyballCourt(game=self)
        player1 = Stickman(
            conf.SCREEN_WIDTH // 4, 3 * conf.SCREEN_HEIGHT // 4, keymap=Player1, facing_right=True,
        )
        level.add(
            player1, type="character",
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
        frame_by_frame = False
        ii = 0
        while run:
            ii += 1
            KeyHandler.read_new_keypresses()
            self.window.fill((255, 255, 255))  # clear screen

            if KeyHandler.is_pressed(pygame.K_ESCAPE):
                run = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button = pygame.mouse.get_pressed()
                    x, y = pygame.mouse.get_pos()
                    if button[0]:
                        level.add(Volleyball(x, y), type="projectile")
                    if button[-1]:
                        level.add(Bowlingball(x, y), type="projectile")

            if KeyHandler.is_pressed(pygame.K_F1):
                debug = not debug
            if KeyHandler.is_pressed(pygame.K_F2):
                frame_by_frame = not frame_by_frame
            if KeyHandler.is_pressed(pygame.K_b):
                level.add(
                    Volleyball(conf.SCREEN_WIDTH // 4, conf.SCREEN_HEIGHT // 4), type="projectile"
                )
            if KeyHandler.is_down(pygame.K_r):
                transparent_red = (*pygame.color.THECOLORS["red"][:3], 150)
                draw.rect(self.window, transparent_red, (100, 100, 60, 200))

            # wait for button press before advancing
            if frame_by_frame:
                if not KeyHandler.is_pressed(pygame.K_F3):
                    print(f"waiting on frame {ii}")
                    continue  # skip the rest of the actions
                else:
                    print("advanced 1 frame")

            level.update()
            print(player1.u)

            # draw stuff
            level.draw(
                self.window, debug=debug,
            )
            pygame.display.flip()

            # destroy hitboxes
            level.hitboxes.kill()

            self.clock.tick(self.fps)
