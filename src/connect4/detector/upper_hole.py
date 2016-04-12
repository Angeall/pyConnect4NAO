import numpy as np
from connect4.model.default_model import DefaultConnect4Model
import cv2
from scipy.spatial import KDTree
import utils.geom as geom

__author__ = 'Anthony Rouneau'


class UpperHoleDetector(object):
    """

    """

    def __init__(self, c4_model):
        """
        :param c4_model: the model that represents the connect 4
        :type c4_model: DefaultConnect4Model
        """
        self.model = c4_model
        self.rectangles = []
        self.holes = []
        self.lines = []
        # The KDTree only stocks Point2Ds. Hence we maintain a correspondence table
        #  between the rectangle centres and the rectangles indices.
        self.centres_to_indices = {}
        self.boxes = []
        self.kdtree = None
        self.filtered_rectangle_centres = []

    def clear(self):
        """
        Clears all the inner variables of the detector
        """
        self.rectangles = []
        self.holes = []
        self.lines = []
        self.centres_to_indices = {}
        self.boxes = []
        self.kdtree = None
        self.filtered_rectangle_centres = []

    def runDetection(self, rectangles, lines):
        self.clear()
        self.rectangles = rectangles
        self.lines = lines
        self.kdtree, self.centres_to_indices, self.boxes = self.init_structures()
        self.filtered_rectangle_centres = self.filter_included_rectangles()
        self.filtered_rectangle_centres = self.filter_other_rectangles()
        for rect_centre in self.filtered_rectangle_centres:
            self.holes.append(self.rectangles[self.centres_to_indices[rect_centre]])

    def init_structures(self):
        """
        :return: the kdtree, the centre to indices map and the box list, in this order
        :rtype: tuple
        Initialize the data structures used inside the detector
        """
        data = []
        boxes = []
        centres_to_indices = {}
        for i, rect in enumerate(self.rectangles):
            centres_to_indices[rect[0]] = i
            boxes.append(cv2.boxPoints(rect))
            data.append(rect[0])
        return KDTree(data), centres_to_indices, boxes

    def filter_included_rectangles(self):
        """
        :return: the list containing all the rectangle centres that passed through the filter
        :rtype: list
        Filters the rectangles that are partially included with each other.
        """
        filtered_rectangle_centres = []
        number_of_neighbours = 2
        max_common_area = 0.4
        to_ignore = {}
        for rect_centre in self.centres_to_indices.keys():
            if not to_ignore.get(rect_centre, False):
                added = False
                neighbours = self.kdtree.query(rect_centre, number_of_neighbours)[1]
                rect1_index = self.centres_to_indices[rect_centre]
                rect1 = self.rectangles[rect1_index]
                for neighbour in neighbours:
                    if not to_ignore.get(neighbour, False):
                        common_area = geom.common_boxes_area(self.boxes[rect1_index], self.boxes[neighbour])
                        if common_area / geom.rectangle_area(rect1) > max_common_area:
                            to_ignore[neighbour] = True
                            if not added:
                                filtered_rectangle_centres.append(rect_centre)
                                added = True
        return filtered_rectangle_centres

    def filter_other_rectangles(self):
        filtered_rectangle_centres = []
        contains_map = {}
        # The ratio between the hole length + the horizontal space and the hole length
        model_hole_space_ratio = (self.model.hole_length + self.model.hole_h_space) / self.model.hole_length
        model_length_width_ratio = (self.model.hole_length / self.model.hole_width)
        for centre in self.filtered_rectangle_centres:
            if not contains_map.get(centre, False):
                box = self.boxes[self.centres_to_indices[centre]]
                box_vector, box_length, _, box_width = geom.get_box_info(box)
                max_distance = 0.5 * box_length
                # If the rectangle is not too small and the length/width ratio is the ratio expected by the model
                if box_length > 30 and geom.are_ratio_similar(box_length / box_width, model_length_width_ratio, 1.75):
                    for other_centre in self.filtered_rectangle_centres:
                        if other_centre is not centre:
                            other_box = self.boxes[self.centres_to_indices[other_centre]]
                            other_box_vector, other_box_length, _, other_box_width = geom.get_box_info(other_box)
                            centres_vector = geom.vectorize(centre, other_centre)
                            # If the other rectangle is not too small and the length/width ratio
                            #   is the ratio expected by the model
                            #   and : the two rectangle have the same length
                            #   and : the distance between the rectangles is the distance expected by the model
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
