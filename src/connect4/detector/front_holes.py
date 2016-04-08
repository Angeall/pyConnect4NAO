import cv2
import numpy as np

from connect4.image.default_image import DefaultConnect4Image
from utils.circle_grid_detector import CircleGridDetector, CircleGridNotFoundException

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

    def __init__(self, connect4_model):
        super(FrontHolesDetector, self).__init__()
        # Image of reference
        self.model = connect4_model
        self.image_of_reference = connect4_model.image_of_reference
        self.connect4_img = self.model.image_of_reference.img
        self.reference_mapping = self.image_of_reference.pixel_mapping
        self.exception = FrontHolesGridNotFoundException

    def runDetection(self, circles, pixel_error_margin=10, min_similar_vectors=15, img=None,
                     ref_img=None, grid_shape=(6, 7)):
        """
        Runs the detection on circles
        :param circles: The circles detected in an image that could be the connect 4 front holes
        :param pixel_error_margin: The maximum error to allow to consider two circles as neighbours
        :param min_similar_vectors: The minimum number of similar vectors to consider a connection
                                    between two circles as not a noise
        :param img: The image in which the detection has been
        :param ref_img: The image of reference
        :param grid_shape: The shape of the grid (used in superclass, but constant in Connect 4 : (6, 7))
        """
        grid_shape = (6, 7)
        super(FrontHolesDetector, self).runDetection(circles, pixel_error_margin, min_similar_vectors, img,
                                                     self.connect4_img, grid_shape)

    def match3DModel(self, camera_matrix, camera_dist):
        """
        Find the 3D coordinates of the Connect4Handler
        :param camera_matrix: The intrinsic camera matrix that can be get via camera calibration
        :param camera_dist: The intrinsic camera distortion coefficients that can be get via camera calibration
        :return: (rvec, tvec) : rvec = rotation vector, tvec translation vector
        """
        object_points = np.array(self.model.three_d[1])
        image_points = []
        for i in range(42):
            image_points.append(0)
        print "Reference Mapping", self.reference_mapping, "\n\n"
        print "Reference Mapping Keys", self.reference_mapping.keys()
        for key in self.reference_mapping.keys():
            model_key = self.model.FRONT_HOLE_MAPPING[key]
            print "MODEL KEY", model_key, "Reference Value", self.reference_mapping[key]
            image_points[model_key] = self.reference_mapping[key]
        print "IMG POINTS INIT", image_points
        print "OBJ POINTS", object_points
        image_points = cv2.perspectiveTransform(np.float32(image_points).reshape(1, -1, 2),
                                                self.homography).reshape(-1, 2)
        print "IMG POINTS", image_points
        # retval, rvec, tvec = cv2.solvePnP(object_points, image_points, np.eye(3), None)
        retval, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, camera_dist)
        if not retval:
            print "ERR: SolvePnP failed"
        return rvec, tvec