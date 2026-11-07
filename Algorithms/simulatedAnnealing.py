import time
import random
from math import exp

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

def simulated_annealing(f, initial, *, initial_temperature=None):
    current = initial

    if initial.n == 1:
        return current

    index = random.randrange(initial.n * initial.n)
    currentCell = Cell(index, initial.array[index])

    t = (0.38 * initial.n**2.5 * (initial.n**2 - 3)
         if initial_temperature is None else initial_temperature)
    if t <= 0:
        raise ValueError("initial_temperature must be positive")
    start = time.monotonic()

    if(f(current.array) == 0):
        return current

    best = current
    best_value = f(current.array)
    while 1:
        for i in range(1000):
            if(time.monotonic() - start > 1800):
                return best
            next, nextCell = swap_random(current)
            de = f(next.array) - f(current.array)
            if de < 0 or random.random() < exp(-de / t):
                current = next
                currentCell = nextCell
                value = f(current.array)
                if(best_value > value):
                    best = current
                    best_value = value
                if value == 0:
                    return current
        t *= 0.9991  # 0.99 (5x5) - 0.995(6x6)

    return best
