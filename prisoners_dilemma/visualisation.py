import numpy
from matplotlib import pyplot as plt

from prisoners_dilemma.referee import Referee


def plot_game(ref: Referee):
    fig, ax = plt.subplots()
    for n in (0, 1):
        player = ref.players[n].__class__.__name__
        points = [0, *numpy.cumsum(ref.points[n])]
        plt.plot(points, label=player, drawstyle="steps-pre")
    plt.legend()
    plt.show()
