import threading

from naoqi import ALModule, ALProxy, ALBroker

import nao.data
from ai.connect4.game import Game
from ai.connect4.strategy.naive import Naive
from connect4.connect4handler import Connect4Handler
from connect4.connect4tracker import Connect4Tracker
from connect4.detector.front_holes import FrontHolesDetector, FrontHolesGridNotFoundException
from connect4.detector.upper_hole import UpperHolesDetector
from connect4.model.default_model import DefaultModel
from nao.controller.motion import MotionController
from nao.controller.video import VideoController

__author__ = 'Anthony Rouneau'

event = threading.Event()
callbackObject = None
memory_proxy = None
broker = None
motion = None


class HeadSensorCallbackModule(ALModule):
    """ Mandatory docstring.
      comment needed to create a new python module
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
            comment needed to create a bound method
        """
        memory_proxy.unsubscribeToEvent("FrontTactilTouched", "callbackObject")
        memory_proxy.unsubscribeToEvent("MiddleTactilTouched", "callbackObject")
        memory_proxy.unsubscribeToEvent("RearTactilTouched", "callbackObject")
        global event
        motion.motion_proxy.closeHand("LHand")
        event.set()


class DiscNotObtainedException(BaseException):
    def __init__(self, msg):
        super(DiscNotObtainedException, self).__init__(msg)


class Connect4NAO(object):
    def __init__(self):
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
        if not self.camera_subscribed[camera_num]:
            self.nao_video = VideoController()
            ret = self.nao_video.connectToCamera(res=camera_num + 1, fps=30, camera_num=camera_num,
                                                 subscriber_id="C4N_" + str(camera_num))
            if ret < 0:
                print "Could not open camera"
                return None
        return self.nao_video.getImageFromCamera(camera_num=camera_num)

    def findGameBoard(self):
        distances = [0.5, 1.0, 1.3, 1.75, 2.2, 2.5, 3.0]
        for dist in distances:
            try:
                coord = self.c4_handler \
                    .getUpperHoleCoordinatesUsingFrontHoles(dist, True, 3,
                                                            self.nao_motion.get_camera_top_position_from_torso(),
                                                            nao.data.CAM_MATRIX, nao.data.CAM_DISTORSION,
                                                            debug=False, tries=2)
                self.nao_motion.move_at(coord)
                self.estimated_distance = dist
                break
            except FrontHolesGridNotFoundException:
                continue
                # TODO : Walk around checking for a Connect 4 (variate distances)

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
        global event, callbackObject, broker
        self.nao_motion.motion_proxy.openHand("LHand")
        # self.memory_proxy.subscribeToEvent("FrontTactilTouched", "HeadSensorCallbackModule", "HeadTouched")
        callbackObject = HeadSensorCallbackModule()
        # Waiting for the detector to detect landmarks
        if not event.wait(timeout / 1000.0):
            raise DiscNotObtainedException("NAO has not been tapped on the head")
        # time.sleep(timeout)
        # Exiting...
        broker.shutdown()
        event.clear()


if __name__ == "__main__":
    ip = nao.data.IP
    port = nao.data.PORT
    broker = ALBroker("myBroker", "0.0.0.0", 0, ip, port)
    try:
        c4nao = Connect4NAO()
        c4nao.wait_for_disc()
    except KeyboardInterrupt:
        broker.shutdown()
