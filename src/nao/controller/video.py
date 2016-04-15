import numpy as np
import time
from naoqi import ALProxy, ALModule, ALBroker

import nao.data as nao
import threading

__author__ = 'Anthony Rouneau'

SUBSCRIBER_ID = "Connect4NAO"

event = threading.Event()


class VideoController(object):
    def __init__(self, robot_ip=nao.IP, port=nao.PORT):
        """
        :param robot_ip: the ip address of the robot
        :param port: the port of the robot
        Connect to the robot camera proxy
        """
        self.ip = robot_ip
        self.port = port
        self.video_device = ALProxy("ALVideoDevice", robot_ip, port)
        # self.barcode_reader = ALProxy("ALBarcodeReader,", robot_ip, port)
        # self.memory_proxy = ALProxy("ALMemory", robot_ip, port)
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
        :param subscriber_id: The subscriber identifier to disconnect from. If None, use the default id
        :type subscriber_id: str
        Unsubscribe from the camera using the subscriber identifier
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
        :return: The picture taken or None if there was a connection problem
        :rtype: np.matrix
        Take a picture that can be used by OpenCV
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

#     def detectBarcode(self, expected_barcode_number=2, timeout=500, detection_period=100, subscriber_id="C4_Holes"):
#         """
#         :param expected_barcode_number: the minimum number of landmarks to detect to consider the detection as
#             successful.
#         :type expected_barcode_number: int
#         :param timeout: if no landmark was detected in this amount of milliseconds, raise an excetion
#         :type timeout: int
#         :param detection_period: the period between two detection in millisecond
#         :type detection_period: int
#         :param subscriber_id: the subscriber id to the nao memory
#         :type subscriber_id: str
#         :return:
#         """
#         global event
#         # Broker to be able to subscribe to NAO events
#         broker = ALBroker("myBroker", "127.0.0.1", 0, self.ip, self.port)
#         # Launch the detector every "detection_period" ms
#         self.barcode_reader.subscribe(subscriber_id, detection_period, 1.0)
#
#         # Preparing the callback method
#         barcode_callback_name = "barcode_callback"
#         barcode_callback = BarcodeCallbackModule(barcode_callback_name, expected_barcode_number)
#         self.memory_proxy.subscribeToEvent("BarcodeReader/BarcodeDetected", barcode_callback_name, "onBarcodeUpdated")
#
#         # Waiting for the detector to detect landmarks
#         event.wait(timeout/1000.0)
#
#         # Exiting...
#         self.barcode_reader.unsubscribe(subscriber_id)
#         self.memory_proxy.unsubscribeToEvent("BarcodeReader/BarcodeDetected", barcode_callback_name)
#         broker.shutdown()
#         event.clear()
#
#
# class BarcodeCallbackModule(ALModule):
#     """ The main point here is to declare a module with a call back function
#       that is called by ALMemory whenever the landmark's results change. """
#     def __init__(self, variable_name, expected_barcode_number):
#         super(BarcodeCallbackModule, self).__init__(variable_name)
#         self.expected_barcode_number = expected_barcode_number
#
#     # Call back function registered with subscribeOnDataChange that handles
#     # changes in LandMarkDetection results.
#     def onBarcodeUpdated(self, dataName, value, msg):
#         global event
#         """ Call back method called when naomark detection updates its results. """
#         if len(value) != 0:
#             # TODO: Use expected_barcode_number
#             event.set()
#             print "We detected barcode !"
#             print str(value)
