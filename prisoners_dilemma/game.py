import random
from functools import lru_cache
from typing import Type

import matplotlib.pyplot as plt

from prisoners_dilemma import player
from prisoners_dilemma.player import Player
from prisoners_dilemma.referee import Referee


# @lru_cache()
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


def aggregate_round_robin(
    population: dict[Type[Player] : int], n_turns: int
) -> dict[Type[Player] : int]:
    scores = {contestant: 0 for contestant in population}
    for player_class_i, count_i in population.items():
        for player_class_j, count_j in population.items():
            n_matches = count_i * count_j
            score_i, score_j = one_on_one(player_class_i, player_class_j, n_turns)
            total_i = score_i * n_matches
            total_j = score_j * n_matches
            scores[player_class_i] += total_i
            scores[player_class_j] += total_j
    return scores


def play_generation(
    population: dict[Type[Player] : int],
    n_turns=100,
):
    scores = aggregate_round_robin(population, n_turns=n_turns)
    total_points = sum(scores.values())
    percentages = {name: round(score / total_points * 100) for name, score in scores.items()}
    return percentages


def census(contestants: list[Player], names: list[str]):
    return {name: len([c for c in contestants if c.name == name]) for name in names}


def evolution_game():
    population = {
        player.NeverForgive: 1,  # random.randint(1, 100),
        player.TitForTat: 1,  # random.randint(1, 100),
        player.RetaliateTwice: 1,  # random.randint(1, 100),
        player.TolerateTwoHits: 1,  # random.randint(1, 100),
        player.AlwaysCooperate: 1,  # random.randint(1, 100),
        player.MostlyNice: 1,  # random.randint(1, 100),
        player.RandomPlayer: 1,  # random.randint(1, 100),
        player.MostlyNasty: 1,  # random.randint(1, 100),
        player.AlwaysDefect: 1,  # random.randint(1, 100),
    }
    n_generations = 99999999999999
    turns_per_gen = 100
    population_history = []
    for gen in range(n_generations):
        print("")
        print(f"--- gen {gen} ---")
        population = play_generation(population, n_turns=turns_per_gen)

        print("")
        print("Population now looks like:")
        for contestant in sorted(population, key=lambda x: -population[x]):
            print(f"{contestant.__name__:<20}{population[contestant]}")

        population_history.append({**population})
        if len(population_history) > 3 and (
            population_history[-3] == population_history[-2] == population_history[-1]
        ):
            break
    fig, ax = plt.subplots()
    counts = [[item[contestant] for item in population_history] for contestant in population]
    labels = [contestant.__name__ for contestant in population]
    plt.stackplot(range(len(population_history)), *counts, labels=labels)
    plt.legend(
        loc="best",
        bbox_to_anchor=(0.35, 0.65, 0.5, 0.5),
        fontsize="x-small",
        ncol=3,
    )
    plt.show()


if __name__ == "__main__":
    evolution_game()
