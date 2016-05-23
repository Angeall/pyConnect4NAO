import numpy as np

from ai.connect4 import disc
from ai.connect4.c4_state import C4State
from utils.ai.game_state import InvalidStateException
from utils.ai.strategy import Strategy

__author__ = 'Anthony Rouneau'

nao_video = None


def bgr_to_hsv(bgr_list):
    """
    :param bgr_list: sequence of triplet (b, g, r)
    :return: the sequence of hsv values, resulting of the conversion of each bgr value of the initial sequence
    """
    hsv_list = []
    for bgr in bgr_list:
        _bgr = [bgr[0] / 255.0, bgr[1] / 255.0, bgr[2] / 255.0]
        max_index = np.argmax(_bgr)
        min_index = np.argmin(_bgr)
        delta = _bgr[max_index] - _bgr[min_index]
        if delta == 0:
            h = 0
        elif max_index == 0:
            h = (60 * (((_bgr[2] - _bgr[1]) / delta) + 4)) % 360
        elif max_index == 1:
            h = (60 * (((_bgr[0] - _bgr[2]) / delta) + 2)) % 360
        else:
            h = (60 * (((_bgr[1] - _bgr[0]) / delta) % 6)) % 360
        if _bgr[max_index] == 0:
            s = 0
        else:
            s = (delta / _bgr[max_index]) * 100
        v = _bgr[max_index] * 100
        hsv_list.append(np.array([h, s, v]))
    return hsv_list


def hsv_mean(bgr_list):
    """
    :param bgr_list: sequence of triplet (b, g, r)
    :return: the mean of the bgr values, transformed into hsv values.
    """
    hsv_list = bgr_to_hsv(bgr_list.ravel().reshape(-1, 3))
    res = np.array([0, 0, 0])
    for hsv in hsv_list:
        res += hsv
    res /= len(hsv_list)
    return res


def color_classifier(hsv):
    """
    :param hsv: The hsv value to classify
    :return: the color represented by the HSV value
    """
    h, s, v = hsv
    if h > 220 or h < 70:  # If the color is in the RED range
        return disc.RED
    elif s > 65:  # We are sure of the color
        if 70 < h < 210:  # If the color is in the GREEN range
            if h > 165:
                return disc.EMPTY
            else:
                return disc.GREEN
        else:
            return disc.EMPTY
    else:  # We will work on brightness
        if v < 45:
            return disc.GREEN
        else:
            return disc.EMPTY


class ActionNotYetPerformedException(BaseException):
    """
    Raised when the image analysis concluded that there was not action since the last game state
    """
    def __init__(self, msg):
        super(ActionNotYetPerformedException, self).__init__(msg)


class TooManyDifferencesException(InvalidStateException):
    """
    Raised when there are too many changes in the game state compared to the last game state in memory
    """
    def __init__(self, msg):
        super(TooManyDifferencesException, self).__init__(msg)


class NAOVision(Strategy):
    """
    Replace the other player in the real world.
    Decide of the action by looking at a picture of the Connect 4
    """

    def __init__(self, hole_mapping, get_c4_img_func, cheating_reaction_func=lambda: None):
        super(NAOVision, self).__init__()
        self.hole_mapping = hole_mapping
        self.cheated_reaction = cheating_reaction_func
        self.c4_img_func = get_c4_img_func
        self.cheated = False

    def eval(self, state, other_player=False):
        return 0

    def chooseNextAction(self, state):
        """
        :param state: the state before this player's action
        :type state: C4State
        :return: the action performed by this player
        """
        previous_action = None
        tries = 3
        attempt = 0
        action = None
        while attempt < tries:
            img = self.c4_img_func()
            action = self.analysePossibleActions(state, img)
            if previous_action is not None:
                if action != previous_action:
                    raise InvalidStateException("The action detection was unstable")
            attempt += 1
        return action

    def analysePossibleActions(self, state, img=None):
        """
        :param state:
        :type state: C4State
        :param img:
        :return:
        """
        probable_actions = []  # Will contain the differences that are located at the first empty space of a column
        if img is None:
            img = self.c4_img_func()
        space = 3  # Number of pixels to take around the point
        for column_no in state.possibleActions():
            line_no = state.getTopSlotNumber(column_no)
            img_coord = self.hole_mapping[
                (column_no, 5 - line_no)]  # The mapping is ordered differently (cols, 5-lines)
            # pixels = [img[coord[1]][coord[0]]]
            pixels = img[img_coord[1] - space:img_coord[1] + space, img_coord[0] - space:img_coord[0] + space]
            color = color_classifier(hsv_mean(pixels))
            if state.board[line_no][column_no] != color:
                # If the difference is not the color of the other player or the disc is not on top of a column
                if color != self.player_id or not state.checkTopColumn(line_no, column_no):
                    raise InvalidStateException("There is an abnormal modification in the game board")
                else:
                    probable_actions.append(column_no)
        if len(probable_actions) == 0:
            raise ActionNotYetPerformedException("This player has not yet performed his action")
        elif len(probable_actions) > 1:
            self.cheated_reaction()
            raise TooManyDifferencesException("The other player has cheated")
        return probable_actions[0]

    def analyseFullImage(self, state, img=None, debug=False):
        """
        :param state:
        :type state: C4State
        :param img:
        :return:
        """
        probable_actions = []  # Will contain the differences that are located at the first empty space of a column
        if img is None:
            img = self.c4_img_func()
        if state is None:
            board = np.ones((6, 7)) * disc.EMPTY
        else:
            board = state.board
        space = 7  # Number of pixels to take around the point
        for line_no in range(6):
            for column_no in range(7):
                img_coord = self.hole_mapping[
                    (column_no, 5 - line_no)]  # The mapping is ordered differently (cols, 5-lines)
                pixels = img[img_coord[1] - space:img_coord[1] + space, img_coord[0] - space:img_coord[0] + space]

                mean = hsv_mean(pixels)
                color = color_classifier(mean)
                # print "(", 5-line_no, ",", column_no, ")", mean, disc.color_string(color)
                if not debug:
                    if state.board[line_no][column_no] != color:
                        # If the difference is not the color of this player or the disc is not on top of a column
                        if color == self.player_id or not state.checkTopColumn(line_no, column_no):
                            raise InvalidStateException("There is an abnormal modification in the game board")
                        else:
                            probable_actions.append(column_no)
                else:
                    board[line_no][column_no] = color
        if not debug:
            if len(probable_actions) == 0:
                raise ActionNotYetPerformedException("This player has not yet performed his action")
            elif len(probable_actions) > 1:
                self.cheated_reaction()
                raise TooManyDifferencesException("The player has cheated")
        if debug:
            return board
        else:
            return probable_actions
