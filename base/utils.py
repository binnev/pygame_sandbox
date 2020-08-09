from collections import namedtuple

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