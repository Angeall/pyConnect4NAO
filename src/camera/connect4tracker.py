import cv2
import numpy as np
from connect4.connect4 import Connect4
from utils import geom

__author__ = 'Anthony Rouneau'


class Connect4Tracker(object):
    CAMERA_TOP_OBJECT = "CameraTop"
    UPPER_HOLE_0_OBJECT = "MyHole0"
    UPPER_HOLE_1_OBJECT = "MyHole1"
    UPPER_HOLE_2_OBJECT = "MyHole2"
    UPPER_HOLE_3_OBJECT = "MyHole3"
    UPPER_HOLE_4_OBJECT = "MyHole4"
    UPPER_HOLE_5_OBJECT = "MyHole5"
    UPPER_HOLE_6_OBJECT = "MyHole6"
    WORLD_CATEGORY_NAME = "C4Tracker"
    objects_tab = [UPPER_HOLE_0_OBJECT,
                   UPPER_HOLE_1_OBJECT,
                   UPPER_HOLE_2_OBJECT,
                   UPPER_HOLE_3_OBJECT,
                   UPPER_HOLE_4_OBJECT,
                   UPPER_HOLE_5_OBJECT,
                   UPPER_HOLE_6_OBJECT]

    def __init__(self, rvec, tvec, camera_matrix, dist_coeff):
        """
        Creates the tracker to refresh and keep the Connect 4 position in 3D
        :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type tvec: np.array
        :param camera_matrix:
        :type camera_matrix: np.matrix
        :param dist_coeff:
        :type dist_coeff: np.matrix
        """
        # Transformation from camera's world axes to nao's world axes
        around_x = np.pi/2
        around_y = -np.pi/2
        self.nao_axes_mat = np.matrix([[np.cos(around_y),           0,              np.sin(around_y)],
                                       [0,                          1,                   0],
                                       [-np.sin(around_y),          0,              np.cos(around_y)]])\
                          * np.matrix([[1,                          0,                   0],
                                       [0,                    np.cos(around_x),    -np.sin(around_x)],
                                       [0,                    np.sin(around_x),     np.cos(around_x)]])
        # Camera parameters
        self.camera_matrix = camera_matrix
        self.disto_coeff = dist_coeff
        self.connect4 = Connect4()
        self.connect4_rmat = cv2.Rodrigues(rvec)
        self.connect4_tvec = tvec
        # TODO : find the camera axis rotation and translation
        self.camera_rmat = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.camera_tvec = np.array([0, 0, 0])
        self.upper_hole_positions = self.initialize_positions()

    def initialize_positions(self):
        """
        Computes the position of each upper hole of the board.
        :return: The list that contains the upper holes position
        :rtype: list
        """
        positions = []
        for i in range(0, len(self.objects_tab) * 2, 2):
            # We take the top left corner and the bottom right corner of the hole
            model_coord_0 = self.connect4.getUpperHoleFromModel(i)
            model_coord_1 = self.connect4.getUpperHoleFromModel(i)
            # This is the translation vector to add to the left top corner in roder to get the middle of the hole
            middle_vector = (model_coord_1 - model_coord_0) / 2
            model_coord = model_coord_0 + middle_vector  # The coordinates of the middle of the hole

            # Rotate and translate to get real position with camera axes
            new_coord = geom.transform_vector(model_coord, self.connect4_rmat, self.connect4_tvec)
            # Rotate to get real position with NAO's axes
            new_coord = geom.transform_vector(new_coord, self.nao_axes_mat, np.array([0, 0, 0]))

            # Add 3 rotation values (0) to match the Position6D requirements of NAO
            for _ in range(3):
                new_coord.append(0)
            positions.append(new_coord)
        return positions

    def refreshPositions(self, rvec, tvec):
        """
        Refresh the connect 4 position
        :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type tvec: np.array
        """
        self.connect4_rmat = cv2.Rodrigues(rvec)
        self.connect4_tvec = tvec
        self.upper_hole_positions = self.initialize_positions()
