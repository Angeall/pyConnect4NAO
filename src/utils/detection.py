__author__ = 'Angeall'
import numpy as np
from scipy.cluster.vq import kmeans, vq
import random
from Queue import Queue


# Returns the vector made by the two input points
def vectorize(p1, p2):
    return float(p2[0]) - float(p1[0]), float(p2[1]) - float(p1[1])


# Returns the distance between two points (the norm of the vector made by the input two points)
def point_distance(p1, p2):
    return np.linalg.norm(vectorize(p1, p2))


def normalize(vector):
    norm = np.linalg.norm(vector)
    return vector[0] / norm, vector[1] / norm


# Returns a list with connections between keypoints.
#   Those connections are computed this way:
#       For every couple of keypoints (a, b) such that a is not b:
#           if there's no keypoint c such that ((dist(a,c) < dist(a,b)) and (dist(c, b) < dist(a, c)))
#           then add the vector (a,b) to the connection with the indices of the keypoints a and b
# Elements of this list are :
#   [vectors, circle_list_indices]
def connect_keypoints(circles, max_distance=0, exclude_list=[]):
    connections = [[], []]
    for i, keypoint in enumerate(circles):
        if i in exclude_list:
            continue
        for j, compare_point in enumerate(circles):
            if j in exclude_list:
                continue
            couple_dist = point_distance((keypoint[0], keypoint[1]), (compare_point[0], compare_point[1]))
            if max_distance != 0 and couple_dist > max_distance:
                continue
            closer = True
            if not (keypoint is compare_point):
                for l, c in enumerate(circles):
                    if l in exclude_list:
                        continue
                    if not (c is keypoint) and not (c is compare_point):
                        k_c_dist = point_distance((keypoint[0], keypoint[1]), (c[0], c[1]))
                        comp_c_dist = point_distance((compare_point[0], compare_point[1]), (c[0], c[1]))
                        if k_c_dist < couple_dist and comp_c_dist < couple_dist:
                            closer = False
                if closer:
                    connections[0].append(vectorize((circles[i][0], circles[i][1]), (circles[j][0], circles[j][1])))
                    connections[1].append((i, j))
    return connections


# Returns a list with connections between keypoints.
#   Those connections are computed this way:
#       For every existing connection, check that there's minimum "min_to_keep" other vectors with the same values
#       (Same value following the threshold). If it's True, keep the connection, otherwise discard it
# Elements of this list are :
#   [vectors, circle_list_indices]
def filter_connections(connections, pixel_threshold=10, min_to_keep=15):
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


def cluster_vectors(filtered_connections, nb_clusters=4, ):
    return kmeans(filtered_connections[0], nb_clusters)


# Returns an array with vectors belonging to the cluster right and the cluster up
# Array form : [[right vector couples], [up vector couples]]
def filter_right_up_vectors(filtered_connections):
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
    x_max = -np.infty
    y_max = -np.infty
    for (a, b) in list_tuple:
        if a > x_max:
            x_max = a
        if b > y_max:
            y_max = b
    return x_max, y_max


def min_tuple(list_tuple):
    x_min = np.infty
    y_min = np.infty
    for (a, b) in list_tuple:
        if a < x_min:
            x_min = a
        if b < y_min:
            y_min = b
    return x_min, y_min


# Goal : erase noise, then try to connect more true keypoints (by avoiding noise keypoints)
# 1) Connect couple of centers, filter it
# 2) Remove every center that is not linked with another center after the filter of 1)
# 3) Re-connect couple of centers, ignoring the centers removed in 2) and re-filter
# 4) Returns result of 3)
def double_pass_filter(circle_centers, max_distance=0, pixel_threshold=10, min_to_keep=15):
    connections = connect_keypoints(circle_centers, max_distance)
    filtered_connections = filter_connections(connections, pixel_threshold, min_to_keep)
    centers_to_keep = []
    centers_to_remove = range(len(circle_centers))
    for (center1, center2) in filtered_connections[1]:
        if center1 not in centers_to_keep:
            centers_to_keep.append(center1)
            centers_to_remove.remove(center1)
        if center2 not in centers_to_keep:
            centers_to_keep.append(center2)
            centers_to_remove.remove(center2)
    connections = connect_keypoints(circle_centers, max_distance, centers_to_remove)
    return filter_connections(connections, pixel_threshold, min_to_keep)


def normalize_coord_mapping(mapping, x_shift=None, y_shift=None):
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


# A rectangle is [[(coord_up_left), (coord_up_right)], [(coord_down_left), (coord_down_right)]]
def get_inner_rectangles(rectangle, y_max_coord, x_max_coord):
    # Make sure it is a rectangle
    [[up_left, up_right], [down_left, down_right]] = rectangle
    assert(up_left[1] == up_right[1])
    assert(down_left[1] == down_right[1])
    assert(up_left[0] == down_left[0])
    assert(up_right[0] == down_right[0])
    assert(up_left[0] < up_right[0])
    assert(up_left[1] > down_left[1])
    rectangles = []
    width = up_right[0] - up_left[0] + 1
    height = up_right[1] - down_right[1] + 1
    if width < x_max_coord or height < y_max_coord:
        return rectangles
    elif width == x_max_coord and height == y_max_coord:
        return rectangle
    else:
        x_diff = width - x_max_coord
        y_diff = height - y_max_coord
        for x_shift in range(x_diff+1):
            for y_shift in range(y_diff+1):
                x_base = down_left[0]+x_shift
                y_base = down_left[1]+y_shift
                rectangles.append([[(x_base, y_base + y_max_coord-1),
                                    (x_base + x_max_coord-1, y_base + y_max_coord-1)],
                                   [(x_base, y_base),
                                    (x_base + x_max_coord-1, y_base)]])
    return rectangles
    # TODO : Finish unit testing this function


def bfs_marking(vector_clusters, start_node):
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
            # print right_vectors, (right_cost + 1, up_cost)
            # print up_vectors, (right_cost, up_cost + 1)
            # print neg_right_vectors, (right_cost - 1, up_cost)
            # print neg_up_vectors, (right_cost, up_cost - 1)
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


def detect_grid(circles, horizontal_length=7, vertical_length=6, min_circles=25,
                max_distance=0, pixel_threshold=10, min_to_keep=15):
    if len(circles) < min_circles:
        return False, None

    circle_indices = range(len(circles))
    random.shuffle(circle_indices)
    filtered_connections = filter_right_up_vectors(double_pass_filter(circles, max_distance,
                                                                      pixel_threshold, min_to_keep))
    found = False
    result = {}
    for start_node in circle_indices:
        result = bfs_marking(filtered_connections, start_node)
        (max_x, max_y) = max_tuple(result.keys())
        if max_x < horizontal_length or max_y < vertical_length:
            continue
        elif max_x == horizontal_length and max_y == vertical_length:
            return result
        else:
            # TODO: case where grid detected is larger than expected: decompose into multiple grid and count connections
            pass
