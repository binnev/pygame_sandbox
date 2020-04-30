import pygame


def sign(number):
    # todo: this will not work correctly for zero...
    return 1 if number > 0 else -1

def recolor(surface, old_color, new_color):
    old_color = pygame.Color(*old_color)
    new_color = pygame.Color(*new_color)
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            pixel = surface.get_at((x, y))
            if pixel == old_color:
                surface.set_at((x, y), pygame.Color(*new_color))
    return surface