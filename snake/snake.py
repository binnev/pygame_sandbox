import pygame


class snake:
    def __init__(self, color, pos):
        pass

    def move(self):
        pass

    def reset(self):
        pass

    def addCube(self):
        pass

    def draw(self):
        pass


def drawGrid(w, rows, surface):
    pass


def redrawWindow(surface):
    surface.fill((0, 0, 0))
    drawGrid(surface)
    pygame.display.update()


def randomSnack(rows, items):
    pass


def message_box(subject, content):
    pass


def main():
    width = 500
    height = 500
    rows = 20
    win = pygame.display.set_mode((width, height))

    s = snake((255, 0, 0), (10, 10))
    flag = True

    clock = pygame.time.Clock()

    while flag:
        pygame.time.delay(50)  # sets the delay between actions? Lower = faster
        clock.tick(10)  # sets the FPS. Lower = slower
        redrawWindow(win)
