import cv2
import numpy as np
from scipy.spatial import KDTree

import utils.camera.geom as geom
from connect4.model.default_model import DefaultConnect4Model

__author__ = 'Anthony Rouneau'


class NotEnoughLandmarksException(BaseException):
    def __init__(self, msg):
        super(NotEnoughLandmarksException, self).__init__(msg)


class UpperHoleDetector(object):
    """

    """

    def __init__(self, c4_model):
        """
        :param c4_model: the _model that represents the connect 4
        :type c4_model: DefaultConnect4Model
        """
        self._model = c4_model
        self._rectangles = []
        self._holes = []
        self._hamcodes = []
        # The KDTree only stocks Point2Ds. Hence we maintain a correspondence table
        #  between the rectangle centres and the _rectangles indices.
        self._centres_to_indices = {}
        self._boxes = []
        self._kdtree = None
        self._filtered_rectangle_centres = []
        self._ham_id_to_rect_centres = {}

    def _clear(self):
        """
        Clears all the inner variables of the detector
        """
        self._rectangles = []
        self._holes = []
        self._hamcodes = []
        self._centres_to_indices = {}
        self._boxes = []
        self._kdtree = None
        self._filtered_rectangle_centres = []
        self._ham_id_to_rect_centres = {}

    def runDetection(self, rectangles, hamcodes):
        self._clear()
        self._rectangles = rectangles
        self._hamcodes = hamcodes
        self._kdtree, self._centres_to_indices, self._boxes = self._init_structures()
        self._filtered_rectangle_centres = self._filter_included_rectangles()
        self._filtered_rectangle_centres = self._filter_other_rectangles()
        if hamcodes is not None and len(hamcodes) > 0:
            self._ham_id_to_rect_centres = self._find_hamcodes_rectangles()
        for rect_centre in self._filtered_rectangle_centres:
            self._holes.append(self._rectangles[self._centres_to_indices[rect_centre]])

    def _init_structures(self):
        """
        :return: the _kdtree, the centre to indices map and the box list, in this order
        :rtype: tuple
        Initialize the data structures used inside the detector
        """
        data = []
        boxes = []
        centres_to_indices = {}
        for i, rect in enumerate(self._rectangles):
            centres_to_indices[rect[0]] = i
            boxes.append(geom.sort_rectangle_corners(cv2.boxPoints(rect)))
            data.append(rect[0])
        return KDTree(data), centres_to_indices, boxes

    def _filter_included_rectangles(self):
        """
        :return: the list containing all the rectangle centres that passed through the filter
        :rtype: list
        Filters the _rectangles that are partially included with each other.
        """
        filtered_rectangle_centres = []
        number_of_neighbours = 2
        max_common_area = 0.4
        to_ignore = {}
        for rect_centre in self._centres_to_indices.keys():
            if not to_ignore.get(rect_centre, False):
                added = False
                neighbours = self._kdtree.query(rect_centre, number_of_neighbours)[1]
                rect1_index = self._centres_to_indices[rect_centre]
                rect1 = self._rectangles[rect1_index]
                for neighbour in neighbours:
                    if not to_ignore.get(neighbour, False):
                        common_area = geom.common_boxes_area(self._boxes[rect1_index], self._boxes[neighbour])
                        if common_area / geom.rectangle_area(rect1) > max_common_area:
                            to_ignore[neighbour] = True
                            if not added:
                                filtered_rectangle_centres.append(rect_centre)
                                added = True
        return filtered_rectangle_centres

    def _filter_other_rectangles(self):
        filtered_rectangle_centres = []
        contains_map = {}
        # The ratio between the hole length + the horizontal space and the hole length
        model_hole_space_ratio = (self._model.hole_length + self._model.hole_h_space) / self._model.hole_length
        model_length_width_ratio = (self._model.hole_length / self._model.hole_width)
        for centre in self._filtered_rectangle_centres:
            if not contains_map.get(centre, False):
                box = self._boxes[self._centres_to_indices[centre]]
                box_vector, box_length, _, box_width = geom.get_box_info(box)
                max_distance = 0.5 * box_length
                # If the rectangle is not too small and the length/width ratio is the ratio expected by the _model
                if box_length > 30 and geom.are_ratio_similar(box_length / box_width, model_length_width_ratio, 1.75):
                    for other_centre in self._filtered_rectangle_centres:
                        if other_centre is not centre:
                            other_box = self._boxes[self._centres_to_indices[other_centre]]
                            other_box_vector, other_box_length, _, other_box_width = geom.get_box_info(other_box)
                            centres_vector = geom.vectorize(centre, other_centre)
                            # If the other rectangle is not too small and the length/width ratio
                            #   is the ratio expected by the _model
                            #   and : the two rectangle have the same length
                            #   and : the distance between the _rectangles is the distance expected by the _model
                            #   and : the vector of the long_side of the rectangle and the vector that binds the
                            #       two centres is approximately parallel
                            if other_box_length > 30 \
                                    and geom.are_ratio_similar(other_box_length / other_box_width,
                                                               model_length_width_ratio, 1.75) \
                                    and geom.are_vectors_similar(box_vector, other_box_vector, max_distance,
                                                                 signed=False) \
                                    and geom.are_ratio_similar(np.linalg.norm(centres_vector) / box_length,
                                                               model_hole_space_ratio, 0.25) \
                                    and abs((np.dot(box_vector, centres_vector) / (
                                                box_length * np.linalg.norm(centres_vector))) - 1 < 0.4):
                                if not contains_map.get(centre, False):
                                    filtered_rectangle_centres.append(centre)
                                    contains_map[centre] = True
                                if not contains_map.get(other_centre, False):
                                    filtered_rectangle_centres.append(other_centre)
                                    contains_map[other_centre] = True
        return filtered_rectangle_centres

    def _find_hamcodes_rectangles(self):
        hamcodes_id_to_rect_centres = {}
        for hamcode in self._hamcodes:
            hamcode.contours = geom.sort_rectangle_corners(hamcode.contours)
            ham_long_vector = geom.vectorize(hamcode.contours[0], hamcode.contours[1])
            for rect_centre in self._filtered_rectangle_centres:
                ((long_vector, long_norm), (_, _)) = geom.get_box_info(self._boxes[self._centres_to_indices[rect_centre]])
                if geom.are_vectors_parallel(long_vector, ham_long_vector, 0.25):
                    hamcode_vector = geom.vectorize(hamcode.contours[0], hamcode.contours[1])
                    centers_vector = geom.vectorize(hamcode.center, rect_centre)
                    model_ratio = (self._model.hamcode_v_margin + (self._model.hamcode_side / 2.)
                                   - self._model.hole_v_margin - (self._model.hole_width / 2.)) / self._model.hamcode_side
                    image_ratio = np.linalg.norm(centers_vector) / np.linalg.norm(hamcode_vector)
                    if geom.are_ratio_similar(image_ratio, model_ratio, 1.75):
                        hamcodes_id_to_rect_centres[hamcode.id] = rect_centre
        return hamcodes_id_to_rect_centres

    def match_3d_model(self, camera_matrix, camera_dist, res=640, min_number_of_holes=2):
        if self._hamcodes is None:
            raise NotImplementedError("The current 3D matching algorithm uses Hamming codes and can't work without")
        if len(self._hamcodes) < min_number_of_holes:
            raise NotEnoughLandmarksException("The model needs at least " + str(min_number_of_holes) + " detected codes")
        res_diff = res/320.  # Because the calibration was made using 320x240 images
        object_points = []
        image_points = []
        for hamcode in self._hamcodes:
            hole_id = int(round(int(hamcode.id)/1000))-1
            if 0 <= hole_id <= 6:  # If the code has been read correctly and is one of the Connect 4 Hamming codes
                object_points.extend(self._model.getHamcode(hole_id))
                # image_points.append(np.uint16(geom.sort_rectangle_corners(hamcode.contours)/res_diff))
                image_points.extend(hamcode.contours)
                if self._ham_id_to_rect_centres.get(hamcode.id) is not None:
                    object_points.extend(self._model.getUpperHole(hole_id))
                    image_points.extend(self._boxes[self._centres_to_indices[self._ham_id_to_rect_centres[hamcode.id]]])
        for i in range(len(image_points)):
            image_points[i] = tuple(image_points[i])
            object_points[i] = tuple(object_points[i])
        object_points = np.array(object_points)
        image_points = np.array(image_points) / res_diff
        retval, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, camera_dist)
        if not retval:
            print "ERR: SolvePnP failed"
        return rvec, tvec
