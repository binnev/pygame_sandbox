# ======= this block has to come first to preserve the pygame loading order ==============
import pygame
from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT
pygame.init()
pygame.font.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("")
# ========================================================================================

from platformer.keyhandler import KeyHandler
from platformer.levels import TestLevel
from platformer.objects import Character

level = TestLevel()
character = Character(50, 200)
level.add(character, type="character")

clock = pygame.time.Clock()

key_handler = KeyHandler(queue_length=5)

run = True
while run:
    keys = pygame.key.get_pressed()
    key_handler.update(keys)

    if keys[pygame.K_ESCAPE]:
        character.x, character.y = 50, 200
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((255, 255, 255))

    # ================== update and draw =========================
    level.update(keys)
    level.draw(
        window,
        debug=True,
    )
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
