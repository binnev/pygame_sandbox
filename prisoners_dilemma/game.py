import matplotlib.pyplot as plt

from prisoners_dilemma import player
from prisoners_dilemma.player import Player
from prisoners_dilemma.referee import Referee


def one_on_one(player_i: Player, player_j: Player, n_turns=100):
    ref = Referee(player_i, player_j)
    ref.play_game(n_turns)
    player_i.score += sum(ref.points[0])
    player_j.score += sum(ref.points[1])


def round_robin(contestants: list[Player], n_turns=100):
    for ii, contestant_i in enumerate(contestants):
        for jj, contestant_j in enumerate(contestants):
            one_on_one(contestant_i, contestant_j, n_turns)


def play_generation(contestants: list[Player], n_turns=100, reproduction_threshold=1000):
    round_robin(contestants, n_turns=n_turns)
    for contestant in sorted(contestants, key=lambda c: -c.score):
        print(f"{contestant:<20}{contestant.score}", end="")
        reproductions = 0
        while contestant.score >= reproduction_threshold:
            contestants.append(contestant.__class__()),
            contestant.score -= reproduction_threshold
            reproductions += 1
        print(f" --> {reproductions} reproductions!" if reproductions else "")


def census(contestants: list[Player]):
    contestant_names = {c.name for c in contestants}
    return {name: len([c for c in contestants if c.name == name]) for name in contestant_names}


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
    n_generations = 5
    turns_per_gen = 10
    reproduction_threshold = 500
    population_history = {c.name: [] for c in contestants}
    for gen in range(n_generations):
        print("")
        print(f"--- gen {gen} ---")
        play_generation(
            contestants,
            n_turns=turns_per_gen,
            reproduction_threshold=reproduction_threshold,
        )

        print("")
        print("Population now looks like:")
        population = census(contestants)
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
