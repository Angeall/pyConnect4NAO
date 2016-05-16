import cv2
import numpy as np
# from shapely.geometry import Polygon

__author__ = 'Anthony Rouneau'


class ImpossibleEquationException(Exception):
    pass


def al_kashi(a=None, b=None, c=None, angle=None):
    """
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
    Solve the Al-Khachi equation :  a^2 = b^2 + c^2 - 2*b*c*Cos(angle)
    There must be one and only one parameter set to None, it is the unknown
    """
    nones = []
    args = [a, b, c, angle]
    for i in args:
        if i is None:
            nones.append(i)
    if len(nones) > 1:
        raise ImpossibleEquationException("Too many unknown in equation")
    elif len(nones) == 1:
        if a is None:
            return np.sqrt(np.power(b, 2) + np.power(c, 2) - (2 * b * c * np.cos(angle)))
        elif b is None:
            return max(np.roots([1, 2 * c * np.cos(angle), - np.power(a, 2) + np.power(c, 2)]))
        elif c is None:
            return max(np.roots([1, 2 * b * np.cos(angle), - np.power(a, 2) + np.power(b, 2)]))
        elif angle is None:
            a = float(a)
            b = float(b)
            c = float(c)
            return np.arccos(np.divide(np.power(c, 2) - np.power(a, 2) + np.power(b, 2), 2 * b * c))
    else:
        raise ImpossibleEquationException("There is no unknown")


def vectorize(p1, p2, signed=True):
    """
    :param p1: point 1
    :type p1: tuple
    :param p2: point 2
    :type p2: tuple
    :param signed: false will make the vector positive in x and y
    :type signed: bool
    :return: The vector made by p1 and p2
    :rtype: np.array
    Computes the vector made by the two input points, p1 to p2
    """
    (x0, y0) = p1
    (x1, y1) = p2
    if not signed:
        return np.array([abs(float(x1) - float(x0)), abs(float(y1) - float(y0))])
    return np.array([float(x1) - float(x0), float(y1) - float(y0)])


def point_distance(p1, p2):
    """
    :param p1: the first point
    :type p1: tuple
    :param p2: the second point
    :type p2: tuple
    :return: The distance between p1 and p2
    :rtype: double
    Returns the distance between two points (the norm of the vector made by the input two points)
    """
    return np.linalg.norm(vectorize(p1, p2))


def vector_distance(v1, v2, signed=True):
    """
    :param v1: the first vector
    :type v1: tuple
    :param v2: the second vector
    :type v2: tuple
    :param signed: true if the vectors must be oriented the same way to be similar
    :type signed: false
    :return: The distance between v1 and v2
    :rtype: double
    Returns the distance between two points (the norm of the vector made by the input two points)
    """
    return np.linalg.norm(vectorize(v1, v2, signed))


def normalize(vector):
    """
    :param vector: the vector to normalize
    :type vector: tuple
    :return: The normalized form of vector
    :rtype: tuple
    Normalize the input vector
    """
    norm = np.linalg.norm(vector)
    return vector[0] / norm, vector[1] / norm


def transform_vector(vector, rmat, tvec):
    """
    :param vector: The coordinates to transform
    :type vector: np.array
    :param rmat: The rotation matrix
    :type rmat: np.matrix
    :param tvec: The translation vector
    :type tvec: np.array
    :return: The transformed coordinates
    :rtype: np.array
    Apply a rotation and a translation to a vector of coordinates
    """
    # Assure that we can make the rotation using the matrix
    assert (rmat.shape[1] == len(vector))
    # Assure that we can translate the coordinates using tvec
    assert (tvec.size == len(vector))
    # Rotate the coordinates
    temp = np.dot(rmat, vector.reshape((3, 1))).reshape(1, 3)[0]
    # Translate the coordinates
    temp = temp + tvec.reshape(1, 3)[0]
    return temp


