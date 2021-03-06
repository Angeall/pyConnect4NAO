from utils.ai.game_state import GameState
from utils.ai.strategy import Strategy

__author__ = 'Anthony Rouneau'


class Human(Strategy):
    """
    Let a human play the game
    """

    def __init__(self):
        super(Human, self).__init__()

    def eval(self, state, other_player=False):
        return 0

    def chooseNextAction(self, state):
        """
        :param state:
        :type state: GameState
        :return:
        """
        action_chosen = False
        action = None
        while not action_chosen:
            try:
                action = int(raw_input("Veuillez choisir un trou parmis les suivants : \n"
                                       + str(state.possibleActions()) + " : "))
                if int(action) not in state.possibleActions():
                    continue
                else:
                    break
            except ValueError:
                continue
        return int(action)


