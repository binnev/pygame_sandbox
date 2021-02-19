from pathlib import Path

import pygame

folder = Path(__file__).parent / "sound_files"
pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()
hit = pygame.mixer.Sound((folder / "hit.ogg").as_posix())
