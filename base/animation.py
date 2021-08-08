from pathlib import Path

import numpy
import pygame


def not_empty(surface: pygame.Surface):
    """Check if a surface has any non-zero pixels. `Surface.get_bounding_rect()` returns the
    smallest rectangle on the surface containing data. If the surface is empty, it will return
    Rect(0, 0, 0, 0), for which `any` returns False"""
    return any(surface.get_bounding_rect())


def relative_folder(current_file: str, folder: str):
    return Path(current_file).parent.absolute() / folder


def pad_alpha(colour_tuple):
    if len(colour_tuple) == 3:
        # if no alpha channel supplied, assume it's full opacity
        return (*colour_tuple, 255)
    elif len(colour_tuple) == 4:
        return colour_tuple
    else:
        raise Exception("bogus colour, man")


def scale_image(image: pygame.Surface, scale: int):
    x_scale = image.get_rect().width * scale
    y_scale = image.get_rect().height * scale
    image = pygame.transform.scale(image, (x_scale, y_scale))
    return image


def flip_image(image, flip_x=False, flip_y=False):
    return pygame.transform.flip(image, bool(flip_x), bool(flip_y))


def recolor_image(surface, color_mapping: dict):

    # make sure the colourmap has alpha channel on all colours
    color_mapping = {pad_alpha(k): pad_alpha(v) for k, v in color_mapping.items()}
    width, height = surface.get_size()
    # surface.copy() inherits surface's colorkey; preserving transparency
    new_surface = surface.copy()

    # iterate over all the pixels in the old surface, and write a pixel to the new surface in the
    # corresponding position. If the colour of the present pixel has an entry in the
    # color_mapping dict, then write the new colour instead of the old one.
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

    sheet: pygame.Surface  # contains all the images of the animation in a grid

    def __init__(self, filename, colorkey=None):
        filename = Path(filename).as_posix()
        self.filename = filename
        self.colorkey = colorkey
        self.load_image_file()

    def load_image_file(self):
        """ Load the image file. Don't call this until pygame.display has been initiated. """
        try:
            self.sheet = pygame.image.load(self.filename).convert_alpha()
        except pygame.error as message:
            print("Unable to load spritesheet image:", self.filename)
            raise Exception(message)

        if self.colorkey is not None:
            if self.colorkey is -1:
                self.colorkey = self.sheet.get_at((0, 0))
            self.sheet.set_colorkey(self.colorkey, pygame.RLEACCEL)

    def get_images(
        self,
        size: (int, int),
        num_images: int = None,
        **kwargs,
    ) -> [pygame.Surface]:
        """This is the main interface for the rest of the code. Split the spritesheet into
        images, scale/flip/recolor them, and return a list of images."""
        width, height = size
        num_horizontal = self.sheet.get_rect().width // width
        num_vertical = self.sheet.get_rect().height // height
        rects = [
            pygame.Rect((width * i, height * j, width, height))
            for j in range(num_vertical)
            for i in range(num_horizontal)
        ]

        images = [self.sheet.subsurface(rect) for rect in rects]
        images = list(filter(not_empty, images))
        if num_images:
            images = images[:num_images]
        return images


class SpriteAnimation:
    """
    Handles the animating of a collection of frames.
    TODO:
      - allow resampling (showing frames more than once with a mapping)
    """

    def __init__(
        self,
        images: [pygame.Surface],
        scale: float = None,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        self.images = images
        if scale:
            self.scale(scale)
        if flip_x or flip_y:
            self.flip(flip_x, flip_y)
        if colormap:
            self.recolor(colormap)

    def play(self, n: int):
        """
        Fetch frame with index n. This is used in the game loop (where n is the iteration
        counter) to animate the sprite. Return False when we've run out of frames.
        """
        try:
            return self.images[n]
        except IndexError:
            return False

    def loop(self, n: int):
        """ If n is greater than the number of frames, start again at the beginning. """
        return self.play(n % len(self.images))

    def flip(self, flip_x: bool, flip_y: bool):
        self.images = [flip_image(image, flip_x, flip_y) for image in self.images]

    def recolor(self, colormap: dict):
        self.images = [recolor_image(image, colormap) for image in self.images]

    def scale(self, scale: float):
        self.images = [scale_image(image, scale) for image in self.images]

    def __len__(self):
        return len(self.images)

    def copy(
        self,
        scale: float = None,
        flip_x=False,
        flip_y=False,
        colormap: dict = None,
    ):
        return self.__class__(self.images, scale, flip_x, flip_y, colormap)


class SpriteDict(dict):
    """
    Manages all the sprites for an entity---e.g. "stand", "run", etc.
    Should offer a method for easy recoloring of all sprites.
    """

    def __init__(
        self,
        size: (int, int) = None,
        file_mapping: dict = None,
        scale: int = 1,
        colormap: dict = None,
    ):
        """
        Default parameters (size, scale, etc) will be used for all sprites, unless the
        individual entry in file_mapping contains alternate values for the same
        parameters; in that case, the specific params override the general ones.
        """
        super().__init__()

        for sprite_name, sprite_info in file_mapping.items():

            defaults = {
                "size": size,
                "scale": scale,
            }
            defaults.update(sprite_info)

            sprite_sheet = SpriteSheet(sprite_info["filename"], colormap)
            frames_list = sprite_sheet.get_images(**defaults)
            sprite_animation = SpriteAnimation(frames_list, **defaults)

            self[sprite_name] = sprite_animation


def ease(start, stop, num, function):
    """ see https://easings.net/ for functions """
    distance = stop - start
    ease = numpy.array(list(map(function, numpy.linspace(0, 1, num))))
    output = start + ease * distance
    return output


def ease_in(start, stop, num, power=3):
    return ease(start, stop, num, function=lambda x: x ** power)


def ease_out(start, stop, num, power=3):
    return ease(start, stop, num, function=lambda x: 1 - (1 - x) ** power)


def ease_in_out(start, stop, num, power=3):
    def _in_out(x, power):
        return 4 * x ** power if x < 0.5 else 1 - (-2 * x + 2) ** power / 2

    return ease(start, stop, num, function=lambda x: _in_out(x, power))
