import disc
from disc import Disc
import numpy as np

__author__ = 'Anthony Rouneau'


class GameState(object):
    def __init__(self, _next_color=disc.RED, _board=None, _hash=None):
        self.next_color = _next_color
        if _board is None:  # If the game has not started yet
            self.board = np.array(np.zeros((6, 7)), np.int8)
            self.board[:] = disc.EMPTY
        else:  # If this GameState is created from another one
            self.board = _board
        self.possible_actions = []
        self.refresh_possible_actions()
        if _hash is None:
            self.hash = _hash
        else:
            self.refresh_hash()

    def refresh_possible_actions(self):
        """
        Refresh with a list of hole indices for which the last slot is still empty.
        """
        self.possible_actions = np.dstack(np.where(self.board[0] == 0))[0][:, 0]

    def possible_actions(self):
        """
        :return: the indices of the holes that can be used
        """
        return self.possible_actions

    def make_fake_action(self, action):
        new_state = self.copy()
        new_state.make_move(action)

    def make_move(self, _action):
        """
        :param _action: the number of the column where the disc will be placed if possible
        :type _action: int
        :return:
        """
        if _action not in self.possible_actions:
            raise AttributeError("This column is full")
        column = self.board[:, _action]
        # has_disc is a vector of bool in which a slot is True if it contains a disc
        has_disc = column >= disc.EMPTY
        # We fulfill the lowest slot available by looking at the slot just before the first disc
        column[np.argmax(has_disc) - 1] = self.next_color
        # Now, it's the other player's turn
        self.next_color = disc.get_opposite_color(self.next_color)
        self.refresh_possible_actions()
        self.refresh_hash()

    def get_board(self):
        return self.board

    def check_end(self):
        """
        :return: a tuple containing three booleans : (red_won, green_won, draw).
                 red_won, green_won is True if there is 4 discs of that color in a row
                 and draw is True if there is a draw
        :rtype: tuple
        """
        win_possible = False
        draw = False
        red_won = False
        green_won = False
        if len(self.possible_actions) == 0:
            draw = True
        if not draw:
            red_won = False
            green_won = False
            rows = self.enumerate_rows()
            for row in rows:
                i = 0
                j = 4
                while j <= len(row) and not red_won and not green_won:
                    slack = row[i:j]
                    if np.logical_or(slack == disc.EMPTY, slack == disc.RED).all():
                        win_possible = True  # If 4 holes can be filled with red discs, a win can happen
                        if (slack == disc.RED).all():
                            red_won = True
                            break
                    if np.logical_or(slack == disc.EMPTY, slack == disc.GREEN).all():
                        win_possible = True  # If 4 holes can be filled with green discs, a win can happen
                        if (slack == disc.GREEN).all():
                            green_won = True
                            break
                    i += 1
                    j += 1
                if red_won or green_won:
                    break
            if not red_won and not green_won and not win_possible:
                draw = True
        assert not (red_won and green_won) and not ((draw and red_won) or (draw and green_won))
        return red_won, green_won, draw

    def enumerate_rows(self):
        """
        :return: a list of rows in which there could be 4 discs aligned
        """
        rows = []

        # Diagonals
        inverted_board = np.fliplr(self.board)
        for i in range(-2, 4):  # Getting the diagonals where there might be 4 in a row
            rows.append(self.board.diagonal(i))
            rows.append(inverted_board.diagonal(i))

        # Lines
        for i in range(6):
            rows.append(self.board[i])

        # Columns
        for i in range(7):
            rows.append(self.board[:, i])

        return rows

    def copy(self):
        return GameState(self.next_color, self.board.copy(), self.hash)

    def __hash__(self):
        return self.hash

    def refresh_hash(self):
        self.hash = (tuple(self.board.ravel().tolist()), self.next_color).__hash__()

