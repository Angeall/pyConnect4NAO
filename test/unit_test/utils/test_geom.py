import unittest

from utils.camera.geom import *


class GeomTestCase(unittest.TestCase):
    def setUp(self):
        # Rectangles to test

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

        # Vectors to transform
        self.vector_1 = np.array([1, 0, 0])
        self.vector_2 = np.array([0, 1, 0])
        self.vector_3 = np.array([0, 0, 1])
        around_x = np.pi/2
        around_y = -np.pi/2
        self.test_mat = np.matrix([[np.cos(around_y),           0,              np.sin(around_y)],
                                   [0,                          1,                   0],
                                   [-np.sin(around_y),          0,              np.cos(around_y)]])\
                      * np.matrix([[1,                          0,                   0],
                                   [0,                    np.cos(around_x),    -np.sin(around_x)],
                                   [0,                    np.sin(around_x),     np.cos(around_x)]])

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

    def test_transform_vector1(self):
        rot_mat = self.test_mat
        tvec = np.array([0, 0, 0])
        vector_1 = transform_vector(self.vector_1, rmat=rot_mat, tvec=tvec)
        vector_2 = transform_vector(self.vector_2, rmat=rot_mat, tvec=tvec)
        vector_3 = transform_vector(self.vector_3, rmat=rot_mat, tvec=tvec)
        vector_1 = vector_1.tolist()[0]
        vector_2 = vector_2.tolist()[0]
        vector_3 = vector_3.tolist()[0]
        for i in range(3):
            self.assertAlmostEqual(np.array([0, 0,  1])[i], vector_1[i], delta=0.0001)
        for i in range(3):
            self.assertAlmostEqual(np.array([-1, 0, 0])[i], vector_2[i], delta=0.0001)
        for i in range(3):
            self.assertAlmostEqual(np.array([0, -1, 0])[i], vector_3[i], delta=0.0001)

    # def test_common_area_included(self):
    #     rect1 = ((2.34, 5.56), (12, 5), 45.)
    #     rect2 = ((2.34, 5.56), (5, 2), 45.)
    #     self.assertEqual(10, round(common_area(rect1, rect2)))


if __name__ == '__main__':
    unittest.main()
