import cv2

from camera.gameboard import calibration
from camera.gameboard.connect4 import Connect4

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
        self.rmat = cv2.Rodrigues(rvec)
        self.tvec = tvec
        self.upper_hole_positions = self.initialize_positions()

    def initialize_positions(self):
        positions = []
        for i in range(0, len(self.indices_tab)*2, 2):
            # We take the top left corner and the bottom right corner of the hole
            model_coord_0 = self.connect4.getUpperHoleFromModel(i)
            model_coord_1 = self.connect4.getUpperHoleFromModel(i)
            # This is the translation vector to add to the left top corner in roder to get the middle of the hole
            middle_vector = (model_coord_1-model_coord_0)/2
            model_coord = model_coord_0 + middle_vector
            temp = (self.rmat*model_coord.reshape((3, 1))).getA1()
            temp += self.tvec
            positions.append(temp)
        return positions

    def refreshPositions(self, new_rvec, new_tvec):
        self.rmat = cv2.Rodrigues(new_rvec)
        self.tvec = new_tvec
        self.upper_hole_positions = self.initialize_positions()
        pass

    # TODO : storeObjects with detected position (solvePnP result)

    def transformPosition(self, model_index):
        """
        Transform a camera position (solvePnP result) into a NAO World position.
        :param new_position: the new position of the object in the camera world (solvePnP result)
        :return: the new position of the object in the NAO World
        """
        return cv2.projectPoints(self.connect4.model[model_index], self.rvec, self.tvec, self.camera_matrix,
                                 self.disto_coeff)


