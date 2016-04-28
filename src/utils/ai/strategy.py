from abc import ABCMeta, abstractmethod

__author__ = 'Anthony Rouneau'


class Strategy:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.player_id = None
        self.other_id = None

    def set_players_id(self, _player_id, _other_id):
        self.player_id = _player_id
        self.other_id = _other_id

    @abstractmethod
    def choose_next_action(self, state):
        pass

    @abstractmethod
    def eval(self, state, other_player=False):
        pass
