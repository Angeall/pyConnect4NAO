import math

__author__ = 'Anthony Rouneau'


class AlphaBeta(object):
    """
    Simple implementation of a cutoff alpha-beta
    Requires the state object to be hashable so it can use dynamic programming
    """
    def __init__(self, utility_fct, terminal_check_fct, _max_player_id, _min_player_id, _max_depth=7):
        """

        :param utility_fct: objective function that computes a score given a state for one player
        :param terminal_check_fct: function that checks if the game is finished
        :param _max_player_id: the id to use in the utility function
        :param _min_player_id: the id to use in the utility function
        :param _max_depth: the maximum depth the algorithm can explore the tree
        """
        self.min_player_id = _min_player_id
        self.max_player_id = _max_player_id
        self.terminal_test = terminal_check_fct
        self.utility = utility_fct
        self.max_depth = _max_depth
        self.actions = {}  # Will retain the best action for a given state (will speed up the tree search)

    def alpha_beta_searching(self, state):
        value, action = self.max_value(state, -float('inf'), float('inf'), 0)
        return action

    def max_value(self, state, alpha, beta, depth):
        if depth > self.max_depth or self.terminal_test(state):
            return self.utility(state, self.max_player_id)
        max_value = -float('inf')
        best_action = None
        for action in state.possible_actions():
            value = self.min_value(state.make_fake_action(action), alpha, beta, depth+1)
            if value > max_value:
                max_value = value
                best_action = action
                if max_value >= beta:
                    return max_value, best_action
            alpha = max(alpha, value)
        return max_value, best_action

    def min_value(self, state, alpha, beta, depth):
        if depth > self.max_depth or self.terminal_test(state):
            return self.utility(state, self.min_player_id)
        min_value = float('inf')
        best_action = None
        for action in state.possible_actions():
            value = self.max_value(state.make_fake_action(action), alpha, beta, depth + 1)
            if value < min_value:
                min_value = value
                best_action = action
                if min_value <= alpha:
                    return min_value, best_action
            beta = min(beta, value)
        return min_value, best_action

