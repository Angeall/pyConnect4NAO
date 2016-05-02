from utils.ai.alpha_beta import AlphaBeta
from utils.ai.strategy import Strategy

__author__ = 'Anthony Rouneau'


class Naive(Strategy):
    """
    Naive strategy that consists of evaluating if
    it loses or if it wins, nothing more, nothing less.
    """
    WIN = 1000
    LOSE = -1000
    DRAW = 5

    def __init__(self):
        super(Naive, self).__init__()
        self.alpha_beta = AlphaBeta(self.eval, _max_depth=6)

    def eval(self, state, other_player=False):
        factor = 1
        if other_player:
            factor = -1  # If we evaluate for the other player, we must oppose the result
        current_player_won, other_player_won, draw = state.terminal_test()
        if current_player_won:
            # if other_player:
            #     print "MIN win"
            # else:
            #     print "MAX win"
            return factor * self.WIN
        elif other_player_won:
            # if other_player:
            #     print "MAX win"
            # else:
            #     print "MIN win"
            return factor * self.LOSE
        else:
            return factor * self.DRAW

    def choose_next_action(self, state):
        return self.alpha_beta.alpha_beta_searching(state)

    def display_action(self, action):
        print "Chosen action:", action
