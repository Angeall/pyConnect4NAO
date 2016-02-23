import numpy as np

__author__ = 'Anthony Rouneau'


class DefaultConnect4Image(object):

    IMAGE_NAME = "Connect4.png"

    def __init__(self, game_state=None, x_start=56, y_start=31, x_dist=68, y_dist=55, hor=7, ver=6):
        """
        :param x_start: The starting x coordinate
        :type x_start: int
        :param y_start: The starting y coordinate
        :type y_start: int
        :param x_dist: The x distance between two keypoints
        :type x_dist: int
        :param y_dist: The y distance between two keypoints
        :type y_dist: int
        :param hor: The number of keypoints horizontally
        :type hor: int
        :param ver: The number of keypoints vertically
        :type ver: int
        """
        self.game_state = game_state
        if self.game_state is None:
            pass  # Initialize a new game
        self.x_start = x_start
        self.y_start = y_start
        self.x_dist = x_dist
        self.y_dist = y_dist
        self.hor = hor
        self.ver = ver
        self.pixel_mapping = self.generate2DReference()

    def generate2DReference(self, ):
        """
        Create a virtual mapping using a pattern defined with the parameters that refers to the image of reference
        for the homography
        :return: A mapping that defines a circle grid.
                 The keys are relative coordinates : (0, 0), (0, 1), ...
                 The values are pixel coordinates
        :rtype: dict
        """
        grid = {}
        current_x = self.x_start
        current_y = self.y_start
        y_pos = 5
        x_pos = 0
        for i in range(self.ver):
            for j in range(self.hor):
                grid[(x_pos, y_pos)] = np.array([current_x, current_y])
                current_x += self.x_dist
                x_pos += 1
            x_pos = 0
            current_x = self.x_start
            current_y += self.y_dist
            y_pos -= 1
        return grid

if __name__ == "__main__":
    d4 = DefaultConnect4Image()
    ref_mapping = d4.generate2DReference()
    for i in range(7):
        for j in range(6):
            print "(" + str(i), ", " + str(j) + ")", ref_mapping[(i, j)]

