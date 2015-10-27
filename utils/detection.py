__author__ = 'Angeall'
import numpy as np


# Returns the vector made by the two input points
def vectorize(p1, p2):
    return [int(p2[0]) - int(p1[0]), int(p2[1]) - int(p1[1])]


# Returns the distance between two points (the norm of the vector made by the input two points)
def point_distance(p1, p2):
    return np.linalg.norm(vectorize(p1, p2))


# Returns a list with connections between keypoints.
#   Those connections are computed this way:
#       For every couple of keypoints (a, b) such that a is not b:
#           if there's no keypoint c such that ((dist(a,c) < dist(a,b)) and (dist(c, b) < dist(a, c)))
#           then add the vector (a,b) to the connection with the indices of the keypoints a and b
# Elements of this list are :
#   [vectors, circle_list_indices]
def connect_keypoints(circles):
    connections = [[],[]]
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
                    connections[0].append(vectorize((circles[i][0], circles[i][1]), (circles[j][0], circles[j][1])))
                    connections[1].append([i, j])
    return connections


def filter_connections(connections, pixel_threshold=20, min_to_keep=5):
    to_keep = [[], []]
    for i, connection in enumerate(connections[0]):
        similar_counter = 0
        for other in connections[0]:
            if not(connection is other):
                (x_diff, y_diff) = vectorize(connection, other)
                if x_diff < pixel_threshold and y_diff < pixel_threshold:
                    similar_counter += 1
        if similar_counter > min_to_keep:
            to_keep[0].append(connection)
            to_keep[1].append(connections[1][i])
    return to_keep


def cluster_vectors(filtered_connections, nb_clusters=4,):
    print "TODO"

# TODO : Install scipy + scipy.cluster.vq.kmeans
# TODO : unit_test filter_connection with dumb values


circle_list= [(0,  10), (6, 10), (0, 7), (6, 7)]
print connect_keypoints(circle_list)


