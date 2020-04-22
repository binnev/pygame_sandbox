from pathlib import Path

import pygame

from platformer.conf import SCALE_SPRITES, TICKS_PER_SPRITE_FRAME


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
                   width: int,
                   height: int,
                   colorkey=None,
                   scale: float = None,
                   num_images: int = None):
        num_horizontal = self.sheet.get_rect().width // width
        num_vertical = self.sheet.get_rect().height // height
        rects = [(width * i, height * j, width, height)
                 for j in range(num_vertical)
                 for i in range(num_horizontal)]
        result = [self.image_at(rect, colorkey, scale) for rect in rects]
        return result[:num_images] if num_images else result


class SpriteAnimation:
    """
    TODO:
    - allow resampling (showing frames more than once with a mapping)
    - allow non-looping sprites (play once, then repeat last frame)
    """

    def __init__(self,
                 frames: list,
                 flip_horizontal=False,
                 flip_vertical=False,
                 looping=True):
        self.frames = [
            pygame.transform.flip(f, flip_horizontal, flip_vertical)
            for f in frames
        ]
        self.looping = looping

    def get_frame(self, index):
        if self.looping:
            return self.frames[index // TICKS_PER_SPRITE_FRAME %
                               len(self.frames)]
        else:
            return self.frames[min(index // TICKS_PER_SPRITE_FRAME,
                                   len(self.frames) - 1)]


class SpriteGroup(pygame.sprite.Group):

    def draw(self, surface, debug=False):
        """draw all sprites onto the surface
        Group.draw(surface): return None
        Draws all of the member sprites onto the given surface.
        """
        sprites = self.sprites()
        for sprite in sprites:
            sprite.draw(surface, debug)
        self.lostsprites = []


folder = Path("sprites/blob/")
PROJECTILE_SPRITES = {
    "right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_projectile.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
    "left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_projectile.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES),
                        flip_horizontal=True),
}

folder = Path("sprites/blob/")
# todo; make a class for this. SpriteSet?
BLOB_SPRITES = {
    "stand":
        SpriteAnimation(
            SpriteSheet((folder / "blob_stand.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
    "jump":
        SpriteAnimation(
            SpriteSheet((folder / "blob_jump.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "jump_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_jump_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "jump_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_jump_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3),
                        flip_horizontal=True),
    "fall":
        SpriteAnimation(
            SpriteSheet((folder / "blob_fall.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "fall_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_fall_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "fall_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_fall_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3),
                        flip_horizontal=True),
    "crouch":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_crouch.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES),
                        looping=False),
    "run_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_run_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=8)),
    "run_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_run_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=8),
                        flip_horizontal=True),
}
