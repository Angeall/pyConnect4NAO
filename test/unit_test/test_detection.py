__author__ = 'Angeall'
import unittest
from src.utils.detection import *
import random


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
            random.shuffle(connect4)
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
        self.connect4_0 = [(69.564593919157, 220.460199640106), (5.816927563485698, 170.35369997644142),
                           (325.4743645170645, 58.85697181260877), (202.23210977492113, 117.99819406584858),
                           (328.85160643156604, 1.0077235988391493), (3.029849244081838, 2.2850078339426885),
                           (7.114850531089268, 111.17338648080039), (329.0233503875431, 169.97162798950473),
                           (399.750157135183, 110.57380026848236), (9.215756704390031, 281.9869108390031),
                           (326.9658239592276, 112.45212860191774), (198.9468949435946, 220.9893898421675),
                           (66.0097827011303, 3.8899497775144054), (261.2250351153653, 227.01158967582495),
                           (133.60373319443033, 222.7488881961528), (266.34417180071836, 168.26894178481132),
                           (135.24087139782048, 165.8104330748167), (195.7480441873863, 2.6105928837867536),
                           (74.75317027696299, 167.2157880657985), (196.1221985352397, 59.80645975182558),
                           (265.8612885060237, 7.257832877192755), (399.1464213449372, 56.169350056949),
                           (7.234603490828572, 225.92175799328683), (269.0172844193458, 276.8144215251059),
                           (396.77545480560144, 167.45412057937477), (69.51543966681541, 114.85363483683129),
                           (9.078089246658593, 57.57896536865372), (139.46284704346368, 117.49553769775005),
                           (266.06599137441214, 61.72547801050251), (266.82028035225335, 112.77818193701748),
                           (136.7897692661029, 57.381840185453896), (202.40086359784172, 276.074780842928),
                           (137.67324760066174, 282.07062888489287), (325.92686340385006, 220.49731858904886),
                           (198.4850033901905, 168.9415886266548), (329.0977382267979, 280.6915869630235),
                           (398.2117352953058, 7.629069965876825), (74.65983449601644, 55.774452396265445),
                           (130.35501655176614, 7.069153960598512), (395.34536244706607, 220.394591048149),
                           (74.46338920957228, 281.2908287768117), (393.8036401165491, 279.28507977077055)]
        # """"""""Worst case"""""""""
        # Connect 4 with 3 of the 4 corners missing, some internal circles missing, some internal noise, some external noise
        self.connect4_1 = [(69.564593919157, 220.460199640106), (5.816927563485698, 170.35369997644142),
                           (325.4743645170645, 58.85697181260877), (202.23210977492113, 117.99819406584858),
                           (328.85160643156604, 1.0077235988391493),  # (3.029849244081838, 2.2850078339426885),corner 2
                           (7.114850531089268, 111.17338648080039), (329.0233503875431, 169.97162798950473),
                           (399.750157135183, 110.57380026848236),  # (9.215756704390031, 281.9869108390031), corner 1
                           (326.9658239592276, 112.45212860191774), (198.9468949435946, 220.9893898421675),
                           # (66.0097827011303, 3.8899497775144054), (261.2250351153653, 227.01158967582495),
                           (133.60373319443033, 222.7488881961528), (266.34417180071836, 168.26894178481132),
                           (135.24087139782048, 165.8104330748167), (195.7480441873863, 2.6105928837867536),
                           (74.75317027696299, 167.2157880657985),  # (196.1221985352397, 59.80645975182558),
                           (265.8612885060237, 7.257832877192755), (399.1464213449372, 56.169350056949),
                           # (7.234603490828572, 225.92175799328683), (269.0172844193458, 276.8144215251059),
                           (396.77545480560144, 167.45412057937477),  # (69.51543966681541, 114.85363483683129),
                           (9.078089246658593, 57.57896536865372), (139.46284704346368, 117.49553769775005),
                           (266.06599137441214, 61.72547801050251),  # (266.82028035225335, 112.77818193701748),
                           (136.7897692661029, 57.381840185453896), (202.40086359784172, 276.074780842928),
                           (137.67324760066174, 282.07062888489287),  # (325.92686340385006, 220.49731858904886),
                           (198.4850033901905, 168.9415886266548), (329.0977382267979, 280.6915869630235),
                           (74.65983449601644, 55.774452396265445),  # (398.2117352953058, 7.629069965876825), corner 3
                           (130.35501655176614, 7.069153960598512), (395.34536244706607, 220.394591048149),
                           (74.46338920957228, 281.2908287768117),  # (393.8036401165491, 279.28507977077055)]
                           # Noise Goes Here
                           (250.5477833468543, 60.76984968398586), (185.5457457282682, 200.08685858993859),
                           (4.536973469735968, 76.349583498534509), (348.5498450685069840, 15.94824248594889340),
                           (465.04850208450824, 165.9485398539598), (460.3490360964309643, 335.9898285843989438),
                           (70.9498349834589, 340.3454673247267), (200.2336146736588, 200.0248530844380)]

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
        result = filter_connections(connections, pixel_threshold=0.33, min_to_keep=4)[1]
        self.assertItemsEqual(result, expected)

    def test_filter_connection_missing(self):
        grid = self.circles_1
        connections = connect_keypoints(grid)
        expected = connections[1]
        result = filter_connections(connections, pixel_threshold=0.33, min_to_keep=2)[1]
        self.assertItemsEqual(result, expected)

    def test_filter_connection_missing_noise(self):
        grid = self.circles_2
        connections = connect_keypoints(grid)
        result = filter_connections(connections, pixel_threshold=1., min_to_keep=2)[1]
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
        filtered_connections = filter_connections(connect_keypoints(grid), pixel_threshold=0.33, min_to_keep=2)
        result = filter_right_up_vectors(filtered_connections)
        expected = [[(7, 2), (2, 4), (6, 8), (8, 3), (0, 1), (1, 5)], [(0, 6), (6, 7), (1, 8), (8, 2), (5, 3), (3, 4)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_filter_up_right_missing(self):
        grid = self.circles_1
        filtered_connections = filter_connections(connect_keypoints(grid), pixel_threshold=0.33, min_to_keep=2)
        result = filter_right_up_vectors(filtered_connections)
        expected = [[(3, 0), (4, 1)], [(4, 0), (2, 1)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_filter_up_right_missing_noise(self):
        grid = self.circles_2
        filtered_connections = filter_connections(connect_keypoints(grid), pixel_threshold=1., min_to_keep=2)
        result = filter_right_up_vectors(filtered_connections)
        expected = [[(7, 4), (4, 1)], [(7, 3), (2, 1)]]
        self.assertItemsEqual(result[0], expected[0])
        self.assertItemsEqual(result[1], expected[1])

    def test_double_pass_filter_isolated_node(self):
        grid = self.circles_2
        result = double_pass_filter(grid, pixel_threshold=0.22, min_to_keep=2)[1]
        expected = [(3, 7), (7, 3), (4, 1), (1, 4), (1, 2), (2, 1), (4, 7), (7, 4)]
        self.assertItemsEqual(expected, result)

    def test_double_pass_filter_recovering_noised(self):
        grid = self.circles_3
        result = double_pass_filter(grid, pixel_threshold=0.22, min_to_keep=2)[1]
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
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=0.33, min_to_keep=2)),
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
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=1., min_to_keep=2)),
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
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=0.33, min_to_keep=2)),
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
            result = bfs_marking(filter_right_up_vectors(double_pass_filter(grid, pixel_threshold=0.5, min_to_keep=2)),
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

