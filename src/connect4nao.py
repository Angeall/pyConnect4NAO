"""\n
Welcome to Connect4NAO.

Usage:
  connect4nao.py [--help] <command> [-h | --help | <args>...]

Options:
  -h --help         Show this screen.
  --version         Show the version.

Commands:
   game          Launch a virtual Connect 4 game (without the robot)
   board         Tries to detect the game board in front of the robot
   markers       Tries to detect Hamming (7, 4) markers in front of the robot
   state         Analyse the game state of the board in front of NAO
   coordinates   Computes the 3D coordinates of a upper hole
   ik            Make NAO grab and drop a disc in the given hole
   play          (Prototype) play the Connect 4 autonomously
"""
import threading
from time import sleep

import cv2
from docopt import docopt
from hampy import detect_markers
from naoqi import ALBroker, ALModule, ALProxy

from ai.connect4 import disc
from ai.connect4.c4_state import C4State
from ai.connect4.game import Game
from ai.connect4.strategy import basic
from ai.connect4.strategy.basic import Basic
from ai.connect4.strategy.human import Human
from ai.connect4.strategy.nao_vision import NAOVision
from connect4.connect4handler import Connect4Handler
from connect4.detector.front_holes import FrontHolesGridNotFoundException
from connect4.detector.upper_hole import NotEnoughLandmarksException
from connect4.image.default_image import DefaultConnect4Image
from connect4.model.default_model import DefaultModel
from nao import data
from nao.controller.motion import MotionController
from nao.controller.video import VideoController
from prototype.loop import LogicalLoop

__author__ = 'Anthony Rouneau'

# The docstrings of the commands

GAME = """Usage: connect4nao.py game [options]

  -h --help            Show this screen.
  --player1=<str>      Defines the strategy of the player 1 [default: basic].
                       Can be either basic (choice-making AI) or input (human-controlled).
  --player2=<str>      Defines the strategy of the player 2 [default: human].
                       Can be either basic (choice-making AI) or human (human-controlled).
  --max-depth=<int>    Defines the maximum depth of the alpha-beta exploration [default: 6]
"""

BOARD = """Usage: connect4nao.py board [options]

  -h --help                 Show this screen.
  --no-robot                Uses a camera of the computer stream rather than the robot
  --sloped                  If set, the detection consider the board as sloped

  --ip=<ip>                 IP of the robot [default: 169.254.254.250].
  --port=<int>              Port of the robot [default: 9559].
  --dist=<int>              Defines the distance in meters [default: 1.0]
                            between the robot and the game board
  --min-detections=<int>    Defines the minimum number of stable detections [default: 3]
                            for the detection to be considered as successful
  --cam-no=<int>            Defines the camera used [default: 0].
                            If the robot is used : 0=Top_Camera, 1=Bottom_Camera,
                            otherwise, defines the camera hardware used.
"""

MARKERS = """Usage: connect4nao.py markers [options]

  -h --help         Show this screen.
  --no-image        Disable the image output
  --no-robot        Uses a camera of the computer stream rather than the robot

  --ip=<str>        IP of the robot [default: 169.254.254.250].
  --port=<int>      Port of the robot [default: 9559].
  --cam-no=<int>    Defines the camera used [default: 1].
                    If the robot is used : 0=Top_Camera, 1=Bottom_Camera,
                    otherwise, defines the camera hardware used.
"""

STATE = """Usage: connect4nao.py state [options]

  -h --help                 Show this screen.
  --no-image                Disable the image output
  --no-robot                Uses a camera of the computer stream rather than the robot
  --sloped                  If set, the detection consider the board as sloped

  --ip=<ip>                 IP of the robot [default: 169.254.254.250].
  --port=<int>              Port of the robot [default: 9559].
  --dist=<int>              Defines the distance in meters [default: 1]
                            between the robot and the game board
  --min-detections=<int>    Defines the minimum number of stable detections [default: 3]
                            for the detection to be considered as successful
  --cam-no=<int>            Defines the camera used [default: 0].
                            If the robot is used : 0=Top_Camera, 1=Bottom_Camera,
                            otherwise, defines the camera hardware used.
"""

