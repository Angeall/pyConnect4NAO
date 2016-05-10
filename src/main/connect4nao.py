import threading

import numpy as np
from naoqi import ALModule, ALProxy, ALBroker

import nao.data
from ai.connect4.game import Game
from ai.connect4.strategy.naive import Naive
from connect4.connect4handler import Connect4Handler
from connect4.connect4tracker import Connect4Tracker
from connect4.detector.front_holes import FrontHolesDetector, FrontHolesGridNotFoundException
from connect4.detector.upper_hole import UpperHolesDetector, NotEnoughLandmarksException
from connect4.model.default_model import DefaultModel
from nao import data
from nao.controller.motion import MotionController
from nao.controller.video import VideoController

__author__ = 'Anthony Rouneau'

# Global variables for the event reaction of the waitForDisc method.
event = threading.Event()
callbackObject = None
memory_proxy = None
broker = None
motion = None


class HeadSensorCallbackModule(ALModule):
    """ Mandatory docstring
        Module that will be used to react to the "Head touched" event.
    """
    def __init__(self):
        global memory_proxy, callbackObject
        self._module_name = "callbackObject"
        ALModule.__init__(self, self._module_name)
        # Preparing the callback method
        memory_proxy = ALProxy("ALMemory")

        memory_proxy.subscribeToEvent("FrontTactilTouched", "callbackObject", "headTouched")
        memory_proxy.subscribeToEvent("MiddleTactilTouched", "callbackObject", "headTouched")
        memory_proxy.subscribeToEvent("RearTactilTouched", "callbackObject", "headTouched")

    # Call back function registered with subscribeOnDataChange that handles
    # changes in LandMarkDetection results.
    def headTouched(self, eventName, val, subscriberId):
        """ Mandatory docstring.
            Method that will be called by the "headTouched" event.
        """
        memory_proxy.unsubscribeToEvent("FrontTactilTouched", "callbackObject")
        memory_proxy.unsubscribeToEvent("MiddleTactilTouched", "callbackObject")
        memory_proxy.unsubscribeToEvent("RearTactilTouched", "callbackObject")
        global event
        motion.motion_proxy.closeHand("LHand")
        event.set()


class DiscNotObtainedException(BaseException):
    """
    Exception raised when the waitForDisc method reaches a timeout.
    """
    def __init__(self, msg):
        super(DiscNotObtainedException, self).__init__(msg)


class Connect4NAO(object):
    """
    Class that holds the main loop of the project.
    """
    def __init__(self, robot_ip=data.IP, robot_port=data.PORT):
        self.tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
        self.strategy = Naive()
        self.game = Game()
        self.nao_motion = MotionController()
        self.estimated_distance = -1
        global motion
        motion = self.nao_motion
        self.nao_video = VideoController()
        self.camera_subscribed = [False, False]
        self.c4_model = DefaultModel()
        self.c4_tracker = Connect4Tracker(self.c4_model)
        self.c4_handler = Connect4Handler(self.getNaoImage)
        self.front_hole_detector = FrontHolesDetector(self.c4_model)
        self.upper_hole_detector = UpperHolesDetector(self.c4_model)

    def getNaoImage(self, camera_num=0):
        """
        :param camera_num: 0 : TopCamera, 1 : BottomCamera
        :type camera_num: int
        :return: An OpenCV readable image that comes from NAO's camera
        """
        if not self.camera_subscribed[camera_num]:
            self.nao_video = VideoController()
            ret = self.nao_video.connectToCamera(res=camera_num + 1, fps=30, camera_num=camera_num,
                                                 subscriber_id="C4N_" + str(camera_num))
            if ret < 0:
                print "Could not open camera"
                return None
        return self.nao_video.getImageFromCamera(camera_num=camera_num)

    def findGameBoard(self):
        """

        """
        distances = [0.5, 1.0, 1.3, 1.75, 2.2, 2.5, 3.0]
        for dist in distances:
            try:
                coord = self.c4_handler \
                    .getUpperHoleCoordinatesUsingFrontHoles(dist, True, 3,
                                                            self.nao_motion.getCameraTopPositionFromTorso(),
                                                            nao.data.CAM_MATRIX, nao.data.CAM_DISTORSION,
                                                            debug=False, tries=2)
                self.nao_motion.moveAt(coord[0], coord[1], coord[5])
                self.estimated_distance = dist
                break
            except FrontHolesGridNotFoundException:
                continue
                # TODO : Walk around checking for a Connect 4 (variate distances)

    def inverseKinematicsConvergence(self, hole_index):
        """
        :param hole_index: the number of the hole above which we want to move NAO's hand
        :return:
        """
        max_tries = 5  # If we don't see any marker after 5 tries, we assume we are not in front of the Connect4
        i = 0
        stable = False
        while not stable:
            while i < max_tries:
                try:
                    hole_coord = self.c4_handler \
                        .getUpperHoleCoordinatesUsingMarkers(hole_index,
                                                             self.nao_motion.getCameraBottomPositionFromTorso(),
                                                             data.CAM_MATRIX, data.CAM_DISTORSION)
                    i = 0
                    self.nao_motion.setLeftHandPosition(hole_coord, mask=63)
                    diff = self.nao_motion.compareToLeftHandPosition(hole_coord)
                    if np.linalg.norm(diff) < 0.05:
                        stable = True
                        self.nao_motion.playDisc(hole_coord)
                        break
                    else:
                        self.nao_motion.moveAt(diff[0], diff[1], hole_coord[5])
                        i += 1
                except NotEnoughLandmarksException:
                    i += 1
            if not stable:
                self.tts.say("Je ne trouve pas les marqueurs dans mon champ de vision")
                i = 0


    def playingRoutine(self):
        pass
        # TODO: AI + Walk + PutDisc

    def walkTowardConnect4(self):
        pass
        # TODO : divide distance in 4 + refine coordinates / rectify path

    def analyseGameState(self):
        pass
        # TODO : make sure the game state is consistent

    def taunt(self):
        pass
        # TODO : optionnal, robot interaction with human

    def wait_for_disc(self, timeout=105000):
        """
        :param timeout: the maximum time to wait, in milliseconds, for a disc, after that, raises a
                        DiscNotObtainedException.
        """
        global event, callbackObject, broker
        self.nao_motion.setLeftArmToAskingPosition()
        # self.memory_proxy.subscribeToEvent("FrontTactilTouched", "HeadSensorCallbackModule", "HeadTouched")
        callbackObject = HeadSensorCallbackModule()
        # Waiting for the detector to detect landmarks
        if not event.wait(timeout / 1000.0):
            raise DiscNotObtainedException("NAO has not been tapped on the head")
        self.nao_motion.setLeftArmRaised()
        # time.sleep(timeout)
        # Exiting...
        # broker.shutdown()
        event.clear()


if __name__ == "__main__":
    ip = nao.data.IP
    port = nao.data.PORT
    broker = ALBroker("myBroker", "0.0.0.0", 0, ip, port)
    try:
        c4nao = Connect4NAO()
        c4nao.wait_for_disc()
        c4nao.inverseKinematicsConvergence(2)
    except KeyboardInterrupt:
        broker.shutdown()
