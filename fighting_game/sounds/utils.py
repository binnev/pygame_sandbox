import glob
from pathlib import Path

import pygame

folder = Path(__file__).parent / "files"


def load_sound(name):
    files = glob.glob((folder / f"{name}.*").as_posix())
    assert len(files) > 0, f"Couldn't find sound called '{name}'"
    assert len(files) < 2, f"There's more than one sound called '{name}'"
    file = files[0]
    return pygame.mixer.Sound(file)
