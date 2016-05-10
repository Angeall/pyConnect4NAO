__author__ = 'Anthony Rouneau'

# Color constants
RED = 0
GREEN = 1
EMPTY = -1


def color_string(_color):
    if _color == RED:
        return "red"
    elif _color == GREEN:
        return "green"
    elif _color == EMPTY:
        return "empty"
    else:
        return "??"


def get_opposite_color(_color):
    if _color == RED:
        return GREEN
    else:
        return RED


class Disc(object):

    def __init__(self, _color):
        self.color = _color

    def checkColor(self, _color):
        return _color == self.color
