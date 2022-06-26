from prisoners_dilemma.referee import Referee
from prisoners_dilemma import player
from prisoners_dilemma.visualisation import plot_game


def one_on_one():
    ref = Referee(player.RandomPlayer(), player.NeverForgive())
    ref.play_game(100)
    plot_game(ref)


def round_robin():
    N_TURNS = 100
    contestants = [
        player.RandomPlayer,
        player.AlwaysCooperate,
        player.AlwaysDefect,
        player.NeverForgive,
        player.TitForTat,
        player.TitForTwoTat,
        player.MostlyNice,
        player.MostlyNasty,
    ]
    scores = dict()
    for contestant0 in contestants:
        for contestant1 in contestants:
            ref = Referee(contestant0(), contestant1())
            ref.play_game(N_TURNS)
            score0 = sum(ref.points[0])
            score1 = sum(ref.points[1])
            p0_name = contestant0.__name__
            p1_name = contestant1.__name__
            scores[p0_name] = scores.get(p0_name, 0) + score0
            scores[p1_name] = scores.get(p1_name, 0) + score1
    print(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))


if __name__ == "__main__":
    round_robin()
