import utils.geom as geom
import numpy as np

__author__ = 'Anthony Rouneau'

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

# MODEL INDICES : UPPER HOLES (Left to right)
UPPER_HOLE_0_TOP_LEFT = 0
UPPER_HOLE_0_BOTTOM_RIGHT = 1
UPPER_HOLE_1_TOP_LEFT = 2
UPPER_HOLE_1_BOTTOM_RIGHT = 3
UPPER_HOLE_2_TOP_LEFT = 4
UPPER_HOLE_2_BOTTOM_RIGHT = 5
UPPER_HOLE_3_TOP_LEFT = 6
UPPER_HOLE_3_BOTTOM_RIGHT = 7
UPPER_HOLE_4_TOP_LEFT = 8
UPPER_HOLE_4_BOTTOM_RIGHT = 9
UPPER_HOLE_5_TOP_LEFT = 10
UPPER_HOLE_5_BOTTOM_RIGHT = 11
UPPER_HOLE_6_TOP_LEFT = 12
UPPER_HOLE_6_BOTTOM_RIGHT = 13
NUMBER_OF_UPPER_HOLES = 14

class Connect4(object):



    def __init__(self, disc=5.6, length=51.9, width=6.6, height=33.7,
                 hole_length=5.85, hole_width=0.95, hole_h_space=0.95, hole_v_margin=0.4, hole_h_margin=2.75,
                 circle=4.6, circle_h_space=2.183, circle_v_space=0.9, circle_h_margin=3.3, circle_v_margin=0.8):
        self.disc = disc
        self.length = length
        self.width = width
        self.height = height
        self.hole_length = hole_length
        self.hole_width = hole_width
        self.hole_h_space = hole_h_space
        self.hole_v_margin = hole_v_margin
        self.hole_h_margin = hole_h_margin
        self.circle = circle
        self.circle_h_space = circle_h_space
        self.circle_v_space = circle_v_space
        self.circles_h_margin = circle_h_margin
        self.circles_v_margin = circle_v_margin
        self.model = self.generate3DModel()

    def estimate_minradius(self, dist):
        """
        Estimate the minimum radius to detect in an image for a front hole
        :param dist: the distance from the board
        :return:
        """
        return int(round(4.4143*(dist**(-1.1446))/(self.circle/4.6)))

    def estimate_maxradius(self, dist):
        return int(round(8.5468*(dist**(-0.7126))/(self.circle/4.6)))

    def computeMaxRadiusRatio(self, distance):
        """
        Computes the max ratio between the radius of the circle that is the farthest from the robot
        and the radius of the circle that is the closest from the robot.
        :param distance: The distance between the robot and the farthest circle in the Connect 4 grid in cm
        :return: The max radius ratio
        """
        max_angle = np.pi / 2.
        ab = distance  # The length of the vector between the robot and the
        #                farthest point of the farthest vector
        bc = self.circle  # The length of the vector of a circle
        ac = geom.al_kashi(b=ab, c=bc, angle=max_angle)   # The length of the vector between the robot and the closest
        #                                                   point of the farthest vector
        beta = geom.al_kashi(a=bc, b=ab, c=ac)  # Angle of vision of the robot to the farthest vector
        de = bc  # de and bc are the same vectors
        bd = self.length - de  # bd is the length of the gameboard minus one vector
        ad = geom.al_kashi(b=ab, c=bd, angle=max_angle)  # The length of the vector between the robot and the farthest
        #                                                  point of the closest vector
        be = self.length  # The length of the gameboard
        ae = geom.al_kashi(b=ab, c=be, angle=max_angle)  # The length of the vector between the robot and the
        #                                                  closest point of the closest vector
        alpha = geom.al_kashi(a=de, b=ad, c=ae)  # Angle of vision of the robot to the closest vector
        max_error = geom.point_distance()
        return alpha/beta

    def computeMinMaxRadius(self, distance, sloped=False):
        min_radius = self.estimate_minradius(distance)
        max_radius = self.estimate_maxradius(distance)
        if sloped:
            radius_ratio = self.computeMaxRadiusRatio(distance)
            max_radius *= radius_ratio
        return min_radius, max_radius

    def computeMaxPixelError(self, min_radius):
        cm_to_pixels = min_radius/(self.circle/2)
        hor = (self.circle_h_space+self.circle)*cm_to_pixels
        ver = (self.circle_v_space+self.circle)*cm_to_pixels
        hyp = np.sqrt(hor**2 + ver**2)
        return 0.9*hyp

    def generate3DModel(self):
        # Corners model
        corners = range(NUMBER_OF_CORNERS)
        corners[UPPER_LEFT_FRONT_CORNER] = np.array([0, 0, 0])
        corners[UPPER_LEFT_BACK_CORNER] = np.array([0, 0, self.width])
        corners[UPPER_RIGHT_FRONT_CORNER] = np.array([self.length, 0, 0])
        corners[UPPER_RIGHT_BACK_CORNER] = np.array([self.length, 0, self.width])
        corners[LOWER_LEFT_FRONT_CORNER] = np.array([0, self.height, 0])
        corners[LOWER_LEFT_BACK_CORNER] = np.array([0, self.height, self.width])
        corners[LOWER_RIGHT_FRONT_CORNER] = np.array([self.length, self.height, 0])
        corners[LOWER_RIGHT_BACK_CORNER] = np.array([self.length, self.height, self.width])

        # Front holes model
        front_holes = range(NUMBER_OF_FRONT_HOLES)
        x_start = self.circles_h_margin + self.circle/2
        y_start = self.circles_v_margin + self.circle/2
        y_end = self.length - self.circles_v_margin - self.circle/2
        current_x = x_start
        current_y = y_start
        for i in range(3):
            for j in range(3):
                front_holes[(i*7)+j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle
            current_x = self.length/2
            front_holes[(i*7) + 3] = np.array([current_x, current_y, 0])
            current_x += self.circle_h_space + self.circle
            for j in range(4, 7):
                front_holes[(i*7)+j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle
            current_x = x_start
            current_y += self.circle_v_space + self.circle
        current_y = y_end
        for i in range(5, 2, -1):
            for j in range(3):
                front_holes[(i*7)+j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle
            current_x = self.length/2
            front_holes[(i*7) + 3] = np.array([current_x, current_y, 0])
            current_x += self.circle_h_space + self.circle
            for j in range(4, 7):
                front_holes[(i*7)+j] = np.array([current_x, current_y, 0])
                current_x += self.circle_h_space + self.circle
            current_x = x_start
            current_y -= self.circle_v_space + self.circle

        # Upper holes model
        upper_holes = []
        current_x = corners[UPPER_LEFT_FRONT_CORNER][0] + self.hole_h_margin
        current_y = 0
        current_z = corners[UPPER_LEFT_FRONT_CORNER][2] + self.hole_v_margin + self.hole_width
        for i in range(NUMBER_OF_UPPER_HOLES):
            upper_holes.append(np.array([current_x, current_y, current_z]))
            if i % 2 == 0:
                current_z -= self.hole_width
                current_x += self.hole_length
            else:
                current_z += self.hole_width
                current_x += self.hole_h_space

        model = []
        model.append(corners)
        model.append(front_holes)
        model.append(upper_holes)
        return model

    def getUpperHoleFromModel(self, index):
        return self.model[2][index]

    def getFrontHoleFromModel(self, index):
        return self.model[1][index]

    def getCornerFromModel(self, index):
        return self.model[0][index]
















