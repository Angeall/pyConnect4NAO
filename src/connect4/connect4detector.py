import cv2
import numpy as np

import connect4
from connect4 import Connect4
from utils.circle_grid import CircleGridDetector, CircleGridNotFoundException

__author__ = 'Angeall'


class Connect4DetectionException(Exception):
    """
    Exception raised when there was an error during the detection
    """
    pass


class Connect4GridNotFoundException(CircleGridNotFoundException):
    """
    Exception that will be raised when a Grid could not be found in the picture
    """
    NO_GRID = "Could not find a Connect 4 with the given parameters"

    def __init__(self, message=NO_GRID):
        super(Connect4GridNotFoundException, self).__init__(message)


class Connect4Detector(CircleGridDetector):
    """
    Class used to detect a Connect 4 (a 6x7 circle grid)
    """

    def __init__(self):
        connect4_img_name = "Connect4.png"
        self.c4 = Connect4()
        self.connect4_img = cv2.imread(connect4_img_name)
        self.connect4_mapping = self.c4.reference_mapping
        super(Connect4Detector, self).__init__()
        self.exception = Connect4GridNotFoundException

    def runDetection(self, circles, pixel_error_margin=10, min_similar_vectors=15, img=None,
                     ref_img=None, ref_mapping=None, grid_shape=(6, 7)):
        grid_shape = (6, 7)
        super(Connect4Detector, self).runDetection(circles, pixel_error_margin, min_similar_vectors, img,
                                                   self.connect4_img, self.connect4_mapping, grid_shape)

    def match3DModel(self, camera_matrix, camera_dist):
        c4 = Connect4()
        object_points = np.array(c4.model[1])
        image_points = np.array()
        for i in range(42):
            np.append(image_points, 0)
        for key in self.referenceMapping.keys():
            np.put(image_points, connect4.FRONT_HOLE_MAPPING[key], self.referenceMapping[key])
        image_points = cv2.perspectiveTransform(np.float32(image_points).reshape(1, -1, 2),
                                                self.homography).reshape(-1, 2)
        retval, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, camera_dist)
        if not retval:
            print "ERR: SolvePnP failed"
        return rvec, tvec

