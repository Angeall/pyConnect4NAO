__author__ = 'Angeall'

import numpy as np


# Returns the vector made by the two input points
def vectorize(p1, p2):
    return abs(int(p2[0]) - int(p1[0])), abs(int(p2[1]) - int(p1[1]))


# Returns the distance between two points (the norm of the vector made by the input two points)
def point_distance(p1, p2):
    return np.linalg.norm(vectorize(p1, p2))


# Returns a list with connections between keypoints.
#   Those connections are computed this way:
#       For every couple of keypoints (a, b) such that a is not b:
#           if there's no keypoint c such that ((dist(a,c) < dist(a,b)) and (dist(c, b) < dist(a, c)))
#           then add the vector (a,b) to the connection with the indices of the keypoints a and b
# Elements of this list are :
#   (vector, (circle_list_index_1, circle_list_index_1))
def connect_keypoints(circles):
    connections = []
    for i, keypoint in enumerate(circles):
        for j, compare_point in enumerate(circles):
            couple_dist = point_distance((keypoint[0], keypoint[1]), (compare_point[0], compare_point[1]))
            closer = True
            if not(keypoint is compare_point):
                for c in circles:
                    if not(c is keypoint) and not(c is compare_point):
                        k_c_dist = point_distance((keypoint[0], keypoint[1]), (c[0], c[1]))
                        comp_c_dist = point_distance((compare_point[0], compare_point[1]), (c[0], c[1]))
                        if k_c_dist < couple_dist and comp_c_dist < couple_dist:
                            closer = False
                if closer:
                    connections.append((vectorize((circles[i][0], circles[i][1]), (circles[j][0], circles[j][1])),
                                        (i, j)))
    return connections


def filter_connections(connections, pixel_threshold=20, min_to_keep=5):
    to_keep = []
    for connection in connections:
        similar_counter = 0
        for other in connections:
            if not(connection is other):
                (x_diff, y_diff) = vectorize(connection[0], other[0])
                if x_diff < pixel_threshold and y_diff < pixel_threshold:
                    similar_counter += 1
        if similar_counter > min_to_keep:
            to_keep.append(connection)
    return to_keep


# TODO : unit_test filter_connection with dumb values

"""
circle_list= [(0,  10), (6, 10), (0, 7), (6, 7)]
print connect_keypoints(circle_list)
"""

