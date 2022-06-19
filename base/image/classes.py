from abc import ABC
from copy import deepcopy
from pathlib import Path

from pygame import Surface

from base.image.utils import (
    scale_image,
    recolor_image,
    flip_image,
    load_spritesheet,
    load_image_sequence,
    flip_images,
    recolor_images,
    scale_images,
)


class ImageLoader(ABC):
    """A lazy-loader for image files. Can be instantiated -- thus storing the configuration (
    image size, number of images, etc) -- without actually loading the images yet. This allows us
    to instantiate the class before calling pygame.display.init. Image loading is triggered by
    the .load() method."""

    _images: [Surface] = None  # cached list of images

    def __init__(
        self,
        filename: Path | str,
        colorkey=None,
        num_images: int = 0,
        scale: float = 0,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        """
        :param colorkey: used to set transparency.
        :param num_images: can be used to limit the set of images loaded from the spritesheet
        :param scale: scale images by this factor
        :param flip_x: flip images horizontally
        :param flip_y: flip images vertically
        :param colormap: dictionary mapping {old_colour: new_colour}
        """
        self.filename = filename
        self.colorkey = colorkey
        self.num_images = num_images
        self.scale = scale
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.colormap = colormap or dict()

    def _load_images(self):
        """Load image files into memory. Can only be called after pygame.display.init. After this
        method has completed, self.images should be populated."""
        raise NotImplementedError()

    def _process_images(self):
        if self.flip_x or self.flip_y:
            self.flip_images()
        if self.colormap:
            self.recolor_images()
        if self.scale:
            self.scale_images()

    def load(self):
        self._load_images()
        self._process_images()

    @property
    def images(self):
        """Lazy loading to allow this class to be instantiated before pygame.display.set_mode is
        called."""
        if not self._images:
            self.load()
        return self._images

    def flip_images(self):
        self._images = [flip_image(image, self.flip_x, self.flip_y) for image in self._images]

    def recolor_images(self):
        self._images = [recolor_image(image, self.colormap) for image in self._images]

    def scale_images(self):
        self._images = [scale_image(image, self.scale) for image in self._images]


class ImageSequence(ImageLoader):
    """Handles loading a sequence of images."""

    def _load_images(self):
        self._images = load_image_sequence(
            filename=self.filename,
            colorkey=self.colorkey,
            num_images=self.num_images,
        )


class SpriteSheet(ImageLoader):
    """Handles importing spritesheets and dividing into individual frame images."""

    def __init__(self, filename: Path | str, image_size: (int, int) = None, **kwargs):
        self.image_size = image_size
        super().__init__(filename, **kwargs)

    def _load_images(self):
        self._images = load_spritesheet(
            filename=self.filename,
            image_size=self.image_size,
            colorkey=self.colorkey,
            num_images=self.num_images,
        )


class SpriteAnimation:
    """
    Animates a sequence of images.
    Can scale, flip, and recolor itself.
    """

    _images: list[Surface] | None
    source: ImageLoader | None

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
        instance = cls()
        source = SpriteSheet(
            filename=filename,
            colorkey=colorkey,
            scale=scale,
            flip_x=flip_x,
            flip_y=flip_y,
            colormap=colormap,
        )
        instance.source = source
        return instance

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
        instance = cls()
        source = SpriteSheet(
            filename=filename,
            image_size=image_size,
            colorkey=colorkey,
            num_images=num_images,
            scale=scale,
            flip_x=flip_x,
            flip_y=flip_y,
            colormap=colormap,
        )
        instance.source = source
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
        instance = cls()
        source = ImageSequence(
            filename=filename,
            colorkey=colorkey,
            num_images=num_images,
            scale=scale,
            flip_x=flip_x,
            flip_y=flip_y,
            colormap=colormap,
        )
        instance.source = source
        return instance

    def load(self):
        self._images = self.source.images

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
