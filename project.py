import random
from collections import deque
import pandas as pd
import numpy as np

ENERGY_COSTS = {"⛰": -5, ".": -1, "D": 2}
ENERGY = 28
POSSIBLE_CELLS = {"⛰": 39, "X": 9, "D": 3, "S": 1, "G": 1, ".": 91}
MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

def add_energy(cell: str, energy: int):
    return energy + ENERGY_COSTS[cell]


def initialize_board() -> list:
    board = list()
    for cell, num in POSSIBLE_CELLS.items():
        for _ in range(num):
            board.append(cell)

    random.shuffle(board)
    return board

# Agent picks random moves from the moves it can do
def random_agent(board: list, e: int) -> tuple[str, list]:
    moves_taken = []
    deliveries_done = 0
    agent = board.index("S")

    while e > 0:
        row, col = divmod(
            agent,
            12,
        )

        # Create a dictionary containing each possible move, the cell it takes the agent to, and the index of the cell
        neighbor_cells = {}
        for move_name, (dr, dc) in MOVES.items():
            new_row = row + dr
            new_col = col + dc
            new_index = new_row * 12 + new_col

            if new_row < 0 or new_row > 11 or new_col < 0 or new_col > 11:
                continue

            if board[new_index] == "G" and deliveries_done != 3:
                continue

            # Don't add the move if the cell it takes the agent to is a X
            if board[new_index] != "X":
                if board[new_index] == "S":
                    neighbor_cells[move_name] = (".", new_index)
                else:
                    neighbor_cells[move_name] = (board[new_index], new_index)

        if neighbor_cells == {}:
            # print(np.reshape(board, (12, 12)))
            return "Can no longer proceed", moves_taken

        # Choose a move randomly out of all the possible moves
        chosen_move = random.choice(list(neighbor_cells.items()))
        moves_taken.append(chosen_move[0])

        # Check if the cell the move takes the agent to is a delivery point, remove it, and increase the number of deliveries done.
        if chosen_move[1][0] == "D":
            board[chosen_move[1][1]] = "."
            deliveries_done += 1

        if chosen_move[1][0] == "G" and deliveries_done == 3:
            return "Success", moves_taken

        e = add_energy(chosen_move[1][0], e)
        agent = chosen_move[1][1]

    return "Energy ran out", moves_taken


# Agent tries to go to the nearest delivery ppoint or goal, while attempting to avoid nmountains
def reflex_agent(board: list, e: int) -> tuple[str, list]:

    moves_taken = []
    deliveries_done = 0
    agent = board.index("S")
    # Find positions of delivery points and goal point
    deliver_point_indices = np.where(np.array(board) == "D")[0]
    goal_index = np.where(np.array(board) == "G")[0]
    goal_row, goal_col = divmod(goal_index, 12)

    while e > 0:
        row, col = divmod(
            agent,
            12,
        )

        # Create a dictionary containing all the moves, the cell it takes the agent to, the new cell index, and the new distances from the delivery points
        neighbor_cells = {}
        for move_name, (dr, dc) in MOVES.items():
            deliver_point_distances = []
            new_row = row + dr
            new_col = col + dc
            new_index = new_row * 12 + new_col

            # Skip move if it takes the agent off the board
            if new_row < 0 or new_row > 11 or new_col < 0 or new_col > 11:
                continue

            # Skip move if the cell it takes the agent to is the goal cell and it hasn't finished the deliveries yet
            if board[new_index] == "G" and deliveries_done != 3:
                continue

            if board[new_index] != "X":
                # Calculate new distances to the delivery points based on the move
                for index in deliver_point_indices:
                    d_row, d_col = divmod(index, 12)
                    deliver_point_distances.append(
                        (abs(new_row - d_row) + abs(new_col - d_col))
                    )

                if board[new_index] == "S":
                    neighbor_cells[move_name] = (
                        ".",
                        new_index,
                        deliver_point_distances,
                    )
                else:
                    neighbor_cells[move_name] = (
                        board[new_index],
                        new_index,
                        deliver_point_distances,
                    )

        # Check if the agent is stuck
        if neighbor_cells == {}:
            # print(np.reshape(board, (12, 12)))
            return "Can no longer proceed", moves_taken

        # Check for ⛰ in the neighbouring cells and remove them if and only if the agent is left with at least one move
        cells = {}
        for move, tuple in neighbor_cells.items():
            cells[move] = tuple[0]

        if "⛰" in cells.values() and pd.Series(cells.values()).unique().size != 1:
            for move, cell in cells.items():
                if cell == "⛰":
                    neighbor_cells.pop(move)

        # Move the agent towards the nearest delivery point or to the goal if there are no delivery points left
        chosen_move = []
        if deliveries_done < 3:
            min_steps = 100000000000
            for move, tuple in neighbor_cells.items():
                if np.min(tuple[2]) < min_steps:
                    min_steps = np.min(tuple[2])
                    chosen_move = (move, neighbor_cells[move])
        elif deliveries_done == 3:
            distance_to_goal = 1000000000
            for move, tuple in neighbor_cells.items():
                move_row, move_col = divmod(tuple[1], 12)
                new_distance_to_goal = abs(move_row - goal_row) + abs(
                    move_col - goal_col
                )
                if new_distance_to_goal < distance_to_goal:
                    distance_to_goal = new_distance_to_goal
                    chosen_move = (move, neighbor_cells[move])

        moves_taken.append(chosen_move[0])

        # Check whether the chosen move takes the agent to a delivery point, remove it, calculate the indices of the remaining delivery points,
        # and increase the number of deliveries done
        if chosen_move[1][0] == "D":
            board[chosen_move[1][1]] = "."
            deliver_point_indices = np.where(np.array(board) == "D")[0]
            deliveries_done += 1

        if chosen_move[1][0] == "G" and deliveries_done == 3:
            return "Success", moves_taken

        e = add_energy(chosen_move[1][0], e)
        agent = chosen_move[1][1]

    return "Energy ran out", moves_taken


if __name__ == "__main__":
    ra_runs = []
    for _ in range(100):
        board = initialize_board()
        ra_runs.append(random_agent(board, ENERGY)[0])

    print(pd.Series(ra_runs).unique())
    sa_runs = []
    for _ in range(100):
        board = initialize_board()
        sa_runs.append(reflex_agent(board, ENERGY)[0])

    print(pd.Series(sa_runs).unique())
