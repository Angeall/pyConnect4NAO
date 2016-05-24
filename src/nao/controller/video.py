import numpy as np
from naoqi import ALProxy

import nao.data as nao

__author__ = 'Anthony Rouneau'

SUBSCRIBER_ID = "C4N"


class VideoController(object):
    """
    Represents a virtual controller for NAO's videos devices
    """
    def __init__(self, robot_ip=None, robot_port=None):
        """
        :param robot_ip: the ip address of the robot
        :param robot_port: the port of the robot
        Connect to the robot camera proxy
        """
        if robot_ip is None:
            robot_ip = nao.IP
        if robot_port is None:
            robot_port = nao.PORT
        self.ip = robot_ip
        self.port = robot_port
        self.video_device = ALProxy("ALVideoDevice", robot_ip, robot_port)
        self.disconnectFromCamera()
        self.subscriber_ids = [SUBSCRIBER_ID + "_CAM_0", SUBSCRIBER_ID + "_CAM_1"]
        self.cam_connected = False
        self.cam_matrix = nao.CAM_MATRIX
        self.cam_distorsion = nao.CAM_DISTORSION

    def connectToCamera(self, res=1, fps=11, camera_num=0, color_space=13, subscriber_id="C4N"):
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
            self.subscriber_ids[camera_num] = subscriber_id + "_CAM_" + str(camera_num)
            self.disconnectFromCamera(camera_num)
            self.cam_connected = True
            self.subscriber_ids[camera_num] = self.video_device.subscribeCamera(subscriber_id, camera_num, res, color_space, fps)
            self.video_device.setAllCameraParametersToDefault(self.subscriber_ids[camera_num])
            self.video_device.setCameraParameter(self.subscriber_ids[camera_num], 2, 255)
            self.video_device.setCameraParameter(self.subscriber_ids[camera_num], 3, -180)
            self.video_device.setCameraParameter(self.subscriber_ids[camera_num], 6, 255)
            self.video_device.setCameraParameter(self.subscriber_ids[camera_num], 12, 1)
            self.video_device.setCameraParameter(self.subscriber_ids[camera_num], 24, 7)
            self.video_device.setCameraParameter(self.subscriber_ids[camera_num], 1, 64)
        except BaseException, err:
            print "ERR: cannot connect to camera : %s" % err
            return -1
        return 0

    def disconnectFromCamera(self, camera_num=None):
        """
        :param camera_num: the camrea identifier from which we want to disconnect
        :type camera_num: int
        Unsubscribe from the camera using the subscriber identifier
        """
        try:
            if camera_num is None:
                subscribers = self.video_device.getSubscribers()
                if len(subscribers) > 5:  # If too many connections, unsubscribe them all
                    for subscriber in subscribers:
                        if "C4N" in subscriber:
                            self.video_device.unsubscribe(subscriber)
            else:
                for i in range(7):
                    self.video_device.unsubscribe(self.subscriber_ids[camera_num] + "_" + str(i))
        except BaseException, err:
            print "ERR: cannot disconnect from camera : %s" % err

    def getImageFromCamera(self, camera_num=0):
        """
        :param camera_num: 0 : the top camera, 1 : the bottom camera
        :type camera_num: int
        :return: The picture taken or None if there was a connection problem
        :rtype: np.matrix
        Take a picture that can be used by OpenCV
        """
        if not self.cam_connected:
            self.connectToCamera()
        try:
            img = self.video_device.getImageRemote(self.subscriber_ids[camera_num])
            if img is not None:
                converted_img = np.reshape(np.frombuffer(img[6], dtype='%iuint8' % img[2]), (img[1], img[0], img[2]))
                return converted_img
            else:
                return None
        except BaseException, err:
            print "ERR: cannot get image from camera : %s" % err
            return None
