from tic_tac_toe.agent import MinimaxCliAgent, HumanCliAgent
from tic_tac_toe.controller import CliController
from tic_tac_toe.match import Match
from tic_tac_toe.team import TEAM_O, TEAM_X


def main():
    controller = CliController(
        agent_1=MinimaxCliAgent(team=TEAM_O),
        agent_2=HumanCliAgent(team=TEAM_X),
        match=Match(),
    )
    controller.run_match()


if __name__ == "__main__":
    main()
