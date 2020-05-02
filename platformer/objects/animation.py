from copy import deepcopy
from pathlib import Path

import pygame


def pad_alpha(colour_tuple):
    if len(colour_tuple) == 3:
        # if no alpha channel supplied, assume it's full opacity
        return (*colour_tuple, 255)
    elif len(colour_tuple) == 4:
        return colour_tuple
    else:
        raise Exception("bogus colour, man")


def recolor_sprite(surface, color_mapping: dict):

    # make sure the colourmap has alpha channel on all colours
    color_mapping = {
        pad_alpha(k): pad_alpha(v) for k, v in color_mapping.items()
    }
    width, height = surface.get_size()
    # surface.copy() inherits surface's colorkey; preserving transparency
    new_surface = surface.copy()

    # iterate over all the pixels in the old surface, and write a pixel to the new
    # surface in the corresponding position. If the colour of the present pixel has an
    # entry in the color_mapping dict, then write the new colour instead of the old one.
    for x in range(width):
        for y in range(height):
            color = surface.get_at((x, y))[:]
            new_color = color_mapping.get(color)
            if new_color:
                new_surface.set_at((x, y), pygame.Color(*new_color))
            else:
                new_surface.set_at((x, y), pygame.Color(*color))

    return new_surface


class SpriteSheet:
    """Handles importing spritesheets and dividing into individual frame images."""
    sheet: pygame.Surface

    def __init__(self, filename, colormap=None):
        filename = Path(filename).as_posix()
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
            if colormap:
                self.recolor(colormap)
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise Exception(message)

    def image_at(self, rectangle, colorkey=None, scale=None):
        """Load a specific image from a specific rectangle"""

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

    def images_at(self, rects, colorkey=None, scale=None, num_images=None):
        """Load a whole bunch of images and return them as a list"""
        result = [self.image_at(rect, colorkey, scale) for rect in rects]
        return result[:num_images] if num_images else result

    def load_sheet(self,
                   width: int,
                   height: int,
                   colorkey: int = None,
                   scale: float = None,
                   num_images: int = None) -> [pygame.Surface]:
        """Load a whole spritesheet and return frames as a list of images."""
        num_horizontal = self.sheet.get_rect().width // width
        num_vertical = self.sheet.get_rect().height // height
        rects = [(width * i, height * j, width, height)
                 for j in range(num_vertical)
                 for i in range(num_horizontal)]
        result = [self.image_at(rect, colorkey, scale) for rect in rects]
        return result[:num_images] if num_images else result

    def recolor(self, colormap: dict) -> None:
        """Recolor spritesheet in place"""
        self.sheet = recolor_sprite(self.sheet, colormap)

    def copy_and_recolor(self, colormap: dict):
        """Return a recolored copy of the spritesheet (saves reloading the image)"""
        new_spritesheet = deepcopy(self)
        new_spritesheet.recolor(colormap)
        return new_spritesheet


class SpriteAnimation:
    """
    Handles the animating of a collection of frames.
    TODO:
      - allow resampling (showing frames more than once with a mapping)
      - maybe even create functions for ease-in and ease-out sampling?
    """

    def __init__(self,
                 frames: [pygame.Surface],
                 flip_horizontal=False,
                 flip_vertical=False,
                 looping=True,
                 game_ticks_per_sprite_frame=1):
        self.frames = [
            pygame.transform.flip(f, bool(flip_horizontal), bool(flip_vertical))
            for f in frames
        ]
        self.looping = looping
        self.game_ticks_per_sprite_frame = game_ticks_per_sprite_frame

    def get_frame(self, game_tick: int):
        """
        Animate the sprite. Given an integer `game_tick` representing how many
        iterations the game has performed, return a sprite frame. Handles looping
        through a finite list of frames. The higher `game_ticks_per_sprite_frame`,
        the slower the animation will be (the frame will be displayed for more game
        ticks).
        """
        if self.looping:
            return self.frames[game_tick // self.game_ticks_per_sprite_frame %
                               len(self.frames)]
        else:
            return self.frames[min(
                game_tick // self.game_ticks_per_sprite_frame,
                len(self.frames) - 1)]


class SpriteDict(dict):
    """
    Manages all the sprites for an entity---e.g. "stand", "run", etc.
    Should offer a method for easy recoloring of all sprites.
    """

    def __init__(
        self,
        size: (int, int),
        file_mapping: dict,
        scale: int = 1,
        game_ticks_per_sprite_frame: int = 1,
        colormap: dict = None,
    ):
        """
        Default parameters (size, scale, etc) will be used for all sprites, unless the
        individual entry in file_mapping contains alternate values for the same
        parameters; in that case, the specific params override the general ones.
        """
        super().__init__()

        for sprite_name, sprite_info in file_mapping.items():

            # individual sprite parameters override default params
            _size = sprite_info.get("size") or size
            _scale = sprite_info.get("scale") or scale
            _ticks_per_frame = (sprite_info.get("game_ticks_per_sprite_frame")
                                or game_ticks_per_sprite_frame)

            # specific to individual sprites
            filename = sprite_info.get("filename")
            num_images = sprite_info.get("num_images")
            flip_horizontal = sprite_info.get("flip_horizontal")
            flip_vertical = sprite_info.get("flip_vertical")

            sprite_sheet = SpriteSheet(filename, colormap)
            frames_list = sprite_sheet.load_sheet(*_size,
                                                  scale=_scale,
                                                  num_images=num_images)
            sprite_animation = SpriteAnimation(
                frames_list,
                game_ticks_per_sprite_frame=_ticks_per_frame,
                flip_horizontal=flip_horizontal,
                flip_vertical=flip_vertical,
            )

            self[sprite_name] = sprite_animation