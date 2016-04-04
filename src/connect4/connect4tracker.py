import cv2
import numpy as np
from connect4handler import Connect4Handler
from utils import geom

__author__ = 'Anthony Rouneau'


class Connect4Tracker(object):
    CAMERA_TOP_OBJECT = "CameraTop"
    UPPER_HOLE_0_OBJECT = "MyHole0"
    UPPER_HOLE_1_OBJECT = "MyHole1"
    UPPER_HOLE_2_OBJECT = "MyHole2"
    UPPER_HOLE_3_OBJECT = "MyHole3"
    UPPER_HOLE_4_OBJECT = "MyHole4"
    UPPER_HOLE_5_OBJECT = "MyHole5"
    UPPER_HOLE_6_OBJECT = "MyHole6"
    WORLD_CATEGORY_NAME = "C4Tracker"
    objects_tab = [UPPER_HOLE_0_OBJECT,
                   UPPER_HOLE_1_OBJECT,
                   UPPER_HOLE_2_OBJECT,
                   UPPER_HOLE_3_OBJECT,
                   UPPER_HOLE_4_OBJECT,
                   UPPER_HOLE_5_OBJECT,
                   UPPER_HOLE_6_OBJECT]

    def __init__(self, rvec, tvec, camera_rvec, camera_tvec):
        """
        Creates the tracker to refresh and keep the Connect 4 position in 3D
        :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
        :type tvec: np.array
        """
        # Transformation from camera's world axes to nao's world axes
        self.nao_axes_mat = np.matrix([[0, 0, 1],
                                       [-1, 0, 0],
                                       [0, -1, 0]])
        # Connect 4 Model and location information
        self.connect4 = Connect4Handler()
        self.camera_rmat = geom.convert_euler_to_matrix(camera_rvec)
        self.camera_tvec = np.array(camera_tvec)
        self.connect4_rmat, _ = cv2.Rodrigues(rvec)
        self.connect4_tvec = tvec
        self.upper_hole_positions = self.initialize_positions()

    def initialize_positions(self):
        """
        Computes the position of each upper hole of the board.
        :return: The list that contains the upper holes position
        :rtype: list
        """
        positions = []
        for i in range(len(self.objects_tab)):
            # We take the top left corner and the bottom right corner of the hole
            model_coord_0, _, _, model_coord_1 = self.connect4.model.getUpperHole(i)
            # This is the translation vector to add to the left top corner in order to get the middle of the hole
            middle_vector = (model_coord_1 - model_coord_0) / 2
            model_coord = model_coord_0 + middle_vector  # The coordinates of the middle of the hole
            # Rotate and translate to get real position with camera axes
            new_coord = geom.transform_vector(model_coord, self.connect4_rmat, self.connect4_tvec)
            print "Hole", i, "From Camera Original Axes", new_coord
            new_coord = geom.transform_vector(new_coord, self.nao_axes_mat, np.array([[0], [0], [0]], np.int32)) \
                .tolist()[0]
            print "Hole", i, "From Camera", new_coord
            new_coord = geom.transform_vector(np.array(new_coord), self.camera_rmat, self.camera_tvec)
            new_coord = new_coord.tolist()[0]
            print "Hole ", i, "From World", new_coord, '\n'
            # Add 3 rotation values (0) to match the Position6D requirements of NAO
            for _ in range(3):
                new_coord = np.append(new_coord, 0)
            positions.append(new_coord)
        return positions

    def refreshPositions(self, rvec, tvec, camera_position):
        """
        Refresh the connect 4 position
        :param camera_position: The camera position referring to NAO's World
        :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
        :type tvec: np.array
        """
        [x, y, z, Wx, Wy, Wz] = camera_position
        self.camera_tvec = [x, y, z]
        self.camera_rmat = geom.convert_euler_to_matrix((Wx, Wy, Wz))
        self.connect4_rmat, _ = cv2.Rodrigues(rvec)
        self.connect4_tvec = tvec
        self.upper_hole_positions = self.initialize_positions()
