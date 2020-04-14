import pygame

from tutorial.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from tutorial.objects import Thing, Platform

pygame.init()


window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")

class Level:
    pass

level = Level()
level.platforms = [
    Platform([50, 100, 200, 30], can_fall_through=True),
    Platform([200, 300, 150, 30], can_fall_through=False),
    Platform([5, 480, 480, 30], can_fall_through=False),
]
thing = Thing(x=50, y=200, width=40, height=60, level=level)

run = True
while run:
    pygame.time.delay(1000//50)

    # ============= react to key presses ==============
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # make a window class to handle flipping the y axis.
    # simple subclass with a property for y?

    window.fill((0, 0, 0))
    thing.update(keys, window)
    for platform in level.platforms:
        platform.draw(window)
    pygame.display.update()

pygame.quit()
