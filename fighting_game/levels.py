from fighting_game.conf import *
from fighting_game.objects import *


class Level(Scene):
    """ A Scene representing a level of a game. """

    parental_name = "level"
    screen_shake: int
    blast_zone: BlastZone

    def __init__(self):
        super().__init__()
        self.background = Group()
        self.platforms = Group()
        self.characters = Group()
        self.projectiles = Group()
        self.particle_effects = Group()
        self.hitboxes = Group()
        self.invisible_elements = Group()
        self.groups = [
            self.background,
            self.platforms,
            self.characters,
            self.projectiles,
            self.particle_effects,
            self.hitboxes,
            self.invisible_elements,
        ]
        self.state = self.main
        self.hit_handler = HitHandler()
        self.screen_shake = 0

    def add_background(self, *objects):
        self.add_to_group(*objects, group=self.background)

    def add_platform(self, *objects):
        self.add_to_group(*objects, group=self.platforms)

    def add_character(self, *objects):
        self.add_to_group(*objects, group=self.characters)

    def add_projectile(self, *objects):
        self.add_to_group(*objects, group=self.projectiles)

    def add_hitbox(self, *objects):
        self.add_to_group(*objects, group=self.hitboxes)

    def add_particle_effect(self, *objects):
        self.add_to_group(*objects, group=self.particle_effects)

    def add_invisible_element(self, *objects):
        self.add_to_group(*objects, group=self.invisible_elements)

    def main(self):
        self.hit_handler.handle_hits(self.hitboxes, [*self.characters, *self.projectiles])
        self.handle_blast_zone_collisions()
        self.hitboxes.kill()
        if self.screen_shake:
            self.screen_shake -= 1

    def draw(self, surface: Surface, debug=False):
        if self.screen_shake:
            temp_surf = Surface(surface.get_size())
            temp_surf.fill((150, 150, 150))  # overwrite previous stuff on screen
            magnitude = 10
            rect = temp_surf.get_rect()
            rect.centerx += random.randrange(-magnitude, magnitude)
            rect.centery += random.randrange(-magnitude, magnitude)
            super().draw(temp_surf, debug)
            surface.blit(temp_surf, rect)
        else:
            surface.fill((150, 150, 150))  # overwrite previous stuff on screen
            super().draw(surface, debug)

    def handle_blast_zone_collisions(self):
        objects = [*self.characters, *self.projectiles]
        for object in objects:
            if not pygame.sprite.collide_rect(self.blast_zone, object):
                object.kill()
                # todo: logic for keeping track of stocks
                # todo: add particle effect, screen shake, etc
                self.screen_shake = 20
                angle = self.calculate_plume_angle(object)
                self.add_particle_effect(Plume(object.x, object.y, angle))

    def calculate_plume_angle(self, object):
        """ Object has just entered the blastzone """
        if object.x < self.blast_zone.rect.left:
            angle = 0
        elif object.x > self.blast_zone.rect.right:
            angle = 180
        elif object.y > self.blast_zone.rect.bottom:
            angle = 90
        else:
            angle = 270
        return angle

class DefaultLevel(Level):
    def __init__(self):
        super().__init__()
        COURT_WIDTH = 1300
        NET_HEIGHT = 250 - 120

        self.ground = Platform(0, 0, COURT_WIDTH, 30)
        self.ground.x = SCREEN_WIDTH // 2
        self.ground.y = SCREEN_HEIGHT - 50

        self.net = Platform(0, 0, 10, NET_HEIGHT)
        self.net.x = SCREEN_WIDTH // 2
        self.net.y = SCREEN_HEIGHT - 300

        self.net2 = Platform(0, 0, 10, NET_HEIGHT // 4)
        self.net2.x = SCREEN_WIDTH // 2
        self.net2.y = SCREEN_HEIGHT - 75

        self.droppable = Platform(SCREEN_WIDTH // 4, 500, 300, 40, droppable=True)
        self.droppable2 = Platform(SCREEN_WIDTH // 4, 400, 300, 20, droppable=True)
        self.droppable3 = Platform(SCREEN_WIDTH * 3 // 4 - 120, 400, 100, 20, droppable=True)
        self.droppable4 = Platform(SCREEN_WIDTH * 3 // 4, 400, 100, 20, droppable=True)

        self.add_platform(
            self.ground,
            self.net,
            self.net2,
            self.droppable,
            self.droppable2,
            self.droppable3,
            self.droppable4,
        )


class Battlefield(Level):
    def __init__(self):
        super().__init__()

        ground = Platform(0, 0, 800, 1000)
        ground.x = SCREEN_WIDTH // 2
        ground.rect.top = SCREEN_HEIGHT - 150

        left_platform = Platform(0, 0, 100, 20, droppable=True)
        left_platform.x = ground.x - 200
        left_platform.y = ground.rect.top - 100

        right_platform = Platform(0, 0, 100, 20, droppable=True)
        right_platform.x = ground.x + 200
        right_platform.y = ground.rect.top - 100

        top_platform = Platform(0, 0, 100, 20, droppable=True)
        top_platform.x = ground.x
        top_platform.y = ground.rect.top - 200

        self.add_platform(
            ground,
            left_platform,
            right_platform,
            top_platform,
        )

        self.blast_zone = BlastZone(0, 0, 1200, 800)
        self.blast_zone.x = ground.x
        self.blast_zone.y = ground.rect.top - 300
        self.add_invisible_element(self.blast_zone)
