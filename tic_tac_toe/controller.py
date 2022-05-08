from dataclasses import dataclass

from tic_tac_toe.agent import Agent
from tic_tac_toe.constants import X, O
from .match import Match


@dataclass
class Controller:
    """Currently this is implicitly running a match for the CLI. Might need to create specific
    subclasses for GUI"""

    agent_o: Agent
    agent_x: Agent
    match: Match

    def get_agent(self, player: str) -> Agent:
        return {X: self.agent_x, O: self.agent_o}[player]

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
    def display_turn(self):
        player = self.match.player_to_move
        move = self.match.history[-1][0]
        print(f"Player {player} has chosen move {move}")
        self.match.current_state.print()

    def handle_match_end(self):
        winner = self.match.current_state.winner or "no-one"
        print(f"congratulations to {winner}!")
