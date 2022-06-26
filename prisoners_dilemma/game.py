from prisoners_dilemma.referee import Referee
from prisoners_dilemma import player
from prisoners_dilemma.visualisation import plot_game


def main():
    ref = Referee(player.TitForTat(), player.NeverForgive())
    ref.play_game(100)
    plot_game(ref)


if __name__ == "__main__":
    main()
