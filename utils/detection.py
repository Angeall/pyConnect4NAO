__author__ = 'Angeall'
import numpy as np
from scipy.cluster.vq import kmeans, vq


# Returns the vector made by the two input points
def vectorize(p1, p2):
    return [float(p2[0]) - float(p1[0]), float(p2[1]) - float(p1[1])]


# Returns the distance between two points (the norm of the vector made by the input two points)
def point_distance(p1, p2):
    return np.linalg.norm(vectorize(p1, p2))


def normalize(vector):
    norm = np.linalg.norm(vector)
    return [vector[0]/norm, vector[1]/norm]


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
        similar_counter = 1
        for other in connections[0]:
            if not(connection is other):
                (x_diff, y_diff) = vectorize(connection, other)
                if (abs(x_diff) <= pixel_threshold) and (abs(y_diff) <= pixel_threshold):
                    similar_counter += 1
        if similar_counter >= min_to_keep:
            to_keep[0].append(connection)
            to_keep[1].append(connections[1][i])
    return to_keep


def cluster_vectors(filtered_connections, nb_clusters=4,):
    return kmeans(filtered_connections[0], nb_clusters)


# Returns an array with vectors belonging to
def filter_up_right_vectors(filtered_connections, clusters_centroids):
    max_x = (-np.infty, None)
    max_y = (-np.infty, None)
    for i in range(len(clusters_centroids)):
        centroid = clusters_centroids[i]
        print centroid
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


# TODO : Graph longest path with cost
# TODO : Install scipy + scipy.cluster.vq.kmeans
# TODO : unit_test filter_connection with dumb values


circle_list= [(0,  10), (6.3, 10), (0, 7.2), (6.1, 7.1), (0.4,4.12), (6.14,4.04)]
print connect_keypoints(circle_list)
print filter_connections(connect_keypoints(circle_list), pixel_threshold=1, min_to_keep=3)
print cluster_vectors(filter_connections(connect_keypoints(circle_list), pixel_threshold=1, min_to_keep=3))
print filter_up_right_vectors(filter_connections(connect_keypoints(circle_list), pixel_threshold=1, min_to_keep=3), cluster_vectors(filter_connections(connect_keypoints(circle_list), pixel_threshold=1, min_to_keep=3))[0])


