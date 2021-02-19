import pygame

from .utils import load_sound

def _(name):
    return load_sound(f"general/{name}")

pygame.mixer.pre_init(32000, -16, 2, 512)
pygame.mixer.init()

hit = _("hit")
hit2 = _("hit2")
bighit = _("bighit")
bighit2 = _("bighit2")
announcement = _("announcement")


from . import captain_falcon
from . import falco
from . import marth