COORDINATES = """Usage: connect4nao.py coordinates [options]

  Detects the coordinates of the hole set by --hole,
  using the Hamming markers (except --board is set)

  -h --help                 Show this screen.
  --no-image                Disable the image output
  --board                   If set, use the front holes of the board to detect the coordinates
  --sloped                  If set, the detection consider the board as sloped, used if --board is set

  --ip=<ip>                 IP of the robot [default: 169.254.254.250].
  --port=<int>              Port of the robot [default: 9559].
  --hole=<int>              Defines the hole from which we want to detect the position [default: 3]
  --dist=<int>              Defines the distance in meters [default: 1]
                            between the robot and the game board, used if --board is set.
  --min-detections=<int>    Defines the minimum number of stable detections [default: 3]
                            for the detection to be considered as successful
  --cam-no=<int>            Defines the camera used [default: 0].
                            0=Top_Camera, 1=Bottom_Camera,
"""

IK = """Usage: connect4nao.py ik [options]

  -h --help         Show this screen.
  --no-image        Disable the image output
  --no-grab         If set, NAO will not grab a disc and will
                    assume it already has one.

  --ip=<str>        IP of the robot [default: 169.254.254.250].
  --port=<int>      Port of the robot [default: 9559].
  --hole=<int>      Defines the hole in which we want to drop a disc [default: 2]
  --ppA=FLOAT       The perfect position accuracy in meters. While the robot is not located to the perfect
                    position, with a sharper accuracy than ppA, the robot continues to move
                    [default: 0.05]
  --cA=FLOAT        The coordinates accuracy in meters. While the robot's hand has not reached this
                    accuracy, the robot will continue to move to get its hand to a better place.
                    [default: 0.005]
  --rA=FLOAT        The rotation accuracy in radians.
                    While the robot's hand is not inclined with this accuracy
                    compared to the perfect position, the robot will continue to move.
                    [default: 0.8]
"""

PLAY = """Usage: connect4nao.py play [options]

  -h --help                 Show this screen.
  --sloped                  If set, the detection consider the board as sloped
  --no-grab                 If set, NAO will not grab a disc and will
                            assume it already has one.

  --ip=<ip>                 IP of the robot [default: 169.254.254.250].
  --port=<int>              Port of the robot [default: 9559].
  --dist=<int>              Defines the distance in meters [default: -1.0]
                            between the robot and the game board (-1 = unknown)
  --min-detections=<int>    Defines the minimum number of stable detections [default: 3]
                            for the detection to be considered as successful
  --nao-strategy=<str>      Defines the strategy of NAO [default: basic].
                            Can be either basic (choice-making AI) or input (human-controlled).
  --other-strategy=<str>    Defines the strategy of the other player [default: human].
                            Can be either vision (vision state analysis) or human (human-controlled).
  --max-depth=<int>         Defines the maximum depth of the alpha-beta exploration [default: 6]
  --ppA=FLOAT               The perfect position accuracy in meters. While the robot is not located to the perfect
                            position, with a sharper accuracy than ppA, the robot continues to move
                            [default: 0.05]
  --cA=FLOAT                The coordinates accuracy in meters. While the robot's hand has not reached this
                            accuracy, the robot will continue to move to get its hand to a better place.
                            [default: 0.005]
  --rA=FLOAT                The rotation accuracy in radians.
                            While the robot's hand is not inclined with this accuracy
                            compared to the perfect position, the robot will continue to move.
                            [default: 0.8]
"""

# The global functions

cap = None
nao_video = None
nao_motion = None
nao_tracking = None
connect4_model = DefaultModel()

# Global variables for the event reaction of the waitForDisc method.
event = threading.Event()
callbackObject = None
memory_proxy = None
broker = None


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
        global event
        nao_motion.motion_proxy.closeHand("LHand")
        event.set()


