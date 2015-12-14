import src.utils.geom as geom
import numpy as np

__author__ = 'Anthony Rouneau'


def estimate_minradius(dist):
    return int(4.4143*(dist**(-1.1446)))


def estimate_maxradius(dist):
    return int(round(8.5468*(dist**(-0.7126))))


class Connect4(object):
    def __init__(self, disc=5.6, length=51.9, width=6.6, height=33.7,
                 hole_length=5.85, hole_width=0.95, hole_h_space=0.95, hole_v_margin=0.4, hole_h_margin=2.75,
                 circle=4.6, circle_h_space=2.183, circle_v_space=0.9, circle_h_margin=3.3, circle_v_margin=0.8):
        self.disc = disc
        self.length = length
        self.width = width
        self.height = height
        self.hole_length = hole_length
        self.hole_width = hole_width
        self.hole_h_space = hole_h_space
        self.hole_v_margin = hole_v_margin
        self.hole_h_margin = hole_h_margin
        self.circle = circle
        self.circle_h_space = circle_h_space
        self.circle_v_space = circle_v_space
        self.circles_h_margin = circle_h_margin
        self.circles_v_margin = circle_v_margin

    def computeMaxRadiusRatio(self, distance):
        """
        Computes the max ratio between the radius of the circle that is the farthest from the robot
        and the radius of the circle that is the closest from the robot.
        :param distance: The distance between the robot and the farthest circle in the Connect 4 grid in cm
        :return: The max radius ratio
        """
        max_angle = np.pi / 2.
        ab = distance  # The length of the vector between the robot and the
        #                farthest point of the farthest vector
        bc = self.circle  # The length of the vector of a circle
        ac = geom.al_kashi(b=ab, c=bc, angle=max_angle)   # The length of the vector between the robot and the closest
        #                                                   point of the farthest vector
        beta = geom.al_kashi(a=bc, b=ab, c=ac)  # Angle of vision of the robot to the farthest vector
        de = bc  # de and bc are the same vectors
        bd = self.length - de  # bd is the length of the connect4 minus one vector
        ad = geom.al_kashi(b=ab, c=bd, angle=max_angle)  # The length of the vector between the robot and the farthest
        #                                                  point of the closest vector
        be = self.length  # The length of the connect4
        ae = geom.al_kashi(b=ab, c=be, angle=max_angle)  # The length of the vector between the robot and the
        #                                                  closest point of the closest vector
        alpha = geom.al_kashi(a=de, b=ad, c=ae)  # Angle of vision of the robot to the closest vector
        max_error = geom.point_distance()
        return alpha/beta

    def computeMinMaxRadius(self, distance, sloped=False):
        min_radius = estimate_minradius(distance)
        max_radius = estimate_maxradius(distance)
        if sloped:
            radius_ratio = self.computeMaxRadiusRatio(distance)
            max_radius *= radius_ratio
        return min_radius, max_radius
