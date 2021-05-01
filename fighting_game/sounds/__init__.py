import pygame

from .utils import load_sound

def _(name):
    return load_sound(f"general/{name}")

pygame.mixer.pre_init(32000, -16, 2, 512)
pygame.mixer.init()

hit = _("hit")
hit2 = _("hit2")
hit3 = _("hit3")
hit4 = _("hit4")
hit5 = _("hit5")
hit6 = _("hit6")
hit7 = _("hit7")
hit8 = _("hit8")
hit9 = _("hit9")
hit10 = _("hit10")
hit11 = _("hit11")
hit12 = _("hit12")
bighit = _("bighit")
bighit2 = _("bighit2")
bighit3 = _("bighit3")
sword_hit = _("sword_hit")
sword_hit2 = _("sword_hit2")
hit_electric = _("hit_electric")
hit_electric2 = _("hit_electric2")
hit_electric3 = _("hit_electric3")
announcement = _("announcement")
death_plume = _("death_plume")
crowd_ohh = _("crowd_ohh")
sword_clank = _("sword_clank")
sword_clank2 = _("sword_clank2")
sword_clank3 = _("sword_clank3")
sword_clank4 = _("sword_clank4")
sword_swing = _("sword_swing")

swing7 = _("swing7")
swing6 = _("swing6")
swing5 = _("swing5")
swing4 = _("swing4")
swing3 = _("swing3")
swing2 = _("swing2")
swing = _("swing")

smack3 = _("smack3")
smack2 = _("smack2")
smack = _("smack")

tap4 = _("tap4")

from . import captain_falcon
from . import falco
from . import marth
