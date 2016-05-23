import math

from naoqi import ALProxy

import nao.data as nao
from utils.camera import geom

__author__ = "Anthony Rouneau"

# NAO coordinate systems
FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2

# Arm movement joints
LARM_CHAIN = ["LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LElbowYaw", "LWristYaw"]
RARM_CHAIN = ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw", "RWristYaw"]
# Arm angles in radians :
ARM_ALONGSIDE_BODY = [1.62, 0.32, -0.03, -1.31, -0.44]
ARM_ALONGSIDE_BODY_R = [1.62, -0.32, 0.03, 1.31, -0.44]
ASKING_HAND = [-0.07, 0.05, -0.55, -1.29, -0.77]
INTERMEDIATE_TOP = [-1.56, 1.22, -0.03, -1.31, -0.44]
INTERMEDIATE_TOP_R = [1.56, -1.22, 0.03, 1.31, -0.44]
INTERMEDIATE_BOTTOM = [1.56, 1.22, -0.03, -1.31, -0.44]
INTERMEDIATE_BOTTOM_R = [-1.56, -1.22, 0.03, 1.31, -0.44]
RAISED = [-1.22, 0.05, -0.55, -1.29, -0.77]


class MotionController:
    # NAO Default head position in radians
    DEFAULT_HEAD_PITCH = -0.05
    DEFAULT_HEAD_YAW = 0.0

    """
    Represents a virtual controller for NAO's motion system
    """
    def __init__(self, robot_ip=None, robot_port=None):
        """
        :param robot_ip: The IP address of the robot
        :type robot_ip: str
        :param robot_port: The port of the robot
        :type robot_port: int
        Creates a new Virtual Controller for NAO
        """
        if robot_ip is None:
            robot_ip = nao.IP
        if robot_port is None:
            robot_port = nao.PORT

        self.ip = robot_ip
        self.port = robot_port

        # Connect and wake up the robot
        self.motion_proxy = ALProxy("ALMotion", robot_ip, robot_port)
        # self.motion_proxy.wakeUp()
        self.motion_proxy.setCollisionProtectionEnabled("Arms", True)
        self.motion_proxy.setMoveArmsEnabled(False, False)
        # self.moveHead(0.114, 0, radians=True)

    def getCameraTopPositionFromTorso(self):
        """
        :return: The 6D coordinates of the top camera of NAO
                 6D coordinates : (x-translat., y-translat., z-translat., x-rot, y-rot, z-rot)
        """
        return self.motion_proxy.getPosition("CameraTop",
                                             FRAME_TORSO,
                                             True)

    def getCameraBottomPositionFromTorso(self):
        """
        :return: The 6D coordinates of the bottom camera of NAO
                 6D coordinates : (x-translat., y-translat., z-translat., x-rot, y-rot, z-rot)
        """
        return self.motion_proxy.getPosition("CameraBottom",
                                             FRAME_TORSO,
                                             True)

    def getLeftHandPosition(self):
        """
        :return: The 6D coordinates of the left hand of NAO
                 6D coordinates : (x-translat., y-translat., z-translat., x-rot, y-rot, z-rot)
        """
        # print self.motion_proxy.getBodyNames("Chains")
        return self.motion_proxy.getPosition("LHand", FRAME_TORSO, True)

    def setLeftHandPosition(self, coord, mask=7, time_limit=3.0):
        """
        :param coord: the coordinates, relative to the robot torso, where the hand will be placed if possible.
                      6D coordinates : (x-translat., y-translat., z-translat., x-rot, y-rot, z-rot)
        :type coord: list
        :param mask: 6 bits unsigned integer that represents which axis will be moved / rotated.
                     The sum of the following values will set the mask.
                     1 : x-axis translation
                     2 : y-axis translation
                     4 : z-axis translation
                     8 : x-axis rotation
                     16: y-axis rotation
                     32: z-axis rotation
        :type mask: int
        :param time_limit: The maximum time, in seconds, that the move can take. The shorter the faster.
        :type time_limit: float
        Move the hand to the given coordinates if possible.
        """
        self.stand()
        self.motion_proxy.positionInterpolations("LArm", FRAME_TORSO, [tuple(coord)], mask, [time_limit])

    def moveAt(self, x, y, z_rot):
        """
        :param x: the distance to travel forward (negative value = backward) in meters
        :type x: float
        :param y: the distance to travel to the left (negative value = to the right) in meters
        :type y: float
        :param z_rot: the rotation angle, in radians, around the vertical axis
        :type z_rot: float
        Move the robot to a certain position, defined by the three parameters.
        """
        self.stand()
        self.motion_proxy.wakeUp()
        self.motion_proxy.moveTo(x, y, z_rot)

    def getLeftArmAngles(self):
        """
        :return: the angles in radians of the left arm of NAO in this order :
            [ShoulderPitch, ShoulderRoll, ElbowYaw, ElbowRoll, WristYaw]
        :rtype: list
        """
        joint_names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"]
        use_sensors = True
        return self.motion_proxy.getAngles(joint_names, use_sensors)

    def moveHead(self, pitch, yaw, radians=False):
        """
        :param pitch: the future pitch of NAO's head
        :param yaw: the future yaw of NAO's head
        :param radians: True if the angles are given in radians. False by default => angles in degree.
        """
        joint_names = ["HeadYaw", "HeadPitch"]
        if not radians:
            yaw = math.radians(yaw)
            pitch = math.radians(pitch)
        angles = [yaw, pitch]
        self.motion_proxy.angleInterpolation(joint_names, angles, 1., True)

    def compareToLeftHandPosition(self, coord, must_print=False):
        """
        :param coord: the 6D coordinates to compare with the left hand position
        :type coord: list
        :return: the difference of position from the hand to the given coordinates [x-axis, y-axis]
        :rtype: np.array
        """
        hand_coord = self.getLeftHandPosition()
        if must_print:
            print coord
            print hand_coord
        return geom.vectorize(hand_coord[0:2], coord[0:2])

    def playDisc(self, hole_coordinates):
        """
        :param hole_coordinates: The 6D translation + rotation vector of the hole
        """
        self.stand()
        self.setLeftHandPosition(hole_coordinates, mask=63)
        self.motion_proxy.openHand("LHand")
        self.motion_proxy.closeHand("LHand")
        self.setLeftArmAlongsideBody()

    def setLeftArmRaised(self, secure=False):
        """
        Raise NAO's left arm to the sky
        """
        self.stand()
        if secure:
            self.motion_proxy.angleInterpolation(LARM_CHAIN, INTERMEDIATE_BOTTOM, 2., True)
            self.motion_proxy.angleInterpolation(LARM_CHAIN, INTERMEDIATE_TOP, 2., True)
        self.motion_proxy.angleInterpolation(LARM_CHAIN, RAISED, 2., True)

    def setLeftArmAlongsideBody(self):
        """
        Move the left arm of NAO alongside his body.
        """
        self.stand()
        self.motion_proxy.angleInterpolation(LARM_CHAIN, INTERMEDIATE_TOP, 2., True)
        self.motion_proxy.angleInterpolation(LARM_CHAIN, INTERMEDIATE_BOTTOM, 2., True)
        self.motion_proxy.angleInterpolation(LARM_CHAIN, ARM_ALONGSIDE_BODY, 2., True)

    def setRightArmAlongsideBody(self):
        """
        Move the left arm of NAO alongside his body.
        """
        self.stand()
        self.motion_proxy.angleInterpolation(RARM_CHAIN, ARM_ALONGSIDE_BODY_R, 2., True)

    def setLeftArmToAskingPosition(self):
        """
        Move the left arm of NAO in a "asking disc" position, and open his left hand.
        """
        self.stand()
        self.motion_proxy.angleInterpolation(LARM_CHAIN, INTERMEDIATE_BOTTOM, 2., True)
        self.motion_proxy.angleInterpolation(LARM_CHAIN, INTERMEDIATE_TOP, 2., True)
        self.motion_proxy.angleInterpolation(LARM_CHAIN, ASKING_HAND, 2., True)
        self.motion_proxy.openHand("LHand")

    def lookAtGameBoard(self, dist):
        """
        :param dist: the supposed distance between NAO and the board
        Make NAO look to the hypothetical game board position, located at "dist" meters from the robot
        """
        self.crouch()
        height = 0.165
        b = height
        c = geom.pythagore(height, dist)  # The length of the side betwaeen NAO's head and the board to look at
        a = dist  # The difference between the theoretical position (1m) and the actual position (dist)
        pitch_angle = geom.al_kashi(b, a, c, None)
        self.moveHead(pitch_angle, 0, radians=True)

    def stand(self):
        """
        Make the robot stand up
        """
        if not self.motion_proxy.robotIsWakeUp():
            self.motion_proxy.wakeUp()

    def crouch(self):
        """
        Crouch the robot, but stiff the head
        """
        self.motion_proxy.rest()
        self.motion_proxy.setStiffnesses("HeadPitch", 1.0)

    def stiffHead(self):
        """
        Set the stiffness of the head to 1 (Max stiff)
        """
        self.motion_proxy.setStiffnesses(["HeadPitch", "HeadYaw"], [1, 1])

    def releaseHead(self):
        """
        Release the stiffness of the head
        """
        self.motion_proxy.setStiffnesses(["HeadPitch", "HeadYaw"], [0, 0])



