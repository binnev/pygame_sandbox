import pygame

from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from platformer.objects import Platform, Entity, SpriteGroup, Blob, Character, Level

pygame.init()
pygame.font.init()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")




level = Level()
# Platforms
level.add_objects(Platform(50, 100, 200, 30, can_fall_through=True),
                  Platform(200, 300, 150, 30, can_fall_through=False),
                  Platform(5, 480, 480, 30, can_fall_through=False),
                  type="platform")
# Character object
character = Character(50, 200, 40, 60)
level.add_objects(character, type="character")
# # Entity objects
# level.add_objects(Entity(400, 400, 50, 50, color=(0, 255, 255)),
#                   Entity(200, 200, 100, 100, color=(0, 255, 255)))
# # Blob object
# level.add_objects(Blob(0, 0, 40, 60, color=(0, 255, 0)), type="character")

clock = pygame.time.Clock()

run = True
while run:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        character.x, character.y = 50, 200
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((255, 255, 255))

    # ================== update and draw =========================
    level.update(keys)
    level.draw(window, debug=True)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