class DiscNotObtainedException(BaseException):
    """
    Exception raised when the waitForDisc method reaches a timeout.
    """

    def __init__(self, msg):
        super(DiscNotObtainedException, self).__init__(msg)


def close_camera():
    global nao_video, cap, nao_motion
    if nao_video is not None:
        nao_video.disconnectFromCamera()
        nao_motion.crouch()
    if cap is not None:
        cap.release()
    return 0


def get_webcam_image(cam_num=0, res=1):
    global cap
    if cap is None:
        cap = cv2.VideoCapture(cam_num)
        if res == 1:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        elif res == 2:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print "Connected to camera {0} of the computer".format(cam_num)
    has_read, img = cap.read()
    if not has_read:
        print "Image not readable"
        return None
    return img


def get_nao_image(camera_num=0, res=1):
    global nao_video, nao_motion, nao_tracking
    if nao_video is None:
        nao_video = VideoController()
        if nao_motion is None:
            nao_motion = MotionController()
        nao_video.disconnectFromCamera()
        ret = nao_video.connectToCamera(res=res, fps=30, camera_num=camera_num)
        if ret < 0:
            print "Could not open camera"
            return None
    return nao_video.getImageFromCamera(camera_num=camera_num)


def draw_circles(img, circles):
    img2 = img.copy()
    for i in circles:
        # draw the outer circle
        cv2.circle(img2, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img2, (i[0], i[1]), 2, (0, 0, 255), 2)
    return img2


def wait_for_disc(timeout=180000):
    """
    :param timeout: the maximum time to wait, in milliseconds, for a disc, after that, assumes it has the disc
    """
    global event, callbackObject, broker
    nao_motion.setLeftArmToAskingPosition()
    # self.memory_proxy.subscribeToEvent("FrontTactilTouched", "HeadSensorCallbackModule", "HeadTouched")
    if callbackObject is None:
        callbackObject = HeadSensorCallbackModule()
    # Waiting for the detector to detect landmarks
    event.wait(timeout / 1000.0)
    nao_motion.setLeftArmRaised()
    # time.sleep(timeout)
    # Exiting...
    # broker.shutdown()
    event.clear()


# The functions called by the commands


def game(args):
    strategies = {'basic':  Basic,
                  'human':  Human}
    player1 = strategies.get(args['--player1'], None)
    player2 = strategies.get(args['--player2'], None)
    if player1 is None:
        exit("{0} is not a valid strategy. The valid strategies are: basic, human".format(args['--player1']))
    if player2 is None:
        exit("{0} is not a valid strategy. The valid strategies are: basic, human".format(args['--player2']))
    print "A new game is created."
    print
    print "-1 = Empty, 0 = Red, 1 = Green"
    print
    new_game = Game()
    basic.ALPHA_BETA_MAX_DEPTH = int(args['--max-depth'])
    new_game.registerPlayer(player1())
    color_int = new_game.players[0].color
    print "Player 1: {0} with color {1} ({2})".format(player1.__name__, disc.color_string(color_int), color_int)
    new_game.registerPlayer(player2())
    color_int = new_game.players[1].color
    print "Player 2: {0} with color {1} ({2})".format(player2.__name__, disc.color_string(color_int), color_int)
    print
    print
    new_game.playLoop()


def board(args):
    global nao_motion
    data.IP = args['--ip']
    data.PORT = int(args['--port'])
    next_img_func = get_nao_image
    if args['--no-robot']:
        next_img_func = get_webcam_image
    myc4 = Connect4Handler(next_img_func, cam_no=int(args['--cam-no']))
    dist = float(args['--dist'])
    sloped = args['--sloped']
    tries = int(args['--min-detections'])
    nao_motion = MotionController()
    nao_motion.lookAtGameBoard(dist)
    while True:
        try:
            myc4.detectFrontHoles(dist, sloped, tries=tries)
            cv2.imshow("Connect 4 Perspective", myc4.front_hole_detector.getPerspective())
        except FrontHolesGridNotFoundException:
            pass
        img2 = draw_circles(myc4.img, myc4.circles)
        cv2.imshow("Circles detected", img2)
        cv2.imshow("Original picture", myc4.img)
        if cv2.waitKey(10) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
    return 0


