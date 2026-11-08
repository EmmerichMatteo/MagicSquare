from copy import copy
from functools import lru_cache


class Matrix:
    _empty_matrices = {}

    @classmethod
    def empty(cls, n: int):
        # Share one zero-filled template per matrix class and dimension.
        # Copy the template before modifying it.
        cls._validate_size(n)
        key = (cls, n)
        if key not in cls._empty_matrices:
            cls._empty_matrices[key] = cls(n)
        return cls._empty_matrices[key]

    def __init__(self, n: int, array: list[int] | None = None, objective_function=None):
        self._validate_size(n)

        self.n = n
        self.array = [0] * (n * n) if array is None else list(array)
        if len(self.array) != n * n:
            raise ValueError("the array must contain n * n elements")
        self.objective_function = objective_function
        self.value = objective_function(self.array) if objective_function is not None else None

    @staticmethod
    def _validate_size(n: int) -> None:
        if isinstance(n, bool) or not isinstance(n, int) or n <= 2:
            raise ValueError("the side length must be an integer greater than 2")

    @staticmethod
    @lru_cache(maxsize=None)
    def _line_structure(n):
        # Cache immutable rows, columns, diagonals, and cell memberships by size.
        lines = [tuple(range(row * n, (row + 1) * n)) for row in range(n)]
        lines.extend(tuple(row * n + col for row in range(n)) for col in range(n))
        lines.append(tuple(i * n + i for i in range(n)))
        lines.append(tuple(i * n + n - 1 - i for i in range(n)))
        lines_for_cell = [[] for _ in range(n * n)]
        for line_index, line in enumerate(lines):
            for cell in line:
                lines_for_cell[cell].append(line_index)
        return tuple(lines), tuple(tuple(membership) for membership in lines_for_cell)

    @property
    def M(self):
        # Target sum for each row, column, and diagonal of a normal magic square.
        return self.n * (self.n * self.n + 1) // 2

    @property
    def lines(self):
        return self._line_structure(self.n)[0]

    @property
    def lines_for_cell(self):
        return self._line_structure(self.n)[1]

    def copy(self):
        result = copy(self)
        result.array = self.array.copy()
        return result

    def swap(self, i: int, j: int, *, delta=None) -> None:
        """Swap two indices, updating the objective with an optional known delta."""
        self.array[i], self.array[j] = self.array[j], self.array[i]
        if self.objective_function is not None:
            self.value = (self.objective_function(self.array) if delta is None
                          else self.value + delta)

    def print_matrix(self) -> None:
        width = len(str(self.n ** 2))
        separator = "|" + "|".join("_" * (width + 2) for _ in range(self.n)) + "|"
        empty_row = "|" + "|".join(" " * (width + 2) for _ in range(self.n)) + "|"
        print(" " + "_" * (len(separator) - 2) + " ")
        for i in range(self.n):
            row = self.array[i * self.n:(i + 1) * self.n]
            print(empty_row)
            print("|" + "|".join(f" {value:>{width}} " for value in row) + "|")
            print(separator)
        print()

    def row_sum(self, i: int) -> int:
        if not isinstance(i, int) or not 0 <= i < self.n:
            raise IndexError("row index outside the matrix")
        return sum(self.array[i * self.n:(i + 1) * self.n])

    def column_sum(self, j: int) -> int:
        if not isinstance(j, int) or not 0 <= j < self.n:
            raise IndexError("column index outside the matrix")
        return sum(self.array[i * self.n + j] for i in range(self.n))

    def main_diagonal_sum(self) -> int:
        return sum(self.array[i * self.n + i] for i in range(self.n))

    def secondary_diagonal_sum(self) -> int:
        return sum(self.array[i * self.n + (self.n - 1 - i)] for i in range(self.n))

    @staticmethod
    def _line_errors(array, n):
        target = n * (n * n + 1) // 2
        errors = [sum(array[r * n:(r + 1) * n]) - target for r in range(n)]
        errors.extend(sum(array[r * n + c] for r in range(n)) - target
                      for c in range(n))
        errors.append(sum(array[r * n + r] for r in range(n)) - target)
        errors.append(sum(array[r * n + n - 1 - r] for r in range(n)) - target)
        return errors

    @staticmethod
    def _swap_changes(array, i, j, lines):
        difference = array[j] - array[i]
        changes = dict.fromkeys(lines[i], difference)
        for line in lines[j]:
            changes[line] = changes.get(line, 0) - difference
        return changes
