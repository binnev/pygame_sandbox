from pathlib import Path

import pygame

from platformer.objects import SpriteAnimation


class SpriteSheet(object):

    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey=None, scale=None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        if scale:
            image = pygame.transform.scale(image,
                                           (image.get_rect().width * scale,
                                            image.get_rect().height * scale))
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey=None, scale=None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey, scale) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey=None, scale=None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey, scale)

    def load_sheet(self, width, height, colorkey=None, scale=None):
        H = self.sheet.get_rect().width // width
        V = self.sheet.get_rect().height // height
        rects = [(width * i, height * j, width, height)
                 for j in range(V)
                 for i in range(H)]
        return [self.image_at(rect, colorkey, scale) for rect in rects]


# ======================

SPRITE_WIDTH = 32
pygame.init()
window = pygame.display.set_mode((500, 500))
filename = Path("sprites/pixel_art_test/blob_stand.png")
sprite_sheet = SpriteSheet(filename.as_posix())
frames = sprite_sheet.load_sheet(32, 32, scale=5)
sprite_animation = SpriteAnimation([])
sprite_animation.frames = frames
clock = pygame.time.Clock()

run = True
ii = 0
while run:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((255, 255, 255))
    frame = sprite_animation.get_frame(ii)
    window.blit(frame, (0, 0, 32, 32))

    pygame.display.flip()
    clock.tick(10)
    ii += 1

pygame.quit()
