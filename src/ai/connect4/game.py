from random import Random

from ai.connect4 import disc
from ai.connect4.c4_state import C4State
from ai.connect4.player import Player
from ai.connect4.strategy.human import Human
from ai.connect4.strategy.naive import Naive

__author__ = 'Anthony Rouneau'


class Game(object):
    def __init__(self, ):
        self.game_state = C4State()
        self.players = []
        self.draw = False
        self.next_player = None
        self.first_color = Random().randint(disc.RED, disc.GREEN)

    def register_player(self, _strategy):
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

    def make_move(self, _column):
        """
        :param _column: the number of the column where the disc will be placed if possible
        :type _column: int
        """
        self.game_state.perform_action(_column)
        red_won, green_won, draw = self.game_state.terminal_test()
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

    def play_loop(self):
        while True:
            print self.game_state.board
            if self.draw:
                print "It's a draw !"
                break
            elif self.players[0].has_won():
                print "Player 1 win with the " + disc.color_string(self.players[0].color) + " color."
                break
            elif self.players[1].has_won():
                print "Player 2 win with the " + disc.color_string(self.players[1].color) + " color."
                break
            next_move = self.players[self.next_player].choose_move(self.game_state.copy())
            self.make_move(next_move)

if __name__ == "__main__":
    game = Game()
    game.register_player(Naive())
    game.register_player(Human())
    game.play_loop()


