import pygame

from platformer.conf import SCREEN_WIDTH, SCREEN_HEIGHT
from platformer.objects import Platform, Entity, SpriteGroup, Blob, Character

pygame.init()
pygame.font.init()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hello World")


class Level(SpriteGroup):
    # sprite groups
    platforms = SpriteGroup()
    characters = SpriteGroup()
    projectiles = SpriteGroup()

    def add_objects(self, *objects, type=None):
        # add to Level spritegroup (similar to "all" group)
        self.add(*objects)

        # todo: allow multiple types?
        if type == "platform":
            self.platforms.add(*objects)
        if type == "character":
            self.characters.add(*objects)
        if type == "projectile":
            self.projectiles.add(*objects)


level = Level()
# Platforms
level.add_objects(Platform(50, 100, 200, 30, can_fall_through=True),
                  Platform(200, 300, 150, 30, can_fall_through=False),
                  Platform(5, 480, 480, 30, can_fall_through=False),
                  type="platform")
# Character object
level.add_objects(Character(x=50, y=200, width=40, height=60, level=level),
                  type="character")
# Entity objects
level.add_objects(Entity(400, 400, 50, 50, color=(0, 255, 255)),
                  Entity(200, 200, 100, 100, color=(0, 255, 255)))
# Blob object
level.add_objects(Blob(0, 0, 40, 60, color=(0, 255, 0)), type="character")
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

    # ================== update and draw =========================
    level.update(keys)
    level.draw(window, debug=True)
    pygame.display.flip()
    clock.tick(50)

pygame.quit()
