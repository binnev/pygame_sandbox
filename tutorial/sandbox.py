import pygame

from tutorial.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from tutorial.objects import Thing, Platform, Entity

pygame.init()
pygame.font.init()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")


class Level:
    sprite_groups = dict(
        platforms=pygame.sprite.Group(),
        characters=pygame.sprite.RenderPlain(),
        projectiles=pygame.sprite.RenderPlain(),
        enemies=pygame.sprite.RenderPlain(),
    )
    pass


level = Level()
# level.platforms.add(
#     Platform([50, 100, 200, 30], can_fall_through=True),
#     Platform([200, 300, 150, 30], can_fall_through=False),
#     Platform([5, 480, 480, 30], can_fall_through=False),
# )
level.sprite_groups["enemies"].add(
    Entity((255, 0, 0), 400, 400, 50, 50),
    Entity((255, 0, 0), 100, 100, 20, 20),
)
# Thing(x=50, y=200, width=40, height=60, level=level, groups=[level.characters])
entity = Entity((0, 255, 0),
                0,
                0,
                40,
                60,
                groups=[level.sprite_groups["characters"]])
clock = pygame.time.Clock()

run = True
while run:
    # pygame.time.delay(1000//50)

    # ============= react to key presses ==============
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((0, 0, 0))
    for group_name, sprite_group in level.sprite_groups.items():
        if group_name == "characters":
            sprite_group.update(keys)
        sprite_group.draw(window)
    pygame.display.flip()

    clock.tick(50)

pygame.quit()
