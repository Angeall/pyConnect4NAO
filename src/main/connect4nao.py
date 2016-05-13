import threading
import time

from naoqi import ALModule, ALProxy, ALBroker

import nao.data
from ai.connect4.game import Game
from ai.connect4.strategy.naive import Naive
from ai.connect4.strategy.nao_vision import NAOVision, ActionNotYetPerformedException, TooManyDifferencesException
from connect4.connect4handler import Connect4Handler
from connect4.connect4tracker import Connect4Tracker
from connect4.detector.front_holes import FrontHolesDetector, FrontHolesGridNotFoundException
from connect4.detector.upper_hole import UpperHolesDetector, NotEnoughLandmarksException
from connect4.model.default_model import DefaultModel
from nao import data
from nao.controller.motion import MotionController
from nao.controller.video import VideoController
from utils.ai.game_state import InvalidStateException
from utils.camera import geom

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
        self.estimated_distance = -1
        global motion
        # Setting NAO's controllers
        self.tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
        self.nao_motion = MotionController()
        motion = self.nao_motion
        self.nao_video = VideoController()
        self.camera_subscribed = [False, False]
        self.head_position_index = 1
        self.head_positions = [(5, 0), (10, 0), (15, 0), (5, 10), (5, 20), (5, -10), (5, -20)]

        # Connect 4 detectors and models
        self.c4_model = DefaultModel()
        self.c4_tracker = Connect4Tracker(self.c4_model)
        self.c4_handler = Connect4Handler(self.getNaoImage)
        self.front_hole_detector = FrontHolesDetector(self.c4_model)
        self.upper_hole_detector = UpperHolesDetector(self.c4_model)
        self.c4_coords = [0, 0, 0, 0, 0, 0]
        # Creating the strategies that will play the game
        self.strategy = Naive()
        self.vision_strategy = NAOVision(self.c4_model.image_of_reference.pixel_mapping,
                                         self.front_hole_detector.getPerspective())
        # Creating the game and registering the players
        self.game = Game()
        self.NAO_player = self.game.registerPlayer(self.strategy)
        self.human_player = self.game.registerPlayer(self.vision_strategy)

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
        i = 0
        while True:
            distances = [self.estimated_distance]
            if self.estimated_distance == -1:
                distances = [0.5, 1.0, 1.3, 1.75, 2.2, 2.5, 3.0]
            for dist in distances:
                try:
                    coords = self.c4_handler \
                        .getUpperHoleCoordinatesUsingFrontHoles(dist, True, 3,
                                                                self.nao_motion.getCameraTopPositionFromTorso(),
                                                                nao.data.CAM_MATRIX, nao.data.CAM_DISTORSION,
                                                                debug=False, tries=2)
                    self.estimated_distance = dist
                    self.c4_coords = coords
                    break
                except FrontHolesGridNotFoundException:
                    i += 1
                    if i > 5:
                        i = 0
                        self.tts.say("Je ne trouve pas le Puissance 4...")
                        self.moveHeadToNextPosition()
                    continue
                    # TODO : Walk around checking for a Connect 4 (variate distances)

    def inverseKinematicsConvergence(self, hole_index):
        """
        :param hole_index: the number of the hole above which we want to move NAO's hand
        :return:
        """
        self.head_position_index = 0
        self.nao_motion.moveHead(self.nao_motion.DEFAULT_HEAD_PITCH, self.nao_motion.DEFAULT_HEAD_YAW, True)
        max_tries = 5  # If we don't see any marker after 5 tries, we assume we are not in front of the Connect4
        i = 0
        stable = False
        while not stable:
            while i < max_tries:
                try:
                    hole_coord = self.c4_handler \
                        .getUpperHoleCoordinatesUsingMarkers(hole_index,
                                                             self.nao_motion.getCameraBottomPositionFromTorso(),
                                                             data.CAM_MATRIX, data.CAM_DISTORSION, True)

                    if abs(hole_coord[5] + 0.45) > 1:  # If the board is too sloped from the robot, we need to rotate it
                        self.nao_motion.moveAt(0, 0, hole_coord[5] + 0.505)
                        continue
                    dist_from_optimal = geom.vectorize((0.161, 0.113), (hole_coord[0], hole_coord[1]))
                    if abs(dist_from_optimal[0]) > 0.02 or abs(dist_from_optimal[1]) > 0.02:
                        self.nao_motion.moveAt(dist_from_optimal[0], dist_from_optimal[1], hole_coord[5] + 0.505)
                        continue
                    self.estimated_distance = hole_coord[0]
                    i = 0
                    self.nao_motion.setLeftHandPosition(hole_coord, mask=63)
                    diff = self.nao_motion.compareToLeftHandPosition(hole_coord)
                    if abs(diff[0]) < 0.005 and abs(diff[1]) < 0.01:
                        stable = True
                        self.nao_motion.playDisc(hole_coord)
                        break
                    else:
                        self.nao_motion.setLeftArmRaised()
                        self.nao_motion.moveAt(diff[0], diff[1], hole_coord[5] + 0.505)
                        i += 1
                except NotEnoughLandmarksException:
                    i += 1
            if not stable:
                self.tts.say("Je ne trouve pas les marqueurs dans mon champ de vision")
                self.moveHeadToNextPosition()
                i = 0

    def playingRoutine(self):
        action = self.strategy.chooseNextAction(self.game.game_state)
        self.game.makeMove(action)
        self.walkTowardConnect4()
        self.inverseKinematicsConvergence(action)
        self.walkBack()

    def walkBack(self):
        """
        Move NAO back so it can see the game board entirely
        """
        self.nao_motion.moveAt(-0.75, 0, 0)
        self.estimated_distance = 1.
        self.nao_motion.motion_proxy.rest()

    def walkTowardConnect4(self):
        """
        Move NAO to the game board
        """
        self.nao_motion.motion_proxy.wakeUp()
        self.nao_motion.moveAt(self.c4_coords[0] - 0.25, self.c4_coords[1], 0)
        self.estimated_distance = 0.25
        # self.nao_motion.moveAt(coords[0], coords[1], coords[5])

    def analyseGameState(self):
        played = False
        i = 0
        unstable_state = 0
        while not played:
            try:
                self.vision_strategy.chooseNextAction(self.game.game_state)
            except ActionNotYetPerformedException:
                i += 1
            except TooManyDifferencesException:
                self.tts.say("C'est de la triche, je gagne dans ce cas...")
                self.NAO_player.win()
                break
            except InvalidStateException:
                if unstable_state < 3:
                    self.tts.say("Je dois avoir un probleme de vue... Laisse moi encore essayer un moment")
                else:
                    self.tts.say("Je n'arrive vraiment pas a voir le pion que tu as ajouter. " +
                                 "Veux-tu bien l'indiquer sur l'ordinateur ?")
            time.sleep(4)
            if i > 10:
                i = 0
                self.tts.say("Je t'attends pour jouer")
        pass

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

    def moveHeadToNextPosition(self):
        """
        Move NAO's head to the next position
        :return:
        """
        pitch, yaw = self.head_positions[self.head_position_index]
        self.head_position_index += 1
        if self.head_position_index == len(self.head_positions):
            self.head_position_index = 0
        self.nao_motion.moveHead(pitch, yaw)


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
