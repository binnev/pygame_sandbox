from abc import ABC
from copy import deepcopy
from pathlib import Path

from pygame import Surface

from base.image.utils import (
    scale_image,
    recolor_image,
    flip_image,
    load_spritesheet,
)


class ImageLoader(ABC):
    """A lazy-loader for image files. Stores the configuration (image size, number of images,
    etc) without actually loading the images. This allows us to instantiate the class before
    calling pygame.display.init. Image loading is triggered by the .load() method."""

    _images: [Surface] = None  # cached list of images

    def __init__(
        self,
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
        self.colorkey = colorkey
        self.num_images = num_images
        self.scale = scale
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.colormap = colormap or dict()

    def load(self):
        """Load image files into memory. Can only be called after pygame.display.init. After this
        method has completed, self.images should be populated."""
        raise NotImplementedError()

    @property
    def images(self):
        """Lazy loading to allow this class to be instantiated before pygame.display.set_mode is
        called."""
        if not self._images:
            self.load()
        return self._images


class SpriteSheet(ImageLoader):
    """Handles importing spritesheets and dividing into individual frame images. Implements lazy
    loading to allow this class to be instantiated before pygame.display.set_mode is called."""

    sheet: Surface = None  # contains all the images of the animation in a grid

    def __init__(
        self,
        filename: Path | str,
        image_size: (int, int),
        colorkey=None,
        num_images: int = 0,
        scale: float = 0,
        flip_x: bool = False,
        flip_y: bool = False,
        colormap: dict = None,
    ):
        """
        :param filename: complete path to the spritesheet image file
        :param image_size: size of each individual image
        :param colorkey:
        :param num_images: can be used to limit the set of images loaded from the spritesheet
        """
        filename = Path(filename).as_posix()
        self.filename = filename
        self.image_size = image_size
        super().__init__(
            colorkey=colorkey,
            num_images=num_images,
            scale=scale,
            flip_x=flip_x,
            flip_y=flip_y,
            colormap=colormap,
        )

    def load(self) -> [Surface]:
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
        self.images = images
        if scale:
            self.scale(scale)
        if flip_x or flip_y:
            self.flip(flip_x, flip_y)
        if colormap:
            self.recolor(colormap)

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

    def load(self):
        if not self.images:
            self.images = self.source.load()

    @property
    def images(self):
        """Lazy loading to allow this class to be instantiated before pygame.display.set_mode is
        called."""
        if not self._images:
            self.load()
        return self._images

    @images.setter
    def images(self, new_images):
        self._images = new_images

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
        self.images = [flip_image(image, flip_x, flip_y) for image in self.images]

    def recolor(self, colormap: dict):
        self.images = [recolor_image(image, colormap) for image in self.images]

    def scale(self, scale: float):
        self.images = [scale_image(image, scale) for image in self.images]

    ############## edit and copy ###############
    def flipped_copy(self, flip_x: bool, flip_y: bool):
        return deepcopy(self).flip(flip_x, flip_y)

    def recolored_copy(self, colormap: dict):
        return deepcopy(self).recolor(colormap)

    def scaled_copy(self, scale: float):
        return deepcopy(self).scale(scale)

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
