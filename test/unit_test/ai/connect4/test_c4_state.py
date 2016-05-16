import unittest

import numpy as np

from ai.connect4.c4_state import C4State

__author__ = 'Anthony Rouneau'


class C4StateTestCase(unittest.TestCase):

    def setUp(self):
        self.state = C4State()

    def test_not_terminal1(self):
        self.assertTrue(not np.array(self.state.terminalTest()).any())

    def test_not_terminal2(self):
        self.state.performAction(0)
        self.state.performAction(2)
        self.state.performAction(4)
        self.state.performAction(1)
        self.assertTrue((not np.array(self.state.terminalTest()).any()))

    def test_terminal_red_vert(self):
        self.state.performAction(0)  # Red plays in hole   0
        self.state.performAction(1)  # Green plays in hole 1
        self.state.performAction(0)  # Red plays in hole   0
        self.state.performAction(1)  # Green plays in hole 1
        self.state.performAction(0)  # Red plays in hole   0
        self.state.performAction(1)  # Green plays in hole 1
        self.state.performAction(0)  # Red plays in hole   0
        self.assertTrue((np.array(self.state.terminalTest())[1]))

    def test_terminal_red_diag(self):
        self.state.performAction(0)  # Red plays in hole   0
        self.state.performAction(1)  # Green plays in hole 1
        self.state.performAction(1)  # Red plays in hole   1
        self.state.performAction(2)  # Green plays in hole 2
        self.state.performAction(2)  # Red plays in hole   2
        self.state.performAction(3)  # Green plays in hole 3
        self.state.performAction(2)  # Red plays in hole   2
        self.state.performAction(3)  # Green plays in hole 3
        self.state.performAction(4)  # Red plays in hole   4
        self.state.performAction(3)  # Green plays in hole 3
        self.state.performAction(3)  # Red plays in hole   3 and wins
        self.assertTrue((np.array(self.state.terminalTest())[1]))

    def test_terminal_red_horiz(self):
        self.state.performAction(0)  # Red plays in hole   0
        self.state.performAction(0)  # Green plays in hole 0
        self.state.performAction(1)  # Red plays in hole   1
        self.state.performAction(1)  # Green plays in hole 1
        self.state.performAction(2)  # Red plays in hole   2
        self.state.performAction(2)  # Green plays in hole 2
        self.state.performAction(3)  # Red plays in hole   3
        self.assertTrue((np.array(self.state.terminalTest())[1]))

    def test_terminal_green_vert(self):
        self.state.performAction(6)
        self.state.performAction(0)  # Green plays in hole   0
        self.state.performAction(1)  # Red plays in hole 1
        self.state.performAction(0)  # Green plays in hole   0
        self.state.performAction(1)  # Red plays in hole 1
        self.state.performAction(0)  # Green plays in hole   0
        self.state.performAction(1)  # Red plays in hole 1
        self.state.performAction(0)  # Green plays in hole   0
        self.assertTrue((np.array(self.state.terminalTest())[1]))

    def test_terminal_green_diag(self):
        self.state.performAction(6)
        self.state.performAction(0)  # Green plays in hole   0
        self.state.performAction(1)  # Red plays in hole 1
        self.state.performAction(1)  # Green plays in hole   1
        self.state.performAction(2)  # Red plays in hole 2
        self.state.performAction(2)  # Green plays in hole   2
        self.state.performAction(3)  # Red plays in hole 3
        self.state.performAction(2)  # Green plays in hole   2
        self.state.performAction(3)  # Red plays in hole 3
        self.state.performAction(4)  # Green plays in hole   4
        self.state.performAction(3)  # Red plays in hole 3
        self.state.performAction(3)  # Green plays in hole   3 and wins
        self.assertTrue((np.array(self.state.terminalTest())[1]))

    def test_terminal_green_horiz(self):
        self.state.performAction(6)
        self.state.performAction(0)  # Green plays in hole   0
        self.state.performAction(0)  # Red plays in hole 0
        self.state.performAction(1)  # Green plays in hole   1
        self.state.performAction(1)  # Red plays in hole 1
        self.state.performAction(2)  # Green plays in hole   2
        self.state.performAction(2)  # Red plays in hole 2
        self.state.performAction(3)  # Green plays in hole   3
        self.assertTrue((np.array(self.state.terminalTest())[1]))