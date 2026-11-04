from Algorithms.genetic import genetic
import random

from Algorithms.functions import check_constraints, objective_function
from Algorithms.simulatedAnnealing import simulated_annealing
from Entities.cell import Cell
from Entities.matrix import Matrix

N = 5

def main() -> None:
    matrix = Matrix(N)
    generated = [0] * (N * N)

    for key in range(N * N):
        index = random.randrange(N * N)
        while generated[index] == 1:
            index = random.randrange(N * N)

        generated[index] = 1
        number = index + 1
        matrix[Cell(key, number)] = number

    matrix.print_matrix()

    if check_constraints(matrix.array):
        matrix = genetic(objective_function, matrix)
        #matrix = simulated_annealing(objective_function, matrix)

    matrix.print_matrix()

    for i in range(N):
        print(f"Row sum {i + 1}: {matrix.row_sum(i)}")

    for j in range(N):
        print(f"Column sum {j + 1}: {matrix.column_sum(j)}")

    print(f"Main diagonal sum: {matrix.main_diagonal_sum()}")
    print(f"Secondary diagonal sum: {matrix.secondary_diagonal_sum()}")
    print(f"Final fitness: {objective_function(matrix.array)}")


if __name__ == "__main__":
    main()
