import time

from connect_four.state import YELLOW, RED, State
from tic_tac_toe.agent import MinimaxCliAgent, HumanCliAgent, RandomAgent
from tic_tac_toe.controller import CliController
from tic_tac_toe.match import Match


def main():
    controller = CliController(
        agent_1=HumanCliAgent(team=YELLOW),
        agent_2=MinimaxCliAgent(team=RED, depth=6),
        match=Match(initial_state=State.initial()),
    )
    controller.run_match()


if __name__ == "__main__":
    main()
