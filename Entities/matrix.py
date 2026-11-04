from Entities.cell import Cell


class Matrix:
    def __init__(self, n: int, array: list[int] | None = None):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")

        self.n = n
        self.array = [0] * (n * n) if array is None else list(array)
        if len(self.array) != n * n:
            raise ValueError("the array must contain n * n elements")

    def _index(self, cell: Cell) -> int:
        if not isinstance(cell.key, int) or not 0 <= cell.key < self.n * self.n:
            raise IndexError("cell outside the matrix")
        return cell.key

    def __getitem__(self, cell: Cell) -> int:
        return self.array[self._index(cell)]

    def __setitem__(self, cell: Cell, value: int) -> None:
        self.array[self._index(cell)] = value

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

    def neighbor(self, cell: Cell) -> list[Cell]:
        key = self._index(cell)
        neighbors = []
        if key % self.n > 0:
            neighbors.append(Cell(key - 1, self.array[key - 1]))
        if key % self.n < self.n - 1:
            neighbors.append(Cell(key + 1, self.array[key + 1]))
        if key >= self.n:
            neighbors.append(Cell(key - self.n, self.array[key - self.n]))
        if key < self.n * (self.n - 1):
            neighbors.append(Cell(key + self.n, self.array[key + self.n]))
        return neighbors
