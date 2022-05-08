import time

from tic_tac_toe.classes import RandomAgent, HumanAgent, Match, CliController


def main():
    controller = CliController(agent_o=RandomAgent(), agent_x=HumanAgent(), match=Match())
    controller.run_match()

    replay = input("Do you want to replay the match? [y/n]")
    if replay.lower() == "y":
        for move, state in controller.match.history:
            state.print()
            time.sleep(0.5)
            print("")


if __name__ == "__main__":
    main()
