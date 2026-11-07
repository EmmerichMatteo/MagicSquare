import time
import random
from math import exp

from Algorithms.functions import objective_function
from Entities.cell import Cell
from Entities.matrix import Matrix

TEMPERATURE = 1000


def swap(initial: Matrix, current: Cell) -> tuple[Matrix, Cell]:
    neighbors = initial.neighbor(current)

    next_cell = random.choice(neighbors)
    result = Matrix(initial.n, initial.array)
    result[current], result[next_cell] = result[next_cell], result[current]
    next_cell.value = result[next_cell]
    return result, next_cell

def swap_random(initial: Matrix) -> tuple[Matrix, Cell]:
    if len(initial.array) < 2:
        raise ValueError("a random swap requires at least two cells")

    current_index, next_index = random.sample(range(len(initial.array)), 2)
    current = Cell(current_index, initial.array[current_index])
    next_cell = Cell(next_index, initial.array[next_index])

    result = Matrix(initial.n, initial.array)
    result[current], result[next_cell] = result[next_cell], result[current]
    next_cell.value = result[next_cell]

    return result, next_cell

def _line_errors(array, n):
    target = n * (n * n + 1) // 2
    errors = [sum(array[r * n:(r + 1) * n]) - target for r in range(n)]
    errors.extend(sum(array[r * n + c] for r in range(n)) - target
                  for c in range(n))
    errors.append(sum(array[r * n + r] for r in range(n)) - target)
    errors.append(sum(array[r * n + n - 1 - r] for r in range(n)) - target)
    return errors


def _cell_lines(n):
    lines = []
    for index in range(n * n):
        row, col = divmod(index, n)
        membership = [row, n + col]
        if row == col:
            membership.append(2 * n)
        if row + col == n - 1:
            membership.append(2 * n + 1)
        lines.append(tuple(membership))
    return lines


def _swap_changes(array, i, j, lines):
    difference = array[j] - array[i]
    changes = dict.fromkeys(lines[i], difference)
    for line in lines[j]:
        changes[line] = changes.get(line, 0) - difference
    return changes


def simulated_annealing(f, initial, *, initial_temperature=None):

    if initial.n == 1:
        return initial

    t = (0.38 * initial.n**2.5 * (initial.n**2 - 3)
         if initial_temperature is None else initial_temperature)
    if t <= 0:
        raise ValueError("initial_temperature must be positive")
    start = time.monotonic()

    array = initial.array.copy()
    value = f(array)
    if value == 0:
        return initial

    best_array = array.copy()
    best_value = value
    incremental = f is objective_function
    errors = _line_errors(array, initial.n) if incremental else None
    lines = _cell_lines(initial.n) if incremental else None
    positions = range(len(array))
    while True:
        for _ in range(1000):
            if(time.monotonic() - start > 1800):
                return Matrix(initial.n, best_array)
            i, j = random.sample(positions, 2)
            if incremental:
                changes = _swap_changes(array, i, j, lines)
                de = sum(2 * errors[line] * change + change * change
                         for line, change in changes.items())
                candidate_value = value + de
            else:
                # Keep support for objectives other than the magic-square energy.
                array[i], array[j] = array[j], array[i]
                try:
                    candidate_value = f(array)
                finally:
                    array[i], array[j] = array[j], array[i]
                de = candidate_value - value
            if de < 0 or random.random() < exp(-de / t):
                array[i], array[j] = array[j], array[i]
                value = candidate_value
                if incremental:
                    for line, change in changes.items():
                        errors[line] += change
                if best_value > value:
                    best_array = array.copy()
                    best_value = value
                if value == 0:
                    return Matrix(initial.n, array)
        t *= #0.999(10x10) #0.995(7x7)  # 0.99 (5x5) - 0.995(6x6)
