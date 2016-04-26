from random import Random

import numpy as np

from ai.connect4 import disc
from ai.connect4.game_state import GameState
from ai.connect4.player import Player

__author__ = 'Anthony Rouneau'


class Game(object):
    def __init__(self, ):
        self.game_state = GameState()
        self.player1 = None
        self.player2 = None
        self.draw = False
        self.next_player = None
        self.first_color = Random().randint(disc.RED, disc.GREEN)

    def register_player(self, _strategy):
        if self.player1 is None:
            self.player1 = Player(self.first_color, _strategy)
        else:
            if _strategy is self.player1.strategy:
                raise AttributeError("The two players cannot have the same Strategy object")
            second_color = disc.get_opposite_color(self.first_color)
            self.player2 = Player(second_color, _strategy)
            if second_color == self.game_state.next_color:
                self.next_player = self.player2
            else:
                self.next_player = self.player1

    def make_move(self, _column, _disc):
        """
        :param _column: the number of the column where the disc will be placed if possible
        :type _column: int
        :param _disc: the disc to place, mainly contains the color
        :type _disc: Disc
        """
        self.game_state.make_move(_column, _disc)
        red_won, green_won, draw = self.game_state.check_end()
        if red_won:
            if self.player1.color == disc.RED:
                self.player1.win()
            else:
                self.player2.win()
        elif green_won:
            if self.player1.color == disc.GREEN:
                self.player1.win()
            else:
                self.player2.win()
        elif draw:
            self.draw = True
        if self.next_player is self.player2:
            self.next_player = self.player1
        else:
            self.next_player = self.player2

    def play(self):
        while True:
            if self.draw:
                print "It's a draw !"
                break
            elif self.player1.has_won():
                print "Player 1 win with the " + disc.color_string(self.player1.color) + " color."
                break
            elif self.player2.has_won():
                print "Player 2 win with the " + disc.color_string(self.player2.color) + " color."
                break
            next_move = self.next_player.choose_move(self.game_state.copy())
            self.make_move(next_move, disc.Disc(self.next_player.color))


