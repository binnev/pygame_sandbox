import pygame
pygame.init()
window = pygame.display.set_mode((500, 500))

from platformer.sprites import BLOB_SPRITES

SPRITE_WIDTH = 32

clock = pygame.time.Clock()
run = True
ii = 0
while run:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((0, 255, 0))
    jj = 0
    for sprite_name, sprite_animation in BLOB_SPRITES.items():
        frame = sprite_animation.get_frame(ii)
        window.blit(frame, (jj * 100, jj * 100))
        jj += 1

    pygame.display.flip()
    clock.tick(50)
    ii += 1

pygame.quit()
