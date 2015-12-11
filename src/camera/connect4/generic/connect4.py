import numpy as np
import random

import cv2

from src.camera.connect4.generic.circle_grid import CircleGridDetector
from src.utils import geom

__author__ = 'Angeall'

class Connect4DetectionException(Exception):
    """
    Exception that will be raised when a Grid could not be found
    """
    NO_GRID = "Could not find a Connect 4 with the given parameters"
    def __init__(self, message=NO_GRID):
        super(Connect4DetectionException, self).__init__(message)

class Connect4Detector(CircleGridDetector):
    """
    Class used to detect a
    """
    def __init__(self, circles, img, pixel_error_margin, min_similar_vectors):
        connect4_img_name = "Connect4.png"
        connect4_img = cv2.imread(connect4_img_name)
        reference_mapping = geom.map_virtual_circle_grid()
        super(Connect4Detector, self).__init__((6, 7), circles, pixel_error_margin, min_similar_vectors,
                                               img=img, reference_image=connect4_img,
                                               reference_mapping=reference_mapping)
        self.exception = Connect4DetectionException



