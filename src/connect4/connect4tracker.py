import cv2
import numpy as np

from utils.camera import geom

__author__ = 'Anthony Rouneau'


class Connect4Tracker(object):
    """
    Represents the Connect 4 coordinates converter.
     Its main goal is to convert coordinates from the camera space into NAO's.
    """

    def __init__(self, model):
        """
        Creates the tracker to refresh and keep the Connect 4 position in 3D
        """
        # Transformation from camera's world axes to nao's world axes
        self.nao_axes_mat = np.matrix([[0, 0, 1],
                                       [-1, 0, 0],
                                       [0, -1, 0]])
        # Connect 4 Model and location information
        self.model = model
        self.camera_rmat = None
        self.camera_tvec = None
        self.connect4_rmat = None
        self.connect4_tvec = None

    def getHoleCoordinates(self, rvec, tvec, camera_position6d, hole_index):
        # type: (np.array, np.array, tuple, int) -> list
        """
        :param rvec: The rotation vector given by SolvePnP to apply to the _model to get the Connect4Handler 3D coord.
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the _model to get the Connect4Handler 3D coord.
        :type tvec: np.array
        :param camera_position6d: the position 6D (x, y, z, Wx, Wy, Wz) of the camera from the robot torso
        :type camera_position6d: array
        :param hole_index: the index of the hole to get
        :type hole_index: int
        :return: The list that contains the upper _holes position
        :rtype: list
        Computes the position of each upper hole of the board.
        """
        [x, y, z, Wx, Wy, Wz] = camera_position6d
        self.camera_tvec = np.array([x, y, z])
        self.camera_rmat = geom.convert_euler_to_matrix((Wx, Wy, Wz))
        self.connect4_rmat, _ = cv2.Rodrigues(rvec)
        self.connect4_tvec = tvec
        positions = []
        # We take the top left corner and the bottom right corner of the hole
        model_coord_0, _, _, model_coord_1 = self.model.getUpperHole(hole_index)
        # This is the translation vector to add to the left top corner in order to get the middle of the hole
        middle_vector = (model_coord_1 - model_coord_0) / 2
        model_coord = model_coord_0 + middle_vector  # The coordinates of the middle of the hole
        # Rotate and translate to get real position with camera axes
        new_coord = geom.transform_vector(model_coord, self.connect4_rmat, self.connect4_tvec)
        # print "Hole", i, "From Camera Original Axes", new_coord
        new_coord = geom.transform_vector(new_coord, self.nao_axes_mat, np.array([[0], [0], [0]], np.int32)) \
            .tolist()[0]
        # print "Hole", i, "From Camera", new_coord
        new_coord = geom.transform_vector(np.array(new_coord), self.camera_rmat, self.camera_tvec)
        new_coord = new_coord.tolist()[0]
        # print "Hole ", i, "From Torso", new_coord, '\n'
        # Add 3 rotation values (0) to match the Position6D requirements of NAO
        for _ in range(3):
            new_coord = np.append(new_coord, 0)
        return new_coord.tolist()

