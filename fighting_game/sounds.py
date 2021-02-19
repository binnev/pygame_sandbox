from pathlib import Path

import pygame

folder = Path(__file__).parent / "sound_files"
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()


def load_sound(name):
    file = (folder / f"{name}.ogg").as_posix()
    return pygame.mixer.Sound(file)


hit = load_sound("hit")
testing = load_sound("testing")
