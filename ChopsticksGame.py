"""
ChopsticksGame.py
A subclass of aima's Game class. A game is similar to a problem, but it has a utility for each state and a terminal
test instead of a path cost and a goal test.
"""
from aima.utils import *
from aima.games import Game
from aima.games import GameState
from copy import deepcopy

__author__ = "Chris Campell"
__version__ = "10/3/2017"


class ChopsticksGame(Game):
    """
    TODO: class header.
    """
    initial = None

    def __init__(self, num_hands=2, num_fingers=5):
        # self.initial = {'human': (1,1), 'cpu':(1,1), 'turn': 'h'}
        self.num_hands = num_hands
        self.num_fingers = num_fingers
        # Every move is possible starting out; takes the form (from_hand, to_opponents_hand) indexed L=0, R=1:
        moves = [(from_hand, to_hand) for from_hand in range(0, num_hands) for to_hand in range(0, num_hands)]
        human_hands = tuple(1 for i in range(num_hands))
        cpu_hands = tuple(1 for i in range(num_hands))
        self.initial = GameState(to_move='h', utility=0, board={'human': human_hands, 'cpu': cpu_hands}, moves=moves)

    def actions(self, state):
        """
        actions: Returns a list of allowable moves given the current state.
        :param state: The state of the game.
        :return possible_actions: A list of performable actions of the form (from_hand: L or R, to_hand: L or R).
        """
        f_hands = []
        t_hands = []
        if state.to_move == 'h':
            for i in range(len(state.board['human'])):
                if state.board['human'][i] == 0:
                    f_hands.append(i)
            for j in range(len(state.board['cpu'])):
                if state.board['cpu'][j] == 0:
                    t_hands.append(j)
        else:
            for i in range(len(state.board['human'])):
                if state.board['human'][i] == 0:
                    t_hands.append(i)
            for j in range(len(state.board['cpu'])):
                if state.board['cpu'][j] == 0:
                    f_hands.append(j)

        state.move = [(from_hand, to_hand) for from_hand in f_hands for to_hand in t_hands]
        return state.move

    def update_game_board(self, state, move):
        """
        update_game_board: Helper method for result; updates the gameboard (number of fingers in each hand) after
            the specified move is applied.
        :param state: The initial GameState.
        :param move: The move to apply to the GameState.
        :return resultant_game_board: The resultant state of the gameboard after applying the given move.
        """
        resultant_game_board = {'human': None, 'cpu': None}
        # Update the board:
        from_hand = move[0]
        to_hand = move[1]
        if state.to_move == 'h':
            # It is the human's turn to move:
            # Update the finger count on the appropriate hand:
            cpu_updated_to_hand = ((state.board['cpu'][to_hand]
                                    + state.board['human'][from_hand]) % 5)
            # Tuples are immutable so we need a temporary list to modify.
            temp_cpu_hand = list(state.board['cpu'])
            # Iterate through each hand and update the appropriate one:
            for hand, num_fingers in enumerate(temp_cpu_hand):
                if hand == to_hand:
                    temp_cpu_hand[hand] = cpu_updated_to_hand
            # Now that the appropriate hand has been updated, type cast back to a tuple and we are done:
            resultant_game_board['cpu'] = tuple(temp_cpu_hand)
            resultant_game_board['human'] = tuple(state.board['human'])
        else:
            # It is the computer's turn to move:
            # Update the finger count on the appropriate hand:
            human_updated_to_hand = ((state.board['human'][to_hand]
                                      + state.board['cpu'][from_hand]) % 5)
            # Tuples are immutable so we need a temporary list to modify.
            temp_human_hand = list(state.board['human'])
            # Iterate through each hand and update the appropriate one:
            for hand, num_fingers in enumerate(temp_human_hand):
                if hand == to_hand:
                    temp_human_hand[hand] = human_updated_to_hand
            # Now that the appropriate hand has been updated, type cast back to a tuple and we are done:
            resultant_game_board['human'] = tuple(temp_human_hand)
            resultant_game_board['cpu'] = state.board['cpu'].copy()
        return resultant_game_board

    def compute_utility(self, game_board, move, player):
        """
        calculate_utility: Helper method for result; same as AIMA implementation. Calculates the utility given the
            below parameters. Returns 0 regardless of the player if the result is a tie. Returns the utility as a win
            or a loss dependent upon who is asking for the utility (the player parameter).
        :param game_board: The gameboard after executing the specified move.
        :param move: The move made to produce the current gameboard.
        :param player The player performing the utility calculation.
        :return utility: The utility of the state resulting from the provided game_board when the provided move is
            applied; as viewed from the perspective of the provided player.
        """
        human_sum = sum(list(game_board['human']))
        cpu_sum = sum(list(game_board['cpu']))

        if human_sum == 0:
            # The human has no fingers left.
            if player == 'h':
                # The agent requesting the utility calculation is the human.
                return -1
            else:
                # The agent requesting the utility calculation is the cpu.
                return 1
        elif cpu_sum == 0:
            # The cpu has no fingers left.
            if player == 'h':
                # The agent requesting the utility calculation is the human.
                return 1
            else:
                # The agent requesting the utility calculation is the cpu.
                return -1
        else:
            # The utility of the state is unknown or a tie.
            return 0

    def compute_moves(self, player, game_board):
        """
        compute_moves: Helper method for a partial GameState in the instantiation process via self.resultant_state().
            Returns a list of allowable moves given all relevant GameState parameters. Note that the GameState itself
            has not been supplied because this method is used to generate the allowable moves in a GameState which is
            to be constructed pending this method's execution.
        :param player: The player for whom possible moves should be computed.
        :param game_board: The gameboard from which possible moves should be computed.
        :return moves: A list of performable actions of the form (from_hand: L or R, to_hand: L or R).
        """
        moves = []
        if player == 'h':
            # It is the human who wants to know possible moves.
            for human_hand, human_num_fingers in enumerate(game_board['human']):
                from_hand = human_hand
                # Determine which of the opponents hands you can interact with:
                for cpu_hand, cpu_num_fingers in enumerate(game_board['cpu']):
                    to_hand = cpu_hand
                    if human_num_fingers > 0 and cpu_num_fingers > 0:
                        # You can only execute a move if your hand is not out and your opponent's hand is not out.
                        moves.append((from_hand, to_hand))
        else:
            # It is the computer who wants to know possible moves.
            for cpu_hand, cpu_num_fingers in enumerate(game_board['cpu']):
                from_hand = cpu_hand
                # Determine which of the opponents hands you can interact with:
                for human_hand, human_num_fingers in enumerate(game_board['human']):
                    to_hand = human_hand
                    if cpu_num_fingers > 0 and human_num_fingers > 0:
                        # You can only execute a move if your hand is not out and your opponent's  hand is not out.
                        moves.append((from_hand, to_hand))
        return moves

    def result(self, state, move):
        """
        result: Returns the state that results from making a move in the provided state.
        :param state: The initial state.
        :param move: The move performed in the initial state of the form: (from_hand, to_hand)
        :return resultant_state: The GameState resulting from the given move.
        """
        # Update the to_move field appropriately:
        # After this function is done executing, it will be the other players turn:
        updated_to_move = None
        if state.to_move == 'h':
            updated_to_move = 'c'
        else:
            updated_to_move = 'h'
        # Update the gameboard appropriately:
        updated_board = self.update_game_board(state=state, move=move)
        # Update the utility using the new board obtained by the specified move according to player who executed it:
        updated_utility = self.compute_utility(game_board=updated_board, move=move, player=state.to_move)
        # Determine which moves are possible in the new state from the new players perspective:
        updated_moves = self.compute_moves(player=updated_to_move, game_board=updated_board)
        # Construct a new GameState using all updated state information and return it to the method invoker:
        resultant_state = GameState(to_move=updated_to_move, utility=updated_utility,
                                         board=updated_board, moves=updated_moves)
        return resultant_state

    def utility(self, state, player):
        """
        utility: The value of the final state which is returned to the player.
        :param state:
        :param player:
        :return:
        """
        if state.to_move == 'h' and player == 'h':
            if state.board['cpu'] == (0, 0) or state.board['cpu'] == (0,0,0):
                return 1
            else:
                return 0
        elif state.to_move == 'c' and player == 'h':
            if state.board['human'] == (0, 0) or state.board['human'] == (0, 0, 0):
                return -1
            else:
                return 0
        elif state.to_move == 'h' and player == 'c':
            if state.board['cpu'] == (0, 0) or state.board['cpu'] == (0, 0, 0):
                return -1
            else:
                return 0
        elif state.to_move == 'c' and player == 'c':
            if state.board['human'] == (0, 0) or state.board['human'] == (0, 0, 0):
                return 1
            else:
                return 0

    def terminal_test(self, state):
        """
        terminal_test: Returns whether or not the provided state is a final state for the game.
        :param state:
        :return:
        """
        raise NotImplementedError

    def display(self, state):
        if isinstance(state, GameState):
            human_readable_moves = []
            for i, j in state.moves:
                from_hand = None
                to_hand = None
                if i == 0:
                    from_hand = 'L'
                else:
                    from_hand = 'R'
                if j == 0:
                    to_hand = 'L'
                else:
                    to_hand = 'R'
                human_readable_moves.append((from_hand, to_hand))
            game_state = 'to_move=%s, utility=%d, board=%s, moves of form (from_my, to_opponent)=%s' \
                         % (state.to_move, state.utility, state.board, human_readable_moves)
            print(game_state)
        else:
            super().display(state=state)
