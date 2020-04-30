import pygame
pygame.init()
pygame.font.init()
from collections import deque

from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")

from platformer.objects import Platform, Character, Level, MovingEntity

level = Level()
# Platforms
level.add_objects(Platform(50, 100, 200, 30, can_fall_through=True),
                  Platform(300, 200, 50, 30, can_fall_through=False),
                  Platform(200, 400, 150, 30, can_fall_through=False),
                  Platform(-10, 480, 550, 30, can_fall_through=False),
                  type="platform")
# Character object
# character = MovingEntity(50, 200, 40, 60)
character = Character(50, 200)
level.add_objects(character, type="character")

clock = pygame.time.Clock()




keypress_queue = []
keypress_queue_length = 5

run = True
while run:
    keys = pygame.key.get_pressed()
    keypress_queue.append(keys)

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
