__author__ = 'Angeall'
import numpy as np
from scipy.cluster.vq import kmeans, vq
import random
from Queue import Queue


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
    return float(y0) - float(x0), float(y1) - float(x1)


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


def connect_keypoints(keypoints, max_distance=0., exclude_list=[]):
    """
    Returns a list with connections between keypoints.
    For every couple of keypoints (a, b) such that a is not b:
           if there's no keypoint c such that ((dist(a,c) < dist(a,b)) and (dist(c, b) < dist(a, c)))
           then add the vector (a,b) to the connection with the indices of the keypoints a and b
    :param keypoints: The keypoints (list of 2D coordinates).
    :type keypoints: list
    :param max_distance: The maximum distance between two keypoints for them to be considered as couple (connected).
    :type max_distance: float
    :param exclude_list: A list of indices that indicates which keypoints are to be ignored during the connections.
    :type exclude_list: list
    :return: a list of connections: [vectors_between_couples, keypoints_indices]
    :rtype: list
    """
    connections = [[], []]
    for i, keypoint in enumerate(keypoints):
        if i in exclude_list:
            continue
        for j, compare_point in enumerate(keypoints):
            if j in exclude_list:
                continue
            couple_dist = point_distance((keypoint[0], keypoint[1]), (compare_point[0], compare_point[1]))
            if max_distance != 0 and couple_dist > max_distance:
                continue
            closer = True
            if not (keypoint is compare_point):
                for l, c in enumerate(keypoints):
                    if l in exclude_list:
                        continue
                    if not (c is keypoint) and not (c is compare_point):
                        k_c_dist = point_distance((keypoint[0], keypoint[1]), (c[0], c[1]))
                        comp_c_dist = point_distance((compare_point[0], compare_point[1]), (c[0], c[1]))
                        if k_c_dist < couple_dist and comp_c_dist < couple_dist:
                            closer = False
                if closer:
                    connections[0].append(
                        vectorize((keypoints[i][0], keypoints[i][1]), (keypoints[j][0], keypoints[j][1])))
                    connections[1].append((i, j))
    return connections


def filter_connections(connections, pixel_threshold=10., min_to_keep=15):
    """
    For every existing connection, check that there's minimum "min_to_keep" other vectors with the same values
    (Same value following the threshold). If it's True, keep the connection, otherwise discard it
    :param connections: Connections resulting from :py:func:connect_keypoints(keypoints, max_distance, exclude_list)
    :type connections: list
    :param pixel_threshold: The maximum accepted error around a vector.
    :type pixel_threshold: float
    :param min_to_keep: The minimum number of similar vector to keep a type of vector.
    :type min_to_keep: int
    :return: a list of filtered connections: [vectors_between_couples, keypoints_indices]
    :rtype: list
    """
    to_keep = [[], []]
    for i, connection in enumerate(connections[0]):
        similar_counter = 1
        for other in connections[0]:
            if not (connection is other):
                (x_diff, y_diff) = vectorize(connection, other)
                if (abs(x_diff) <= pixel_threshold) and (abs(y_diff) <= pixel_threshold):
                    similar_counter += 1
        if similar_counter >= min_to_keep:
            to_keep[0].append(connection)
            to_keep[1].append(connections[1][i])
    return to_keep


def cluster_vectors(filtered_connections, nb_clusters=4):
    """
    Cluster vectors into "nb_clusters" clusters.
    :param filtered_connections: The list resulting from
           :py:func:filter_connections(connections, pixel_threshold=, min_to_keep)
    :type filtered_connections: list
    :param nb_clusters: The number of clusters returned
    :return: A list with clusters and mean of clusters
    :rtype: list
    """
    return kmeans(filtered_connections[0], nb_clusters)


def filter_right_up_vectors(filtered_connections):
    """
    Computes an array with vectors belonging to the cluster right and the cluster up
    :param filtered_connections: The list of filtered connections resulting from
                                 :py:func:filter_connections(connections, pixel_threshold=, min_to_keep)
    :type filtered_connections: list
    :return: A list of keypoint index couples belonging either to the "up" or the "right" cluster.
             [[right_vector_couples], [up_vector_couples]]
    :rtype: list
    """
    clusters_centroids = cluster_vectors(filtered_connections)[0]
    max_x = (-np.infty, None)
    max_y = (-np.infty, None)
    for i in range(len(clusters_centroids)):
        centroid = clusters_centroids[i]
        if centroid[0] > max_x[0]:
            max_x = (centroid[0], i)
        if centroid[1] > max_y[0]:
            max_y = (centroid[1], i)
    x = max_x[1]
    y = max_y[1]
    belongs_to_cluster = vq(filtered_connections[0], clusters_centroids)[0]
    clusters = [[], []]
    for index, cluster in enumerate(belongs_to_cluster):
        if cluster == x:
            clusters[0].append(filtered_connections[1][index])
        if cluster == y:
            clusters[1].append(filtered_connections[1][index])
    return clusters


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
    for (a, b) in list_tuple:
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
    for (a, b) in list_tuple:
        if a < x_min:
            x_min = a
        if b < y_min:
            y_min = b
    return x_min, y_min


