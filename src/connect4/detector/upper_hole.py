__author__ = 'Anthony Rouneau'
import cv2


class UpperHoleDetector(object):
    """

    """

    def __init__(self, rectangles, lines):
        self.rectangles = rectangles
        self.lines = lines


    @staticmethod
    def rectangles_included(rect1, rect2):
        """
        Checks if the first rectangle is included in the second rectangle
        :param rect1: the first rectangle
        :param rect2: the second rectangle
        :return: true if the first rectangle is included in the second one
        :rtype: bool
        """
        # The order in the result of the boxPoints : bottom_l, up_l, up_r, bottom_r.
        ((left_x1, down_y1), (_, up_y1), (right_x1, _), (_, _)) = cv2.boxPoints(rect1)
        ((left_x2, down_y2), (_, up_y2), (right_x2, _), (_, _)) = cv2.boxPoints(rect2)
        if()



