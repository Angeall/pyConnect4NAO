from naoqi import ALProxy
import numpy as np

__author__ = "Anthony Rouneau"

IP = "192.168.2.16"
PORT = 9559


class NAOController:
    def __init__(self, robot_ip, port):
        self.motion_proxy = ALProxy("ALMotion", robot_ip, port)
        self.video_device = ALProxy("ALVideoDevice", robot_ip, port)
        self.subscriber_id = "Connect4NAO"
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