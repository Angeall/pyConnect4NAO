import cv2
import numpy as np

from ai.connect4 import disc
from ai.connect4.c4_state import C4State
from connect4.connect4handler import Connect4Handler
from connect4.detector.front_holes import FrontHolesGridNotFoundException
from connect4.image.default_image import DefaultConnect4Image
from nao.controller.video import VideoController
from utils.ai.game_state import GameState
from utils.ai.strategy import Strategy

__author__ = 'Anthony Rouneau'

nao_video = None


def hsv_normalizer(hsv):
    """
    :param hsv: the initial hsv values with h, s and v between 0 and 255.
                As H is usually between 0 and 360, h is divided by two => we multiply it by two
                As S and V are usually in percentage, we divide them by 2.55
    :return: the HSV value normalized
    """
    return [hsv[0] * 2, hsv[1] / 2, hsv[2] / 2]


def hsv_mean(hsv_list):
    res = np.array([0, 0, 0])
    for line in hsv_list:
        for hsv in line:
            res += hsv
    res /= (len(hsv_list) * len(hsv_list[0]))
    return hsv_normalizer(res)


def color_classifier(hsv):
    h, s, v = hsv
    print hsv
    if s > 60:  # We are sure of the color
        if h > 270 or h < 25:  # If the color is in the RED range
            return disc.RED
        elif 75 < h < 230:  # If the color is in the GREEN range
            return disc.GREEN
        else:
            return disc.EMPTY
    else:  # We will work on brightness
        if v < 33:
            return disc.GREEN
        else:
            return disc.EMPTY


def get_nao_image(camera_num=0, res=1):
    global nao_video
    if nao_video is None:
        nao_video = VideoController()
        ret = nao_video.connectToCamera(res=res, fps=30, camera_num=camera_num)
        if ret < 0:
            print "Could not open camera"
            return None
    return nao_video.getImageFromCamera()


class TooManyDifferencesException(BaseException):
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
        :param state:
        :type state: GameState
        :return:
        """
        img = self.c4_img_func()
        cv2.imwrite("test.png", img)
        return self._AnalyseImage(state, img)

    def _compareStates(self, state1, state2):
        difference = None

    def _AnalyseImage(self, state, img):
        """
        :param state:
        :type state: C4State
        :param img:
        :return:
        """
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
        space = 4  # Number of pixels to take around the point
        board = np.ones((6, 7))
        for line_no in range(6):
            for column_no in range(7):
                # for column_no in state.possible_actions:
                # column = state.board[:, column_no]
                # has_disc is a vector of bool in which a slot is True if it contains a disc
                # has_disc = column > disc.EMPTY
                # We fulfill the lowest slot available by looking at the slot just before the first disc
                # line_no = np.argmax(has_disc) - 1
                coord = self.hole_mapping[
                    (column_no, 5 - line_no)]  # The mapping is ordered differently (cols, 5-lines)
                # pixels = [img[coord[1]][coord[0]]]
                pixels = img[coord[1] - space:coord[1] + space, coord[0] - space:coord[0] + space]
                color = color_classifier(hsv_mean(pixels))
                board[line_no][column_no] = color
        return board

    def display_action(self, action):
        if self.cheated:
            self.cheated_reaction()
        print "Action seen: ", action


if __name__ == "__main__":
    nao_video = VideoController()
    c4_handler = Connect4Handler(get_nao_image)
    ref_mapping = DefaultConnect4Image().generate2DReference()
    i = 0
    while True:
        try:
            c4_handler.detectFrontHoles(1.23)
            strategy = NAOVision(ref_mapping, lambda: c4_handler.front_hole_detector.getPerspective())
            print strategy.chooseNextAction(None)
        except FrontHolesGridNotFoundException:
            pass
