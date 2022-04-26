from pathlib import Path

import numpy
import pygame
from pygame import Surface


def load_image(filename, colorkey=None) -> Surface:
    try:
        image = pygame.image.load(filename).convert_alpha()
    except pygame.error:
        print("Unable to load image:", filename)
        raise

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    return image


def not_empty(surface: Surface) -> bool:
    """Check if a surface has any non-zero pixels. `Surface.get_bounding_rect()` returns the
    smallest rectangle on the surface containing data. If the surface is empty, it will return
    Rect(0, 0, 0, 0), for which `any` returns False"""
    return any(surface.get_bounding_rect())


def relative_folder(current_file: str, folder: str) -> Path:
    return Path(current_file).parent.absolute() / folder


def pad_alpha(colour_tuple):
    if len(colour_tuple) == 3:
        # if no alpha channel supplied, assume it's full opacity
        return (*colour_tuple, 255)
    elif len(colour_tuple) == 4:
        return colour_tuple
    else:
        raise Exception("bogus colour, man")


def scale_image(image: Surface, scale: int):
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
    """Handles importing spritesheets and dividing into individual frame images. Implements lazy
    loading to allow this class to be instantiated before pygame.display.set_mode is called."""

    sheet: Surface = None  # contains all the images of the animation in a grid
    _images: [Surface] = None  # cached list of images

    def __init__(
        self,
        filename: Path | str,
        image_size: (int, int),
        colorkey=None,
        num_images: int = 0,
    ):
        """
        :param filename: complete path to the spritesheet image file
        :param image_size: size of each individual sprite
        :param colorkey:
        :param num_images: can be used to limit the set of images loaded from the spritesheet
        """
        filename = Path(filename).as_posix()
        self.filename = filename
        self.image_size = image_size
        self.colorkey = colorkey
        self.num_images = num_images

    def load(self):
        """Load the image file. Don't call this until pygame.display has been initiated."""
        filename = Path(self.filename).as_posix()
        self.sheet = load_image(filename, self.colorkey)

    def sample(self) -> [Surface]:
        """This is the main interface for the rest of the code. Split the spritesheet into
        images and return a list of images."""
        if not self.sheet:
            self.load()
        width, height = self.image_size
        num_horizontal = self.sheet.get_rect().width // width
        num_vertical = self.sheet.get_rect().height // height
        rects = [
            pygame.Rect((width * i, height * j, width, height))
            for j in range(num_vertical)
            for i in range(num_horizontal)
        ]

        images = [self.sheet.subsurface(rect) for rect in rects]
        images = list(filter(not_empty, images))
        if self.num_images:
            images = images[: self.num_images]
        self._images = images

    @property
    def images(self):
        """Lazy loading to allow this class to be instantiated before pygame.display.set_mode is
        called."""
        if not self._images:
            self.sample()
        return self._images


class SpriteAnimation:
    """
    Animates a sequence of images.
    Can scale, flip, and recolor itself.
    """

    def __init__(
        self,
        images: [Surface],
        scale: float = None,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        """
        :param images: list of loaded images
        :param scale:
        :param flip_x:
        :param flip_y:
        :param colormap:
        """
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
        """If n is greater than the number of frames, start again at the beginning."""
        return self.play(n % len(self.images))

    def flip(self, flip_x: bool, flip_y: bool):
        self.images = [flip_image(image, flip_x, flip_y) for image in self.images]

    def recolor(self, colormap: dict):
        self.images = [recolor_image(image, colormap) for image in self.images]

    def scale(self, scale: float):
        self.images = [scale_image(image, scale) for image in self.images]

    def __len__(self):
        return len(self.images)


class SpriteDict(dict):
    """
    Manages a collection of sprite animations.
    Takes a folder and list of files as input, and handles the creation of SpriteSheets and
    SpriteAnimations.
    Lazy loading to allow this class to be instantiated before pygame display is initialised.
    """

    _loaded: bool = False  # have the images been loaded yet

    def __init__(
        self,
        folder: str,
        size: (int, int) = None,
        file_mapping: dict = None,
        scale: int = 1,
        colormap: dict = None,
        create_flipped_versions: bool = False,
    ):
        """
        Create SpriteSheet for each file, but don't trigger .load() yet.
        """
        super().__init__()
        self.scale = scale
        self.image_size = size
        self.colormap = colormap
        self.create_flipped_versions = create_flipped_versions
        folder = Path(folder)
        self.folder = folder

        self.sprite_sheets = dict()
        for key, filename in file_mapping.items():
            self.register(key, filename)

    def register(self, key: str, filename: str, image_size=None):
        image_size = image_size or self.image_size
        self.sprite_sheets[key] = SpriteSheet(
            filename=self.folder / filename, image_size=image_size
        )

    def load(self):
        for name, sprite_sheet in self.sprite_sheets.items():
            if self.create_flipped_versions:
                self[f"{name}_right"] = SpriteAnimation(
                    sprite_sheet.images,
                    scale=self.scale,
                    colormap=self.colormap,
                )
                self[f"{name}_left"] = SpriteAnimation(
                    sprite_sheet.images,
                    scale=self.scale,
                    colormap=self.colormap,
                    flip_x=True,
                )
            else:
                self[name] = SpriteAnimation(
                    sprite_sheet.images,
                    scale=self.scale,
                    colormap=self.colormap,
                )
        self._loaded = True

    def __getitem__(self, item):
        if not self._loaded:
            self.load()
        return super().__getitem__(item)
