import cv2

from src.utils import geom
from src.utils.circle_grid import CircleGridDetector, CircleGridNotFoundException

__author__ = 'Angeall'


class Connect4DetectionException(Exception):
    """
    Exception raised when there was an error during the detection
    """
    pass


class Connect4DetectionNotFoundException(CircleGridNotFoundException):
    """
    Exception that will be raised when a Grid could not be found in the picture
    """
    NO_GRID = "Could not find a Connect 4 with the given parameters"
    def __init__(self, message=NO_GRID):
        super(Connect4DetectionNotFoundException, self).__init__(message)

class Connect4Detector(CircleGridDetector):
    """
    Class used to detect a Connect 4 (a 6x7 circle grid)
    """
    def __init__(self):
        connect4_img_name = "Connect4.png"
        self.connect4_img = cv2.imread(connect4_img_name)
        self.connect4_mapping = geom.map_virtual_circle_grid()
        super(Connect4Detector, self).__init__()
        self.exception = Connect4DetectionNotFoundException

    def runDetection(self, circles, pixel_error_margin=10, min_similar_vectors=15, img=None,
                       ref_img=None, ref_mapping=None, grid_shape=(6, 7)):
        grid_shape = (6,7)
        super(Connect4Detector, self).runDetection(circles, pixel_error_margin, min_similar_vectors, img,
                                                   self.connect4_img, self.connect4_mapping, grid_shape)




