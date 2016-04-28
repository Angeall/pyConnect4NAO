import cv2
import numpy as np

import utils.camera.geom as geom
from detector.front_holes import FrontHolesDetector, FrontHolesGridNotFoundException
from detector.upper_hole import UpperHoleDetector
from model.default_model import DefaultConnect4Model

__author__ = 'Anthony Rouneau'

DEFAULT_RESOLUTION = 320

DEFAULT_MODEL = "DEFAULT_MODEL"


class Connect4ModelNotFound(Exception):
    def __init__(self, model_name):
        msg = "The model " + model_name + " does not exists"
        super(Connect4ModelNotFound, self).__init__(msg)


class Connect4Handler(object):
    def __init__(self, next_img_func, model_type=DEFAULT_MODEL):
        if model_type == DEFAULT_MODEL:
            self.model = DefaultConnect4Model()
        else:
            raise Connect4ModelNotFound(model_type)
        self.img = None
        self.next_img_func = next_img_func
        self.front_hole_detector = FrontHolesDetector(self.model)
        self.upper_hole_detector = UpperHoleDetector(self.model)
        # Used for the detection
        self.front_holes_detection_prepared = False
        self.circles = []
        self.param1 = None
        self.param2 = None
        self.min_radius = None
        self.max_radius = None
        self.min_dist = None
        self.sloped = False
        self.pixel_error_margin = None
        self.res = 320
        self.distance = None

    def estimateMinRadius(self, dist):
        """
        Estimate the minimum radius to detect in an image for a front hole
        :param dist: The distance from the board in meters
        :return: The estimated minimum radius to detect
        """
        return int(np.ceil(4.4143 * (dist ** (-1.1446)) / (self.model.circle_diameter / 0.046)))

    def estimateMaxRadius(self, dist):
        """
        Estimate the maximum radius to detect in an image for a front hole
        :param dist: The distance from the board in meters
        :return: The estimated maximum radius to detect
        """
        return int(round(8.5468 * (dist ** (-0.7126)) / (self.model.circle_diameter / 0.046)))

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
        bc = self.model.circle_diameter  # The length of the vector of a circle
        ac = geom.al_kashi(b=ab, c=bc, angle=max_angle)  # The length of the vector between the robot and the closest
        #                                                   point of the farthest vector
        beta = geom.al_kashi(a=bc, b=ab, c=ac)  # Angle of vision of the robot to the farthest vector
        de = bc  # de and bc are the same vectors
        bd = self.model.length - de  # bd is the length of the game board minus one vector
        ad = geom.al_kashi(b=ab, c=bd, angle=max_angle)  # The length of the vector between the robot and the farthest
        #                                                  point of the closest vector
        be = self.model.length  # The length of the game board
        ae = geom.al_kashi(b=ab, c=be, angle=max_angle)  # The length of the vector between the robot and the
        #                                                  closest point of the closest vector
        alpha = geom.al_kashi(a=de, b=ad, c=ae)  # Angle of vision of the robot to the closest vector
        return alpha / beta

    def computeMinMaxRadius(self, distance, sloped=False):
        """
        Get the minimum and the maximum radius to detect during the detection
        :param distance: The distance between the robot and the farthest circle in the Connect 4 grid in meters
        :type distance: float
        :param sloped: True if the connect 4 can be considered as sloped for the robot vision
        :type sloped: bool
        :return: The minimum and the maximum radius to detect (min_radius, max_radius)
        :rtype: tuple
        """
        min_radius = self.estimateMinRadius(distance)
        max_radius = self.estimateMaxRadius(distance)
        if sloped:
            radius_ratio = self.computeMaxRadiusRatio(distance * 100)
            max_radius *= radius_ratio
        return min_radius, int(max_radius)

    def computeMaxPixelError(self, min_radius):
        """
        Get the maximum error box to consider during the front hole detection
        :param min_radius: The minimum radius used during the detection
        :type min_radius: float
        :return: The maximum error in pixel to consider during the front hole detection
        :rtype: float
        """
        cm_to_pixels = min_radius / (self.model.circle_diameter / 2)
        hor = (self.model.circle_h_space + self.model.circle_diameter) * cm_to_pixels
        ver = (self.model.circle_v_space + self.model.circle_diameter) * cm_to_pixels
        hyp = np.sqrt(hor ** 2 + ver ** 2)
        return 0.9 * hyp

    def prepareFrontHolesDetection(self, distance, sloped, res):
        """
        Initialize The parameters for the detection
        :param distance: The distance between the robot and the farthest circle in the Connect 4 grid in meters
        :type distance: float
        :param sloped: True if the connect 4 can be considered as sloped for the robot vision
        :type sloped: bool
        :param res: The resolution (width in pixels) to consider during the detection
        :type res: int
        """
        self.front_holes_detection_prepared = True
        self.res = res
        self.min_radius, self.max_radius = self.computeMinMaxRadius(distance, sloped)
        self.pixel_error_margin = self.computeMaxPixelError(self.min_radius)
        self.min_dist = int(self.min_radius * 2.391 * (self.res / 320))
        self.param1 = 77
        self.param2 = 9.75
        if self.sloped:
            self.param2 = 8

    def detectFrontHoles(self, distance, sloped=False, res=DEFAULT_RESOLUTION, tries=1):
        """
        :param distance: The distance between the robot and the connect4
        :param sloped: true if the connect4 is sloped
        :param res: the resolution of the image
        :param tries: the number of success the algorithm must perform to mark the Connect 4 as detected
        """
        for i in range(tries):
            self.img = self.next_img_func()
            self.circles = []
            if not self.front_holes_detection_prepared:
                self.prepareFrontHolesDetection(distance, sloped, res)
            elif self.distance != distance or self.sloped != sloped:
                self.min_radius, self.max_radius = self.computeMinMaxRadius(distance, sloped)
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            gray = cv2.medianBlur(gray, 3)

            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, self.min_dist,
                                       param1=self.param1, param2=self.param2, minRadius=self.min_radius,
                                       maxRadius=self.max_radius)
            if circles is not None:
                self.circles = circles[0]
                self.front_hole_detector.runDetection(self.circles, pixel_error_margin=self.pixel_error_margin,
                                                      img=self.img)
            else:
                raise FrontHolesGridNotFoundException()

    def getUpperHoleRefinedCoordinates(self, img, approx_coordinates):
        """
        Detect a hole inside the approx_coordinates in the image.
        :param img: the image in which the hole will be detected
        :param approx_coordinates: rectangle of coordinates indicating, using the solvePnP results, where the
                                   hole is approximately.
                                   /!\ must be ordered by top-left, top-right, bottom-right, and bottom-left
        :rtype: np.array
        """
        (tl, tr, br, bl) = approx_coordinates
        # Enlarge the rectangle to consider in order to detect the whole hole
        approx_error = 50 * (self.res / 320)
        tl = [tl[0] - approx_error, tl[1] - approx_error]
        tr = [tr[0] + approx_error, tr[1] - approx_error]
        br = [br[0] + approx_error, br[1] + approx_error]
        bl = [bl[0] - approx_error, bl[1] + approx_error]
        # Computes the new maximal width
        x_1 = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        x_2 = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(x_1), int(x_2))
        # Computes the new maximal height
        y_1 = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        y_2 = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(y_1), int(y_2))
        # The coordinates of the new rectangle containing the transformed image
        new_size = np.array([[0, 0],
                             [max_width - 1, 0],
                             [max_width - 1, max_height - 1],
                             [0, max_height - 1]], dtype="float32")
        # Computes the transformation matrix and warp the original image
        trans_matrix = cv2.getPerspectiveTransform(approx_coordinates, new_size)
        transformed_img = cv2.warpPerspective(img, trans_matrix, (max_width, max_height))
        # Find contours in the reshaped img
        contours, _ = cv2.findContours(transformed_img, 1, 2)
        for cnt in contours:
            # approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            cv2.drawContours(transformed_img, [cnt], 0, 255, -1)
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(transformed_img, [box], 0, (0, 0, 255), 2)
            print cv2.contourArea(cnt)
            print cv2.contourArea(rect)
            # print cv2.contourArea(box)
        # TODO : Test and change return when ok
        return transformed_img, img

    def getUpperHoleCoordinates(self, img, copy_img):
        """
        :param img: the image in which the hole will be detected
        :type img: np.ndarray
        :return: The asked upper hole coordinates
        :rtype: np.array
        Detect holes in the image.
        TODO
        """
        # Find contours in the reshaped img
        _, contours, _ = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            print cnt
            # approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            # copy_img = cv2.drawContours(copy_img, [cnt], 0, (0, 255, 0), -1)
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            copy_img = cv2.drawContours(copy_img, [box], 0, (0, 0, 255), 2)
            print cv2.contourArea(cnt)
            print cv2.contourArea(rect)
            # print cv2.contourArea(box)
        # # # TODO : Test and change return when ok
        return copy_img