def double_pass_filter(keypoints, max_distance=0, pixel_threshold=10, min_to_keep=15):
    """
     Goal : erase noise, then try to connect more true keypoints (by avoiding noise keypoints)
     1) Connect couple of centers, filter it
     2) Remove every center that is not linked with another center after the filter of 1)
     3) Re-connect couple of centers, ignoring the centers removed in 2) and re-filter
     4) Returns result of 3)
    :param keypoints: The keypoints (list of 2D coordinates).
    :type keypoints: list
    :param max_distance: The maximum distance between two keypoints for them to be considered as couple (connected).
    :type max_distance: float
    :param pixel_threshold: The maximum accepted error around a vector.
    :type pixel_threshold: float
    :param min_to_keep: The minimum number of similar vector to keep a type of vector.
    :type min_to_keep: int
    :return: A list of double filtered connections: [vectors_between_couples, keypoints_indices]
    :rtype: list
    """
    connections = connect_keypoints(keypoints, max_distance)
    filtered_connections = filter_connections(connections, pixel_threshold, min_to_keep)
    centers_to_keep = []
    centers_to_remove = range(len(keypoints))
    for (center1, center2) in filtered_connections[1]:
        if center1 not in centers_to_keep:
            centers_to_keep.append(center1)
            centers_to_remove.remove(center1)
        if center2 not in centers_to_keep:
            centers_to_keep.append(center2)
            centers_to_remove.remove(center2)
    connections = connect_keypoints(keypoints, max_distance, centers_to_remove)
    return filter_connections(connections, pixel_threshold, min_to_keep)


#
def normalize_coord_mapping(mapping, x_shift=None, y_shift=None):
    """
    Shift a mapping so that all values of the mapping are shifted by x_shift and y_shift.
    If x_shift is None, The lowest x value will be 0 and other x values are adapted in consequence.
    If y_shift is None, The lowest y value will be 0 and other y values are adapted in consequence.
    :param mapping: The mapping to transform.
    :type mapping: dict
    :param x_shift: The horizontal shift to apply to the mapping.
    :type x_shift: int
    :param y_shift: The horizontal shift to apply to the mapping.
    :type y_shift: int
    :return: The transformed mapping
    :rtype: dict
    """
    if x_shift is None and y_shift is None:
        (x_shift, y_shift) = min_tuple(mapping.keys())
    elif x_shift is None:
        (x_shift, _) = min_tuple(mapping.keys())
    elif y_shift is None:
        (_, y_shift) = min_tuple(mapping.keys())
    new_mapping = {}
    if x_shift != 0 and y_shift != 0:
        keys = mapping.keys()
        for key in keys:
            value = mapping.pop(key)
            new_mapping[(key[0] - x_shift, key[1] - y_shift)] = value
    elif x_shift != 0:
        keys = mapping.keys()
        for key in keys:
            value = mapping.pop(key)
            new_mapping[(key[0] - x_shift, key[1])] = value
    elif y_shift != 0:
        keys = mapping.keys()
        for key in keys:
            value = mapping.pop(key)
            new_mapping[(key[0], key[1] - y_shift)] = value
    else:
        new_mapping = mapping
    return new_mapping


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