def markers(args, must_print=True):
    global nao_motion
    data.IP = args['--ip']
    data.PORT = int(args['--port'])
    next_img_func = get_nao_image
    try:
        if args['--no-robot']:
            next_img_func = get_webcam_image
    except KeyError:
        pass
    end_reached = False
    nao_motion = MotionController()
    nao_motion.stand()
    while not end_reached:
        img = next_img_func(int(args['--cam-no']), res=2)

        detected_markers = detect_markers(img)

        for m in detected_markers:
            m.draw_contour(img)
            cv2.putText(img, str(m.id), tuple(int(p) for p in m.center),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            if must_print:
                print "ID: ", str(m.id), "\n", "Contours: ", str(m.contours.ravel().reshape(-1, 2).tolist())
                print
            else:
                end_reached = True
        print
        if not args['--no-image']:
            cv2.imshow('Markers', img)
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            return 0


def state(args):
    global nao_motion
    print
    print "-1 = Empty, 0 = Red, 1 = Green"
    print
    data.IP = args['--ip']
    data.PORT = int(args['--port'])
    next_img_func = get_nao_image
    if args['--no-robot']:
        next_img_func = get_webcam_image
    myc4 = Connect4Handler(next_img_func, cam_no=int(args['--cam-no']))
    dist = float(args['--dist'])
    sloped = args['--sloped']
    tries = int(args['--min-detections'])

    ref_mapping = DefaultConnect4Image().generate2DReference()
    strategy = NAOVision(ref_mapping, lambda: perspective)

    strategy.player_id = disc.GREEN
    test_state = C4State()
    nao_motion = MotionController()
    nao_motion.lookAtGameBoard(dist)
    while True:
        try:
            myc4.detectFrontHoles(dist, sloped, tries=tries)
            perspective = myc4.front_hole_detector.getPerspective()
            if not args['--no-image']:
                cv2.imshow("Perspective", perspective)
            game_state = strategy.analyseFullImage(test_state, img=perspective, debug=True)
            print game_state
            print
        except BaseException:
            pass
        if cv2.waitKey(1) == 27:
            print "Esc pressed : exit"
            close_camera()
            break
        sleep(0.5)


def coordinates(args):
    data.IP = args['--ip']
    data.PORT = int(args['--port'])
    global nao_motion
    nao_motion = MotionController()
    camera_position_func = nao_motion.getCameraBottomPositionFromTorso
    if int(args['--cam-no']) == 0:
        camera_position_func = nao_motion.getCameraTopPositionFromTorso
    myc4 = Connect4Handler(get_nao_image, cam_no=int(args['--cam-no']))
    tries = int(args['--min-detections'])
    if args['--board']:
        dist = float(args['--dist'])
        sloped = args['--sloped']
        while True:
            try:
                coords = myc4.getUpperHoleCoordinatesUsingFrontHoles(dist, sloped, int(args['--hole']),
                                                                     camera_position_func(),
                                                                     camera_matrix=data.CAM_MATRIX,
                                                                     camera_dist=data.CAM_DISTORSION,
                                                                     tries=tries, debug=not(args['--no-image']))
                # We want the coordinates of the center of the hole, not the hand ideal position
                coords[2] -= 0.12
                coords[5] -= 0.505
                coords[1] -= 0.028
                coords[0] += 0.25
                print coords
            except FrontHolesGridNotFoundException:
                print
            if not(args['--no-image']):
                if cv2.waitKey(50) == 27:
                    print "Esc pressed : exit"
                    close_camera()
                    return 0
    else:
        nao_motion.stand()
        while True:
            try:
                coords = myc4.getUpperHoleCoordinatesUsingMarkers(int(args['--hole']),
                                                                  camera_position_func(),
                                                                  data.CAM_MATRIX, data.CAM_DISTORSION,
                                                                  res=640,
                                                                  debug=False)
                if not args['--no-image']:
                    markers(args, must_print=False)
                # We want the coordinates of the center of the hole, not the hand ideal position
                coords[2] -= 0.12
                coords[5] -= 0.505
                coords[1] -= 0.028
                coords[0] += 0.01
                print coords
                sleep(0.5)
            except NotEnoughLandmarksException:
                pass
            if cv2.waitKey(50) == 27:
                print "Esc pressed : exit"
                close_camera()
                return 0
    return 0


def ik(args):
    global broker, nao_motion, nao_video
    data.IP = args['--ip']
    data.PORT = int(args['--port'])
    broker = ALBroker("myBroker", "0.0.0.0", 0, data.IP, data.PORT)
    nao_motion = MotionController()
    nao_video = VideoController()
    nao_motion.stand()
    nao_tts = ALProxy("ALTextToSpeech", data.IP, data.PORT)
    try:
        loop = LogicalLoop(nao_motion=nao_motion, nao_video=nao_video, nao_tts=nao_tts,
                           ppA=float(args['--ppA']), cA=float(args['--cA']), rA=float(args['--rA']),
                           min_detections=1, wait_disc_func=lambda: None)
        if not args['--no-grab']:
            wait_for_disc()
        else:
            nao_motion.motion_proxy.closeHand("LHand")
            nao_motion.setLeftArmRaised(secure=True)
        loop.inverseKinematicsConvergence(int(args['--hole']))
        nao_motion.crouch()
    except KeyboardInterrupt:
        print "Keyboard interrupt"
        broker.shutdown()
    return 0


def play(args):
    global broker, nao_motion, nao_video
    nao_strategies = {'basic': Basic,
                      'human': Human}
    other_strategies = {'vision': NAOVision,
                        'human': Human}

    nao_strat = nao_strategies.get(args['--nao-strategy'], None)
    other_strat = other_strategies.get(args['--other-strategy'], None)
    if nao_strat is None:
        exit("{0} is not a valid strategy. The valid strategies for NAO are basic and "
             "human".format(args['--nao-strategy']))
    if other_strat is None:
        exit("{0} is not a valid strategy. The valid strategies for the other player are "
             "vision and human".format(args['--other-strategy']))
    basic.ALPHA_BETA_MAX_DEPTH = int(args['--max-depth'])
    data.IP = args['--ip']
    data.PORT = int(args['--port'])
    broker = ALBroker("myBroker", "0.0.0.0", 0, data.IP, data.PORT)
    nao_motion = MotionController()
    nao_video = VideoController()
    nao_tts = ALProxy("ALTextToSpeech", data.IP, data.PORT)
    try:
        loop = LogicalLoop(nao_motion=nao_motion, nao_video=nao_video, nao_tts=nao_tts,
                           ppA=float(args['--ppA']), cA=float(args['--cA']), rA=float(args['--rA']),
                           min_detections=int(args['--min-detections']), sloped=args['--sloped'],
                           dist=float(args['--dist']), nao_strategy=nao_strat, other_strategy=other_strat,
                           wait_disc_func=wait_for_disc, )
        loop.loop()
    except KeyboardInterrupt:
        print "Keyboard interrupt"
    finally:
        broker.shutdown()
    return 0


if __name__ == '__main__':
    arguments = docopt(__doc__, options_first=True, version='1.0.0')
    try:
        if arguments['<command>'] == 'game':
            game(docopt(GAME))
        elif arguments['<command>'] == 'board':
            board(docopt(BOARD))
        elif arguments['<command>'] == 'markers':
            markers(docopt(MARKERS))
        elif arguments['<command>'] == 'state':
            state(docopt(STATE))
        elif arguments['<command>'] == 'coordinates':
            coordinates(docopt(COORDINATES))
        elif arguments['<command>'] == 'ik':
            ik(docopt(IK))
        elif arguments['<command>'] == 'play':
            play(docopt(PLAY))
        else:
            exit("{0} is not a command. See 'connect4nao.py --help'.".format(arguments['<command>']))
    except KeyboardInterrupt:
        close_camera()
        exit("Keyboard interrupt")
