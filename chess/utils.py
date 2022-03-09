from chess.constants import WHITE, BLACK, Teams


def other_team(team: Teams):
    return WHITE if team == BLACK else BLACK
