import pygame

from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from platformer.objects import Platform, Entity, SpriteGroup, Blob

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
    )
    pass


level = Level()
# level.platforms.add(
#     Platform([50, 100, 200, 30], can_fall_through=True),
#     Platform([200, 300, 150, 30], can_fall_through=False),
#     Platform([5, 480, 480, 30], can_fall_through=False),
# )
level.sprite_groups["enemies"].add(
    Entity((0, 255, 255), 400, 400, 50, 50),
    Entity((0, 255, 255), 200, 200, 100, 100),
)
# Character(x=50, y=200, width=40, height=60, level=level, groups=[level.characters])
entity = Blob((0, 255, 0),
                0,
                0,
                40,
                60,
                groups=[level.sprite_groups["characters"]])
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

    # check for collision
    if pygame.sprite.spritecollide(entity,
                                   level.sprite_groups["enemies"],
                                   dokill=False):
        entity.color = (0, 0, 255)
        print("rect collision")
    else:
        entity.color = (0, 255, 0)
    for group_name, sprite_group in level.sprite_groups.items():
        if group_name == "characters":
            sprite_group.update(keys)
        sprite_group.draw(window)

    pygame.display.flip()

    clock.tick(50)

pygame.quit()
