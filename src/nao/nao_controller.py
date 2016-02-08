from naoqi import ALProxy
import numpy as np

from nao.connect4tracker import Connect4Tracker

__author__ = "Anthony Rouneau"

# IP = "127.0.0.1"
IP = "192.168.2.16"
# PORT = 56487
PORT = 9559
FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2


class NAOController:
    def __init__(self, robot_ip, port):
        self.motion_proxy = ALProxy("ALMotion", robot_ip, port)
        self.video_device = ALProxy("ALVideoDevice", robot_ip, port)
        # The World Representation of the robot, used to track the Connect4
        self.world_repr = ALProxy("ALWorldRepresentation", robot_ip, port)
        self.world_repr.createObjectCategory(self.tracker.WORLD_CATEGORY_NAME, True)
        self.tracker = None  # Initialized when needed
        # Camera parameters
        self.subscriber_id = "Connect4NAO"
        self.camera_matrix = np.matrix([[133.1424,     0.,   167.5946],
                                        [0.,       126.5172, 113.2453],
                                        [0.,           0.,       1.]])
        self.dist_coeff = np.matrix([[-1.28412605e+00,  3.23529724e+00, -4.54783485e-04,
                                      -1.10163065e-02, -2.50940379e+00]])
        # self.motion_proxy.wakeUp()
        self.motion_proxy.setCollisionProtectionEnabled("Arms", True)

    def connectToCamera(self, res=1, fps=11, camera_num=0, color_space=13, subscriber_id="Connect4NAO"):
        try:
            self.subscriber_id = self.video_device.subscribeCamera(subscriber_id, camera_num, res, color_space, fps)
        except BaseException, err:
            print "ERR: cannot connect to camera : %s" % err
            return -1
        return 0

    def disconnectFromCamera(self, subscriber_id=None):
        try:
            if subscriber_id is None:
                self.video_device.unsubscribe(self.subscriber_id)
            else:
                self.video_device.unsubscribe(subscriber_id)
        except BaseException, err:
            print "ERR: cannot disconnect from camera : %s" % err

    def getImageFromCamera(self):
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
        for i in range(7):
            self.disconnectFromCamera(subscriber_id=self.subscriber_id + "_" + str(i))

    def initializeTracking(self, rvec, tvec):
        camera_position = self.motion_proxy.getPosition("CameraTop",
                                                        FRAME_TORSO,
                                                        True)
        self.world_repr.storeObjectWithReference(self.tracker.CAMERA_TOP_OBJECT, "Robot_Torso", "HeadPitch",
                                                 camera_position, self.tracker.WORLD_CATEGORY_NAME, [])
        self.tracker = Connect4Tracker(camera_position, rvec, tvec, self.camera_matrix, self.dist_coeff)
        for i in range(len(self.tracker.objects_tab)):
            self.world_repr.storeObject(self.tracker.objects_tab[i], self.tracker.CAMERA_TOP_OBJECT,
                                        self.tracker.upper_hole_positions[i], self.tracker.WORLD_CATEGORY_NAME, [])

    # TODO : initializeTracking : convert position into Position6D (Euler) maybe 0, 0, 0 rotation ?
    # TODO : getConnect4HolePosition : convert Position6D to move the robot ?

    def getConnect4HolePosition(self, hole_no):
        return self.world_repr.getPosition6D("World", self.tracker.objects_tab[hole_no])

    def refreshConnect4Position(self, new_rvec, new_tvec):
        """
        Refresh the connect 4 position in the World Representation of NAO
        :param new_tvec:
        :param new_rvec:
        """
        self.tracker.refreshPositions(new_rvec, new_tvec)
        for i in range(len(self.tracker.objects_tab)):
            self.world_repr.updatePosition(self.tracker.objects_tab[i], self.tracker.upper_hole_positions[i], False)

