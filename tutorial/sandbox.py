import pygame

from tutorial.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from tutorial.objects import Thing

pygame.init()


window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")

thing = Thing(x=50, y=200, width=40, height=60)

run = True
while run:
    pygame.time.delay(20)

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
    pygame.display.update()

pygame.quit()
