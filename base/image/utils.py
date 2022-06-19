import glob
from pathlib import Path

import pygame
from pygame import Surface


def load_image(filename, colorkey=None) -> Surface:
    try:
        image = pygame.image.load(filename).convert_alpha()
    except pygame.error:
        print("Unable to load image:", filename)
        raise

    if colorkey is not None:
        if colorkey == -1:
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


def load_spritesheet(
    filename: Path | str,
    image_size: (int, int),
    colorkey=None,
    num_images: int = 0,
) -> [Surface]:
    """Load the image file. Don't call this until pygame.display has been initiated. Split
    the spritesheet into images and return a list of images."""
    filename = Path(filename).as_posix()
    sheet = load_image(filename, colorkey)

    width, height = image_size
    num_horizontal = sheet.get_rect().width // width
    num_vertical = sheet.get_rect().height // height
    rects = [
        pygame.Rect((width * i, height * j, width, height))
        for j in range(num_vertical)
        for i in range(num_horizontal)
    ]

    images = [sheet.subsurface(rect) for rect in rects]
    images = list(filter(not_empty, images))
    if num_images:
        images = images[:num_images]
    return images


def load_image_sequence(filename: Path | str, colorkey=None, num_images: int = 0) -> [Surface]:
    """Load a sequence of images."""
    filename = Path(filename)
    parent_folder = filename.parent
    pattern = filename.stem
    files = glob.glob(f"{parent_folder}/{pattern}*")
    images = [load_image(file, colorkey) for file in files]
    if num_images:
        images = images[:num_images]
    return images
