from utils.ai.alpha_beta import AlphaBeta
from utils.ai.strategy import Strategy

__author__ = 'Anthony Rouneau'


ALPHA_BETA_MAX_DEPTH = 6


class Basic(Strategy):
    """
    Basic strategy that consists of evaluating if
    it loses or if it wins, nothing more, nothing less.
    """
    WIN = 1000
    LOSE = -1000
    DRAW = 5

    def __init__(self):
        super(Basic, self).__init__()
        self.alpha_beta = AlphaBeta(self.eval, _max_depth=ALPHA_BETA_MAX_DEPTH)

    def eval(self, state, other_player=False):
        factor = 1
        if other_player:
            factor = -1  # If we evaluate for the other player, we must oppose the result
        current_player_won, other_player_won, draw = state.terminalTest()
        if current_player_won:
            return factor * self.WIN
        elif other_player_won:
            return factor * self.LOSE
        else:
            return factor * self.DRAW

    def chooseNextAction(self, state):
        action = self.alpha_beta.alphaBetaSearching(state)
        print "Chosen column: ", action
        print
        return action

