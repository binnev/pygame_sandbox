import pygame

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

TICKS_PER_SPRITE_FRAME = 3  # how long to display each sprite frame? Higher = slower animation
SCALE_SPRITES = 3  # how much to scale up sprites

# key mapping
class Keys:
    JUMP = pygame.K_UP
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    FIRE = pygame.K_SPACE