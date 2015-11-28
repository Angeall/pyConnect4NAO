__author__ = 'Angeall'
import unittest
import random

from src.connect4.generic.grid_detection import *


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
            # random.shuffle(connect4)
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
        self.circles_0 = [(0.17, 0.02), (5.08, 0.02), (5.03, 8.07), (10.0, 4.05), (10.05, 8.15),
                          (10.07, 0.14), (0.19, 4.05), (0.12, 8.01), (5.17, 4.03)]
        # Minimum circles so it can detect a 3x3 grid
        self.circles_1 = [(25.13, 40.07), (50.0, 20.05), (50.07, 0.14), (0.08, 40.01), (25.1, 20.03)]

        # Noise added to self.circles_1. The first element is isolated by noise so it'll be lost by filtering
        self.circles_2 = [(25.13, 40.07), (50.0, 20.05), (50.07, 0.14), (0.08, 40.01),
                          (25.1, 20.03), (10.55, 42.27), (25.2, 25.1), (0.0, 20.05)]

        # Noise removed from self.circles_2. The first element is no more isolated by noise.
        self.circles_3 = [(5.03, 8.07), (10.0, 4.05), (10.07, 0.14), (0.12, 8.01),
                          (5.17, 4.03), (5.2, 5.1), (0.19, 4.05)]

        # Almost perfect Connect 4 (no circle missing, no noise)
        self.connect4_0 = [(330.66, 165.03), (266.84, 225.23), (4.6, 226.29), (73.39, 59.45), (7.79, 165.74),
                           (201.78, 60.89), (2.61, 3.37), (196.68, 275.65), (197.82, 226.24), (70.96, 280.53),
                           (135.23, 221.59), (267.73, 0.85), (0.93, 114.89), (390.74, 59.43), (71.21, 170.33),
                           (332.35, 221.58), (266.7, 62.37), (139.13, 57.53), (328.62, 5.36), (130.34, 171.42),
                           (69.13, 227.69), (198.77, 113.6), (329.04, 276.01), (396.99, 226.91), (327.23, 112.14),
                           (398.36, 5.63), (269.9, 282.73), (391.38, 165.25), (260.13, 114.8), (134.3, 278.42),
                           (8.84, 55.79), (4.87, 278.25), (329.02, 57.58), (390.68, 280.72), (198.86, 6.29),
                           (196.09, 171.47), (265.92, 171.95), (139.39, 6.92), (65.11, 4.72), (393.43, 111.35),
                           (132.36, 115.35), (66.61, 110.04)]
        # """"""""Worst case"""""""""
        # Connect 4 with 3 of the 4 corners missing, some internal circles missing,
        # some internal noise, some external noise
        self.connect4_1 = [(-70.5, 5.97),  # Noise before first node (-1, 0)
                           (7.45, -60.43),  # Noise before first node (0, -1)
                           (8.48, 3.02), (73.67, 2.93), (133.65, 7.65),
                           (160.56, 4.34),  # Noise between (2, 0) and (3, 0)
                           # (200.01, 0.95),  (3, 0) missing
                           (263.12, 1.86),
                           # (328.74, 5.82), (5, 0) missing
                           # (396.51, 7.67), (6, 0) missing
                           (3.11, 55.43), (73.8, 55.55),
                           # (134.77, 62.91), (2, 1) missing
                           (201.69, 56.76),
                           # (262.29, 62.02), (4, 1) missing
                           (332.82, 56.07), (393.96, 58.76),
                           (390.56, 84.45),  # Noise between (6, 1) and (6, 2)
                           # (6.75, 114.49), (0, 2) missing
                           (68.63, 111.92), (133.2, 114.14), (200.58, 113.48), (268.53, 112.87),
                           (263.33, 140.23),  # Noise between (4, 2) and (4, 3)
                           (330.65, 113.21),
                           # (399.9, 114.83), (6, 2) missing
                           (0.01, 172.41),
                           (1.32, 193.34),  # Noise between (0, 3) and (0, 4)
                           (100.01, 150.54),  # Noise in the middle of (1, 2), (2, 2), (1, 3), (2, 3)
                           # (69.1, 172.5), (1, 3)  missing
                           (137.36, 170.85),
                           (199.36, 168.43),
                           (204.12, 201.32),  # Noise between (3, 3) and (3, 4)
                           # (262.98, 172.59), (4, 3) missing
                           (328.45, 169.21),
                           # (395.7, 165.24), (6, 3) missing
                           (9.76, 225.48),
                           # (65.64, 225.93),
                           (102.34, 215.32),  # Noise between (1, 4) and (2, 4)
                           (135.31, 221.72), (203.58, 223.27),
                           # (267.24, 224.12), (4, 4) missing
                           (333.64, 226.46), (390.62, 224.74),
                           # (4.83, 282.79), (0, 5) missing
                           (3.43, 325.65),  # Noise above (0, 5)
                           (68.78, 275.11),
                           # (136.19, 280.97), (203.95, 275.62), (2, 5) and (3, 5) missing
                           (264.9, 279.95),
                           (260.4, 320.12),  # Noise above (4, 5)
                           (326.56, 279.72),
                           (390.34, 277.86),
                           (390.12, 322.45)]  # Noise above (6, 5)

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
        expected_1 = [(7, 2), (2, 7), (2, 4), (4, 2), (6, 8), (8, 6), (8, 3), (3, 8), (0, 1), (1, 0), (1, 5), (5, 1),
                      (7, 6), (6, 7), (6, 0), (0, 6), (2, 8), (8, 2), (8, 1), (1, 8), (4, 3), (3, 4), (3, 5), (5, 3)]
        expected_0 = []
        for (i, j) in expected_1:
            expected_0.append(vectorize(grid[i], grid[j]))
        result = connect_keypoints(grid)
        self.assertItemsEqual(result[1], expected_1)
        self.assertItemsEqual(result[0], expected_0)

    def test_connect_keypoints_missing(self):
        grid = self.circles_1
        expected_1 = [(3, 0), (0, 3), (0, 4), (4, 0), (4, 1), (1, 4), (1, 2), (2, 1)]
        expected_0 = []
        for (i, j) in expected_1:
            expected_0.append(vectorize(grid[i], grid[j]))
        result = connect_keypoints(grid)
        self.assertItemsEqual(result[1], expected_1)
        self.assertItemsEqual(result[0], expected_0)

    def test_connect_keypoints_missing_noise(self):
        grid = self.circles_2
        expected_1 = [(3, 5), (5, 3), (0, 6), (6, 0), (4, 1), (1, 4), (1, 2), (2, 1),
                      (5, 0), (0, 5), (6, 4), (4, 6), (3, 7), (7, 3), (7, 4), (4, 7)]
        expected_0 = []
        for (i, j) in expected_1:
            expected_0.append(vectorize(grid[i], grid[j]))
        result = connect_keypoints(grid)
        self.assertItemsEqual(result[1], expected_1)
        self.assertItemsEqual(result[0], expected_0)

    def test_filter_connection_perfect(self):
        grid = self.circles_0
        connections = connect_keypoints(grid)
        expected = connections[1]
        result = filter_connections(connections, pixel_threshold=0.33, min_similar_vectors=4)[1]
        self.assertItemsEqual(result, expected)

    def test_filter_connection_missing(self):
        grid = self.circles_1
        connections = connect_keypoints(grid)
        expected = connections[1]
        result = filter_connections(connections, pixel_threshold=0.33, min_similar_vectors=2)[1]
        self.assertItemsEqual(result, expected)

    def test_filter_connection_missing_noise(self):
        grid = self.circles_2
        connections = connect_keypoints(grid)
        result = filter_connections(connections, pixel_threshold=1., min_similar_vectors=2)[1]
        expected = connections[1]
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
        filtered_connections = filter_connections(connect_keypoints(grid), pixel_threshold=0.33, min_similar_vectors=2)
        result = filter_right_up_vectors(filtered_connections)
        expected = [[(7, 2), (2, 4), (6, 8), (8, 3), (0, 1), (1, 5)], [(0, 6), (6, 7), (1, 8), (8, 2), (5, 3), (3, 4)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_filter_up_right_missing(self):
        grid = self.circles_1
        filtered_connections = filter_connections(connect_keypoints(grid), pixel_threshold=0.33, min_similar_vectors=2)
        result = filter_right_up_vectors(filtered_connections)
        expected = [[(3, 0), (4, 1)], [(4, 0), (2, 1)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_filter_up_right_missing_noise(self):
        grid = self.circles_2
        filtered_connections = filter_connections(connect_keypoints(grid), pixel_threshold=1., min_similar_vectors=2)
        result = filter_right_up_vectors(filtered_connections)
        expected = [[(7, 4), (4, 1)], [(7, 3), (2, 1)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_double_pass_filter_isolated_node(self):
        grid = self.circles_2
        result = double_pass_filter(grid, pixel_threshold=0.22, min_similar_vectors=2)[1]
        expected = [(3, 7), (7, 3), (4, 1), (1, 4), (1, 2), (2, 1), (4, 7), (7, 4)]
        self.assertItemsEqual(expected, result)

    def test_double_pass_filter_recovering_noised(self):
        grid = self.circles_3
        result = double_pass_filter(grid, pixel_threshold=0.22, min_similar_vectors=2)[1]
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
        for start_node in range(len(grid)):
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=0.33, min_similar_vectors=2)),
                                 start_node)

            self.assertDictEqual(expected, result)

    def test_bfs_marking_missing(self):
        grid = self.circles_1
        expected = {(0, 2): 3,
                    (1, 1): 4,
                    (1, 2): 0,
                    (2, 0): 2,
                    (2, 1): 1}
        for start_node in range(len(grid)):
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=1., min_similar_vectors=2)),
                                 start_node)

            self.assertDictEqual(expected, result)

    def test_bfs_marking_missing_noise(self):
        grid = self.circles_2
        expected = {(0, 2): 3,
                    (1, 1): 4,
                    (2, 0): 2,
                    (0, 1): 7,
                    (2, 1): 1}
        for start_node in range(len(grid)):
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=0.33, min_similar_vectors=2)),
                                 start_node)
            # isolated nodes, not linked with the rest of the grid
            # 0 included, isolated because of noise
            if start_node == 0 or start_node == 5 or start_node == 6:
                self.assertDictEqual(result, {(0, 0): start_node})
            else:
                self.assertDictEqual(expected, result)

    def test_bfs_marking_recovered_noise(self):
        grid = self.circles_3
        expected = {(0, 2): 3,
                    (1, 1): 4,
                    (2, 0): 2,
                    (0, 1): 6,
                    (1, 2): 0,
                    (2, 1): 1}
        for start_node in range(len(grid)):
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=0.5, min_similar_vectors=2)),
                                 start_node)
            # isolated nodes, not linked with the rest of the grid
            # 0 recovered by multi_pass
            if start_node == 5:
                self.assertDictEqual(result, {(0, 0): start_node})
            else:
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
        self.assertTrue(detect_grid(connect4, min_to_keep=15, pixel_threshold=20.)[0])

    def test_detect_grid_worst(self):
        connect4 = self.connect4_1
        expected = {(0, 0): 2, (1, 0): 3, (2, 0): 4, (0, 1): 7, (1, 1): 8, (3, 1): 9, (5, 1): 10, (6, 1): 11,
                    (1, 2): 13, (2, 2): 14, (3, 2): 15, (4, 2): 16, (5, 2): 18, (2, 3): 22, (3, 3): 23, (5, 3): 25,
                    (2, 4): 28, (3, 4): 29, (5, 4): 30, (6, 4): 31, (4,5): 34, (5,5): 36, (6, 5): 37, }
        result = detect_grid(connect4, min_to_keep=8, pixel_threshold=15.)
        self.assertTrue(result[0])
        self.assertDictEqual(expected, result[1])
