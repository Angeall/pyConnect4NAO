import cv2
import numpy as np

import connect4
from connect4 import Connect4
from utils.circle_grid import CircleGridDetector, CircleGridNotFoundException

__author__ = 'Angeall'


class FrontHolesDetectionException(Exception):
    """
    Exception raised when there was an error during the detection
    """
    pass


class FrontHolesGridNotFoundException(CircleGridNotFoundException):
    """
    Exception that will be raised when a Grid could not be found in the picture
    """
    NO_GRID = "Could not find a Connect 4 with the given parameters"

    def __init__(self, message=NO_GRID):
        super(FrontHolesGridNotFoundException, self).__init__(message)


class FrontHolesDetector(CircleGridDetector):
    """
    Class used to detect a Connect 4 (a 6x7 circle grid)
    """

    def __init__(self):
        connect4_img_name = "Connect4.png"
        self.c4 = Connect4()
        self.connect4_img = cv2.imread(connect4_img_name)
        self.connect4_mapping = self.c4.reference_mapping
        super(FrontHolesDetector, self).__init__()
        self.exception = FrontHolesGridNotFoundException

    def runDetection(self, circles, pixel_error_margin=10, min_similar_vectors=15, img=None,
                     ref_img=None, ref_mapping=None, grid_shape=(6, 7)):
        """
        Runs the detection on circles
        :param circles: The circles detected in an image that could be the connect 4 front holes
        :param pixel_error_margin: The maximum error to allow to consider two circles as neighbours
        :param min_similar_vectors: The minimum number of similar vectors to consider a connection
                                    between two circles as not a noise
        :param img: The image in which the detection has been
        :param ref_img: The image of reference
        :param ref_mapping: The mapping from front holes position ((0, 0), (0, 1) , ...) to pixels in image of reference
        :param grid_shape: The shape of the grid (used in superclass, but constant in Connect 4 : (6, 7))
        """
        grid_shape = (6, 7)
        super(FrontHolesDetector, self).runDetection(circles, pixel_error_margin, min_similar_vectors, img,
                                                     self.connect4_img, self.connect4_mapping, grid_shape)

    def match3DModel(self, camera_matrix, camera_dist):
        """
        Find the 3D coordinates of the Connect4
        :param camera_matrix: The intrinsic camera matrix that can be get via camera calibration
        :param camera_dist: The intrinsic camera distortion coefficients that can be get via camera calibration
        :return: (rvec, tvec) : rvec = rotation vector, tvec translation vector
        """
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

