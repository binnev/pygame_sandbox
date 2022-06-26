"""Prisoner's dilemma game strategies inspired by The Selfish Gene"""
from prisoners_dilemma.constants import (
    DEFECT,
    MUTUAL_DEFECT,
    COOPERATE,
    MUTUAL_COOP,
    INDIVIDUAL_DEFECT,
    INDIVIDUAL_COOP,
)
from prisoners_dilemma.player import Player


def assign_rewards(p1_move, p2_move):
    moves = p1_move, p2_move
    if moves == (DEFECT, DEFECT):
        return MUTUAL_DEFECT, MUTUAL_DEFECT
    if moves == (COOPERATE, COOPERATE):
        return MUTUAL_COOP, MUTUAL_COOP
    if moves == (DEFECT, COOPERATE):
        return INDIVIDUAL_DEFECT, INDIVIDUAL_COOP
    if moves == (COOPERATE, DEFECT):
        return INDIVIDUAL_COOP, INDIVIDUAL_DEFECT


class Controller:
    players: tuple[Player, Player]
    moves: list[list[str], list[str]]
    points: list[list[int], list[int]]

    def __init__(self, player0: Player, player1: Player):
        self.players = player0, player1
        self.moves = [[], []]
        self.points = [[], []]

    def play_turn(self):
        moves = []
        for n in (0, 1):
            other_n = int(not bool(n))
            player: Player = self.players[n]
            move = player.play_turn(
                self_history=self.moves[n],
                other_history=self.moves[other_n],
            )
            moves.append(move)

        points = assign_rewards(*moves)
        for n, move in enumerate(moves):
            self.moves[n].append(move)
        for n, point in enumerate(points):
            self.points[n].append(point)
