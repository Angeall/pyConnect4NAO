from random import Random

from ai.connect4 import disc
from ai.connect4.c4_state import C4State
from ai.connect4.player import Player

__author__ = 'Anthony Rouneau'


class Game(object):
    """
    Represents a Connect 4 game with two players (to be registered into the game)
    """
    def __init__(self, ):
        """
        Create a new instance of a Connect 4 Game
        """
        self.game_state = C4State()
        self.players = []
        self.draw = False
        self.next_player = None
        self.first_color = Random().randint(disc.RED, disc.GREEN)

    def checkPlayerTurn(self, player):
        """
        :param player: the payer we want to know if it is its turn to play
        :return: true if its the given player's turn.
        """
        return player is self.players[self.next_player]

    def registerPlayer(self, _strategy):
        """
        :param _strategy: the strategy that the player uses
        :type _strategy: utils.ai.strategy.Strategy
        Registers a new player in the game
        """
        if len(self.players) == 0:
            self.players.append(Player(self.first_color, _strategy))
            _strategy.set_players_id(self.first_color, disc.get_opposite_color(self.first_color))
        else:
            if _strategy is self.players[0].strategy:
                raise AttributeError("The two players cannot have the same Strategy object")
            second_color = disc.get_opposite_color(self.first_color)
            self.players.append(Player(second_color, _strategy))
            _strategy.set_players_id(second_color, self.first_color)
            if second_color == self.game_state.next_color:
                self.next_player = 1
            else:
                self.next_player = 0
        return self.players[-1]

    def makeMove(self, _column):
        """
        :param _column: the number of the column where the disc will be placed if possible
        :type _column: int
        Play an action in the game
        """
        self.game_state.performAction(_column)
        red_won, green_won, draw = self.game_state.terminalTest()
        if red_won:
            if self.players[0].color == disc.RED:
                self.players[0].win()
            else:
                self.players[1].win()
        elif green_won:
            if self.players[0].color == disc.GREEN:
                self.players[0].win()
            else:
                self.players[1].win()
        elif draw:
            self.draw = True
        self.next_player = (self.next_player + 1) % 2

    def playLoop(self):
        """
        A basic logical loop for the game
        """
        while True:
            print self.game_state.board
            if self.draw:
                print "It's a draw !"
                break
            elif self.players[0].hasWon():
                print "Player 1 win with the " + disc.color_string(self.players[0].color) + " color."
                break
            elif self.players[1].hasWon():
                print "Player 2 win with the " + disc.color_string(self.players[1].color) + " color."
                break
            next_move = self.players[self.next_player].chooseMove(self.game_state.copy())
            self.makeMove(next_move)
