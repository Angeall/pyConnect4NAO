from naoqi import ALProxy
import nao.data as nao

__author__ = 'Anthony Rouneau'


class Localizer(object):
    def __init__(self, robot_ip=nao.IP, port=nao.PORT):
        self.localizer = ALProxy("ALLocalization", robot_ip, port)
        self.home = self.localizer.getRobotPosition(True)
        self.localizer.learnHome()
