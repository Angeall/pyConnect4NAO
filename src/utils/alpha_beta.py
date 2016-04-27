from game_state import GameState


__author__ = 'Anthony Rouneau'


class AlphaBeta(object):
    """
    Simple implementation of a cutoff alpha-beta
    Assert that the player using this Alpha Beta is the "MAX" player.
    """
    def __init__(self, eval_fct, terminal_check_fct, _max_player_id, _min_player_id, _max_depth=7):
        """

        :param eval_fct: objective function that computes a score given a state for one player
        :type eval_fct: function
        :param terminal_check_fct: function that checks if the game is finished
        :type terminal_check_fct: function
        :param _max_player_id: the id to use in the eval function
        :type _max_player_id: int, whatever
        :param _min_player_id: the id to use in the utility function
        :type _min_player_id: int, whatever
        :param _max_depth: the maximum depth of the tree the algorithm can explore
        :type _max_depth: int
        """
        self.min_player_id = _min_player_id
        self.max_player_id = _max_player_id
        self.terminal_test = terminal_check_fct
        self.eval = eval_fct
        self.max_depth = _max_depth
        self.actions = {}  # Will retain the best action for a given state (will speed up the tree search)

    def alpha_beta_searching(self, state):
        """
        :param state: The current state of the game (including the current player)
        :type state: GameState
        :return: the best action among the possible ones
        """
        value, action = self.max_value(state, -float('inf'), float('inf'), 0)
        return action

    def max_value(self, state, alpha, beta, depth):
        """
        :param state: the state of the current node
        :type state: GameState
        :param alpha: the alpha bound
        :param beta: the beta bound
        :param depth: the current depth in the tree
        :return: the best value and the best action among its children or
                 the value of the terminal state
        Computes the best step possible for the "MAX" Player
        """
        if depth > self.max_depth or self.terminal_test(state):
            return self.eval(state, self.max_player_id)
        best_value = -float('inf')
        best_action = None
        for action in state.possible_actions():
            value = self.min_value(state.simulate_action(action), alpha, beta, depth + 1)
            if value > best_value:
                best_value = value
                best_action = action
                if best_value >= beta:
                    return best_value, best_action
            alpha = max(alpha, value)
        return best_value, best_action

    def min_value(self, state, alpha, beta, depth):
        """
        :param state: the state of the current node
        :type state: GameState
        :param alpha: the alpha bound
        :param beta: the beta bound
        :param depth: the current depth in the tree
        :return: the best value and the best action among its children or
                 the value of the terminal state
        Computes the best step possible for the "MAX" Player
        """
        if depth > self.max_depth or self.terminal_test(state):
            return self.eval(state, self.min_player_id)
        best_value = float('inf')
        best_action = None
        for action in state.possible_actions():
            value = self.max_value(state.simulate_action(action), alpha, beta, depth + 1)
            if value < best_value:
                best_value = value
                best_action = action
                if best_value <= alpha:
                    return best_value, best_action
            beta = min(beta, value)
        return best_value, best_action

