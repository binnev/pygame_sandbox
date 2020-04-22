from pathlib import Path

import pygame


class SpriteSheet(object):

    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey=None, scale=None):

        rect = pygame.Rect(rectangle)
        image = self.sheet.subsurface(rect)

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
    def images_at(self, rects, colorkey=None, scale=None, num_images=None):
        "Loads multiple images, supply a list of coordinates"
        result = [self.image_at(rect, colorkey, scale) for rect in rects]
        return result[:num_images] if num_images else result

    def load_sheet(self,
                   width,
                   height,
                   colorkey=None,
                   scale=None,
                   num_images=None):
        num_horizontal = self.sheet.get_rect().width // width
        num_vertical = self.sheet.get_rect().height // height
        rects = [(width * i, height * j, width, height)
                 for j in range(num_vertical)
                 for i in range(num_horizontal)]
        result = [self.image_at(rect, colorkey, scale) for rect in rects]
        return result[:num_images] if num_images else result


class SpriteAnimation:

    def __init__(self,
                 frames: list,
                 flip_horizontal=False,
                 flip_vertical=False):
        self.frames = [
            pygame.transform.flip(f, flip_horizontal, flip_vertical)
            for f in frames
        ]

    def get_frame(self, index):
        return self.frames[index % len(self.frames)]


# sprite_folder = Path("sprites/blob/")
# blob_spritesheets = {
#     "stand": SpriteSheet(sprite_folder / "stand.png"),
# }
#
# blob_sprite_animations = {
#     key: SpriteAnimation(spritesheet.load_sheet())
#     for key, spritesheet in blob_spritesheets.items()
# }
