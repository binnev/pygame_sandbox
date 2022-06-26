from functools import lru_cache
from typing import Type

import matplotlib.pyplot as plt

from prisoners_dilemma import player
from prisoners_dilemma.player import Player
from prisoners_dilemma.referee import Referee


@lru_cache()
def one_on_one(player_i: Type[Player], player_j: Type[Player], n_turns=100):
    ref = Referee(player_i(), player_j())
    ref.play_game(n_turns)
    score_i = sum(ref.points[0])
    score_j = sum(ref.points[1])
    return score_i, score_j


def round_robin(contestants: list[Player], n_turns=100):
    for ii, player_i in enumerate(contestants):
        for jj, player_j in enumerate(contestants):
            score_i, score_j = one_on_one(player_i.__class__, player_j.__class__, n_turns)
            player_i.score += score_i
            player_j.score += score_j


def play_generation(
    contestants: list[Player],
    n_turns=100,
    reproduction_threshold=1000,
    penalty_func=lambda pop: 0,
):
    round_robin(contestants, n_turns=n_turns)
    penalty = penalty_func(len(contestants))
    print(f"Population = {len(contestants)} so penalty = {penalty}")
    for contestant in contestants:
        contestant.score -= penalty
    for contestant in sorted(contestants, key=lambda c: -c.score):
        print(f"{contestant:<20}{contestant.score}", end="")
        reproductions = 0
        while contestant.score >= reproduction_threshold:
            contestants.append(contestant.__class__()),
            contestant.score -= reproduction_threshold
            reproductions += 1
        print(f" --> {reproductions} reproductions!" if reproductions else "")
        if contestant.score < 0:
            print(f"{contestant} died")
            contestants.remove(contestant)


def census(contestants: list[Player], names: list[str]):
    return {name: len([c for c in contestants if c.name == name]) for name in names}


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
    contestant_names = {c.name for c in contestants}
    n_generations = 20
    turns_per_gen = 10
    reproduction_threshold = 500
    penalty_func = lambda pop: 0.8 * pop**2
    population_history = {c.name: [] for c in contestants}
    for gen in range(n_generations):
        print("")
        print(f"--- gen {gen} ---")
        play_generation(
            contestants,
            n_turns=turns_per_gen,
            reproduction_threshold=reproduction_threshold,
            penalty_func=penalty_func,
        )

        print("")
        print("Population now looks like:")
        population = census(contestants, contestant_names)
        for name in sorted(population, key=lambda x: -population[x]):
            print(f"{name:<20}{population[name]}")

        for name, count in population.items():
            population_history[name].append(count)

    fig, ax = plt.subplots()
    plt.stackplot(
        range(n_generations),
        *population_history.values(),
        labels=population_history.keys(),
    )
    plt.legend(loc="upper left")
    plt.show()


if __name__ == "__main__":
    evolution_game()
