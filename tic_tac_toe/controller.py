from dataclasses import dataclass

from tic_tac_toe.agent import Agent
from .match import Match


@dataclass
class Controller:
    """Currently this is implicitly running a match for the CLI. Might need to create specific
    subclasses for GUI"""

    agent_1: Agent
    agent_2: Agent
    match: Match

    def get_agent(self, player: str) -> Agent:
        return next(agent for agent in [self.agent_1, self.agent_2] if agent.team.symbol==player)

    def display_turn(self):
        raise NotImplementedError

    def run_turn(self):
        player = self.match.player_to_move
        agent = self.get_agent(player)
        move = agent.choose_move(self.match.current_state)
        self.match.do_move(move)

    def run_match(self):
        while self.match.is_active:
            self.run_turn()
            self.display_turn()
        self.handle_match_end()

    def handle_match_end(self):
        raise NotImplementedError


class CliController(Controller):

    def run_match(self):
        print("Starting position:")
        self.match.current_state.print()
        super().run_match()

    def display_turn(self):
        player = self.match.history[-2][1].player_to_move
        move = self.match.history[-1][0]
        print(f"Player {player} has chosen move {move}")
        self.match.current_state.print()
        print("-" * 80)

    def handle_match_end(self):
        winner = self.match.current_state.winner or "no-one"
        print(f"congratulations to {winner}!")
