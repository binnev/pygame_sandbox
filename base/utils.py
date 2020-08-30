from collections import namedtuple

import numpy
import pygame

Point = namedtuple("Point", ["x", "y"])


def touching(entity1: "Entity", entity2: "Entity") -> bool:
    """Determine whether entity1 is touching entity2. This function is directional by
    design---i.e. it checks whether
        (a) entity1.touchbox collides with entity2.rect
        it does *not* check whether
        (b) entity2.touchbox collides with entity1.rect.

    This is because in most cases the entities will have touchboxes with the same width
    buffer. If this is the case then (a) cannot be true without (b) also being true,
    and we needn't bother doing both calculations.

    Also, I want to allow for the possibility of unequal touchbox buffer widths; in
    this case, the order *will* matter. The entity with the larger touchbox buffer will
    "touch" the other entity, but not vice versa. """
    return entity1.touchbox.colliderect(entity2.rect)


def get_overlap_between_objects(obj1, obj2):
    """Get the x and y overlap between obj1 and obj2.rect"""
    x_overlap = min(obj1.rect.right, obj2.rect.right) - max(obj1.rect.left, obj2.rect.left)
    y_overlap = min(obj1.rect.bottom, obj2.rect.bottom) - max(obj1.rect.top, obj2.rect.top)
    return x_overlap, y_overlap


def un_overlap(movable_object, immovable_object):
    """Move movable_object outside boundaries of immovable_object."""
    x_overlap, y_overlap = get_overlap_between_objects(movable_object, immovable_object)
    if x_overlap > y_overlap:
        if movable_object.centroid.y >= immovable_object.centroid.y:
            movable_object.rect.top = immovable_object.rect.bottom
        else:
            movable_object.rect.bottom = immovable_object.rect.top
    else:
        if movable_object.centroid.x >= immovable_object.centroid.x:
            movable_object.rect.left = immovable_object.rect.right
        else:
            movable_object.rect.right = immovable_object.rect.left


# need these helper functions because pygame.mask.Mask methods aren't actually
# implemented as they are described in the docs...
def maskFromSurface(surface, threshold=127):
    # return pygame.mask.from_surface(surface, threshold)

    mask = pygame.mask.Mask(surface.get_size())
    key = surface.get_colorkey()
    if key:
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if surface.get_at((x, y)) != key:
                    mask.set_at((x, y), 1)
    else:
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if surface.get_at((x, y))[3] > threshold:
                    mask.set_at((x, y), 1)
    return mask


def mask_to_surface(mask, set_color=None):
    set_color = set_color if set_color else pygame.color.THECOLORS["magenta"]
    width, height = mask.get_size()
    surface = pygame.Surface((width, height)).convert_alpha()
    surface.fill((0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            if mask.get_at((x, y)):
                surface.set_at((x, y), set_color)
    return surface


def ticks_to_frames(tick, ticks_per_frame):
    return tick // ticks_per_frame


def draw_arrow_between_points(surface, p1, p2, color=None):
    p1 = numpy.array(p1)
    p2 = numpy.array(p2)
    dx, dy = p2 - p1

    # y is down in pygame, but rotations are still counterclockwise, so we need to reverse y.
    # Great job, pygame developers -.-
    angle = numpy.rad2deg(numpy.arctan2(-dy, dx))
    color = color if color else pygame.color.THECOLORS["red"]
    pygame.draw.line(surface, color, p1, p2, 2)

    font = pygame.font.Font(pygame.font.match_font("ubuntucondensed"), 30)
    text = font.render(f"dx={dx} dy={dy} angle={angle} ", True, color)
    surface.blit(text, (100, 100))

    arrowhead_width = 20
    arrowhead_length = 40
    arrowhead_image = pygame.Surface((arrowhead_length, arrowhead_width)).convert_alpha()
    arrowhead_image.fill((0, 0, 0, 0))
    arrowhead_origin = numpy.array(arrowhead_image.get_rect().midleft)
    pygame.draw.polygon(
        arrowhead_image,
        color,
        [
            arrowhead_origin + (arrowhead_length, 0),
            arrowhead_origin + (0, arrowhead_width / 2),
            arrowhead_origin + (0, -arrowhead_width / 2),
        ],
    )
    arrowhead_image = pygame.transform.rotate(arrowhead_image, angle)
    image_rect = arrowhead_image.get_rect()
    image_rect.center = p2
    surface.blit(arrowhead_image, image_rect)


def draw_arrow(surface, origin, angle: "degrees", color=None, length=50):
    """ angle needs to be in degrees """
    angle = numpy.deg2rad(angle)
    dx = length * numpy.cos(angle)
    dy = -length * numpy.sin(angle)  # dy needs to be flipped because pygame y downwards

    p2 = numpy.array(origin) + (dx, dy)
    draw_arrow_between_points(surface, origin, p2, color)
