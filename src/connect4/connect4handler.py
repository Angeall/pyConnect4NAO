import cv2
import numpy as np
from hampy import detect_markers

import utils.camera.geom as geom
from connect4.connect4tracker import Connect4Tracker
from detector.front_holes import FrontHolesDetector, FrontHolesGridNotFoundException
from detector.upper_hole import UpperHolesDetector, NotEnoughLandmarksException
from model.default_model import DefaultModel

__author__ = 'Anthony Rouneau'

DEFAULT_RESOLUTION = 320

DEFAULT_MODEL = "DEFAULT_MODEL"


def draw_circles(img, circles):
    img2 = img.copy()
    for i in circles:
        # draw the outer circle
        cv2.circle(img2, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img2, (i[0], i[1]), 2, (0, 0, 255), 2)
    return img2


class Connect4ModelNotFound(Exception):
    def __init__(self, model_name):
        msg = "The _model " + model_name + " does not exists"
        super(Connect4ModelNotFound, self).__init__(msg)


class Connect4Handler(object):
    def __init__(self, next_img_func, model_type=DEFAULT_MODEL):
        if model_type == DEFAULT_MODEL:
            self.model = DefaultModel()
        else:
            raise Connect4ModelNotFound(model_type)
        self.img = None
        self.next_img_func = next_img_func
        self.front_hole_detector = FrontHolesDetector(self.model)
        self.upper_hole_detector = UpperHolesDetector(self.model)
        self.tracker = Connect4Tracker(self.model)
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
        return int(np.ceil(5.1143 * (dist ** (-1.1446)) / (self.model.circle_diameter / 0.046)))

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
        self.param1 = 70
        self.param2 = 10.5
        if self.sloped:
            self.param2 = 8

    def detectFrontHoles(self, distance, sloped=False, res=DEFAULT_RESOLUTION, tries=1, debug=False):
        """
        :param distance: The distance between the robot and the connect4
        :type distance: float
        :param sloped: True if the connect4 is sloped or in an unknown position
        :type sloped: bool
        :param res: the resolution of the image
        :type res: int
        :param tries: the number of success the algorithm must perform to mark the Connect 4 as detected
        :type tries: int
        :param debug: if True, displays image of the current detection
        :type debug: bool
        Detect the front holes in the next image of the "next_img_func".
        If the connect 4 is not found in one attempt, the whole detection fails (see the 'tries' parameter).
        """
        last_0_0_coord = None
        for i in range(tries):
            print "try", i
            self.img = self.next_img_func(0)  # We detect the front holes using the top camera
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
                if debug:
                    img2 = draw_circles(self.img, self.circles)
                    cv2.imshow("Circles detected", img2)
                    cv2.imshow("Original picture", self.img)
                (cur_0_0_coord, cur_1_0_coord) = cv2.perspectiveTransform(
                    np.float32(np.array([self.front_hole_detector.reference_mapping[(0, 0)],
                                         self.front_hole_detector.reference_mapping[(1, 0)]])).reshape(1, -1, 2),
                    self.front_hole_detector.homography).reshape(-1, 2)
                if last_0_0_coord is not None:

                    vertical_max_dist = geom.point_distance(cur_0_0_coord, cur_1_0_coord)
                    # If the distance between two board detection exceed 3/4 * distance between two rows,
                    #    the detection is considered as unstable because two different grids have been detected
                    if geom.point_distance(cur_0_0_coord, last_0_0_coord) > 0.75 * vertical_max_dist:
                        raise FrontHolesGridNotFoundException(
                            "The detection was not stable as it detected two different boards during {0} attempt(s)"
                                .format(str(i)))
                last_0_0_coord = cur_0_0_coord
                if debug:
                    cv2.imshow("Perspective", self.front_hole_detector.getPerspective())
                    if cv2.waitKey(1) == 27:
                        print "Esc pressed : exit"
                        cv2.destroyAllWindows()
                        raise FrontHolesGridNotFoundException("The detection was interrupted")
            else:
                raise FrontHolesGridNotFoundException(
                    "The detection was not stable as it lost the board after {0} attempt(s)".format(str(i)))

    def getUpperHoleCoordinatesUsingMarkers(self, index, camera_position, camera_matrix, camera_dist,
                                            tries=1, debug=False):
        """
        :param index: the index of the hole
        :type index: int
        :param camera_position: the 6D position of the camera used for the detection (the bottom one),
                                    from the robot torso
        :type camera_position: tuple
        :param camera_matrix: the camera distortion matrix
        :type camera_matrix: np.array
        :param camera_dist: the camera distortion coefficients vector
        :type camera_dist: np.array
        :param debug: if True, draw the detected markers
        :type debug: bool
        :param tries: the number of times the detection will be run. If one try fails,
                      the whole detection is considered as failed
        :type tries: int
        Get an upper hole's coordinates using the Hamming markers on the Connect 4.
        This method assumes that the Hamming codes are visible on the image it will
            acquire using its "next_img_func". Otherwise, the detection fails
        """
        max_nb_of_markers = 0
        rvec = None
        tvec = None
        for i in range(tries):
            img = self.next_img_func(1)  # We get the image from the bottom camera
            min_nb_of_codes = 2
            markers = detect_markers(img)
            if markers is not None and len(markers) >= min_nb_of_codes:
                if debug:
                    for m in markers:
                        m.draw_contour(img)
                        cv2.putText(img, str(m.id), tuple(int(p) for p in m.center),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    cv2.imshow("Debug", img)
                    if cv2.waitKey(100) == 27:
                        raise NotEnoughLandmarksException("The detection was interrupted")
                self.upper_hole_detector._hamcodes = markers
                self.upper_hole_detector.runDetection([], markers)
                if len(markers) > max_nb_of_markers:
                    max_nb_of_markers = len(markers)
                    rvec, tvec = self.upper_hole_detector.match3DModel(camera_matrix, camera_dist)
            else:
                raise NotEnoughLandmarksException("The model needs at least " + str(min_nb_of_codes) + " detected codes")
        return self._getUpperHoleCoordinates(rvec, tvec, index, camera_position)

    def getUpperHoleCoordinatesUsingFrontHoles(self, distance, sloped, index, camera_position, camera_matrix,
                                               camera_dist, debug=False, tries=1):
        """
        :param distance: The distance between the robot and the connect4
        :type distance: float
        :param sloped: True if the connect4 is sloped or in an unknown position
        :type sloped: bool
        :param index: the index of the hole
        :type index: int
        :param camera_position: the 6D position of the camera used for the detection (the top one),
                                    from the robot torso
        :type camera_position: tuple
        :param camera_matrix: the camera distortion matrix
        :type camera_matrix: np.array
        :param camera_dist: the camera distortion coefficients vector
        :type camera_dist: np.array
        :param debug: if True, draw the detected markers
        :type debug: bool
        :param tries: the number of times the detection will be run. If one try fails,
                      the whole detection is considered as failed
        :type tries: int
        Get an upper hole's coordinates using the front holes of the Connect 4.
        This method assumes that the front holes are visible on the image it will
            acquire using its "next_img_func". Otherwise, the detection fails
        """
        self.detectFrontHoles(distance, sloped, tries=tries, debug=debug)
        rvec, tvec = self.front_hole_detector.match3DModel(camera_matrix, camera_dist)
        return self._getUpperHoleCoordinates(rvec, tvec, index, camera_position)

    def _getUpperHoleCoordinates(self, rvec, tvec, index, camera_position):
        """
        :param img: the image in which the hole will be detected
        :type img: np.ndarray
        :param index: the index of the hole
        :type index: int
        :param camera_position: the 6D position of the camera used for the detection, from the robot torso
        :type camera_position: tuple
        :return: The asked upper hole 3D coordinates
        :rtype: np.array
        Detect holes in the image using the Hamming codes.
        """
        coords = self.tracker.get_holes_coordinates(rvec, tvec, camera_position, index)
        coords[2] += 0.06  # So the hand of NAO is located above the connect 4, not on it
        print coords
        return coords
