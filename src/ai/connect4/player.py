__author__ = 'Anthony Rouneau'


class Player(object):

    def __init__(self, _color, _strategy):
        """
        :param _color: the color of the player's discs
        :type _color: int
        :param _strategy: the strategy this player will chooseMove
        :type _strategy: Strategy
        """
        self.color = _color
        self.won = False
        self.strategy = _strategy

    def hasWon(self):
        return self.won

    def win(self):
        self.won = True

    def chooseMove(self, game_state):
        """
        :param game_state: the current state of the game
        :type game_state: C4State
        :return: the number of the hole in which place the disc
        :rtype: int
        """
        return self.strategy.chooseNextAction(game_state)


