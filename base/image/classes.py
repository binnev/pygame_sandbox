from pathlib import Path
from typing import Callable

from pygame import Surface

from base.image.utils import (
    load_spritesheet,
    load_image_sequence,
    flip_images,
    recolor_images,
    scale_images,
)


class SpriteAnimation:
    """
    Animates a sequence of images.
    Can scale, flip, and recolor itself.
    """

    _images: list[Surface] | None
    source: Callable | None

    def __init__(
        self,
        images: [Surface] = None,
        scale: float = None,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        self._images = images
        if scale:
            self.scale(scale)
        if flip_x or flip_y:
            self.flip(flip_x, flip_y)
        if colormap:
            self.recolor(colormap)

    @classmethod
    def from_image(
        cls,
        filename: Path | str,
        colorkey=None,
        scale: float = None,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        return cls.from_spritesheet(
            filename=filename,
            image_size=None,
            colorkey=colorkey,
            flip_x=flip_x,
            flip_y=flip_y,
            colormap=colormap,
            scale=scale,
        )

    @classmethod
    def from_spritesheet(
        cls,
        filename: Path | str,
        image_size: (int, int),
        colorkey=None,
        num_images: int = 0,
        scale: float = None,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        def spritesheet_loader():
            images = load_spritesheet(
                filename=filename, image_size=image_size, colorkey=colorkey, num_images=num_images
            )
            images = cls._process_images(
                images, flip_x=flip_x, flip_y=flip_y, scale=scale, colormap=colormap
            )
            return images

        instance = cls()
        instance.source = spritesheet_loader
        return instance

    @classmethod
    def from_image_sequence(
        cls,
        filename: Path | str,
        colorkey=None,
        num_images: int = 0,
        scale: float = None,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        def image_sequence_loader():
            images = load_image_sequence(
                filename=filename, colorkey=colorkey, num_images=num_images
            )
            images = cls._process_images(
                images, flip_x=flip_x, flip_y=flip_y, scale=scale, colormap=colormap
            )
            return images

        instance = cls()
        instance.source = image_sequence_loader
        return instance

    @classmethod
    def _process_images(cls, images, flip_x, flip_y, colormap, scale):
        if flip_x or flip_y:
            images = flip_images(images, flip_x, flip_y)
        if colormap:
            images = recolor_images(images, colormap)
        if scale:
            images = scale_images(images, scale)
        return images

    def load(self):
        self._images = self.source()

    @property
    def images(self):
        """Lazy loading to allow this class to be instantiated before pygame.display.set_mode is
        called."""
        if not self._images:
            self.load()
        return self._images

    ############## playback ###############
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

    ############## edit in place ###############
    def flip(self, flip_x: bool, flip_y: bool):
        self._images = flip_images(self.images, flip_x, flip_y)

    def recolor(self, colormap: dict):
        self._images = recolor_images(self.images, colormap)

    def scale(self, scale: float):
        self._images = scale_images(self.images, scale)

    ############## edit and copy ###############
    def flipped_copy(self, flip_x=False, flip_y=False):
        return self.__class__(images=flip_images(self.images, flip_x, flip_y))

    def recolored_copy(self, colormap: dict):
        return self.__class__(images=recolor_images(self.images, colormap))

    def scaled_copy(self, scale: float):
        return self.__class__(images=scale_images(self.images, scale))

    def __len__(self):
        return len(self.images)

    @property
    def is_loaded(self):
        return bool(self.images)


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
        folder: Path | str,
        size: (int, int) = None,
        file_mapping: dict = None,
        scale: int = 1,
        colormap: dict = None,
        create_flipped_versions: bool = False,
        type="spritesheet",
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
        self.type = type
        self.sprite_sheets = dict()
        if file_mapping:
            for key, filename in file_mapping.items():
                self.register(**{key: filename})

    def register(self, **kwargs):
        for key, filename in kwargs.items():
            if self.type == "spritesheet":  # todo: add other options
                self[key] = SpriteAnimation.from_spritesheet(
                    self.folder / filename,
                    image_size=self.image_size,
                    colormap=self.colormap,
                    scale=self.scale,
                )
                if self.create_flipped_versions:
                    self[f"{key}_right"] = self[key]
                    self[f"{key}_left"] = SpriteAnimation.from_spritesheet(
                        self.folder / filename,
                        image_size=self.image_size,
                        colormap=self.colormap,
                        scale=self.scale,
                        flip_x=True,
                    )

    def load(self):
        for key, item in self.items():
            item.load()
        self._loaded = True

    def __getitem__(self, item):
        if not self._loaded:
            self.load()
        return super().__getitem__(item)
