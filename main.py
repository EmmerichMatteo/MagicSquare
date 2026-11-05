from Algorithms.genetic import genetic
import random
import time

from Algorithms.functions import check_constraints, objective_function
from Algorithms.simulatedAnnealing import simulated_annealing
from Entities.cell import Cell
from Entities.matrix import Matrix

N = 5

def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def main() -> None:
    count = 0
    round = 0
    total_start_time = time.time()

    for i in range(100):
        round += 1
        round_start_time = time.time()
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

        result = objective_function(matrix.array)
        if(result == 0):
            solution_time = time.time() - round_start_time
            count = count + 1
            matrix.print_matrix()

            for i in range(N):
                print(f"Row sum {i + 1}: {matrix.row_sum(i)}")

            for j in range(N):
                print(f"Column sum {j + 1}: {matrix.column_sum(j)}")

            print(f"Main diagonal sum: {matrix.main_diagonal_sum()}")
            print(f"Secondary diagonal sum: {matrix.secondary_diagonal_sum()}")
            print(f"Final fitness: {result}")
            print(f"Time to find this solution: {format_time(solution_time)}")
            
            print(f"Number of solutions after {round} rounds: {count}")
            total_elapsed_time = time.time() - total_start_time
            print(f"Total execution time: {format_time(total_elapsed_time)}")
        print("--------------------------------------------")

    total_elapsed_time = time.time() - total_start_time
    print(f"Number of solutions found: {count}/{round}")
    print(f"Total execution time: {format_time(total_elapsed_time)}")

if __name__ == "__main__":
    main()
