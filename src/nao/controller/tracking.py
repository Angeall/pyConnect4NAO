from naoqi import ALProxy
from connect4.connect4tracker import Connect4Tracker
import nao.data as nao

__author__ = 'Anthony Rouneau'


class TrackingController(object):
    pass
    # def __init__(self, robot_ip=nao.IP, port=nao.PORT):
    #     """
    #     :param robot_ip: the ip address of the robot
    #     :param port: the port of the robot
    #     Connect to the robot
    #     """
    #     # The World Representation of the robot, used to track the Connect4Handler
    #     self.world_repr = ALProxy("ALWorldRepresentation", robot_ip, port)
    #     self.tracker = None  # Initialized when needed
    #     self.tracking_initiated = False
    #
    # def initializeTracking(self, rvec, tvec, camera_position):
    #     """
    #     :param camera_position: The camera position refering to NAO'w World
    #     :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
    #     :type rvec: np.array
    #     :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
    #     :type tvec: np.array
    #     Begin to track the Connect 4 that was already detected inside the room
    #     """
    #     print camera_position
    #     self.tracker = Connect4Tracker(rvec, tvec, camera_position[3:6], camera_position[0:3])
    #     self.world_repr.createObjectCategory(self.tracker.WORLD_CATEGORY_NAME, True)
    #     for i in range(len(self.tracker.objects_tab)):
    #         position = self.tracker.upper_hole_positions[i].tolist()
    #
    #         self.world_repr.storeObject(self.tracker.objects_tab[i], "World", position,
    #                                     self.tracker.WORLD_CATEGORY_NAME, [])
    #     self.tracking_initiated = True
    #
    # def getConnect4HolePosition(self, hole_no, world="World"):
    #     """
    #     :param hole_no: The number of the hole to get its position
    #     :type hole_no: int
    #     :return: A 6D vector; a translation vector followed by 3 euler angles (see NAO documentation)
    #     :rtype: np.matrix
    #     Get the position of an upper hole of the Connect 4 relative to the World
    #     """
    #     if hole_no > 6:
    #         print "ERR: The Connect4Handler have only 7 holes. Please ask for a hole between 0 and 6"
    #         return None
    #     else:
    #         return self.world_repr.getPosition6D(world, self.tracker.objects_tab[hole_no])
    #
    # def refreshConnect4Position(self, rvec, tvec, camera_position):
    #     """
    #     :param camera_position:
    #     :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
    #     :type rvec: np.array
    #     :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4Handler 3D coordinates
    #     :type tvec: np.array
    #     Refresh the connect 4 position in the World Representation of NAO
    #     """
    #     self.tracker.refreshPositions(rvec, tvec, camera_position)
    #     for i in range(len(self.tracker.objects_tab)):
    #         self.world_repr.updatePosition(self.tracker.objects_tab[i], self.tracker.upper_hole_positions[i], False)
