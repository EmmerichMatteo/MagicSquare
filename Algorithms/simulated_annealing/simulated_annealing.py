import time
import random
from math import exp

from Algorithms.configuration import validate_fixed_cells, random_completion
from Algorithms.functions import error_function_square
from Entities.matrix import Matrix
from .simulated_annealing_helpers import do_next_step, propose_next_step

THIRTY_MINUTES = 1800
ITERATIONS = 1000

def simulated_annealing(f, n, fixed_cells=None):
    fixed = validate_fixed_cells(n, fixed_cells)
    cells = [cell for cell in range(n*n) if cell not in fixed]
    # Set temperature
    temperature = 0.38 * n**2.5 * (n**2 - 3)

    # Random matrix
    current = Matrix(n, random_completion(n, fixed), f)

    # Random matrix is a magic square?
    if current.value == 0 or len(cells) < 2:
        return current

    best_matrix = current.copy()
    errors = lines = None
    if current.objective_function is error_function_square:
        errors = Matrix._line_errors(current.array, current.n)
        lines = current.lines_for_cell

    # Start time range
    start = time.monotonic()
    while True:
        for _ in range(ITERATIONS):

            # Check time range
            if(time.monotonic() - start > THIRTY_MINUTES):
                return best_matrix

            # Randomly selected successor of current
            de, i, j, changes = propose_next_step(current, errors, lines, cells)

            # Assign successor
            if de < 0 or random.random() < exp(-de / temperature):
                do_next_step(current, i, j, de, errors, changes)

                if best_matrix.value > current.value:
                    best_matrix = current.copy()

            # New value is a magic square?
            if current.value == 0:
                return current

        temperature *= 0.9991  # (10x10) #0.995(7x7)  # 0.99 (5x5) - 0.995(6x6)
