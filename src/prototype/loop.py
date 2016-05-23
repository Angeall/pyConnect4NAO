import time

import nao.data
from ai.connect4 import disc
from ai.connect4.game import Game
from ai.connect4.strategy.basic import Basic
from ai.connect4.strategy.nao_vision import NAOVision, ActionNotYetPerformedException, TooManyDifferencesException
from connect4.connect4handler import Connect4Handler
from connect4.connect4tracker import Connect4Tracker
from connect4.detector.front_holes import FrontHolesGridNotFoundException
from connect4.detector.upper_hole import NotEnoughLandmarksException
from connect4.model.default_model import DefaultModel
from nao import data
from utils.ai.game_state import InvalidStateException
from utils.camera import geom

__author__ = 'Anthony Rouneau'


HEAD_STEP = 5
MAX_YAW = 30
MAX_PITCH = 30


class LogicalLoop(object):
    """
    Class that holds the main loop of the project.
    """

    def __init__(self, nao_motion, nao_video, nao_tts, wait_disc_func, ppA=0.05, cA=0.005, rA=0.8, min_detections=3,
                 dist=-1, sloped=True, nao_strategy=Basic, other_strategy=NAOVision):
        """
        :param nao_motion: an instance of the motion controller of NAO
        :type nao_motion: nao.controller.motion.MotionController
        :param nao_video: an instance of the video controller of NAO
        :type nao_video: nao.controller.video.VideoController
        :param nao_tts: an instance of the TTS proxy of NAO
        :type nao_tts: naoqi.ALProxy
        :param ppA: the perfect position accuracy in meters. While the robot is not located to the perfect
                    position, with a sharper accuracy than ppA, the robot continues to move
        :param cA: the coordinates accuracy in meters. While the robot's hand has not reached this
                   accuracy, the robot will continue to move to get its hand to a better place.
        :param rA: the rotation accuracy in radians. While the robot's hand is not inclined with this accuracy
                   compared to the perfect position, the robot will continue to move.
        :param min_detections: the minimum number of success before a detection is considered as successful
        :param dist: the distance in meters between NAO and the game board, -1 = unknown
        :param sloped: True if the game board is sloped from NAO
        :param nao_strategy: the class that defines NAO's strategy
        :param other_strategy: the class that defines the other player's strategy
        """
        self.rA = rA
        self.cA = cA
        self.ppA = ppA
        self.estimated_distance = dist
        self.min_detections = min_detections
        self.sloped = sloped
        self.wait_disc_func = wait_disc_func
        # Setting NAO's controllers
        self.tts = nao_tts
        self.nao_motion = nao_motion
        self.nao_video = nao_video
        self.camera_subscribed = [False, False]
        self.current_yaw = self.nao_motion.DEFAULT_HEAD_YAW
        self.current_pitch = self.nao_motion.DEFAULT_HEAD_PITCH
        self.yaw_sign = 1
        self.pitch_sign = -1

        # Connect 4 detectors and models
        self.c4_model = DefaultModel()
        self.c4_tracker = Connect4Tracker(self.c4_model)
        self.c4_handler = Connect4Handler(self.getNaoImage)
        self.c4_coords = [0, 0, 0, 0, 0, 0]
        # Creating the strategies that will play the game
        self.strategy = nao_strategy()
        if other_strategy is NAOVision:
            self.other_strategy = NAOVision(self.c4_model.image_of_reference.pixel_mapping,
                                            self.c4_handler.front_hole_detector.getPerspective)
        else:
            self.other_strategy = other_strategy()
        # Creating the game and registering the players
        self.game = Game()
        self.NAO_player = self.game.registerPlayer(self.strategy)
        self.human_player = self.game.registerPlayer(self.other_strategy)
        print "Lancement du jeu, la couleur de NAO est le {0}".format(disc.color_string(self.NAO_player.color))
        print "Le premier joueur est la couleur : {0}".format(disc.color_string(self.game.next_player))

    def getNaoImage(self, camera_num=0, res=1):
        """
        :param res: The resolution parameter
        :param camera_num: 0 : TopCamera, 1 : BottomCamera
        :type camera_num: int
        :return: An OpenCV readable image that comes from NAO's camera
        """
        if not self.camera_subscribed[camera_num]:
            ret = self.nao_video.connectToCamera(res=camera_num + 1, fps=30, camera_num=camera_num,
                                                 subscriber_id="C4N_Loop" + str(camera_num))
            self.camera_subscribed[camera_num] = True
            if ret < 0:
                print "Could not open camera"
                return None
        return self.nao_video.getImageFromCamera(camera_num=camera_num)

    def findGameBoard(self):
        """

        """
        i = 0
        distances = [self.estimated_distance]
        if self.estimated_distance == -1:
            distances = [0.5, 1.0, 1.3, 1.75, 2.2, 2.5, 3.0]
        while True:
            for dist in distances:
                try:
                    self.nao_motion.lookAtGameBoard(self.estimated_distance)
                    coords = self.c4_handler \
                        .getUpperHoleCoordinatesUsingFrontHoles(dist, self.sloped, 3,
                                                                self.nao_motion.getCameraTopPositionFromTorso(),
                                                                nao.data.CAM_MATRIX, nao.data.CAM_DISTORSION,
                                                                debug=True, tries=self.min_detections)
                    coords[0] += 0.25  # Fix calibration error
                    self.estimated_distance = coords[0]
                    self.c4_coords = coords
                    return 0
                except FrontHolesGridNotFoundException:
                    i += 1
                    if i > 5:
                        i = 0
                        self.tts.say("Je ne trouve pas le Puissance 4...")
                        self.nao_motion.moveAt(0, 0, 0.8)
                    continue

    def inverseKinematicsConvergence(self, hole_index):
        """
        :param hole_index: the number of the hole above which we want to move NAO's hand
        :return:
        """
        self.nao_motion.moveHead(self.nao_motion.DEFAULT_HEAD_PITCH, self.nao_motion.DEFAULT_HEAD_YAW, True)
        max_tries = 4  # If we don't see any marker after 2 tries, we move NAO's head
        i = 0
        stable = False
        while not stable:
            while i < max_tries:
                try:
                    hole_coord = self.c4_handler \
                        .getUpperHoleCoordinatesUsingMarkers(hole_index,
                                                             self.nao_motion.getCameraBottomPositionFromTorso(),
                                                             data.CAM_MATRIX, data.CAM_DISTORSION,
                                                             tries=self.min_detections)
                    self.resetHead()
                    if abs(hole_coord[5] + 0.505) > self.rA:  # If the board is sloped from NAO, we need to rotate NAO
                        self.nao_motion.moveAt(0, 0, (hole_coord[5] + 0.505)/3)
                        continue
                    dist_from_optimal = geom.vectorize((0.161, 0.113), (hole_coord[0], hole_coord[1]))
                    if abs(dist_from_optimal[0]) > self.ppA or abs(dist_from_optimal[1]) > 2 * self.ppA:
                        self.nao_motion.moveAt(dist_from_optimal[0], dist_from_optimal[1], hole_coord[5] + 0.505)
                        continue
                    self.estimated_distance = hole_coord[0]
                    i = 0
                    self.nao_motion.setLeftHandPosition(hole_coord, mask=63)
                    diff = self.nao_motion.compareToLeftHandPosition(hole_coord)
                    if abs(diff[0]) < self.cA and abs(diff[1]) < 2 * self.cA:
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
                # self.tts.say("Je ne trouve pas les marqueurs dans mon champ de vision")
                self.moveHeadToNextPosition()
                time.sleep(0.500)
                i = 0

    def loop(self):
        self.findGameBoard()
        self.walkTowardConnect4(analysis=not self.game.checkPlayerTurn(self.NAO_player))
        finished = 0
        while not finished:
            if not self.game.checkPlayerTurn(self.NAO_player):
                finished = self.analyseGameState()
            if not finished:
                self.playingRoutine()

    def playingRoutine(self):
        action = self.strategy.chooseNextAction(self.game.game_state)
        self.game.makeMove(action)
        if self.estimated_distance > 0.3:
            self.walkTowardConnect4()
        self.wait_disc_func()
        self.inverseKinematicsConvergence(action)
        if type(self.other_strategy) is NAOVision:
            self.walkBack()

    def walkBack(self):
        """
        Move NAO back so it can see the game board entirely
        """
        self.nao_motion.moveAt(-0.50, 0, 0)
        self.estimated_distance = 0.50
        self.nao_motion.crouch()

    def walkTowardConnect4(self, analysis=False):
        """
        Move NAO to the game board
        """
        self.nao_motion.motion_proxy.wakeUp()
        next_dist = 0.25
        if analysis:
            next_dist = 0.5
        self.nao_motion.moveAt(self.c4_coords[0] - next_dist, self.c4_coords[1], 0)
        self.estimated_distance = next_dist
        # self.nao_motion.moveAt(coords[0], coords[1], coords[5])

    def analyseGameState(self):
        self.nao_motion.crouch()
        played = False
        i = 0
        j = 0
        unstable_state = 0
        self.nao_motion.lookAtGameBoard(self.estimated_distance)
        while not played:
            try:
                if type(self.strategy) is NAOVision:
                    self.c4_handler.detectFrontHoles(self.estimated_distance, False)
                action = self.other_strategy.chooseNextAction(self.game.game_state)
                self.game.makeMove(action)
                print self.game.game_state.board
                if self.NAO_player.won:
                    self.tts.say("Je gagne !")
                    return 1
                elif self.human_player.won:
                    self.tts.say("Tu gagnes !")
                    return 1
                elif self.game.draw:
                    self.tts.say("Match nul!")
                    return 1
                return 0
            except ActionNotYetPerformedException:
                i += 1
                print "Pas d'action jouee..."
            except TooManyDifferencesException:
                self.tts.say("C'est de la triche, je gagne dans ce cas...")
                self.NAO_player.win()
                return 1
            except FrontHolesGridNotFoundException:
                j += 1
                if j > 5:
                    j = 0
                    self.tts.say("Je n'arrive pas a voir le plateau de jeu...")

            except InvalidStateException:
                unstable_state += 1
                if unstable_state < 3:
                    self.tts.say("Je dois avoir un probleme de vue... Laisse moi encore essayer un moment")
                else:
                    self.tts.say("Je n'arrive vraiment pas a voir le pion que tu as ajouter. " +
                                 "Veux-tu bien l'indiquer sur l'ordinateur ?")
                    action = None
                    while type(action) is not int:
                        action = input("Derniere colonne jouee")
                    self.game.makeMove(action)

            time.sleep(4)
            if i > 10:
                i = 0
                self.tts.say("Je t'attends pour jouer")

    def taunt(self):
        pass
        # TODO : optionnal, robot interaction with human

    def moveHeadToNextPosition(self):
        """
        Move NAO's head to the next position of the spiral
        """
        if self.pitch_sign == -1:
            if self.yaw_sign == 1:
                self.yaw_sign = -1
                self.current_yaw += HEAD_STEP
            else:
                if self.yaw_sign == -1:
                    self.pitch_sign = 1
                    self.current_pitch += HEAD_STEP
        elif self.yaw_sign == -1:
            self.yaw_sign = 1
            self.current_yaw += HEAD_STEP
        else:
            self.pitch_sign = -1
            self.current_pitch += HEAD_STEP
        if self.current_yaw > 40 or self.current_pitch > 40:
            self.nao_motion.releaseHead()
            self.tts.say("Veuillez placer ma tete au bon endroit s'il vous plait")
            time.sleep(5)
        else:
            self.nao_motion.moveHead(self.current_pitch * self.pitch_sign,
                                     self.current_yaw * self.yaw_sign,
                                     radians=False)

    def resetHead(self):
        """
        Set the head to the default position
        """
        self.nao_motion.moveHead(self.nao_motion.DEFAULT_HEAD_PITCH, self.nao_motion.DEFAULT_HEAD_YAW, True)
        self.current_pitch = self.nao_motion.DEFAULT_HEAD_PITCH
        self.current_yaw = self.nao_motion.DEFAULT_HEAD_YAW
        self.pitch_sign = -1
        self.yaw_sign = 1
