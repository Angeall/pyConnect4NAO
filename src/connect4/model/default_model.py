from connect4.image.default_image import DefaultConnect4Image
import numpy as np

__author__ = 'Anthony Rouneau'


class DefaultConnect4Model(object):
    CORNERS = 0
    # MODEL INDICES : CORNERS
    UPPER_LEFT_BACK_CORNER = 1
    UPPER_LEFT_FRONT_CORNER = 0
    LOWER_LEFT_BACK_CORNER = 5
    LOWER_LEFT_FRONT_CORNER = 4
    UPPER_RIGHT_BACK_CORNER = 3
    UPPER_RIGHT_FRONT_CORNER = 2
    LOWER_RIGHT_BACK_CORNER = 7
    LOWER_RIGHT_FRONT_CORNER = 6
    NUMBER_OF_CORNERS = 8

    FRONT_HOLES = 1
    # MODEL INDICES : FRONT HOLES (Left to right, bottom to top)
    FRONT_HOLE_0_0 = 35
    FRONT_HOLE_0_1 = 28
    FRONT_HOLE_0_2 = 21
    FRONT_HOLE_0_3 = 14
    FRONT_HOLE_0_4 = 7
    FRONT_HOLE_0_5 = 0
    FRONT_HOLE_1_0 = 36
    FRONT_HOLE_1_1 = 29
    FRONT_HOLE_1_2 = 22
    FRONT_HOLE_1_3 = 15
    FRONT_HOLE_1_4 = 8
    FRONT_HOLE_1_5 = 1
    FRONT_HOLE_2_0 = 37
    FRONT_HOLE_2_1 = 30
    FRONT_HOLE_2_2 = 23
    FRONT_HOLE_2_3 = 16
    FRONT_HOLE_2_4 = 9
    FRONT_HOLE_2_5 = 2
    FRONT_HOLE_3_0 = 38
    FRONT_HOLE_3_1 = 31
    FRONT_HOLE_3_2 = 24
    FRONT_HOLE_3_3 = 17
    FRONT_HOLE_3_4 = 10
    FRONT_HOLE_3_5 = 3
    FRONT_HOLE_4_0 = 39
    FRONT_HOLE_4_1 = 32
    FRONT_HOLE_4_2 = 25
    FRONT_HOLE_4_3 = 18
    FRONT_HOLE_4_4 = 11
    FRONT_HOLE_4_5 = 4
    FRONT_HOLE_5_0 = 40
    FRONT_HOLE_5_1 = 33
    FRONT_HOLE_5_2 = 26
    FRONT_HOLE_5_3 = 19
    FRONT_HOLE_5_4 = 12
    FRONT_HOLE_5_5 = 5
    FRONT_HOLE_6_0 = 41
    FRONT_HOLE_6_1 = 34
    FRONT_HOLE_6_2 = 27
    FRONT_HOLE_6_3 = 20
    FRONT_HOLE_6_4 = 13
    FRONT_HOLE_6_5 = 6
    NUMBER_OF_FRONT_HOLES = 42
    FRONT_HOLE_MAPPING = {(0, 0): 35, (0, 1): 28, (0, 2): 21, (0, 3): 14, (0, 4): 7, (0, 5): 0,
                          (1, 0): 36, (1, 1): 29, (1, 2): 22, (1, 3): 15, (1, 4): 8, (1, 5): 1,
                          (2, 0): 37, (2, 1): 30, (2, 2): 23, (2, 3): 16, (2, 4): 9, (2, 5): 2,
                          (3, 0): 38, (3, 1): 31, (3, 2): 24, (3, 3): 17, (3, 4): 10, (3, 5): 3,
                          (4, 0): 39, (4, 1): 32, (4, 2): 25, (4, 3): 18, (4, 4): 11, (4, 5): 4,
                          (5, 0): 40, (5, 1): 33, (5, 2): 26, (5, 3): 19, (5, 4): 12, (5, 5): 5,
                          (6, 0): 41, (6, 1): 34, (6, 2): 27, (6, 3): 20, (6, 4): 13, (6, 5): 6}

    UPPER_HOLES = 2
    # MODEL INDICES : UPPER HOLES (Left to right)
    UPPER_HOLE_0_TOP_LEFT = 0
    UPPER_HOLE_0_TOP_RIGHT = 1
    UPPER_HOLE_0_BOTTOM_LEFT = 2
    UPPER_HOLE_0_BOTTOM_RIGHT = 3
    UPPER_HOLE_1_TOP_LEFT = 4
    UPPER_HOLE_1_TOP_RIGHT = 5
    UPPER_HOLE_1_BOTTOM_LEFT = 6
    UPPER_HOLE_1_BOTTOM_RIGHT = 7
    UPPER_HOLE_2_TOP_LEFT = 8
    UPPER_HOLE_2_TOP_RIGHT = 9
    UPPER_HOLE_2_BOTTOM_LEFT = 10
    UPPER_HOLE_2_BOTTOM_RIGHT = 11
    UPPER_HOLE_3_TOP_LEFT = 12
    UPPER_HOLE_3_TOP_RIGHT = 13
    UPPER_HOLE_3_BOTTOM_LEFT = 14
    UPPER_HOLE_3_BOTTOM_RIGHT = 15
    UPPER_HOLE_4_TOP_LEFT = 16
    UPPER_HOLE_4_TOP_RIGHT = 17
    UPPER_HOLE_4_BOTTOM_LEFT = 18
    UPPER_HOLE_4_BOTTOM_RIGHT = 19
    UPPER_HOLE_5_TOP_LEFT = 20
    UPPER_HOLE_5_TOP_RIGHT = 21
    UPPER_HOLE_5_BOTTOM_LEFT = 22
    UPPER_HOLE_5_BOTTOM_RIGHT = 23
    UPPER_HOLE_6_TOP_LEFT = 24
    UPPER_HOLE_6_TOP_RIGHT = 25
    UPPER_HOLE_6_BOTTOM_LEFT = 26
    UPPER_HOLE_6_BOTTOM_RIGHT = 27
    NUMBER_OF_UPPER_HOLE_CORNERS = 28

    HAMCODES = 2
    # MODEL INDICES : HAMMING CODES (Left to right)
    HAMCODE_0_TOP_LEFT = 0
    HAMCODE_0_TOP_RIGHT = 1
    HAMCODE_0_BOTTOM_LEFT = 2
    HAMCODE_0_BOTTOM_RIGHT = 3
    HAMCODE_1_TOP_LEFT = 4
    HAMCODE_1_TOP_RIGHT = 5
    HAMCODE_1_BOTTOM_LEFT = 6
    HAMCODE_1_BOTTOM_RIGHT = 7
    HAMCODE_2_TOP_LEFT = 8
    HAMCODE_2_TOP_RIGHT = 9
    HAMCODE_2_BOTTOM_LEFT = 10
    HAMCODE_2_BOTTOM_RIGHT = 11
    HAMCODE_3_TOP_LEFT = 12
    HAMCODE_3_TOP_RIGHT = 13
    HAMCODE_3_BOTTOM_LEFT = 14
    HAMCODE_3_BOTTOM_RIGHT = 15
    HAMCODE_4_TOP_LEFT = 16
    HAMCODE_4_TOP_RIGHT = 17
    HAMCODE_4_BOTTOM_LEFT = 18
    HAMCODE_4_BOTTOM_RIGHT = 19
    HAMCODE_5_TOP_LEFT = 20
    HAMCODE_5_TOP_RIGHT = 21
    HAMCODE_5_BOTTOM_LEFT = 22
    HAMCODE_5_BOTTOM_RIGHT = 23
    HAMCODE_6_TOP_LEFT = 24
    HAMCODE_6_TOP_RIGHT = 25
    HAMCODE_6_BOTTOM_LEFT = 26
    HAMCODE_6_BOTTOM_RIGHT = 27
    NUMBER_OF_HAMCODE_CORNERS = 28

    def __init__(self, disc_diameter=0.056, length=0.519, width=0.066, height=0.337,
                 hole_length=0.0585, hole_width=0.0095, hole_h_space=0.0095, hole_v_margin=0.004, hole_h_margin=0.0275,
                 circle_diameter=0.046, circle_h_space=0.02183, circle_v_space=0.009, circle_h_margin=0.033,
                 circle_v_margin=0.008, hamcode_side=0.0425, hamcode_h_space=0.0255, hamcode_h_margin=0.03525,
                 hamcode_v_margin=0.019, hamcode_hole_space=0.01, ):
        """
        :param disc_diameter: the size of a playing disc (m)
        :param length: the lateral length of the Connect 4 (m)
        :param width: the width of the Connect 4 (m)
        :param height: the height of the Connect 4 (m)
        :param hole_length: the length of an upper hole on the Connect 4 (m)
        :param hole_width: the width of an upper hole on the Connect 4 (m)
        :param hole_h_space: the space between two upper _holes on the Connect 4 (m)
        :param hole_v_margin: the margin between the front side of the Connect 4
            and the bottom left corner of an upper hole (m)
        :param hole_h_margin: the margin between the left side of the Connect 4
            and the bottom left corner of an upper hole (m)
        :param circle_diameter: the diameter of a front hole on the Connect 4 (m)
        :param circle_h_space: the horizontal space between two neighbour front _holes (m)
        :param circle_v_space: the vertical space between two neighbour front _holes (m)
        :param circle_h_margin: the horizontal margin between the left side of the Connect 4
            and a left side front hole (m)
        :param circle_v_margin: the vertical margin between the upper side of the Connect 4
            and a top front hole (m)
        :param hamcode_side: the length of a side of a hamming code (m)
        :param hamcode_h_space: the horizontal space between two hamming codes (m)
        :param hamcode_h_margin: the horizontal margin between the left side and the first hamming code (m)
        :param hamcode_v_margin: the vertical margin between the front side and the first hamming code (m)
        :param hamcode_hole_space: the vertical space between the bottom of a hamming code and the
            center of its related hole. (m)
        """
        self.image_of_reference = DefaultConnect4Image()
        self.disc_diameter = disc_diameter
        self.length = length
        self.width = width
        self.height = height
        self.hole_length = hole_length
        self.hole_width = hole_width
        self.hole_h_space = hole_h_space
        self.hole_v_margin = hole_v_margin
        self.hole_h_margin = hole_h_margin
        self.circle_diameter = circle_diameter
        self.circle_h_space = circle_h_space
        self.circle_v_space = circle_v_space
        self.circles_h_margin = circle_h_margin
        self.circles_v_margin = circle_v_margin
        self.hamcode_side = hamcode_side
        self.hamcode_h_space = hamcode_h_space
        self.hamcode_h_margin = hamcode_h_margin
        self.hamcode_v_margin = hamcode_v_margin
        self.hamcode_hole_space = hamcode_hole_space
        self.three_d = self.generate3DModel()

    def generate3DModel(self):
        """
        Generate the inner variables containing the Connect 4 3D _model to consider during the Connect 4 detection
        """
        # Corners _model
        corners = range(self.NUMBER_OF_CORNERS)
        corners[self.UPPER_LEFT_FRONT_CORNER] = np.array([0, 0, 0])
        corners[self.UPPER_LEFT_BACK_CORNER] = np.array([0, 0, self.width])
        corners[self.UPPER_RIGHT_FRONT_CORNER] = np.array([self.length, 0, 0])
        corners[self.UPPER_RIGHT_BACK_CORNER] = np.array([self.length, 0, self.width])
        corners[self.LOWER_LEFT_FRONT_CORNER] = np.array([0, self.height, 0])
        corners[self.LOWER_LEFT_BACK_CORNER] = np.array([0, self.height, self.width])
        corners[self.LOWER_RIGHT_FRONT_CORNER] = np.array([self.length, self.height, 0])
        corners[self.LOWER_RIGHT_BACK_CORNER] = np.array([self.length, self.height, self.width])

        # Front _holes _model
        front_holes = range(self.NUMBER_OF_FRONT_HOLES)
        x_start = self.circles_h_margin + self.circle_diameter / 2
        y_start = self.circles_v_margin + self.circle_diameter / 2
        y_end = self.length - self.circles_v_margin - self.circle_diameter / 2
        current_x = x_start
        current_y = y_start
        for i in range(3):
            for j in range(3):
                front_holes[(i * 7) + j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle_diameter
            current_x = self.length / 2
            front_holes[(i * 7) + 3] = np.array([current_x, current_y, 0])
            current_x += self.circle_h_space + self.circle_diameter
            for j in range(4, 7):
                front_holes[(i * 7) + j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle_diameter
            current_x = x_start
            current_y += self.circle_v_space + self.circle_diameter
        current_y = y_end
        for i in range(5, 2, -1):
            for j in range(3):
                front_holes[(i * 7) + j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle_diameter
            current_x = self.length / 2
            front_holes[(i * 7) + 3] = np.array([current_x, current_y, 0])
            current_x += self.circle_h_space + self.circle_diameter
            for j in range(4, 7):
                front_holes[(i * 7) + j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle_diameter
            current_x = x_start
            current_y -= self.circle_v_space + self.circle_diameter

        # Upper _holes _model
        upper_holes = []
        current_x = corners[self.UPPER_LEFT_FRONT_CORNER][0] + self.hole_h_margin
        current_y = 0
        current_z = corners[self.UPPER_LEFT_FRONT_CORNER][2] + self.hole_v_margin + self.hole_width
        for i in range(self.NUMBER_OF_UPPER_HOLE_CORNERS):
            upper_holes.append(np.array([current_x, current_y, current_z]))
            modulo = i % 4
            if modulo == 0 or modulo == 2:
                current_x += self.hole_length
            elif modulo == 1:
                current_z -= self.hole_width
                current_x -= self.hole_length
            else:
                current_z += self.hole_width
                current_x += self.hole_h_space

        # Hamming codes
        hamcodes = []
        current_x = corners[self.UPPER_LEFT_FRONT_CORNER][0] + self.hamcode_h_margin
        current_y = 0
        current_z = corners[self.UPPER_LEFT_FRONT_CORNER][2] + self.hamcode_v_margin + self.hamcode_side
        for i in range(self.NUMBER_OF_HAMCODE_CORNERS):
            hamcodes.append(np.array([current_x, current_y, current_z]))
            modulo = i % 4
            if modulo == 0 or modulo == 2:
                current_x += self.hamcode_side
            elif modulo == 1:
                current_z -= self.hamcode_side
                current_x -= self.hamcode_side
            else:
                current_z += self.hamcode_side
                current_x += self.hamcode_h_space

        model = np.array([corners, front_holes, upper_holes, hamcodes])
        return model

    def getUpperHole(self, index):
        """
        :param index: Indicates which hole you want to get (see the constants)
        :type index: int
        :return: The 3D coordinate of the wanted hole in the _model : [NW, NE, SW, SE]
        :rtype: np.array
        Get the coordinates of an upper hole of the 3D _model of the Connect 4
        """
        return self.three_d[self.UPPER_HOLES][index * 4], self.three_d[self.UPPER_HOLES][(index * 4) + 1], \
               self.three_d[self.UPPER_HOLES][(index * 4) + 2], self.three_d[self.UPPER_HOLES][(index * 4) + 3]

    def getFrontHole(self, index):
        """
        :param index: Indicates which front hole you want to get (see the constants)
        :type index: int
        :return: The 3D coordinate of the wanted hole in the _model
        :rtype: np.array
        Get the coordinates of a front hole of the 3D _model of the Connect 4
        """
        return self.three_d[self.FRONT_HOLES][index]

    def getCorner(self, index):
        """
        :param index: Indicates which corner you want to get (see the constants)
        :type index: int
        :return: The 3D coordinate of the wanted corner in the _model
        :rtype: np.array
        Get the coordinates of a corner of the 3D _model of the Connect 4
        """
        return self.three_d[self.CORNERS][index]

    def getHamcode(self, index):
        """
        :param index: indicates which hamming code you want to get (see the constants)
        :type index: int
        :return:  the 3D coordinates of the wanted hamming code : [NW, NE, SW, SE]
        :rtype: np.array
        Get the coordinates of a hamming code of the 3D _model of the Connect 4
        """
        return self.three_d[self.HAMCODES][index * 4], self.three_d[self.HAMCODES][(index * 4) + 1],\
               self.three_d[self.HAMCODES][(index * 4) + 2], self.three_d[self.HAMCODES][(index * 4) + 3]
