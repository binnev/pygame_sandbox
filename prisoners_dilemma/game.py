from typing import Type

from prisoners_dilemma.player import Player
from prisoners_dilemma.referee import Referee
from prisoners_dilemma import player
from prisoners_dilemma.visualisation import plot_game


def one_on_one(player_i: Player, player_j: Player, n_turns=100):
    ref = Referee(player_i, player_j)
    ref.play_game(n_turns)
    player_i.score += sum(ref.points[0])
    player_j.score += sum(ref.points[1])


def round_robin(contestants: list[Player], n_turns=100):
    for ii, contestant_i in enumerate(contestants):
        for jj, contestant_j in enumerate(contestants):
            one_on_one(contestant_i, contestant_j, n_turns)


def evolution_game():
    contestants = [
        player.RandomPlayer(),
        player.AlwaysCooperate(),
        player.AlwaysDefect(),
        player.NeverForgive(),
        player.TitForTat(),
        player.TitForTwoTat(),
        player.MostlyNice(),
        player.MostlyNasty(),
    ]
    n_generations = 10
    turns_per_gen = 10
    reproduction_threshold = 1000
    for gen in range(n_generations):
        round_robin(contestants, n_turns=turns_per_gen)
        print("")
        print(f"--- gen {gen} ---")
        for contestant in sorted(contestants, key=lambda c: -c.score):
            print(f"{contestant:<20}{contestant.score}", end="")
            reproductions = 0
            while contestant.score >= reproduction_threshold:
                contestants.append(contestant.__class__()),
                contestant.score -= reproduction_threshold
                reproductions += 1
            print(f" --> {reproductions} reproductions!" if reproductions else "")

        print("")
        print("Population now looks like:")
        contestant_names = {c.name for c in contestants}
        for name in sorted(contestant_names):
            print(f"{name:<20}{len([c for c in contestants if c.name == name])}")





if __name__ == "__main__":
    evolution_game()