from fighting_game.sounds.utils import load_sound


def _(name):
    return load_sound(f"falco/{name}")


death = _("death")
gun = _("gun")
laser = _("laser")
airdodge = _("airdodge")
