from fighting_game.sounds.utils import load_sound


def _(name):
    return load_sound(f"marth/{name}")


sword_swing = _("sword_swing")
sword_swing2 = _("sword_swing2")
sword_swing3 = _("sword_swing3")
sword_swing4 = _("sword_swing4")