def bfs_marking(vector_clusters, start_node):
    """
    Explore keypoints as a graph using vectors (filtered before).
    Use Breadth First Search, starting from the keypoint "start_node"
    :param vector_clusters: The up and right connections that were filtered before.
    :type vector_clusters: list
    :param start_node: The keypoint index from where the exploration starts.
    :type start_node: int
    :return: A mapping between relative coordinates ( (0, 0), (0, 1), ...) and keypoints indices.
    :rtype: dict
    """
    # Contains nodes and position of node
    frontier = Queue()
    frontier.put([start_node, (0, 0)])
    mapping = {}
    explored = []
    while not frontier.empty():
        [current_node, (right_cost, up_cost)] = frontier.get()
        if not (current_node in explored):
            # print current_node, (right_cost, up_cost)
            explored.append(current_node)
            mapping[(right_cost, up_cost)] = current_node
            right_vectors = filter(lambda x: x[0] == current_node, vector_clusters[0])
            up_vectors = filter(lambda x: x[0] == current_node, vector_clusters[1])
            neg_right_vectors = filter(lambda x: x[1] == current_node, vector_clusters[0])
            neg_up_vectors = filter(lambda x: x[1] == current_node, vector_clusters[1])
            for vector in right_vectors:
                frontier.put([vector[1], (right_cost + 1, up_cost)])
            for vector in up_vectors:
                frontier.put([vector[1], (right_cost, up_cost + 1)])
            for vector in neg_right_vectors:
                frontier.put([vector[0], (right_cost - 1, up_cost)])
            for vector in neg_up_vectors:
                frontier.put([vector[0], (right_cost, up_cost - 1)])
    new_mapping = normalize_coord_mapping(mapping)
    return new_mapping


def count_rectangle_connections(rectangle, mapping, up_right_connections):
    """
    Count the keypoints connections inside a rectangle in the grid.
    :param rectangle: The rectangle to consider in the grid.
                      A rectangle is [[(coord_up_left), (coord_up_right)], [(coord_down_left), (coord_down_right)]]
    :type rectangle: list
    :param mapping: The grid mapping between relative coordinates and keypoint index representing the grid.
    :type mapping: dict
    :param up_right_connections: The up and right keypoints connections that were filtered.
    :type up_right_connections: list
    :return: The number of keypoints connections inside a rectangle in the grid.
    :rtype: int
    """
    [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = rectangle
    circles = []
    for (x, y) in mapping.keys():
        if min_x <= x <= max_x and min_y <= y <= max_y:
            circles.append(mapping[(x, y)])

    nb_connection = filter(lambda (x, y): x in circles and y in circles, up_right_connections[0])
    nb_connection += filter(lambda (x, y): x in circles and y in circles, up_right_connections[1])
    return len(nb_connection)


def detect_grid(keypoints, ver=6, hor=7, min_keypoints=20,
                max_distance=0, pixel_threshold=10, min_to_keep=15):
    """
    Tries to detect a grid in the keypoints.
    :param keypoints: The keypoints (list of 2D coordinates).
    :type keypoints: list
    :param hor: The number of keypoints horizontally.
    :type hor: int
    :param ver: The number of keypoints vertically.
    :type ver: int
    :param min_keypoints: The minimum keypoints to consider searching after a grid.
    :type min_keypoints: int
    :param max_distance: The maximum distance between two keypoints for them to be considered as couple (connected).
    :type max_distance: float
    :param pixel_threshold: The maximum accepted error around a vector.
    :type pixel_threshold: float
    :param min_to_keep: The minimum number of similar vector to keep a type of vector when filtering keypoints.
    :type min_to_keep: int
    :return: A tuple (Control value, Mapping of the keypoints) where the control value is True if the grid is found.
    :rtype: tuple
    """
    if len(keypoints) < min_keypoints:
        return False, None

    circle_indices = range(len(keypoints))
    random.shuffle(circle_indices)
    filtered_connections = filter_right_up_vectors(double_pass_filter(keypoints, max_distance,
                                                                      pixel_threshold, min_to_keep))
    for start_node in circle_indices:
        result = bfs_marking(filtered_connections, start_node)
        (max_x, max_y) = max_tuple(result.keys())
        if max_x + 1 < hor or max_y + 1 < ver:
            continue
        elif max_x + 1 == hor and max_y + 1 == ver:
            return True, result
        else:
            # Rectangle too big, need to consider inner rectangles
            rectangles = get_inner_rectangles([[(0, max_y), (max_x, max_y)], [(0, 0), (max_x, 0)]],
                                              ver, hor)
            max_connection = -np.infty
            max_rectangle = None
            for rectangle in rectangles:
                [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = rectangle
                # Count the number of connection inside the rectangle
                nb_connection = count_rectangle_connections(rectangle, result, filtered_connections)
                if nb_connection > max_connection:
                    max_connection = nb_connection
                    max_rectangle = rectangle
            [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = max_rectangle
            # Returns the rectangle that has the more connection inside (filters the dict with the values of the rect
            new_mapping = normalize_coord_mapping({(x, y): v for (x, y), v in result.iteritems()
                                                   if min_x <= x <= max_x and min_y <= y <= max_y})
            return True, new_mapping
    return False, None


def map_virtual_circle_grid(x_start=45, y_start=45, x_dist=68, y_dist=68, hor=7, ver=6):
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
