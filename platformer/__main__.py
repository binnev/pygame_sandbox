import pygame

from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from platformer.objects import Platform, Entity, SpriteGroup, Blob, Character

pygame.init()
pygame.font.init()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")


class Level:
    sprite_groups = dict(
        platforms=SpriteGroup(),
        characters=SpriteGroup(),
        projectiles=SpriteGroup(),
        enemies=SpriteGroup(),
        all=SpriteGroup(),
    )


level = Level()
# Platforms
sprite_groups = [level.sprite_groups["platforms"], level.sprite_groups["all"]]
Platform(50, 100, 200, 30, can_fall_through=True, groups=sprite_groups),
Platform(200, 300, 150, 30, can_fall_through=False, groups=sprite_groups),
Platform(5, 480, 480, 30, can_fall_through=False, groups=sprite_groups),
# Character object
sprite_groups = [level.sprite_groups["characters"], level.sprite_groups["all"]]
Character(x=50, y=200, width=40, height=60, level=level, groups=sprite_groups)
# Entity objects
sprite_groups = [level.sprite_groups["enemies"], level.sprite_groups["all"]]
Entity(400, 400, 50, 50, color=(0, 255, 255), groups=sprite_groups),
Entity(200, 200, 100, 100, color=(0, 255, 255), groups=sprite_groups),
# Blob object
sprite_groups = [level.sprite_groups["characters"], level.sprite_groups["all"]]
Blob(0, 0, 40, 60, color=(0, 255, 0), groups=sprite_groups)
clock = pygame.time.Clock()

run = True
while run:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((0, 0, 0))

    # ================== action happens here =========================
    # check for collision
    # if pygame.sprite.spritecollide(entity,
    #                                level.sprite_groups["enemies"],
    #                                dokill=False):
    #     entity.color = (0, 0, 255)
    #     print("rect collision")
    # else:
    #     entity.color = (0, 255, 0)
    level.sprite_groups["characters"].update(keys)

    # ================= draw all sprites ========================
    level.sprite_groups["all"].draw(window)
    pygame.display.flip()

    clock.tick(50)

pygame.quit()
