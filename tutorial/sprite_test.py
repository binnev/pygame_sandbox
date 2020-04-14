import pygame

from tutorial.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from tutorial.objects import SpriteSheet

pygame.init()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sprite test")



run = True
frame = 0
while run:
    pygame.time.delay(1000 // 10)

    # ============= react to key presses ==============
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((0, 0, 0))
    # blit sprite here
    window.blit(strip, (10, SCREEN_HEIGHT // 4))
    index = frame % len(sprites)
    sprite = sprites[index]
    print(f"sprites = ", sprites)
    print(f"trying to load sprite", index)
    print("sprite = ", sprite)
    window.blit(sprite, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    pygame.display.update()
    frame += 1

pygame.quit()
