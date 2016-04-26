from ai.connect4 import disc
from ai.connect4.strategy import Strategy
from ai.connect4.game import GameState


__author__ = 'Anthony Rouneau'


class Player(object):

    def __init__(self, _color, _strategy):
        """
        :param _color: the color of the player's discs
        :type _color: int
        :param _strategy: the strategy this player will choose_move
        :type _strategy: Strategy
        """
        self.color = _color
        self.won = False
        self.strategy = _strategy

    def has_won(self):
        return self.won

    def win(self):
        self.won = True

    def choose_move(self, game_state):
        """
        :param game_state: the current state of the game
        :type game_state: GameState
        :return: the number of the hole in which place the disc
        :rtype: int
        """
        return self.strategy.next_move(game_state)


