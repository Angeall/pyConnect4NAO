import cv2
import numpy as np
from Queue import Queue
from scipy.spatial import KDTree

import src.utils.geom as geom
__author__ = 'Anthony Rouneau'

class CircleGridException(Exception):
    """
    Exception raised when the detector fails to detect a circle grid with the given parameters
    """
    NO_GRID = "Could not find a circle grid with the given parameters"
    def __init__(self, message=NO_GRID):
        super(CircleGridException, self).__init__(message)

class CircleGridDetector(object):
    def __init__(self, grid_shape, circles, pixel_error_margin=10, min_similar_vectors=15,
                 reference_image=None, reference_mapping=None, img=None):
        """

        :param grid_shape: The shape of the grid to detect (e.g. (6, 7) for a Connect 4 grid)
        :type grid_shape: tuple
        :param reference_image:
        :param reference_mapping:
        :param circles:
        :param img:
        :param pixel_error_margin:
        :param min_similar_vectors:
        :return:
        """
        self.referenceImg = reference_image
        self.referenceMapping = reference_mapping
        self.circles = circles
        self.img = img
        self.gridShape = grid_shape
        self.pixelErrorMargin = pixel_error_margin
        self.minSimilarVectors = min_similar_vectors
        img_shape = img.shape
        self.imageRect = [0, 0, img_shape[0] + 1, img_shape[1] + 1]
        self.exception = CircleGridException()
        self.relativeCoordinates = {}
        self.filteredArcIndices = []
        self.filteredArcVectors = []
        self.noiseCircles = []
        self.originalArcIndices = []
        self.originalArcVectors = []
        self.circleGridMapping = {}
        self.objectPerspective = None

        self.detectCircleGrid()

    def clear(self):
        """
        Private method: Clear the private parameters of the object
        """
        self.relativeCoordinates = {}
        self.filteredArcIndices = []
        self.filteredArcVectors = []
        self.noiseCircles = []
        self.originalArcIndices = []
        self.originalArcVectors = []
        self.circleGridMapping = {}
        self.detectCircleGrid()
        self.objectPerspective = np.ndarray()

    def changeImage(self, circles, pixel_error_margin=10, min_similar_vectors=15, img=None):
        """
        Change the image in which detect the circle grid
        :param circles:
        :param pixel_error_margin:
        :param min_similar_vectors:
        :param img:
        :return:
        """
        self.circles = circles
        self.img = img
        self.pixelErrorMargin = pixel_error_margin
        self.minSimilarVectors = min_similar_vectors
        img_shape = img.shape
        self.imageRect = [0, 0, img_shape[0] + 1, img_shape[1] + 1]
        self.clear()
        self.detectCircleGrid()


    def detectCircleGrid(self):
        """
        Private method : method that launches the detection routine
        """
        self.connectCircles()  # Fill originalArcIndices and originalArcVectors
        self.doublePassFilter() # Fill filteredArcIndices, filteredArcVectors and noiseCircles
        self.bfsMarking() # Fill relativeCoordinates
        self.checkForGrid()
        self.circleGridMapping = geom.index_mapping_into_pixel_mapping(self.relativeCoordinates, self.circles)
        self.findPerspective()

    def getCircleGrid(self):
        """
        Public method : retrieve the circle grid mapping
        :return: A dict with relative coordinates in keys and pixel coordinates in values
                 Example : {(0, 0): (34, 43), (0, 1): (54, 43), ... }
        :rtype: dict
        """
        return self.circleGridMapping

    def rectContains(self, point):
        if point[0] < self.imageRect[0]:
            return False
        elif point[1] < self.imageRect[1]:
            return False
        elif point[0] > self.imageRect[2]:
            return False
        elif point[1] > self.imageRect[3]:
            return False
        return True

    def connectCircles(self):
        """
        Returns a list with connections between keypoints.
        For every couple of keypoints (a, b) such that a is not b:
               if there's no keypoint c such that ((dist(a,c) < dist(a,b)) and (dist(c, b) < dist(a, c)))
               then add the vector (a,b) to the connection with the indices of the keypoints a and b

        :param rect: The image dimensions
        :type rect: tuple
        :param keypoints: The keypoints (list of 2D coordinates).
        :type keypoints: list
        :param exclude_list: A list of indices that indicates which keypoints are to be ignored during the connections.
        :type exclude_list: list
        :return: a list of connections: [vectors_between_couples, keypoints_indices]
        :rtype: list
        """
        keypoints = self.circles
        circles_dict = {}
        vectors_dict = {}

        subdiv = cv2.Subdiv2D()
        subdiv.initDelaunay(self.imageRect)
        for i in range(len(keypoints)):
            keypoint = keypoints[i]
            if not self.noiseCircles[i]: # If the circle i is not a noisy circle
                key = (float(keypoint[0]), float(keypoint[1]))
                circles_dict[key] = i
                subdiv.insert(key)

        triangle_list = subdiv.getTriangleList()
        edge_list = subdiv.getEdgeList()
        # An edge is the coordinates of two points. 1st coordinate = (edge[0], edge[1]), 2nd = (edge[2], edge[3])
        for edge in edge_list:
            pt1 = (edge[0], edge[1])
            pt2 = (edge[2], edge[3])
            if self.rectContains(pt1) and self.rectContains(pt2):
                vectors_dict[(pt1, pt2)] = geom.vectorize(pt1, pt2)
                vectors_dict[(pt2, pt1)] = geom.vectorize(pt2, pt1)

        for triangle in triangle_list:
            pt1 = (triangle[0], triangle[1])
            pt2 = (triangle[2], triangle[3])
            pt3 = (triangle[4], triangle[5])
            if self.rectContains(pt1) and self.rectContains(pt2) and self.rectContains(pt3):
                dist1 = geom.point_distance(pt1, pt2)
                dist2 = geom.point_distance(pt2, pt3)
                dist3 = geom.point_distance(pt3, pt1)
                max_dist = max(dist1, dist2, dist3)
                if max_dist == dist1:
                    if vectors_dict.has_key((pt1, pt2)) and vectors_dict.has_key((pt2, pt1)):
                        vectors_dict.pop((pt1, pt2))
                        vectors_dict.pop((pt2, pt1))
                elif max_dist == dist2:
                    if vectors_dict.has_key((pt2, pt3)) and vectors_dict.has_key((pt3, pt2)):
                        vectors_dict.pop((pt2, pt3))
                        vectors_dict.pop((pt3, pt2))
                else:
                    if vectors_dict.has_key((pt1, pt3)) and vectors_dict.has_key((pt3, pt1)):
                        vectors_dict.pop((pt3, pt1))
                        vectors_dict.pop((pt1, pt3))
        vectors = []
        indices = []
        for (pt1, pt2) in vectors_dict:
            vectors.append(vectors_dict[(pt1, pt2)])
            indices.append((circles_dict[pt1], circles_dict[pt2]))
        self.originalArcVectors = vectors
        self.originalArcIndices = indices


    def filterConnections(self):
        """
        For every existing connection, check that there's minimum "min_similar_vectors" other vectors with the same values
        (Same value following the threshold). If it's True, keep the connection, otherwise discard it
        :param connections: Connections resulting from :py:func:connect_keypoints(keypoints, max_distance, exclude_list)
        :type connections: list
        :param pixel_threshold: The maximum accepted error around a vector.
        :type pixel_threshold: float
        :param min_similar_vectors: The minimum number of similar vector to keep a type of vector.
        :type min_similar_vectors: int
        :return: a list of filtered connections: [vectors_between_couples, keypoints_indices]
        :rtype: list
        """
        filteredArcVectors = []
        filteredArcIndices = []
        if self.minSimilarVectors > len(self.originalArcVectors):
            raise self.exception
        if len(self.originalArcVectors) > 0:
            t = KDTree(self.originalArcVectors)
            for j, connection in enumerate(self.originalArcVectors):
                nearest_neighbours = t.query(connection, self.minSimilarVectors)[1]
                if (geom.point_distance(connection, self.originalArcVectors[nearest_neighbours
                                                        [(self.minSimilarVectors-1)]])) <= self.pixelErrorMargin:
                    filteredArcVectors.append(connection)
                    filteredArcIndices.append(self.originalArcIndices[j])
        self.filteredArcVectors = filteredArcVectors
        self.filteredArcIndices = filteredArcIndices

    def doublePassFilter(self):
        """
         Goal : erase noise, then try to connect more true keypoints (by avoiding noise keypoints)
         1) Connect couple of centers, filter it
         2) Remove every center that is not linked with another center after the filter of 1)
         3) Re-connect couple of centers, ignoring the centers removed in 2) and re-filter
         4) Returns result of 3)
        :param keypoints: The keypoints (list of 2D coordinates).
        :type keypoints: list
        :param rect: The image dimensions
        :type rect: tuple
        :param max_distance: The maximum distance between two keypoints for them to be considered as couple (connected).
        :type max_distance: float
        :param pixel_threshold: The maximum accepted error around a vector.
        :type pixel_threshold: float
        :param min_similar_vectors: The minimum number of similar vector to keep a type of vector.
        :type min_similar_vectors: int
        :return: A list of double filtered connections: [vectors_between_couples, keypoints_indices]
        :rtype: list
        """
        self.filterConnections()
        centers_to_remove = []
        for i in range(len(self.circles)):
            centers_to_remove.append(True)
        for (center1, center2) in self.filteredArcIndices:
            if centers_to_remove[center1]: # If the node was assumed as noisy, we set it as non-noisy
                centers_to_remove[center1] = False
            if centers_to_remove[center2]: # If the node was assumed as noisy, we set it as non-noisy
                centers_to_remove[center2] = False
        # Second pass into the filters with a set of circles detected as noise
        self.noiseCircles = centers_to_remove
        self.connectCircles()
        self.filterConnections()


    def filterRightUpVectors(self):
        """
        Computes an array with vectors belonging to the cluster right and the cluster up
        :param filtered_connections: The list of filtered connections resulting from
                                     :py:func:filter_connections(connections, pixel_threshold=, min_to_keep)
        :type filtered_connections: list
        :return: A list of keypoint index couples belonging either to the "up" or the "right" cluster.
                 [[right_vector_couples], [up_vector_couples]]
        :rtype: list
        """
        if len(self.filteredArcVectors) == 0:
            raise self.exception
        clustering = geom.cluster_vectors(self.filteredArcVectors)
        clusters_centroids = clustering[2]
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
        belongs_to_cluster = clustering[1]
        right_vectors = []
        up_vectors = []
        for index, cluster in enumerate(belongs_to_cluster):
            if cluster == x:
                right_vectors.append(self.filteredArcIndices[index])
            if cluster == y:
                up_vectors.append(self.filteredArcIndices[index])
        self.upVectors = up_vectors
        self.rightVectors = right_vectors

    def bfsMarking(self):
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
        start_node = 0
        frontier.put([start_node, (0, 0)])
        adj_right_dict = {}
        adj_up_dict = {}
        mapping = {}
        explored = []

        for i in range(len(self.circles)):
            explored.append(False)

        for (x, y) in self.rightVectors:
            if adj_right_dict.has_key(x):
                adj_right_dict[x][0].append((x, y))
            else:
                adj_right_dict[x] = [[(x, y)], []]
                adj_up_dict[x] = [[], []]
            if adj_right_dict.has_key(y):
                adj_right_dict[y][1].append((x, y))
            else:
                adj_right_dict[y] = [[], [(x, y)]]
                adj_up_dict[y] = [[], []]

        for (x, y) in self.upVectors:
            if adj_up_dict.has_key(x):
                adj_up_dict[x][0].append((x, y))
            else:
                adj_up_dict[x] = [[(x, y)], []]
                if not adj_right_dict.has_key(x):
                    adj_right_dict[x] = [[], []]
            if adj_up_dict.has_key(y):
                adj_up_dict[y][1].append((x, y))
            else:
                adj_up_dict[y] = [[], [(x, y)]]
                if not adj_right_dict.has_key(y):
                    adj_right_dict[y] = [[], []]
        if not adj_right_dict.has_key(start_node):
            return {(0, 0): start_node}

        while not frontier.empty():
            [current_node, (right_cost, up_cost)] = frontier.get()
            if not explored[current_node]:
                explored[current_node] = True
                mapping[(right_cost, up_cost)] = current_node

                right_vectors = adj_right_dict[current_node][0]
                up_vectors = adj_up_dict[current_node][0]
                neg_right_vectors = adj_right_dict[current_node][1]
                neg_up_vectors = adj_up_dict[current_node][1]
                for vector in right_vectors:
                    frontier.put([vector[1], (right_cost + 1, up_cost)])
                for vector in up_vectors:
                    frontier.put([vector[1], (right_cost, up_cost + 1)])
                for vector in neg_right_vectors:
                    frontier.put([vector[0], (right_cost - 1, up_cost)])
                for vector in neg_up_vectors:
                    frontier.put([vector[0], (right_cost, up_cost - 1)])
        self.relativeCoordinates = mapping
        self.normalizeRelativeCoordinates()

    def normalizeRelativeCoordinates(self, x_shift=None, y_shift=None):
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
            (x_shift, y_shift) = geom.min_tuple(self.relativeCoordinates.keys())
        elif x_shift is None:
            (x_shift, _) = geom.min_tuple(self.relativeCoordinates.keys())
        elif y_shift is None:
            (_, y_shift) = geom.min_tuple(self.relativeCoordinates.keys())
        new_mapping = {}
        if x_shift != 0 and y_shift != 0:
            keys = self.relativeCoordinates.keys()
            for key in keys:
                value = self.relativeCoordinates.pop(key)
                new_mapping[(key[0] - x_shift, key[1] - y_shift)] = value
        elif x_shift != 0:
            keys = self.relativeCoordinates.keys()
            for key in keys:
                value = self.relativeCoordinates.pop(key)
                new_mapping[(key[0] - x_shift, key[1])] = value
        elif y_shift != 0:
            keys = self.relativeCoordinates.keys()
            for key in keys:
                value = self.relativeCoordinates.pop(key)
                new_mapping[(key[0], key[1] - y_shift)] = value
        else:
            new_mapping = self.relativeCoordinates
        self.relativeCoordinates = new_mapping

    def countRectangleConnections(self, rectangle):
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
        for (x, y) in self.relativeCoordinates.keys():
            if min_x <= x <= max_x and min_y <= y <= max_y:
                circles.append(self.relativeCoordinates[(x, y)])

        nb_connection = filter(lambda (x, y): x in circles and y in circles, self.rightVectors)
        nb_connection += filter(lambda (x, y): x in circles and y in circles, self.upVectors)
        return len(nb_connection)

    def checkForGrid(self):
        (max_x, max_y) = geom.max_tuple(self.relativeCoordinates.keys())
        if max_x + 1 < self.gridShape[1] or max_y + 1 < self.gridShape[0]:
            raise self.exception
        elif max_x + 1 != self.gridShape[1] or max_y + 1 != self.gridShape[0]:
            # Rectangle too big, need to consider inner rectangles
            rectangles = geom.get_inner_rectangles([[(0, max_y), (max_x, max_y)], [(0, 0), (max_x, 0)]],
                                              self.gridShape[0], self.gridShape[1])
            max_connection = -np.infty
            max_rectangle = None
            unsure = False
            for rectangle in rectangles:
                [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = rectangle
                # Count the number of connection inside the rectangle
                nb_connection = self.countRectangleConnections(rectangle)
                if nb_connection == max_connection:
                    unsure = True
                if nb_connection > max_connection:
                    unsure = False
                    max_connection = nb_connection
                    max_rectangle = rectangle
                if unsure: # If two rectangles could be a circle grid, then we decide to reject this analysis
                    raise self.exception
            [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = max_rectangle
            # Returns the rectangle that has the more connection inside (filters the dict with the values of the rect
            new_mapping = {(x, y): v for (x, y), v in self.relativeCoordinates.iteritems()
                                                   if min_x <= x <= max_x and min_y <= y <= max_y}
            self.relativeCoordinates = new_mapping
            self.normalizeRelativeCoordinates()

    def mappingHomography(self):
        """
        Find a homography between an object and a scene, represented by two mappings with similar keys.
        Warning : keys of scene_mapping must be included in the keys of object_mapping.
        :param object_mapping: The mapping between relative coordinates and pixel coordinates of the searched object.
        :type object_mapping: dict
        :param scene_mapping: The mapping between relative coordinates and pixel coordinates of the object in the scene.
        :type scene_mapping: dict
        :return: The homography, computed by OpenCV, between the object and the scene
        :rtype: np.matrix
        """
        obj = []
        scene = []
        for key in self.circleGridMapping.keys():
            obj.append(self.referenceMapping[key])
            scene.append(self.circleGridMapping[key])
        obj = np.array(obj)
        scene = np.array(scene)
        self.homography = cv2.findHomography(obj, scene, cv2.RANSAC)[0]


    def findPerspective(self):
        """
        Use OpenCV's warpPerspective to isolate the object in the scene.
        :param homography: The homography, result of mapping_homography
        :type homography: np.matrix
        :param object_img: The image representing the object to find in the scene
        :type object_img: np.matrix
        :param scene_img: The scene in which you want to find the object
        :type scene_img: np.matrix
        :return: The scene, reshaped so only the object in the scene is visible, formatted as object_img
        """
        rows, cols, _ = self.referenceImg.shape
        if self.img is not None and self.referenceImg is not None and self.referenceMapping is not None:
            self.mappingHomography()
            self.objectPerspective =  cv2.warpPerspective(self.img, self.homography,(cols, rows),flags=cv2.WARP_INVERSE_MAP)


    def get_perspective(self):
        """
        Get the image of a specific object in a scene
        :param object_mapping: The mapping between relative coordinates and pixel coordinates of the searched object.
        :type object_mapping: dict
        :param scene_mapping: The mapping between relative coordinates and pixel coordinates of the object in the scene.
        :type scene_mapping: dict
        :param object_img: The image representing the object to find in the scene
        :type object_img: np.matrix
        :param scene_img: The scene in which you want to find the object
        :type scene_img: np.matrix
        :return: The image of the object in the scene
        :rtype: np.matrix
        """
        return self.objectPerspective