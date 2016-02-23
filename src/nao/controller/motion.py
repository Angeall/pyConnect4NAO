import numpy as np
from naoqi import ALProxy
import nao.data as nao

__author__ = "Anthony Rouneau"


FRAME_TORSO = 0
FRAME_WORLD = 1
FRAME_ROBOT = 2


class MotionController:
    def __init__(self, robot_ip=nao.IP, port=nao.PORT):
        """
        Creates a new Virtual Controller for NAO
        :param robot_ip: The IP address of the robot
        :type robot_ip: str
        :param port: The port of the robot
        :type port: int
        """
        # Connect and wake up the robot
        self.motion_proxy = ALProxy("ALMotion", robot_ip, port)
        self.track_proxy = ALProxy("ALTracker", robot_ip, port)
        self.motion_proxy.setCollisionProtectionEnabled("Arms", True)

    def getCameraPositionFromWorld(self):
        return self.motion_proxy.getPosition("CameraTop",
                                             FRAME_WORLD,
                                             True)

    def putHandAt(self, coord, mask=7):
        self.motion_proxy.setPositions("LArm", 1, coord, 0.1, mask)

    def moveAt(self, coord, mask=7):
        self.motion_proxy.setPositions("Legs", 1, coord, 0.1, mask)
