__author__ = 'Angeall'
import unittest

from camera.gameboard.connect4detector import *
from utils.geom import *


class DetectionTestCase(unittest.TestCase):
    def setUp(self):
        def create_connect4(x_dist=65, y_dist=55, max_x_error=10, max_y_error=8, hor=7, vert=6):
            connect4 = []
            current_x = 0
            current_y = 0
            for i in range(vert):
                for j in range(hor):
                    error_x = random.random() * max_x_error
                    error_y = random.random() * max_y_error
                    connect4.append((round(current_x + error_x, 2), round(current_y + error_y, 2)))
                    current_x += x_dist
                current_y += y_dist
                current_x = 0
            # random.shuffle(gameboard)
            return connect4

        # OK 7x8 rectangle
        self.rectangle_0 = [[(2, 7), (9, 7)], [(2, 1), (9, 1)]]
        # OK 6x7 rectangle
        self.rectangle_1 = [[(3, 5), (9, 5)], [(3, 0), (9, 0)]]
        # OK 6x9 rectangle
        self.rectangle_2 = [[(1, 5), (9, 5)], [(1, 0), (9, 0)]]
        # OK 8x7 rectangle
        self.rectangle_3 = [[(3, 8), (9, 8)], [(3, 1), (9, 1)]]
        # Not a rectangle... x components : 0, 1, 7
        self.rectangle_4 = [[(1, 10), (7, 10)], [(0, 2), (7, 2)]]
        # Not a rectangle... y components : 2, 10, 11
        self.rectangle_5 = [[(0, 11), (7, 10)], [(0, 2), (7, 2)]]
        # Not a rectangle... x components : 0, 1, 7
        self.rectangle_6 = [[(0, 10), (7, 10)], [(1, 2), (7, 2)]]
        # Not a rectangle... y components : 2, 3, 10
        self.rectangle_7 = [[(0, 10), (7, 10)], [(0, 2), (7, 3)]]

        # Almost perfect circle grid (no circle missing, no noise)
        self.circles_0 = [(0, 0), (5, 0), (5, 8), (10, 4), (10, 8),
                          (10, 0), (0, 4), (0, 8), (5, 4)]
        # Minimum circles so it can detect a 3x3 grid
        self.circles_1 = [(25, 40), (50, 20), (50, 0), (0, 40), (25, 20)]

        # Noise added to self.circles_1. The first element is isolated by noise so it'll be lost by filtering
        self.circles_2 = [(25, 40), (50, 20), (50, 0), (0, 40),
                          (25, 20), (10, 42), (25, 25), (0, 20)]

        # Noise removed from self.circles_2. The first element is no more isolated by noise.
        self.circles_3 = [(5, 8), (10, 4), (10, 0), (0, 8),
                          (5, 4), (5, 5), (0, 4)]

        # Almost perfect Connect 4 (no circle missing, no noise)
        self.connect4_0 = [(331, 165), (267, 225), (5, 226), (73, 59), (8, 166),
                           (202, 61), (3, 3), (197, 276), (198, 226), (71, 281),
                           (135, 222), (268, 1), (1, 115), (391, 59), (71, 170),
                           (332, 222), (267, 62), (139, 58), (329, 5), (130, 171),
                           (69, 228), (199, 114), (329, 276), (397, 227), (327, 112),
                           (398, 6), (267, 282), (391, 165), (260, 115), (134, 278),
                           (9, 56), (5, 278), (329, 58), (391, 281), (199, 6),
                           (196, 171), (266, 172), (139, 7), (65, 5), (393, 111),
                           (132, 115), (67, 110)]
        # """"""""Worst case"""""""""
        # Connect 4 with 3 of the 4 corners missing, some internal circles missing,
        # some internal noise, some external noise
        self.connect4_1 = [(-71, 6),  # Noise before first node (-1, 0)
                           (7, -60),  # Noise before first node (0, -1)
                           (8, 3), (74, 3), (134, 8),
                           (161, 4),  # Noise between (2, 0) and (3, 0)
                           # (200.01, 0.95),  (3, 0) missing
                           (263, 2),
                           # (328.74, 5.82), (5, 0) missing
                           # (396.51, 7.67), (6, 0) missing
                           (3, 55), (74, 56),
                           # (134.77, 62.91), (2, 1) missing
                           (202, 57),
                           # (262.29, 62.02), (4, 1) missing
                           (333, 56), (394, 59),
                           (391, 84),  # Noise between (6, 1) and (6, 2)
                           # (6.75, 114.49), (0, 2) missing
                           (69, 112), (133, 114), (201, 113), (269, 113),
                           (263, 140),  # Noise between (4, 2) and (4, 3)
                           (331, 113),
                           # (399.9, 114.83), (6, 2) missing
                           (0, 172),
                           (1, 193),  # Noise between (0, 3) and (0, 4)
                           (100, 151),  # Noise in the middle of (1, 2), (2, 2), (1, 3), (2, 3)
                           # (69.1, 172.5), (1, 3)  missing
                           (137, 171),
                           (199, 168),
                           (204, 201),  # Noise between (3, 3) and (3, 4)
                           # (262.98, 172.59), (4, 3) missing
                           (328, 169),
                           # (395.7, 165.24), (6, 3) missing
                           (10, 225),
                           # (65.64, 225.93),
                           (102, 215),  # Noise between (1, 4) and (2, 4)
                           (135, 222), (204, 223),
                           # (267.24, 224.12), (4, 4) missing
                           (334, 226), (391, 225),
                           # (4.83, 282.79), (0, 5) missing
                           (3, 326),  # Noise above (0, 5)
                           (69, 275),
                           # (136.19, 280.97), (203.95, 275.62), (2, 5) and (3, 5) missing
                           (265, 280),
                           (260, 320),  # Noise above (4, 5)
                           (327, 280),
                           (390, 278),
                           (390, 322)]  # Noise above (6, 5)
        tuple_min = min_tuple(self.connect4_1)
        temp = []
        for (x, y) in self.connect4_1:
            x0 = x - tuple_min[0]
            y0 = y - tuple_min[1]
            temp.append((x0, y0))
        self.connect4_1 = temp
        self.c4Detector = Connect4Detector()
        self.circleGridDetector = CircleGridDetector()

    def test_vectorize1(self):
        expected = (5.55, 6.56)
        v1 = (18.2, 60.74)
        v2 = (23.75, 67.3)
        result = vectorize(v1, v2)
        self.assertAlmostEqual(expected[0], result[0])
        self.assertAlmostEqual(expected[1], result[1])

    def test_vectorize2(self):
        expected = (5.55, -4.36)
        v1 = (18.2, 60.74)
        v2 = (23.75, 56.38)
        result = vectorize(v1, v2)
        self.assertAlmostEqual(expected[0], result[0])
        self.assertAlmostEqual(expected[1], result[1])

    def test_vectorize3(self):
        expected = (-3.45, 6.56)
        v1 = (18.2, 60.74)
        v2 = (14.75, 67.3)
        result = vectorize(v1, v2)
        self.assertAlmostEqual(expected[0], result[0])
        self.assertAlmostEqual(expected[1], result[1])

    def test_vectorize4(self):
        expected = (-3.0, -7.9)
        v1 = (18.2, 60.74)
        v2 = (15.2, 52.84)
        result = vectorize(v1, v2)
        self.assertAlmostEqual(expected[0], result[0])
        self.assertAlmostEqual(expected[1], result[1])

    def test_connect_keypoints_perfect(self):
        grid = self.circles_0
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        result = self.circleGridDetector.originalArcIndices
        expected_1 = [(7, 2), (2, 7), (2, 4), (4, 2), (6, 8), (8, 6), (8, 3), (3, 8), (0, 1), (1, 0), (1, 5), (5, 1),
                      (7, 6), (6, 7), (6, 0), (0, 6), (2, 8), (8, 2), (8, 1), (1, 8), (4, 3), (3, 4), (3, 5), (5, 3)]
        self.assertItemsEqual(result, expected_1)

    def test_connect_keypoints_missing(self):
        grid = self.circles_1
        expected_1 = [(3, 0), (0, 3), (0, 4), (4, 0), (4, 1), (1, 4), (1, 2), (2, 1)]
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        result = self.circleGridDetector.originalArcIndices
        self.assertItemsEqual(result, expected_1)

    def test_connect_keypoints_missing_noise(self):
        grid = self.circles_2
        expected_1 = [(3, 5), (5, 3), (0, 6), (6, 0), (4, 1), (1, 4), (1, 2), (2, 1),
                      (5, 0), (0, 5), (6, 4), (4, 6), (3, 7), (7, 3), (7, 4), (4, 7)]
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        result = self.circleGridDetector.originalArcIndices
        self.assertItemsEqual(result, expected_1)

    def test_filter_connection_perfect(self):
        grid = self.circles_0
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.33, min_similar_vectors=4)
        self.circleGridDetector.filterConnections()
        expected = self.circleGridDetector.originalArcIndices
        result = self.circleGridDetector.filteredArcIndices
        self.assertItemsEqual(result, expected)

    def test_filter_connection_missing(self):
        grid = self.circles_1
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.33, min_similar_vectors=2)
        self.circleGridDetector.filterConnections()
        expected = self.circleGridDetector.originalArcIndices
        result = self.circleGridDetector.filteredArcIndices
        self.assertItemsEqual(result, expected)

    def test_filter_connection_missing_noise(self):
        grid = self.circles_2
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=1., min_similar_vectors=2)
        self.circleGridDetector.filterConnections()
        expected = self.circleGridDetector.originalArcIndices
        result = self.circleGridDetector.filteredArcIndices
        expected.remove((0, 6))
        expected.remove((6, 0))
        expected.remove((6, 4))
        expected.remove((4, 6))
        expected.remove((3, 5))
        expected.remove((5, 3))
        expected.remove((5, 0))
        expected.remove((0, 5))
        self.assertItemsEqual(result, expected)

    def test_filter_up_right_perfect(self):
        grid = self.circles_0
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.1, min_similar_vectors=2)
        self.circleGridDetector.filterConnections()
        self.circleGridDetector.filterRightUpVectors()
        result = [self.circleGridDetector.rightVectors, self.circleGridDetector.upVectors]
        expected = [[(7, 2), (2, 4), (6, 8), (8, 3), (0, 1), (1, 5)], [(0, 6), (6, 7), (1, 8), (8, 2), (5, 3), (3, 4)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_filter_up_right_missing(self):
        grid = self.circles_1
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.1, min_similar_vectors=2)
        self.circleGridDetector.filterConnections()
        self.circleGridDetector.filterRightUpVectors()
        result = [self.circleGridDetector.rightVectors, self.circleGridDetector.upVectors]
        expected = [[(3, 0), (4, 1)], [(4, 0), (2, 1)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_filter_up_right_missing_noise(self):
        grid = self.circles_2
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.1, min_similar_vectors=2)
        self.circleGridDetector.filterConnections()
        self.circleGridDetector.filterRightUpVectors()
        result = [self.circleGridDetector.rightVectors, self.circleGridDetector.upVectors]
        expected = [[(7, 4), (4, 1)], [(7, 3), (2, 1)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_double_pass_filter_isolated_node(self):
        grid = self.circles_2
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.22, min_similar_vectors=2)
        self.circleGridDetector.doublePassFilter()
        result = self.circleGridDetector.filteredArcIndices
        expected = [(3, 7), (7, 3), (4, 1), (1, 4), (1, 2), (2, 1), (4, 7), (7, 4)]
        self.assertItemsEqual(expected, result)

    def test_double_pass_filter_recovering_noised(self):
        grid = self.circles_3
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0, min_similar_vectors=2)
        self.circleGridDetector.doublePassFilter()
        result = self.circleGridDetector.filteredArcIndices
        expected = [(3, 6), (6, 3), (3, 0), (0, 3), (0, 4), (4, 0), (4, 1), (1, 4), (1, 2), (2, 1), (4, 6), (6, 4)]
        self.assertItemsEqual(expected, result)

    def test_bfs_marking_perfect(self):
        grid = self.circles_0
        expected = {(0, 0): 0,
                    (0, 1): 6,
                    (0, 2): 7,
                    (1, 0): 1,
                    (1, 1): 8,
                    (1, 2): 2,
                    (2, 0): 5,
                    (2, 1): 3,
                    (2, 2): 4}
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.22, min_similar_vectors=2)
        self.circleGridDetector.doublePassFilter()
        self.circleGridDetector.prepareBFS()
        self.circleGridDetector.bfsMarking()
        result = self.circleGridDetector.relativeCoordinates
        self.assertDictEqual(expected, result)

    def test_bfs_marking_missing(self):
        grid = self.circles_1
        expected = {(0, 2): 3,
                    (1, 1): 4,
                    (1, 2): 0,
                    (2, 0): 2,
                    (2, 1): 1}
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=1, min_similar_vectors=2)
        self.circleGridDetector.doublePassFilter()
        self.circleGridDetector.prepareBFS()
        self.circleGridDetector.bfsMarking()
        result = self.circleGridDetector.relativeCoordinates
        self.assertDictEqual(expected, result)

    def test_bfs_marking_missing_noise(self):
        grid = self.circles_2
        expected = {(0, 2): 3,
                    (1, 1): 4,
                    (2, 0): 2,
                    (0, 1): 7,
                    (2, 1): 1}
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.22, min_similar_vectors=2)
        self.circleGridDetector.doublePassFilter()
        self.circleGridDetector.prepareBFS()
        self.circleGridDetector.bfsMarking()
        result = self.circleGridDetector.relativeCoordinates
        # isolated nodes, not linked with the rest of the grid
        # 0 included, isolated because of noise
        self.assertDictEqual(expected, result)

    def test_bfs_marking_recovered_noise(self):
        grid = self.circles_3
        expected = {(0, 2): 3,
                    (1, 1): 4,
                    (2, 0): 2,
                    (0, 1): 6,
                    (1, 2): 0,
                    (2, 1): 1}
        self.circleGridDetector.prepareConnection(grid)
        self.circleGridDetector.connectCircles()
        self.circleGridDetector.prepareFiltering(pixel_error_margin=0.22, min_similar_vectors=2)
        self.circleGridDetector.doublePassFilter()
        self.circleGridDetector.prepareBFS()
        self.circleGridDetector.bfsMarking()
        result = self.circleGridDetector.relativeCoordinates
        self.assertDictEqual(expected, result)

    def test_get_inner_rectangles_OK1(self):
        rectangle = self.rectangle_0
        expected = [[[(2, 6), (8, 6)], [(2, 1), (8, 1)]],
                    [[(2, 7), (8, 7)], [(2, 2), (8, 2)]],
                    [[(3, 6), (9, 6)], [(3, 1), (9, 1)]],
                    [[(3, 7), (9, 7)], [(3, 2), (9, 2)]]]
        result = get_inner_rectangles(rectangle, 6, 7)
        self.assertTrue(result == expected)

    def test_get_inner_rectangles_OK2(self):
        rectangle = self.rectangle_1
        expected = rectangle
        result = get_inner_rectangles(rectangle, 6, 7)
        self.assertTrue(result == expected)

    def test_get_inner_rectangles_OK3(self):
        rectangle = self.rectangle_2
        expected = [[[(1, 5), (7, 5)], [(1, 0), (7, 0)]],
                    [[(2, 5), (8, 5)], [(2, 0), (8, 0)]],
                    [[(3, 5), (9, 5)], [(3, 0), (9, 0)]]]
        result = get_inner_rectangles(rectangle, 6, 7)
        self.assertTrue(result == expected)

    def test_get_inner_rectangles_OK4(self):
        rectangle = self.rectangle_3
        expected = [[[(3, 6), (9, 6)], [(3, 1), (9, 1)]],
                    [[(3, 7), (9, 7)], [(3, 2), (9, 2)]],
                    [[(3, 8), (9, 8)], [(3, 3), (9, 3)]]]
        result = get_inner_rectangles(rectangle, 6, 7)
        self.assertTrue(result == expected)

    def test_get_inner_rectangles_Error1(self):
        rectangle = self.rectangle_4
        self.assertRaises(AssertionError, get_inner_rectangles, rectangle, 6, 7)

    def test_get_inner_rectangles_Error2(self):
        rectangle = self.rectangle_5
        self.assertRaises(AssertionError, get_inner_rectangles, rectangle, 6, 7)

    def test_get_inner_rectangles_Error3(self):
        rectangle = self.rectangle_6
        self.assertRaises(AssertionError, get_inner_rectangles, rectangle, 6, 7)

    def test_get_inner_rectangles_Error4(self):
        rectangle = self.rectangle_7
        self.assertRaises(AssertionError, get_inner_rectangles, rectangle, 6, 7)

    def test_detect_grid_perfect(self):
        connect4 = self.connect4_0
        self.c4Detector.runDetection(connect4, pixel_error_margin=20., min_similar_vectors=15)
        result = self.c4Detector.relativeCoordinates
        self.assertTrue(len(result) == 42)

    def test_detect_grid_worst(self):
        connect4 = self.connect4_1
        expected = {(0, 0): 2, (1, 0): 3, (2, 0): 4, (0, 1): 7, (1, 1): 8, (3, 1): 9, (5, 1): 10, (6, 1): 11,
                    (1, 2): 13, (2, 2): 14, (3, 2): 15, (4, 2): 16, (5, 2): 18, (2, 3): 22, (3, 3): 23, (5, 3): 25,
                    (2, 4): 28, (3, 4): 29, (5, 4): 30, (6, 4): 31, (4, 5): 34, (5, 5): 36, (6, 5): 37, }
        self.c4Detector.runDetection(connect4, pixel_error_margin=15., min_similar_vectors=8)
        result = self.c4Detector.relativeCoordinates
        self.assertDictEqual(expected, result)
