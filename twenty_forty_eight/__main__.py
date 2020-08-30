import matplotlib.pyplot as plt
import pygame

from base.keyhandler import KeyHandler
from twenty_forty_eight.objects import Board

cm = plt.cm.viridis


def colormap(value, max_):
    offset = 70
    return [offset + i * (255 - offset) for i in cm(value / max_)[:-1]]


KeyHandler.initialise()
pygame.init()
X = 400
Y = 400

font = pygame.font.Font("freesansbold.ttf", 32)

window = pygame.display.set_mode((X, Y))
pygame.display.set_caption("Hello World")
board = Board(4)

run = True
while run:
    pygame.time.delay(100)

    # ============= react to key presses ==============
    keys = pygame.key.get_pressed()
    KeyHandler.append(keys)
    if KeyHandler.is_pressed(pygame.K_ESCAPE):
        pygame.quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if any(keys):
        print("a key was pressed this tick")
        board.update()

        if board.is_full():
            run = False
            print("YOU LOSE, LOSER")
        if board.has_changed():
            board.add_random_entry()

    # draw the board
    window.fill((0, 0, 0))
    for y, row in enumerate(board.grid):
        for x, char in enumerate(row):
            color = (50, 50, 50) if char == 0 else colormap(char, 128)
            text = font.render(str(char), True, color, None)
            textRect = text.get_rect()
            textRect.center = (50 + x * 100, 50 + y * 100)
            window.blit(text, textRect)
    pygame.display.update()

pygame.quit()
