from prisoners_dilemma.controller import Controller
from prisoners_dilemma.player import AlwaysCooperate, RandomPlayer, AlwaysDefect, TitForTat


def main():
    ref = Controller(RandomPlayer(), TitForTat())
    for turn in range(10):
        ref.play_turn()
        print("-" * 20 + f"turn {turn} " + "-" * 20)
        for n in (0, 1):
            player = ref.players[n]
            move = ref.moves[n][-1]
            points = sum(ref.points[n])
            print(f"{player} chose {move} and has {points} points")


if __name__ == "__main__":
    main()
