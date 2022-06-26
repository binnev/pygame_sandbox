from unittest.mock import patch

from prisoners_dilemma import player
from prisoners_dilemma.game import one_on_one


@patch("prisoners_dilemma.referee.Referee.play_game")
def test_caching(mock):
    for ii in range(3):
        one_on_one(player.RandomPlayer, player.RandomPlayer)

    assert mock.call_count == 1

