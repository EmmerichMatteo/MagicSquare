from Entities.cell import Cell


class Matrix:
    def __init__(self, n: int, array: list[int] | None = None):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n deve essere un intero positivo")

        self.n = n
        self.array = [0] * (n * n) if array is None else list(array)
        if len(self.array) != n * n:
            raise ValueError("l'array deve contenere n * n elementi")

    def _index(self, cell: Cell) -> int:
        if not isinstance(cell.key, int) or not 0 <= cell.key < self.n * self.n:
            raise IndexError("cella fuori dalla matrice")
        return cell.key

    def __getitem__(self, cell: Cell) -> int:
        return self.array[self._index(cell)]

    def __setitem__(self, cell: Cell, value: int) -> None:
        self.array[self._index(cell)] = value

    def stampa(self) -> None:
        larghezza = len(str(self.n ** 2))
        separatore = "|" + "|".join("_" * (larghezza + 2) for _ in range(self.n)) + "|"
        riga_vuota = "|" + "|".join(" " * (larghezza + 2) for _ in range(self.n)) + "|"
        print(" " + "_" * (len(separatore) - 2) + " ")
        for i in range(self.n):
            riga = self.array[i * self.n:(i + 1) * self.n]
            print(riga_vuota)
            print("|" + "|".join(f" {valore:>{larghezza}} " for valore in riga) + "|")
            print(separatore)
        print()

    def somma_riga(self, i: int) -> int:
        if not isinstance(i, int) or not 0 <= i < self.n:
            raise IndexError("indice di riga fuori dalla matrice")
        return sum(self.array[i * self.n:(i + 1) * self.n])

    def somma_colonna(self, j: int) -> int:
        if not isinstance(j, int) or not 0 <= j < self.n:
            raise IndexError("indice di colonna fuori dalla matrice")
        return sum(self.array[i * self.n + j] for i in range(self.n))

    def somma_diagonale_principale(self) -> int:
        return sum(self.array[i * self.n + i] for i in range(self.n))

    def somma_diagonale_secondaria(self) -> int:
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
