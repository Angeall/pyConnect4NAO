from Queue import Queue

import cv2
import numpy as np
from scipy.spatial import KDTree

import utils.camera.geom as geom

__author__ = 'Anthony Rouneau'


class CircleGridException(Exception):
    """
    Exception raised when there was an error while detecting a circle grid
    """
    pass


class CircleGridNotFoundException(Exception):
    """
    Exception raised when the detector detect no circle grids with the given parameters
    """
    NO_GRID = "Could not find a circle grid with the given parameters"

    def __init__(self, message=NO_GRID):
        super(CircleGridNotFoundException, self).__init__(message)


class CircleGridDetector(object):
    """
    Class used to detect a circle grid using circles detected in a picture.
    """
    def __init__(self):
        self._MIN_CIRCLES_PER_LINE = 2
        self.reference_img = None
        self.reference_mapping = None
        self._circles = None
        self._img = None
        self._grid_shape = None
        self._pixel_error_margin = None
        self._min_similar_vectors = None
        self._bounds = [0, 0, 0, 0]
        self._exception = CircleGridNotFoundException()
        self._relative_coordinates = None
        self._filtered_arc_indices = None
        self._filtered_arc_vectors = None
        self._noise_circles = []
        self._original_arc_indices = None
        self._original_arc_vectors = None
        self._circle_grid_mapping = None
        self.object_perspective = None
        self._up_vectors = None
        self._right_vectors = None
        self.homography = None

    def clear(self):
        """
        Private method: Clear the private parameters of the object
        """
        self._relative_coordinates = None
        self._filtered_arc_indices = None
        self._filtered_arc_vectors = None
        self._noise_circles = []
        self._original_arc_indices = None
        self._original_arc_vectors = None
        self._circle_grid_mapping = None
        self.object_perspective = None
        self._up_vectors = None
        self._right_vectors = None
        self.homography = None

    def runDetection(self, circles, pixel_error_margin=10., min_similar_vectors=15, img=None,
                     ref_img=None, grid_shape=None):
        """
        :param circles: The circles in which detect a circle grid
        :type circles: list
        :param pixel_error_margin: The error margin allowed to consider two vectors equal
        :type pixel_error_margin: float
        :param min_similar_vectors: The minimum number of similar vectors a considered vector must have in order
                                    to be considered as non-noise
        :type min_similar_vectors: int
        :param img: The image in which the circle grid must be detected, can be None
        :type img: numpy.ndarray
        :param ref_img: The image of reference that represents the circle grid searched, can be None
        :type ref_img: numpy.ndarray
        :param grid_shape: The shape of the grid to detect (e.g. (6, 7) for a 6x7 connect 4 board)
        :type grid_shape: tuple
        Public method.
        Runs a new detection to find a Connect 4
        """
        self.clear()
        if grid_shape is None:
            raise CircleGridException("No grid_shape set, don't know what type of grid to detect")
        if img is not None:
            bounds = (0, 0, img.shape[1] + 1, img.shape[0] + 1)
            # bounds = (0, 0, img.shape[0] + 1, img.shape[1] + 1)
        else:
            bounds = None
        self.prepareConnection(circles, bounds)
        self.connectCircles()  # Fills originalArcIndices and originalArcVectors

        self.prepareFiltering(pixel_error_margin, min_similar_vectors)
        self.doublePassFilter()  # Fills filteredArcIndices, filteredArcVectors and noiseCircles

        self.prepareBFS()
        self.bfsMarking()  # Fills relativeCoordinates

        self.prepareGrid(grid_shape)
        self.checkForGrid()

        self.reference_img = ref_img
        self._img = img

        if self.reference_mapping is not None:
            self._circle_grid_mapping = geom.index_mapping_into_pixel_mapping(self._relative_coordinates, self._circles)
            if img is not None:
                # TODO : 3D Model
                if ref_img is not None:
                    self.findPerspective()

    def getCircleGrid(self):
        """
        Public method : retrieve the circle grid mapping
        :return: A dict with relative coordinates in keys and pixel coordinates in values
                 Example : {(0, 0): (34, 43), (0, 1): (54, 43), ... }
        :rtype: dict
        """
        return self._circle_grid_mapping

    def checkInBounds(self, point):
        """
        Check if a point is included in the boundaries of the analysis
        :param point: The point to check if included in the boundaries
        """
        if point[0] < self._bounds[0]:
            return False
        elif point[1] < self._bounds[1]:
            return False
        elif point[0] > self._bounds[2]:
            return False
        elif point[1] > self._bounds[3]:
            return False
        return True

    def prepareConnection(self, circles, bounds=None):
        """
        :param circles: The circles in which a circle grid will be detected
        :type circles: list
        :param bounds: The boundaries of the image in which the circles have been detected
        :type bounds: list
        Method to call before self.connectCircles to set the object parameters properly
        """
        self._circles = circles
        for i in range(len(circles)):
            self._noise_circles.append(False)
        if bounds is None:
            tuple_max = geom.max_tuple(circles)
            tuple_min = geom.min_tuple(circles)
            # bounds = (int(tuple_min[1]), int(tuple_min[0]), int(tuple_max[1]) + 1, int(tuple_max[0]) + 1)
            bounds = (int(tuple_min[0]), int(tuple_min[1]), int(tuple_max[0]) + 1, int(tuple_max[1]) + 1)
        self._bounds = bounds

    def connectCircles(self):
        """
        Private method.
        Computes a list with connections between circle centres.
        For every couple of centres (a, b) such that a is not b:
               if there's no centre c such that ((dist(a,c) < dist(a,b)) and (dist(c, b) < dist(a, c)))
               then add the vector (a,b) to the connection with the indices of the centres a and b
        self.prepareGraph must be called before this one
        """
        keypoints = self._circles
        circles_dict = {}
        vectors_dict = {}

        subdiv = cv2.Subdiv2D()
        subdiv.initDelaunay(self._bounds)
        for i in range(len(keypoints)):
            keypoint = keypoints[i]
            if not self._noise_circles[i]:  # If the circle i is not a noisy circle
                key = (float(keypoint[0]), float(keypoint[1]))
                circles_dict[key] = i
                subdiv.insert(key)

        triangle_list = subdiv.getTriangleList()
        edge_list = subdiv.getEdgeList()
        # An edge is the coordinates of two points. 1st coordinate = (edge[0], edge[1]), 2nd = (edge[2], edge[3])
        for edge in edge_list:
            pt1 = (edge[0], edge[1])
            pt2 = (edge[2], edge[3])
            if self.checkInBounds(pt1) and self.checkInBounds(pt2):
                vectors_dict[(pt1, pt2)] = geom.vectorize(pt1, pt2)
                vectors_dict[(pt2, pt1)] = geom.vectorize(pt2, pt1)

        for triangle in triangle_list:
            pt1 = (triangle[0], triangle[1])
            pt2 = (triangle[2], triangle[3])
            pt3 = (triangle[4], triangle[5])
            if self.checkInBounds(pt1) and self.checkInBounds(pt2) and self.checkInBounds(pt3):
                dist1 = geom.point_distance(pt1, pt2)
                dist2 = geom.point_distance(pt2, pt3)
                dist3 = geom.point_distance(pt3, pt1)
                max_dist = max(dist1, dist2, dist3)
                if max_dist == dist1:
                    if (pt1, pt2) in vectors_dict and (pt2, pt1) in vectors_dict:
                        vectors_dict.pop((pt1, pt2))
                        vectors_dict.pop((pt2, pt1))
                elif max_dist == dist2:
                    if (pt2, pt3) in vectors_dict and (pt3, pt2) in vectors_dict:
                        vectors_dict.pop((pt2, pt3))
                        vectors_dict.pop((pt3, pt2))
                else:
                    if (pt1, pt3) in vectors_dict and (pt3, pt1) in vectors_dict:
                        vectors_dict.pop((pt3, pt1))
                        vectors_dict.pop((pt1, pt3))
        vectors = []
        indices = []
        for (pt1, pt2) in vectors_dict:
            vectors.append(vectors_dict[(pt1, pt2)])
            indices.append((circles_dict[pt1], circles_dict[pt2]))
        self._original_arc_vectors = vectors
        self._original_arc_indices = indices

    def prepareFiltering(self, pixel_error_margin=10., min_similar_vectors=15):
        """
        :param pixel_error_margin: The error margin allowed to consider two vector as equal
        :type pixel_error_margin: float
        :param min_similar_vectors: The minimum number of similar vector a considered vector must have to be
                                    considered as non-noise
        :type min_similar_vectors: int
        Must be called after self.connectCircles
        """
        if self._original_arc_vectors is None or self._original_arc_indices is None:
            raise CircleGridException("connectCircles must be performed before prepareFiltering")
        self._pixel_error_margin = pixel_error_margin
        self._min_similar_vectors = min_similar_vectors

    def filterConnections(self):
        """
        For every existing connection, check that there's minimum "min_similar_vectors" other vectors with the same
        values (Same value following the threshold). If it's True, keep the connection, otherwise discard it
        """
        filtered_arc_vectors = []
        filtered_arc_indices = []
        if self._min_similar_vectors > len(self._original_arc_vectors):
            raise self._exception
        if len(self._original_arc_vectors) > 0:
            space_tree = KDTree(self._original_arc_vectors)
            for j, connection in enumerate(self._original_arc_vectors):
                nearest_neighbours = space_tree.query(connection, self._min_similar_vectors)[1]
                if (geom.point_distance(connection, self._original_arc_vectors[nearest_neighbours
                                                            [(self._min_similar_vectors - 1)]])) <= self._pixel_error_margin:
                    filtered_arc_vectors.append(connection)
                    filtered_arc_indices.append(self._original_arc_indices[j])
        self._filtered_arc_vectors = filtered_arc_vectors
        self._filtered_arc_indices = filtered_arc_indices

    def doublePassFilter(self):
        """
         Goal : erase noise, then try to connect more true circle centres (by avoiding noise)
             1) Connect into a graph
             2) Filter it
             3) Remove every centre that is not linked with another centre after 2)
             4) Re-connect couple of centres, ignoring the centers removed in 3) and re-filter
        """
        self.filterConnections()
        centers_to_remove = []
        for i in range(len(self._circles)):
            centers_to_remove.append(True)
        for (center1, center2) in self._filtered_arc_indices:
            if centers_to_remove[center1]:  # If the node was assumed as noisy, we set it as non-noisy
                centers_to_remove[center1] = False
            if centers_to_remove[center2]:  # If the node was assumed as noisy, we set it as non-noisy
                centers_to_remove[center2] = False
        # Second pass into the filters with a set of circles detected as noise
        self._noise_circles = centers_to_remove
        self.connectCircles()
        self.filterConnections()

    def filterRightUpVectors(self):
        """
        Private method.
        Computes vectors belonging to the cluster right and the cluster up
        Sets self.upVectors and self.rightVectors lists of index couples that forms vectors belonging
                 either to the "up" or the "right" cluster.
        """
        if len(self._filtered_arc_vectors) == 0:
            raise self._exception
        clustering = geom.cluster_vectors(self._filtered_arc_vectors)
        clusters_centroids = clustering[2]
        max_x = (-np.infty, None)
        min_y = (np.infty, None)
        for i in range(len(clusters_centroids)):
            centroid = clusters_centroids[i]
            if centroid[0] > max_x[0]:
                max_x = (centroid[0], i)
            if centroid[1] < min_y[0]:
                min_y = (centroid[1], i)
        x = max_x[1]
        y = min_y[1]
        belongs_to_cluster = clustering[1]
        right_vectors = []
        up_vectors = []
        for index, cluster in enumerate(belongs_to_cluster):
            if cluster == x:
                right_vectors.append(self._filtered_arc_indices[index])
            if cluster == y:
                up_vectors.append(self._filtered_arc_indices[index])
        self._up_vectors = up_vectors
        self._right_vectors = right_vectors

    def prepareBFS(self):
        if self._filtered_arc_indices is None or self._filtered_arc_vectors is None or self._circles is None:
            raise CircleGridException("filtering must be performed before prepareBFS")
        self.filterRightUpVectors()

    def bfsMarking(self):
        """
        Private method.
        Must execute prepareBFS first.
        Explore circle centres as a graph using vectors (filtered before) marking
        with relative positions.
        Use Breadth First Search.
        """
        frontier = Queue()  # Contains nodes and position of node
        start_node = 0
        while self._noise_circles[start_node]:
            start_node += 1
        frontier.put([start_node, (0, 0)])
        adj_right_dict = {}
        adj_up_dict = {}
        mapping = {}
        explored = []

        for i in range(len(self._circles)):
            explored.append(False)

        for (x, y) in self._right_vectors:
            if x in adj_right_dict:
                adj_right_dict[x][0].append((x, y))
            else:
                adj_right_dict[x] = [[(x, y)], []]
                adj_up_dict[x] = [[], []]
            if y in adj_right_dict:
                adj_right_dict[y][1].append((x, y))
            else:
                adj_right_dict[y] = [[], [(x, y)]]
                adj_up_dict[y] = [[], []]

        for (x, y) in self._up_vectors:
            if x in adj_up_dict:
                adj_up_dict[x][0].append((x, y))
            else:
                adj_up_dict[x] = [[(x, y)], []]
                if x not in adj_right_dict:
                    adj_right_dict[x] = [[], []]
            if y in adj_up_dict:
                adj_up_dict[y][1].append((x, y))
            else:
                adj_up_dict[y] = [[], [(x, y)]]
                if y not in adj_right_dict:
                    adj_right_dict[y] = [[], []]
        if start_node not in adj_right_dict:
            self._relative_coordinates = {(0, 0): start_node}
            return

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
        self._relative_coordinates = mapping
        self.normalizeRelativeCoordinates()

    def normalizeRelativeCoordinates(self, x_shift=None, y_shift=None):
        """
        :param x_shift: The shift to apply to the X axis
        :type x_shift: int
        :param y_shift: The shift to apply to the Y axis
        :type y_shift: int
        Shift a mapping so that all values of the mapping are shifted by x_shift and y_shift.
        If x_shift is None, The lowest x value will be 0 and other x values are adapted in consequence.
        If y_shift is None, The lowest y value will be 0 and other y values are adapted in consequence.
        """
        if x_shift is None and y_shift is None:
            (x_shift, y_shift) = geom.min_tuple(self._relative_coordinates.keys())
        elif x_shift is None:
            (x_shift, _) = geom.min_tuple(self._relative_coordinates.keys())
        elif y_shift is None:
            (_, y_shift) = geom.min_tuple(self._relative_coordinates.keys())
        new_mapping = {}
        if x_shift != 0 and y_shift != 0:
            keys = self._relative_coordinates.keys()
            for key in keys:
                value = self._relative_coordinates.pop(key)
                new_mapping[(key[0] - x_shift, key[1] - y_shift)] = value
        elif x_shift != 0:
            keys = self._relative_coordinates.keys()
            for key in keys:
                value = self._relative_coordinates.pop(key)
                new_mapping[(key[0] - x_shift, key[1])] = value
        elif y_shift != 0:
            keys = self._relative_coordinates.keys()
            for key in keys:
                value = self._relative_coordinates.pop(key)
                new_mapping[(key[0], key[1] - y_shift)] = value
        else:
            new_mapping = self._relative_coordinates
        self._relative_coordinates = new_mapping

    def countRectangleConnections(self, rectangle):
        """
        :param rectangle: The rectangle to consider in the grid.
                          A rectangle is [[(coord_up_left), (coord_up_right)], [(coord_down_left), (coord_down_right)]]
        :type rectangle: list
        Count the keypoints connections inside a rectangle in the grid.
        """
        lines_counter = {}  # Will assure that the top and the bottom lines have at least MIN_CIRCLES_PER_LINE circles
        [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = rectangle
        circles = []
        for (x, y) in self._relative_coordinates.keys():
            if min_x <= x <= max_x and min_y <= y <= max_y:
                circles.append(self._relative_coordinates[(x, y)])
                lines_counter[y] = lines_counter.get(x, 0) + 1
        if lines_counter[max(lines_counter.keys())] < self._MIN_CIRCLES_PER_LINE \
                or lines_counter[min(lines_counter.keys())] < self._MIN_CIRCLES_PER_LINE:
            return -1

        nb_connection = filter(lambda (x0, y0): x0 in circles and y0 in circles, self._right_vectors)
        nb_connection += filter(lambda (x1, y1): x1 in circles and y1 in circles, self._up_vectors)
        return len(nb_connection)

    def prepareGrid(self, grid_shape):
        """
        :param grid_shape: the shape of the grid to detect
        :type grid_shape: tuple
        """
        if self._relative_coordinates is None or self._right_vectors is None or self._up_vectors is None:
            raise CircleGridException("prepareBFS and bfsMarking must be called before prepareForGrid")
        self._grid_shape = grid_shape

    def checkForGrid(self):
        """
        Checks for a grid inside a mapping done with bfsMarking.
        bfsMarking can detect multiple possible grids, this method will check if there is at least one possible grid.

        It will also decide, in the case of multiple possible grids, which grid is the good one by counting the
          number of vectors detected earlier inside the grid (the bigger amount of vectors, the better the grid)
        """
        (max_x, max_y) = geom.max_tuple(self._relative_coordinates.keys())
        if max_x + 1 < self._grid_shape[1] or max_y + 1 < self._grid_shape[0]:
            raise self._exception
        elif max_x + 1 != self._grid_shape[1] or max_y + 1 != self._grid_shape[0]:
            # Rectangle too big, need to consider inner _rectangles
            rectangles = geom.get_inner_rectangles([[(0, max_y), (max_x, max_y)], [(0, 0), (max_x, 0)]],
                                                   self._grid_shape[0], self._grid_shape[1])
            max_connection = -np.infty
            max_rectangle = None
            unsure = False
            for rectangle in rectangles:
                [[(_, _), (max_x, _)], [(_, min_y), (_, _)]] = rectangle
                # Count the number of connection inside the rectangle
                nb_connection = self.countRectangleConnections(rectangle)
                if nb_connection == max_connection:
                    unsure = True
                elif nb_connection > max_connection and nb_connection != -1:
                    unsure = False
                    max_connection = nb_connection
                    max_rectangle = rectangle
            # If two _rectangles could be a circle grid or no correct rectangle was found,
            #   then we decide to reject this analysis
            if unsure or max_rectangle is None:
                raise self._exception
            [[(min_x, max_y), (max_x, _)], [(_, min_y), (_, _)]] = max_rectangle
            # Returns the rectangle that has the more connection inside (filters the dict with the values of the rect)
            new_mapping = {(x, y): v for (x, y), v in self._relative_coordinates.iteritems()
                           if min_x <= x <= max_x and min_y <= y <= max_y}
            self._relative_coordinates = new_mapping
            self.normalizeRelativeCoordinates()

    def mappingHomography(self):
        """
        Find a homography between an object and a scene, represented by two mappings with similar keys.
        /!\ Warning /!\ keys of scene_mapping must be included in the keys of object_mapping.
        """
        obj = []
        scene = []
        for key in self._circle_grid_mapping.keys():
            obj.append(self.reference_mapping[key])
            scene.append(self._circle_grid_mapping[key])
        obj = np.array(obj)
        scene = np.array(scene)
        self.homography = cv2.findHomography(obj, scene, cv2.LMEDS)[0]

    def match3DModel(self, camera_matrix, camera_dist):
        # Need to define 3D _model in subclass
        return None

    def findPerspective(self):
        """
        Use OpenCV's warpPerspective to isolate the object in the scene.

        Sets self.objectPerspective to the scene image, reshaped and transformed so that
        only the object in the scene is visible, formatted as object_img
        """
        rows, cols, _ = self.reference_img.shape
        self.mappingHomography()
        self.object_perspective = cv2.warpPerspective(self._img, self.homography, (cols, rows),
                                                      flags=cv2.WARP_INVERSE_MAP)
        # for i in self.reference_mapping.values():
        #     cv2.circle(self.object_perspective, (i[0], i[1]), 2, (0, 0, 255), 2)

    def getPerspective(self):
        """
        Get an image cropped and transformed of a specific object in a scene image
        """
        return self.object_perspective
