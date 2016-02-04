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

    def __init__(self, camera_position, rvec, tvec, camera_matrix, dist_coeff):
        self.camera_matrix = camera_matrix
        self.disto_coeff = dist_coeff
        self.camera_position = camera_position
        self.connect4 = Connect4()
        self.rvec = rvec
        self.tvec = tvec

    # TODO : storeObjects with detected position (solvePnP result)

    def transformPosition(self, model_index):
        """
        Transform a camera position (solvePnP result) into a NAO World position.
        :param new_position: the new position of the object in the camera world (solvePnP result)
        :return: the new position of the object in the NAO World
        """
        return cv2.projectPoints(self.connect4.model[model_index], self.rvec, self.tvec, self.camera_matrix,
                                 self.disto_coeff)


