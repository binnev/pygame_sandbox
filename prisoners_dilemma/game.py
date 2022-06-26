from prisoners_dilemma.referee import Referee
from prisoners_dilemma import player
from prisoners_dilemma.visualisation import plot_game


def one_on_one():
    ref = Referee(player.RandomPlayer(), player.TitForTat())
    ref.play_game(100)
    plot_game(ref)


if __name__ == "__main__":
    one_on_one()
