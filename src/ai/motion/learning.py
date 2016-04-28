import numpy as np
from hampy import detect_markers

import nao.data as nao
from nao.controller.motion import MotionController
from nao.controller.video import VideoController
from utils.camera import geom

__author__ = 'Anthony Rouneau'


class Connect4Learning(object):

    def __init__(self, robot_ip=nao.IP, robot_port=nao.PORT):
        """
        :param robot_ip: The IP address of the robot
        :type robot_ip: str
        :param robot_port: The port of the robot
        :type robot_port: int
        Creates a new learning module for NAO
        """
        self.nao_motion = MotionController(robot_ip=robot_ip, robot_port=robot_port)
        self.nao_video = VideoController(robot_ip=robot_ip, robot_port=robot_port)
        self.nao_video.connectToCamera(res=2, fps=30, camera_num=1, subscriber_id="C4Learning")
        self.left_arm_angles = []
        self.min_head_pitch = 0.
        self.max_head_pitch = 0.
        self.min_head_yaw = 0.
        self.max_head_yaw = 0.
        self.selected_hole = 0
        self.shoulder_pitch_array = []
        self.shoulder_pitch_file = None
        self.shoulder_roll_array = []
        self.shoulder_roll_file = None
        self.elbow_yaw_array = []
        self.elbow_yaw_file = None
        self.elbow_roll_array = []
        self.elbow_roll_file = None
        self.wrist_yaw_array = []
        self.wrist_yaw_file = None

    def open_files(self):
        self.shoulder_pitch_array = []
        self.shoulder_pitch_file = open("../../values/learning/shoulder_pitch", 'a')
        self.shoulder_roll_array = []
        self.shoulder_roll_file = open("../../values/learning/shoulder_roll", 'a')
        self.elbow_yaw_array = []
        self.elbow_yaw_file = open("../../values/learning/shoulder_yaw", 'a')
        self.elbow_roll_array = []
        self.elbow_roll_file = open("../../values/learning/shoulder_roll", 'a')
        self.wrist_yaw_array = []
        self.wrist_yaw_file = open("../../values/learning/wrist_yaw", 'a')

    def waiting_nao_position(self):
        raw_input("Please place NAO's left arm in the perfect position and press Enter")
        self.left_arm_angles = self.nao_motion.get_left_arm_angles()
        self.selected_hole = int(raw_input("Enter the index of the selected hole, [0, 6]: "))
        self.min_head_yaw = float(raw_input("Enter the min head yaw in degrees: "))
        self.max_head_yaw = float(raw_input("Enter the max head yaw in degrees: "))
        self.min_head_pitch = float(raw_input("Enter the min head pitch in degrees: "))
        self.max_head_pitch = float(raw_input("Enter the max head pitch in degrees: "))
        self.open_files()

    def learning_routine(self):
        self.nao_motion.raise_left_arm()
        for current_pitch in np.arange(self.min_head_pitch, self.max_head_pitch, 0.5):
            for current_yaw in np.arange(self.min_head_yaw, self.max_head_yaw, 0.5):
                self.nao_motion.move_head(current_pitch, current_yaw, radians=False)
                self.detect_marker(current_pitch, current_yaw)
        self.write_in_file()

    def detect_marker(self, current_pitch, current_yaw):
        marker_found = False, None
        tries = 0
        while not marker_found[0] and tries < 10:
            img = self.nao_video.getImageFromCamera()
            markers = detect_markers(img)
            tries += 1
            for marker in markers:
                if marker.id == (self.selected_hole + 1) * 1000:
                    marker_found = True, marker
        if marker_found[0]:
            self.record(marker_found[1], current_pitch, current_yaw)

    def record(self, marker, pitch, yaw):
        # Variables set
        corners = np.array(geom.sort_rectangle_corners(marker.contours)).ravel().tolist()
        variables = [pitch, yaw]
        variables.extend(corners)
        variables = np.array(variables)

        # Result set
        self.shoulder_pitch_array.append(np.append(variables, self.left_arm_angles[0]))
        self.shoulder_roll_array.append(np.append(variables, self.left_arm_angles[1]))
        self.elbow_yaw_array.append(np.append(variables, self.left_arm_angles[2]))
        self.elbow_roll_array.append(np.append(variables, self.left_arm_angles[3]))
        self.wrist_yaw_array.append(np.append(variables, self.left_arm_angles[4]))

    def write_in_file(self):
        np.savetxt(self.shoulder_pitch_file, np.array(self.shoulder_pitch_array), delimiter=",")
        self.shoulder_pitch_file.close()
        self.shoulder_pitch_array = []
        np.savetxt(self.shoulder_roll_file, np.array(self.shoulder_roll_array), delimiter=",")
        self.shoulder_roll_file.close()
        self.shoulder_roll_array = []
        np.savetxt(self.elbow_yaw_file, np.array(self.elbow_yaw_array), delimiter=",")
        self.elbow_yaw_file.close()
        self.elbow_yaw_array = []
        np.savetxt(self.elbow_roll_file, np.array(self.elbow_roll_array), delimiter=",")
        self.elbow_roll_file.close()
        self.elbow_roll_array = []
        np.savetxt(self.wrist_yaw_file, np.array(self.wrist_yaw_array), delimiter=",")
        self.wrist_yaw_file.close()
        self.wrist_yaw_array = []

    def learn(self):
        while True:
            self.waiting_nao_position()
            self.learning_routine()


if __name__ == '__main__':
    c4l = Connect4Learning("169.254.40.131", 9559)
    c4l.learn()


