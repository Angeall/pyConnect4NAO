import unittest

import cv2
import numpy as np

from ai.connect4 import disc
from ai.connect4.c4_state import C4State
from ai.connect4.strategy.nao_vision import NAOVision
from connect4.image.default_image import DefaultConnect4Image

__author__ = 'Anthony Rouneau'


class NAOVisionTestCase(unittest.TestCase):

    def setUp(self):
        ref_mapping = DefaultConnect4Image().generate2DReference()
        self.img = cv2.imread("state_detection_test.png")
        self.strategy = NAOVision(ref_mapping, lambda: self.img)
        self.strategy.player_id = disc.GREEN

    def test_analyse(self):
        test_board = np.array([[disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY],
                               [disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY, disc.EMPTY],
                               [disc.EMPTY, disc.EMPTY, disc.GREEN, disc.GREEN, disc.EMPTY, disc.EMPTY, disc.EMPTY],
                               [disc.RED,   disc.RED,   disc.GREEN, disc.RED,   disc.EMPTY, disc.EMPTY, disc.EMPTY],
                               [disc.GREEN, disc.GREEN, disc.RED,   disc.RED,   disc.EMPTY, disc.EMPTY, disc.EMPTY],
                               [disc.RED,   disc.RED,   disc.GREEN, disc.GREEN, disc.GREEN, disc.EMPTY, disc.RED]])
        test_state = C4State()
        test_state.board = test_board
        chosen_action = self.strategy.chooseNextAction(test_state)
        self.assertTrue(chosen_action == 2)

    def test_debug(self):
        test_state = C4State()
        board = self.strategy.analyseFullImage(test_state, img=self.img, debug=True)
        self.assertTrue((board == np.array([[-1, -1,  0,  1, -1, -1, -1],
                                            [-1, -1,  0,  1, -1, -1, -1],
                                            [-1, -1,  0,  1, -1, -1, -1],
                                            [-1, -1,  0,  1, -1, -1, -1],
                                            [-1, -1,  0,  1, -1, -1,  0],
                                            [ 1,  0,  0,  1, -1,  0,  1]])).all())
