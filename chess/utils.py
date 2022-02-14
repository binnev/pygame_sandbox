from chess.constants import WHITE, BLACK


def other_team(team: str):
    return WHITE if team == BLACK else BLACK
