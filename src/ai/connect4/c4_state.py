import numpy as np

import disc
from utils.ai.game_state import GameState

__author__ = 'Anthony Rouneau'


class C4State(GameState):
    def __init__(self, _next_color=disc.RED, copied_state=None):
        """
        :param _next_color:
        :param copied_state:
        :type copied_state: C4State
        """
        super(C4State, self).__init__()
        self.next_color = _next_color
        if copied_state is None:
            self.board = np.array(np.zeros((6, 7)), np.int8)
            self.board[:] = disc.EMPTY
            self.actions = range(7)
            self.terminal = False, False, False
            self.hash = self.compute_hash()
        else:  # If this C4State is created from another one
            self.board = copied_state.board.copy()
            self.terminal = copied_state.terminal
            self.hash = copied_state.hash
            self.actions = copied_state.actions

    def compute_possible_actions(self):
        """
        Refresh with a list of hole indices for which the last slot is still empty.
        """
        return np.dstack(np.where(self.board[0] == disc.EMPTY))[0][:, 0].ravel().tolist()

    # @Override
    def possible_actions(self):
        """
        :return: the indices of the _holes that can be used
        """
        return self.actions

    # @Override
    def perform_action(self, column_no):
        """
        :param column_no: the number of the column where the disc will be placed if possible
        :type column_no: int
        """
        if column_no not in self.actions:
            raise AttributeError("This column is full")
        line_no = self.get_top_slot_number(column_no)
        self.board[line_no][column_no] = self.next_color
        color_played = self.next_color
        # Now, it's the other player's turn
        self.next_color = disc.get_opposite_color(self.next_color)
        # We refresh the vars
        self.actions = self.compute_possible_actions()
        self.hash = self.compute_hash()
        self.terminal = self.compute_terminal_local(line_no, column_no, color_played)

    # @Override
    def terminal_test(self):
        """
        :return: a tuple containing three booleans : (red_won, green_won, draw).
                 red_won, green_won is True if there is 4 discs of that color in a row
                 and draw is True if there is a draw
        :rtype: tuple
        """
        return self.terminal

    def compute_terminal_local(self, line, column, color):
        """
        :param line: The line of the last played disc
        :param column: The column of the last played disc
        :param color: The color of the last disc played
        :return: a tuple containing three booleans : (red_won, green_won, draw).
                 red_won, green_won is True if there is 4 discs of that color in a row
                 and draw is True if there is a draw
        :rtype: tuple
        Assume that the game was not terminal before the disc at (line, column) was placed.
        Check if the game is terminated due to the (line, column) disc.
        """
        if len(self.actions) == 0:
            return False, False, True
        red_won = False
        green_won = False
        rows = self.enumerate_rows_local(line, column)
        for row in rows:
            i = 0
            j = 4
            while j <= len(row) and not red_won and not green_won:
                slack = row[i:j]
                if (slack == color).all():
                    if color == disc.RED:
                        red_won = True
                    elif color == disc.GREEN:
                        green_won = True
                    break
                i += 1
                j += 1
            if red_won or green_won:
                break
        if self.next_color == disc.RED:
            return red_won, green_won, False
        else:
            return green_won, red_won, False

    def compute_terminal_global(self):
        """
        :return: a tuple containing three booleans : (red_won, green_won, draw).
                 red_won, green_won is True if there is 4 discs of that color in a row
                 and draw is True if there is a draw
        :rtype: tuple
        Check if the game is terminated for every combination possible on the board
        """
        win_possible = False
        draw = False
        if len(self.actions) == 0:
            return False, False, True
        red_won = False
        green_won = False
        rows = self.enumerate_rows_global()
        for row in rows:
            i = 0
            j = 4
            while j <= len(row) and not red_won and not green_won:
                slack = row[i:j]
                if np.logical_or(slack == disc.EMPTY, slack == disc.RED).all():
                    win_possible = True  # If 4 _holes can be filled with red discs, a win can happen
                    if (slack == disc.RED).all():
                        red_won = True
                        break
                if np.logical_or(slack == disc.EMPTY, slack == disc.GREEN).all():
                    win_possible = True  # If 4 _holes can be filled with green discs, a win can happen
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
        if self.next_color == disc.RED:
            return red_won, green_won, draw
        else:
            return green_won, red_won, draw

    def enumerate_rows_local(self, line, column):
        """
        :param line: the line of the last disc placed
        :param column: the column of the last disc placed
        :return: a list of rows in which the disc in (line, column) could have changed
        """
        rows = []

        # Diagonals
        inverted_board = np.fliplr(self.board)
        rows.append(self.board.diagonal(column - line))
        rows.append(inverted_board.diagonal(6 - column - line))

        # Line
        rows.append(self.board[line])

        # Column
        rows.append(self.board[:, column][line:])

        return rows

    def enumerate_rows_global(self):
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

    # @Override
    def copy(self):
        """
        :return: A copy of this GameState
        """
        return C4State(self.next_color, self)

    # @Override
    def __hash__(self):
        return self.hash

    def compute_hash(self):
        """
        :return: the hash code of this GameState
        """
        res = (tuple(self.board.ravel().tolist()), self.next_color).__hash__()
        return res

    def get_top_slot_number(self, column_no):
        column = self.board[:, column_no]
        # has_disc is a vector of bool in which a slot is True if it contains a disc
        has_disc = column > disc.EMPTY
        # We take the lowest slot available by looking at the slot just before the first disc
        return (np.argmax(has_disc) - 1) % 6

    def check_top_column(self, line_no, column_no):
        # We check if line_no is the lowest slot available by looking at the slot just before the first disc
        return line_no == self.get_top_slot_number(column_no)

