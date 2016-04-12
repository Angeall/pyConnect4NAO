import numpy as np
import time
from naoqi import ALProxy

import nao.data as nao

__author__ = 'Anthony Rouneau'

SUBSCRIBER_ID = "Connect4NAO"




class VideoController(object):
    def __init__(self, robot_ip=nao.IP, port=nao.PORT):
        """
        :param robot_ip: the ip address of the robot
        :param port: the port of the robot
        Connect to the robot camera proxy
        """
        self.video_device = ALProxy("ALVideoDevice", robot_ip, port)
        self.landmark_detector = ALProxy("ALLandMarkDetection,", robot_ip, port)
        self.memory_proxy = ALProxy("ALMemory", robot_ip, port)
        self.subscriber_id = SUBSCRIBER_ID
        self.cam_connected = False
        self.cam_matrix = nao.CAM_MATRIX
        self.cam_distorsion = nao.CAM_DISTORSION

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
            self.cam_connected = True
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
        if not self.cam_connected:
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

    def detectLandmarks(self, period, subscriber_id="Upper_Holes"):
        """
        :param period: the period between two detection in millisecond
        :type period: int
        :param subscriber_id: the subscriber id to the nao memory
        :type subscriber_id: str
        :return:
        """
        self.landmark_detector.subscribe(subscriber_id, period)