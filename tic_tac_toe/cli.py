import time

from tic_tac_toe.agent import MinimaxCliAgent, HumanCliAgent
from tic_tac_toe.constants import X, O
from tic_tac_toe.controller import CliController
from tic_tac_toe.match import Match


def main():
    controller = CliController(
        agent_o=MinimaxCliAgent(team=O),
        agent_x=HumanCliAgent(team=X),
        match=Match(),
    )
    controller.run_match()

    replay = input("Do you want to replay the match? [y/n]")
    if replay.lower() == "y":
        for move, state in controller.match.history:
            state.print()
            time.sleep(0.5)
            print("")


if __name__ == "__main__":
    main()
