import cv2
import numpy as np

from camera.gameboard import calibration
from camera.gameboard.connect4 import Connect4
from utils import geom

__author__ = 'Anthony Rouneau'


class Connect4Tracker(object):
    CAMERA_TOP_OBJECT = "MyCameraTop"
    UPPER_HOLE_0_OBJECT = "MyHole0"
    UPPER_HOLE_1_OBJECT = "MyHole1"
    UPPER_HOLE_2_OBJECT = "MyHole2"
    UPPER_HOLE_3_OBJECT = "MyHole3"
    UPPER_HOLE_4_OBJECT = "MyHole4"
    UPPER_HOLE_5_OBJECT = "MyHole5"
    UPPER_HOLE_6_OBJECT = "MyHole6"
    indices_tab = [UPPER_HOLE_0_OBJECT,
                   UPPER_HOLE_1_OBJECT,
                   UPPER_HOLE_2_OBJECT,
                   UPPER_HOLE_3_OBJECT,
                   UPPER_HOLE_4_OBJECT,
                   UPPER_HOLE_5_OBJECT,
                   UPPER_HOLE_6_OBJECT]

    def __init__(self, camera_position, rvec, tvec, camera_matrix, dist_coeff):
        self.camera_matrix = camera_matrix
        self.disto_coeff = dist_coeff
        self.camera_position = camera_position
        self.connect4 = Connect4()
        self.connect4_rmat = cv2.Rodrigues(rvec)
        self.connect4_tvec = tvec
        # TODO : find the camera axis rotation and translation
        self.camera_rmat = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.camera_tvec = np.array([0, 0, 0])
        self.upper_hole_positions = self.initialize_positions()

    def initialize_positions(self):
        positions = []
        for i in range(0, len(self.indices_tab)*2, 2):
            # We take the top left corner and the bottom right corner of the hole
            model_coord_0 = self.connect4.getUpperHoleFromModel(i)
            model_coord_1 = self.connect4.getUpperHoleFromModel(i)
            # This is the translation vector to add to the left top corner in roder to get the middle of the hole
            middle_vector = (model_coord_1-model_coord_0)/2
            model_coord = model_coord_0 + middle_vector  # The coordinates of the middle of the hole
            new_coord = geom.transform_vector(model_coord, self.connect4_rmat, self.connect4_tvec) # Rotate and translate
            positions.append(new_coord)
        return positions

    def refreshPositions(self, new_rvec, new_tvec):
        self.connect4_rmat = cv2.Rodrigues(new_rvec)
        self.connect4_tvec = new_tvec
        self.upper_hole_positions = self.initialize_positions()
        pass

    # TODO : storeObjects with detected position (solvePnP result)

    def transformPosition(self, model_index):
        """
        Transform a camera position (solvePnP result) into a NAO World position.
        :param new_position: the new position of the object in the camera world (solvePnP result)
        :return: the new position of the object in the NAO World
        """
        return cv2.projectPoints(self.connect4.model[model_index], self.rvec, self.connect4_tvec, self.camera_matrix,
                                 self.disto_coeff)


