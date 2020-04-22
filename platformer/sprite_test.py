from pathlib import Path

import pygame

from platformer.sprites import SpriteSheet, SpriteAnimation

SPRITE_WIDTH = 32
pygame.init()
window = pygame.display.set_mode((500, 500))
filename = Path("sprites/pixel_art_test/blob_stand.png")
sprite_sheet = SpriteSheet(filename.as_posix())
frames = sprite_sheet.load_sheet(32, 32, scale=5)
sprite_animation = SpriteAnimation(frames)

clock = pygame.time.Clock()
run = True
ii = 0
while run:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((0, 255, 0))
    sheet = sprite_sheet.sheet
    window.blit(sheet, (0, 0))
    subsurface = sheet.subsurface((0, 0, 32, 32))
    window.blit(subsurface, (100, 100))
    frame = sprite_animation.get_frame(ii)
    window.blit(frame, (200, 200))

    pygame.display.flip()
    clock.tick(10)
    ii += 1

pygame.quit()
