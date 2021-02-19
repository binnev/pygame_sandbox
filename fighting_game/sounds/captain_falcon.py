from fighting_game.sounds.utils import load_sound


def _(name):
    return load_sound(f"captain_falcon/{name}")


show_me_your_moves = _("show_me_your_moves")
death = _("death")
death2 = _("death2")
swing = _("swing")
swish = _("swish")
dodge = _("dodge")
eagle = _("eagle")
