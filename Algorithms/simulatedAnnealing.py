import random
from math import exp

from Entities.cell import Cell
from Entities.matrix import Matrix

TEMPERATURE = 80000


def swap(initial: Matrix, current: Cell) -> tuple[Matrix, Cell]:
    neighbors = initial.neighbor(current)

    next_cell = random.choice(neighbors)
    result = Matrix(initial.n, initial.array)
    result[current], result[next_cell] = result[next_cell], result[current]
    next_cell.value = result[next_cell]
    return result, next_cell


def simulated_annealing(f, initial):
    current = initial

    if initial.n == 1:
        return current

    index = random.randrange(initial.n * initial.n)
    currentCell = Cell(index, initial.array[index])

    t = TEMPERATURE
    while t > 0 and f(current.array) != 0:
        next, nextCell = swap(current, currentCell)
        de = f(next.array) - f(current.array)
        if de < 0 or random.random() < exp(-de / t):
            current = next
            currentCell = nextCell
        t -= 0.01

    return current
