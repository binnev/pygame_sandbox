from dataclasses import dataclass
from typing import Protocol

FloatRect = tuple[float, float, float, float]  # like Rect but with floats


class ViewportHandler(Protocol):
    """
    Handles pan / zoom functionality.
    Generates a Rect of the viewport in xy matrix coordinates.
    Multiple frontends can listen to this.
    """

    x: float
    y: float
    width: float
    height: float
    viewport: FloatRect  # in xy matrix coords

    def zoom(self, amount: float):
        """
        If amount > 0: zoom in.
        If amount < 0: zoom out.
        """

    def pan(self, x: float = 0, y: float = 0):
        """
        If x > 0: move viewport right. If x < 0: move viewport left.
        If y > 0: move viewport down. If y < 0: move viewport up.
        """


@dataclass
class DefaultViewportHandler:
    """
    Being quite militant about the protocols thing here...
    """

    x: float
    y: float
    width: float
    height: float

    scale: float = 4.0

    ZOOM_SPEED = 1.1
    MIN_WIDTH = MIN_HEIGHT = 3.0
    MAX_WIDTH = MAX_HEIGHT = 1000.0

    @property
    def viewport(self) -> FloatRect:
        """Here I treat self.x, self.y as the center of the viewport; this makes sure when we
        zoom, we zoom on the center of the viewport, not the top left corner. """
        x = self.x - self.width / 2
        y = self.y - self.height / 2
        return (x, y, self.width, self.height)

    def zoom(self, amount: float):
        """
        NOTE: when zoomed in so far that only 1 pixel is on screen, the draw speed can
        increase dramatically. I think this is because even though only 1 cell is being drawn,
        the big_img is many times the size of the surface, with no upper limit on its size. So
        if using this method, put a sensible limit on how far you can zoom in.
        """
        # ignoring the value of amount and multiplying by a speed factor gives more uniform zoom
        # feel at varying scales
        if amount > 0:
            self.width /= self.ZOOM_SPEED
            self.height /= self.ZOOM_SPEED
        elif amount < 0:
            self.width *= self.ZOOM_SPEED
            self.height *= self.ZOOM_SPEED
        self.width = max(self.MIN_WIDTH, self.width)
        self.width = min(self.MAX_WIDTH, self.width)
        self.height = max(self.MIN_HEIGHT, self.height)
        self.height = min(self.MAX_HEIGHT, self.height)

    def pan(self, x: float = 0, y: float = 0):
        speed = 0.01 * min(self.width, self.height)
        self.x += x * speed
        self.y += y * speed