def cluster_vectors(vectors, nb_clusters=4):
    """
    :param vectors: A list containing vectors
    :type vectors: list
    :param nb_clusters: The number of clusters returned
    :type nb_clusters: int
    :return: A list with clusters and mean of clusters
    :rtype: list
    Cluster vectors into "nb_clusters" clusters.
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
    :param list_tuple: A list of tuple to explore. [..., (x_i, y_i), ...]
    :type list_tuple: list
    :return: A tuple that contains (max_x, max_y)
    :rtype: tuple
    Get the two max values of a list of tuple
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
    :param list_tuple: A list of tuple to explore. [..., (x_i, y_i), ...]
    :type list_tuple: list
    :return: A tuple that contains (min_x, min_y)
    :rtype: tuple
    Get the two min values of a list of tuple
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
    :param rectangle: The rectangle to consider in the grid.
                      A rectangle is [[(coord_up_left), (coord_up_right)], [(coord_down_left), (coord_down_right)]]
    :type rectangle: list
    :param y_max_length: The maximum vertical length of the searched grid.
    :type y_max_length: int
    :param x_max_length: The maximum horizontal length of the searched grid.
    :type x_max_length: int
    :return: A list of inner _rectangles inside the _rectangles defined in parameters
    :rtype: list
    Computes a list of inner _rectangles of dimensions (y_max_length, x_max_length) that are included inside "rectangle".
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


def index_mapping_into_pixel_mapping(index_mapping, keypoints_list):
    """
    :param index_mapping: The index mapping to transform.
    :type index_mapping: dict
    :param keypoints_list: The list that contains the values of the new pixel mapping
    :type keypoints_list: list
    :return: The new mapping, its values are pixels.
    :rtype: dict
    Transform an index mapping (indices referring to keypoints_list)  into a pixel mapping
    """
    mapping_pixels = {}
    for key in index_mapping.keys():
        keypoint = keypoints_list[index_mapping[key]]
        mapping_pixels[key] = np.array([keypoint[0], keypoint[1]])
    return mapping_pixels


def convert_euler_to_matrix(rvec):
    """
    :param rvec: The vector of roation in Euler angle in the form : [roll, pitch, yaw]
    :type rvec: tuple
    :return: The rotation matrix that corresponds to the input rotation vector
    :rtype: np.matrix
    Convert euler angles ZYX into a 3D rotation matrix
    """
    [roll, pitch, yaw] = rvec
    c1 = np.cos(yaw)
    s1 = np.sin(yaw)
    c2 = np.cos(pitch)
    s2 = np.sin(pitch)
    c3 = np.cos(roll)
    s3 = np.sin(roll)

    m00 = c1 * c2
    m01 = c1 * s2 * s3 - c3 * s1
    m02 = s1 * s3 + c1 * c3 * s2
    m10 = c2 * s1
    m11 = c1 * c3 + s1 * s2 * s3
    m12 = c3 * s1 * s2 - c1 * s3
    m20 = -s2
    m21 = c2 * s3
    m22 = c2 * c3
    return np.matrix([[m00, m01, m02],
                      [m10, m11, m12],
                      [m20, m21, m22]])


# def common_area(rect1, rect2):
#     """
#     :param rect1: the first rectangle
#     :param rect2: the second rectangle
#     :return: the common area between the two _rectangles
#     :rtype: double
#     Get the common area between two _rectangles
#     """
#     return common_boxes_area(cv2.boxPoints(rect1), cv2.boxPoints(rect2))


# def common_boxes_area(box1, box2):
#     """
#     :param box1: the first box, an array of edges coordinates
#     :param box2: the second box, an array of edges coordinates
#     :return: the common area between the two _boxes
#     :rtype: double
#     Get the common  area between two _boxes
#     """
#     # The order in the result of the boxPoints : bottom_l, up_l, up_r, bottom_r.
#     if not (box1[0] == box1[-1]).all():  # If the box is not closed, we close it
#         box1 = np.append(box1, [box1[0]], axis=0)
#     if not (box2[0] == box2[-1]).all():  # If the box is not closed, we close it
#         box2 = np.append(box2, [box2[0]], axis=0)
#     return Polygon(box1).intersection(Polygon(box2)).area


def rectangle_area(rect):
    """
    :param rect: the rectangle, obtained by an OpenCV method : ((center_x, center_y), (width, height), angle_degrees)
    :type rect: tuple
    :return: the unsigned area of the rectangle
    :rtype: double
    Get the area of an OpenCV rectangle
    """
    return rect[1][0] * rect[1][1]


def are_vectors_similar(vector1, vector2, max_distance, signed=True):
    """
    :param vector1: the first vector
    :type vector1: tuple
    :param vector2: the second vector
    :type vector2: tuple
    :param max_distance: the maximum distance to allow between the two vectors to consider them as similar
    :type max_distance: float
    :param signed: true if the vectors must be oriented the same way to be similar
    :type signed: false
    :return: true if the two vectors are similar, for the given maximum distance
    """
    return vector_distance(vector1, vector2, signed) < max_distance


def get_box_info(box):
    """
    :param box: the box, consisting of 4 points
    :type box: np.ndarray
    :return: ((long_side_vector, long_side_norm), (short_side_vector, short_side_norm))
    :rtype: tuple
    """
    vector1 = vectorize(box[0], box[2])
    vector2 = vectorize(box[0], box[1])
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    if norm1 > norm2:
        return ((vector1, norm1), (vector2, norm2))
    else:
        return ((vector2, norm2), (vector1, norm1))


def are_ratio_similar(ratio1, ratio2, max_difference):
    """
    :param ratio1: the first ratio
    :type ratio1: double
    :param ratio2: the second ratio
    :type ratio2: double
    :param max_difference: the maximum allowed difference between the two ratios
    :type max_difference: double
    :return: true if the two ratio are similar, given the maximum allowed difference
    :rtype: bool
    """
    return abs(ratio1 - ratio2) < max_difference


def are_vectors_parallel(vector1, vector2, max_difference):
    """
    :param vector1: the first vector
    :type vector1: tuple
    :param vector2: the second vector
    :type vector2: tuple
    :param max_difference: the maximum allowed error to consider the two vectors as parallels
    :type max_difference: double
    :return: true if the two vectors can be considered as parallel, given the maximum allowed error
    """
    return abs(abs(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))) - 1) < max_difference


def sort_rectangle_corners(rectangle):
    """
    :param rectangle: the rectangle (box points) from which we will sort the corners
    :type rectangle: np.array
    :return: the sorted corners of the rectangle ( [NW, NE, SW, SE] )
    :rtype: list
    """
    ordered_corners = []
    rect = rectangle.reshape(4, 2)
    rect = rect[
        np.lexsort((rect[:, 0], rect[:, 1]))]  # The contours are now ordered following the y-axis
    # We take the two topmost points and we order it following the x-axis
    ordered_corners.extend(rect[0:2][np.lexsort((rect[0:2][:, 1], rect[0:2][:, 0]))])
    # Now we take the two other points and we order it following the x-axis
    ordered_corners.extend(rect[-2:][np.lexsort((rect[-2:][:, 1], rect[-2:][:, 0]))])
    # At this point, ordered contains [NW, NE, SW, SE]
    return ordered_corners
