from abc import ABCMeta, abstractmethod, abstractproperty

__author__ = 'Anthony Rouneau'


class InvalidStateException(BaseException):
    def __init__(self, msg):
        super(InvalidStateException, self).__init__(msg)


class GameState:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def simulateAction(self, action):
        """
        :param action: The action to simulate
        :return: A copy of this instance on which we performed the action
        :rtype: GameState
        """
        if action not in self.possibleActions():
            raise AssertionError("This action is not in the possible actions for this state")
        new_state = self.copy()
        new_state.performAction(action)
        return new_state

    @abstractproperty
    def possibleActions(self):
        """
        :return: The possible actions for this state
        :rtype: list
        """
        pass  # ToImplement

    @abstractproperty
    def copy(self):
        """
        :return: A copy of this state, from which we cann simulate action
        :rtype: GameState
        """
        pass  # ToImplement

    @abstractproperty
    def __hash__(self):
        """
        :return: A hash code for this Game State
        :rtype: int
        """
        print "OK..."
        pass  # ToImplement

    @abstractmethod
    def performAction(self, action):
        """
        :param action: The action to perform on this game state
        :except AssertionError: If the action is not contained in the possible moves,
            it must raise an AssertionError
        """
        pass  # ToImplement

    @abstractproperty
    def terminalTest(self):
        """
        Checks if the game is finished
        :return: Three booleans : (current_player_hasWon, previous_player_hasWon, is_a_draw)
        :rtype: tuple
        """
        pass
