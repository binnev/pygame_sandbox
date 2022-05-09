import time

from tic_tac_toe.agent import MinimaxCliAgent, HumanCliAgent
from tic_tac_toe.constants import X, O
from tic_tac_toe.controller import CliController
from tic_tac_toe.match import Match


def main():
    controller = CliController(
        agent_1=MinimaxCliAgent(team=O),
        agent_2=HumanCliAgent(team=X),
        match=Match(),
    )
    controller.run_match()


if __name__ == "__main__":
    main()
