from .state import State


class Match:
    history: list[tuple[int | None, State]]

    def __init__(self, initial_state: State = None):
        state = initial_state or State.initial()
        self.history = []
        self.history.append((None, state))

    def do_move(self, move: int):
        next_state = self.current_state.do_move(move)
        self.history.append((move, next_state))

    @property
    def current_state(self):
        return self.history[-1][1]

    @property
    def is_active(self) -> bool:
        return not self.current_state.is_game_over

    @property
    def player_to_move(self):
        return self.current_state.player_to_move
