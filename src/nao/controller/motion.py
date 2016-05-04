import math

from naoqi import ALProxy

import nao.data as nao

__author__ = "Anthony Rouneau"


callbackObject = None
memory_proxy = None
broker = None

FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2


class MotionController:
    def __init__(self, robot_ip=nao.IP, robot_port=nao.PORT):
        """
        :param robot_ip: The IP address of the robot
        :type robot_ip: str
        :param robot_port: The port of the robot
        :type robot_port: int
        Creates a new Virtual Controller for NAO
        """
        self.ip = robot_ip
        self.port = robot_port

        # Connect and wake up the robot
        self.motion_proxy = ALProxy("ALMotion", robot_ip, robot_port)
        self.track_proxy = ALProxy("ALTracker", robot_ip, robot_port)
        self.localization_proxy = ALProxy("ALLocalization", robot_ip, robot_port)
        self.motion_proxy.setCollisionProtectionEnabled("Arms", True)

    def get_camera_top_position_from_torso(self):
        return self.motion_proxy.getPosition("CameraTop",
                                             FRAME_TORSO,
                                             True)

    def get_camera_bottom_position_from_torso(self):
        return self.motion_proxy.getPosition("CameraBottom",
                                             FRAME_TORSO,
                                             True)

    def put_hand_at(self, coord, mask=7):
        self.motion_proxy.setPositions("LArm", FRAME_TORSO, coord, 0.6, mask)
        # self.motion_proxy.positionInterpolations("LArm", 0, [tuple(coord)], mask, [5.0])

    def move_at(self, coord, mask=7):
        self.motion_proxy.setPositions("Legs", FRAME_TORSO, coord, 0.6, mask)

    def get_left_arm_angles(self):
        """
        :return: the angles in radians of the left arm of NAO in this order :
            [ShoulderPitch, ShoulderRoll, ElbowYaw, ElbowRoll, WristYaw]
        :rtype: list
        """
        joint_names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"]
        use_sensors = True
        return self.motion_proxy.getAngles(joint_names, use_sensors)

    def raise_left_arm(self):
        """
        Raise the robot left arm to the sky
        """
        joint_name = "LShoulderPitch"
        angle = -2
        fraction_max_speed = 0.4
        self.motion_proxy.setAngles(joint_name, angle, fraction_max_speed)

    def move_head(self, pitch, yaw, radians=False):
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
        fraction_max_speed = 0.1
        self.motion_proxy.setAngles(joint_names, angles, fraction_max_speed)



    def playDisc(self, hole_coordinates):
        pass


