import random

from Entities.matrix import Matrix
from Algorithms.configuration import validate_fixed_cells
from .backtracking_helpers import eliminated_candidates, generate_successors, _propagate


def back_tracking(n: int, fixed_cells=None) -> Matrix | None:
    fixed = validate_fixed_cells(n, fixed_cells)
    # Set the empty matrix
    board = Matrix.empty(n).copy()
    size = n * n

    lines = board.lines
    lines_for_cell = board.lines_for_cell

    # Set the domain from 1 to n^2
    domains = [set(range(1, size + 1)) for _ in range(size)]

    for cell, value in fixed.items():
        domains[cell] = {value}
    if fixed and not _propagate(board, domains, lines, lines_for_cell):
        return None

    # Keep an iterator for each active branch to preserve depth-first search.
    branches = [iter([(board, domains)])]
    while branches:
        try:
            current, current_domains = next(branches[-1])
        except StopIteration:
            branches.pop()
            continue

        empty = [cell for cell in range(size) if current.array[cell] == 0]
        if not empty:
            if all(sum(current.array[cell] for cell in line) == current.M for line in lines):
                return current
            continue

        # MRV: choose the smallest domain, breaking ties randomly.
        smallest_domain = min(len(current_domains[cell]) for cell in empty)
        tied_cells = [cell for cell in empty if len(current_domains[cell]) == smallest_domain]
        cell = random.choice(tied_cells)

        # LCV: try values that eliminate the fewest candidates first.
        values = sorted(current_domains[cell])
        random.shuffle(values)
        values.sort(key=lambda value: eliminated_candidates(value, current_domains, empty, cell))

        # constraint propagation
        branches.append(generate_successors(
            current, current_domains, cell, values, lines, lines_for_cell
        ))

    return None
