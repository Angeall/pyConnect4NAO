import numpy as np
import cv2
__author__ = 'Anthony Rouneau'


class ImpossibleEquationException(Exception):
    pass

'''
def al_kashi(a=None, b=None, c=None, angle=None):
    """
    Solve the Al-Khachi equation :  a^2 = b^2 + c^2 - 2*b*c*Cos(angle)
    There must be one and only one parameter set to None, it is the unknown
    :param a: The variable a in the equation
    :type a: float
    :param b: The variable b in the equation
    :type b: float
    :param c: The variable c in the equation
    :type c: float
    :param angle: The angle in the equation in radians
    :type angle: float
    :return: The unknown of the equation
    :rtype: float
    """
    nones = []
    args = [a, b, c, angle]
    for i in args:
        if i is None:
            nones.append(i)
    if len(nones)>1:
        raise ImpossibleEquationException("Too many unknown in equation")
    elif len(nones) == 1:
        if a is None:
            return np.sqrt(np.power(b, 2) + np.power(c, 2) - (2*b*c*np.cos(angle)))
        elif b is None:
            return max(np.roots([1, 2*c*np.cos(angle), - np.power(a, 2) + np.power(c, 2)]))
        elif c is None:
            return max(np.roots([1, 2*b*np.cos(angle), - np.power(a, 2) + np.power(b, 2)]))
        elif angle is None:
            a = float(a)
            b = float(b)
            c = float(c)
            return np.arccos(np.divide(np.power(c, 2) - np.power(a, 2) + np.power(b, 2), 2*b*c))
    else:
        raise ImpossibleEquationException("There is no unknown")
'''


def vectorize((x0, x1), (y0, y1)):
    """
    Computes the vector made by the two input points
    :param p1: point 1
    :type p1: tuple
    :param p2: point 2
    :type p2: tuple
    :return: The vector made by p1 and p2
    :rtype: tuple
    """
    return np.array([float(y0) - float(x0), float(y1) - float(x1)])


def point_distance(p1, p2):
    """
    Returns the distance between two points (the norm of the vector made by the input two points)
    :param p1:
    :param p2:
    :return: The distance between p1 and p2
    """
    return np.linalg.norm(vectorize(p1, p2))


def normalize(vector):
    """
    Normalize the input vector
    :param vector:
    :type vector: tuple
    :return: The normalized form of vector
    """
    norm = np.linalg.norm(vector)
    return vector[0] / norm, vector[1] / norm


def cluster_vectors(vectors, nb_clusters=4):
    """
    Cluster vectors into "nb_clusters" clusters.
    :param vectors: A list containing vectors
    :type vectors: list
    :param nb_clusters: The number of clusters returned
    :return: A list with clusters and mean of clusters
    :rtype: list
    """
    result = [[], [], []]
    if len(vectors) > 3:
        data = np.array(vectors, dtype=np.float32)
        while len(result[2]) != nb_clusters:
            result = cv2.kmeans(data, nb_clusters, None,
                                (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                                 10, 1.0), 10, cv2.KMEANS_PP_CENTERS)
    return result


def max_tuple(list_tuple):
    """
    Get the two max values of a list of tuple
    :param list_tuple: A list of tuple to explore. [..., (x_i, y_i), ...]
    :type list_tuple: list
    :return: A tuple that contains (max_x, max_y)
    :rtype: tuple
    """
    x_max = -np.infty
    y_max = -np.infty
    for atuple in list_tuple:
        a = atuple[0]
        b = atuple[1]
        if a > x_max:
            x_max = a
        if b > y_max:
            y_max = b
    return x_max, y_max


def min_tuple(list_tuple):
    """
    Get the two min values of a list of tuple
    :param list_tuple: A list of tuple to explore. [..., (x_i, y_i), ...]
    :type list_tuple: list
    :return: A tuple that contains (min_x, min_y)
    :rtype: tuple
    """
    x_min = np.infty
    y_min = np.infty
    for atuple in list_tuple:
        a = atuple[0]
        b = atuple[1]
        if a < x_min:
            x_min = a
        if b < y_min:
            y_min = b
    return x_min, y_min


def get_inner_rectangles(rectangle, y_max_length, x_max_length):
    """
    Computes a list of inner rectangles of dimensions (y_max_length, x_max_length) that are included inside "rectangle".
    :param rectangle: The rectangle to consider in the grid.
                      A rectangle is [[(coord_up_left), (coord_up_right)], [(coord_down_left), (coord_down_right)]]
    :type rectangle: list
    :param y_max_length: The maximum vertical length of the searched grid.
    :type y_max_length: int
    :param x_max_length: The maximum horizontal length of the searched grid.
    :type x_max_length: int
    :return: A list of inner rectangles inside the rectangles defined in parameters
    :rtype: list
    """
    # Make sure it is a rectangle
    [[up_left, up_right], [down_left, down_right]] = rectangle
    assert (up_left[1] == up_right[1])
    assert (down_left[1] == down_right[1])
    assert (up_left[0] == down_left[0])
    assert (up_right[0] == down_right[0])
    assert (up_left[0] < up_right[0])
    assert (up_left[1] > down_left[1])
    rectangles = []
    width = up_right[0] - up_left[0] + 1
    height = up_right[1] - down_right[1] + 1
    if width < x_max_length or height < y_max_length:
        return rectangles
    elif width == x_max_length and height == y_max_length:
        return rectangle
    else:
        x_diff = width - x_max_length
        y_diff = height - y_max_length
        for x_shift in range(x_diff + 1):
            for y_shift in range(y_diff + 1):
                x_base = down_left[0] + x_shift
                y_base = down_left[1] + y_shift
                rectangles.append([[(x_base, y_base + y_max_length - 1),
                                    (x_base + x_max_length - 1, y_base + y_max_length - 1)],
                                   [(x_base, y_base),
                                    (x_base + x_max_length - 1, y_base)]])
    return rectangles


def map_virtual_circle_grid(x_start=56, y_start=31, x_dist=68, y_dist=55, hor=7, ver=6):
    """
    Create a virtual mapping using a pattern defined with the parameters
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
    :return: A mapping that defines a circle grid.
             The keys are relative coordinates : (0, 0), (0, 1), ...
             The values are pixel coordinates
    :rtype: dict
    """
    grid = {}
    current_x = x_start
    current_y = y_start
    y_pos = 0
    x_pos = 0
    for i in range(ver):
        for j in range(hor):
            grid[(x_pos, y_pos)] = np.array([current_x, current_y])
            current_x += x_dist
            x_pos += 1
        x_pos = 0
        current_x = x_start
        current_y += y_dist
        y_pos += 1
    return grid


def index_mapping_into_pixel_mapping(index_mapping, keypoints_list):
    """
    Transform an index mapping (indices referring to keypoints_list)  into a pixel mapping
    :param index_mapping: The index mapping to transform.
    :type index_mapping: dict
    :param keypoints_list: The list that contains the values of the new pixel mapping
    :type keypoints_list: list
    :return: The new mapping, its values are pixels.
    :rtype: dict
    """
    mapping_pixels = {}
    for key in index_mapping.keys():
        keypoint = keypoints_list[index_mapping[key]]
        mapping_pixels[key] = np.array([keypoint[0], keypoint[1]])
    return mapping_pixels
