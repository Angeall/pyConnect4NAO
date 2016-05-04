import threading

from naoqi import ALModule, ALProxy, ALBroker

import nao.data
from ai.connect4.game import Game
from ai.connect4.strategy.naive import Naive
from connect4.connect4tracker import Connect4Tracker
from connect4.detector.front_holes import FrontHolesDetector
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


class Connect4NAO(object):
    def __init__(self):
        self.strategy = Naive()
        self.game = Game()
        self.nao_motion = MotionController()
        global motion
        motion = self.nao_motion
        self.nao_video = VideoController()
        self.c4_model = DefaultModel()
        self.c4tracker = Connect4Tracker(self.c4_model)
        self.front_hole_detector = FrontHolesDetector(self.c4_model)
        self.upper_hole_detector = UpperHolesDetector(self.c4_model)

    def findGameBoard(self):
        pass
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
        event.wait(timeout / 1000.0)
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
