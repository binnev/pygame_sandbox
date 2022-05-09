from connect_four.state import State
from connect_four.team import TEAM_RED, TEAM_YELLOW
from tic_tac_toe.agent import MinimaxCliAgent, HumanCliAgent
from tic_tac_toe.controller import CliController
from tic_tac_toe.match import Match


def main():
    controller = CliController(
        agent_1=HumanCliAgent(team=TEAM_YELLOW),
        agent_2=MinimaxCliAgent(team=TEAM_RED, depth=7),
        match=Match(initial_state=State.initial()),
    )
    controller.run_match()


if __name__ == "__main__":
    main()
