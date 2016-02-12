import numpy as np
from naoqi import ALProxy

from connect4.connect4tracker import Connect4Tracker
from utils import geom

__author__ = "Anthony Rouneau"

# IP = "127.0.0.1"
IP = "192.168.2.16"
# PORT = 56487
PORT = 9559
FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2


class NAOController:
    def __init__(self, robot_ip=IP, port=PORT):
        """
        Creates a new Virtual Controller for NAO
        :param robot_ip: The IP address of the robot
        :type robot_ip: str
        :param port: The port of the robot
        :type port: int
        """
        # Connect and wake up the robot
        self.motion_proxy = ALProxy("ALMotion", robot_ip, port)
        self.video_device = ALProxy("ALVideoDevice", robot_ip, port)
        # self.motion_proxy.wakeUp()
        # ALProxy("AutonomousLife", robot_ip, port).setState("disabled")
        self.motion_proxy.setCollisionProtectionEnabled("Arms", True)
        # The World Representation of the robot, used to track the Connect4
        self.world_repr = ALProxy("ALWorldRepresentation", robot_ip, port)
        self.tracker = None  # Initialized when needed
        self.tracking_initiated = False
        # Camera parameters
        self.subscriber_id = "Connect4NAO"
        self.camera_connected = False
        self.camera_matrix = np.matrix([[133.1424,     0.,   167.5946],
                                        [0.,       126.5172, 113.2453],
                                        [0.,           0.,       1.]])
        self.dist_coeff = np.matrix([[-1.28412605e+00,  3.23529724e+00, -4.54783485e-04,
                                      -1.10163065e-02, -2.50940379e+00]])

    def clean(self):
        """
        Disconnect NAO from all camera subscription of this application
        """
        for i in range(7):
            self.disconnectFromCamera(subscriber_id="Connect4NAO_" + str(i))

    def connectToCamera(self, res=1, fps=11, camera_num=0, color_space=13, subscriber_id="Connect4NAO"):
        """
        Subscribe to the robot camera
        :param res: Type of resolution (see NAO documentation)
        :type res: int
        :param fps: Frame per second (max fps set by NAO documentation)
        :type fps: int
        :param camera_num: The camera to subscribe to (0 = Top, 1 = Bottom)
        :type camera_num: int
        :param color_space: The color space that the camera will use (see NAO documentation)
        :type color_space: int
        :param subscriber_id: The subscriber identifier
        :type subscriber_id: str
        :return: -1 in case of error, 0 else
        :rtype: int
        """
        try:
            self.camera_connected = True
            self.subscriber_id = self.video_device.subscribeCamera(subscriber_id, camera_num, res, color_space, fps)
        except BaseException, err:
            print "ERR: cannot connect to camera : %s" % err
            return -1
        return 0

    def disconnectFromCamera(self, subscriber_id=None):
        """
        Unsubscribe from the camera using the subscriber identifier
        :param subscriber_id: The subscriber identifier to disconnect from. If None, use the default id
        :type subscriber_id: str
        """
        try:
            if subscriber_id is None:
                self.video_device.unsubscribe(self.subscriber_id)
            else:
                self.video_device.unsubscribe(subscriber_id)
        except BaseException, err:
            print "ERR: cannot disconnect from camera : %s" % err

    def getImageFromCamera(self):
        """
        Take a picture that can be used by OpenCV
        :return: The picture taken or None if there was a connection problem
        :rtype: np.matrix
        """
        if not self.camera_connected:
            self.connectToCamera()
        try:
            img = self.video_device.getImageRemote(self.subscriber_id)
            if img is not None:
                converted_img = np.reshape(np.frombuffer(img[6], dtype='%iuint8' % img[2]), (img[1], img[0], img[2]))
                return converted_img
            else:
                return None
        except BaseException, err:
            print "ERR: cannot get image from camera : %s" % err
            return None

    def unsubscribeAllCameras(self):
        """
        Unsubscribe from all camera that this application could have subscribed to
        """
        for i in range(7):
            self.disconnectFromCamera(subscriber_id=self.subscriber_id + "_" + str(i))

    def initializeTracking(self, rvec, tvec):
        """
        Begin to track the Connect 4 that was already detected inside the room
        :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type tvec: np.array
        """
        self.tracking_initiated = True
        self.tracker = Connect4Tracker(rvec, tvec)
        self.world_repr.createObjectCategory(self.tracker.WORLD_CATEGORY_NAME, True)
        self.refreshCameraPosition()
        for i in range(len(self.tracker.objects_tab)):
            position = self.tracker.upper_hole_positions[i]
            self.world_repr.storeObject(self.tracker.objects_tab[i], self.tracker.CAMERA_TOP_OBJECT,
                                        position, self.tracker.WORLD_CATEGORY_NAME, [])

    def getConnect4HolePosition(self, hole_no):
        """
        Get the position of an upper hole of the Connect 4
        :param hole_no: The number of the hole to get its position
        :type hole_no: int
        :return: A 6D vector; a translation vector followed by 3 euler angles (see NAO documentation)
        :rtype: np.matrix
        """
        if hole_no > 6:
            print "ERR: The Connect4 have only 7 holes. Please ask for a hole between 0 and 6"
            return None
        else:
            return self.world_repr.getPosition6D("World", self.tracker.objects_tab[hole_no])

    def refreshConnect4Position(self, rvec, tvec):
        """
        Refresh the connect 4 position in the World Representation of NAO
        :param rvec: The rotation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type rvec: np.array
        :param tvec: The translation vector given by SolvePnP to apply to the model to get the Connect4 3D coordinates
        :type tvec: np.array
        """
        self.tracker.refreshPositions(rvec, tvec)
        for i in range(len(self.tracker.objects_tab)):
            self.world_repr.updatePosition(self.tracker.objects_tab[i], self.tracker.upper_hole_positions[i], False)

    def refreshCameraPosition(self):
        camera_position = self.getCameraPositionFromTorso()
        if self.tracking_initiated:
            self.world_repr.updateObjectWithReference(self.tracker.CAMERA_TOP_OBJECT, "Robot_Torso", "HeadPitch",
                                                      camera_position, self.tracker.WORLD_CATEGORY_NAME, [])
        else:
            self.world_repr.storeObjectWithReference(self.tracker.CAMERA_TOP_OBJECT, "Robot_Torso", "HeadPitch",
                                                     camera_position, self.tracker.WORLD_CATEGORY_NAME, [])

    def lookAtCoordinates(self, coordinates):
        """
        Make the robot look at a certain coordinate
        :param coordinates: The coordinates of the object to look at (relative to the robot torso)
        """
        camera_position = self.getCameraPositionFromTorso()
        translated_camera = [camera_position[0]+1, camera_position[1], camera_position[2]]
        camera_vector = geom.vectorize(camera_position, translated_camera)
        # Head Yaw
        yaw_coordinates = [coordinates[0], coordinates[1], camera_position[2]]
        yaw_vector = geom.vectorize(camera_position, yaw_coordinates)
        yaw = np.arccos(np.dot(camera_vector, yaw_vector))
        # Head Pitch
        pitch_coordinates = [coordinates[0], camera_position[1], coordinates[2]]
        pitch_vector = geom.vectorize(camera_position, pitch_coordinates)
        pitch = np.arccos(np.dot(camera_vector, pitch_vector))
        # Moving the robot's head
        names = ["HeadYaw", "HeadPitch"]
        angles = [yaw, pitch]
        fraction_max_speed = 0.4
        self.motion_proxy.setAngles(names, angles, fraction_max_speed)

    def getCameraPositionFromTorso(self):
        return self.motion_proxy.getPosition("CameraTop",
                                             FRAME_TORSO,
                                             True)



