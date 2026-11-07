from Algorithms.genetic import genetic
import argparse
import json
import random
import time

from Algorithms.functions import check_constraints, objective_function
from Algorithms.simulatedAnnealing import simulated_annealing
from Entities.cell import Cell
from Entities.matrix import Matrix

N = 10

def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def main(rounds: int = 100, size: int = N, seed: int | None = None, report=None) -> None:
    if rounds <= 0 or size <= 2:
        raise ValueError("rounds must be positive and size must be greater than 2")
    if seed is not None:
        random.seed(seed)
    N = size
    count = 0
    round = 0
    total_start_time = time.perf_counter()

    for i in range(rounds):
        round += 1
        round_start_time = time.perf_counter()
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
            #matrix = genetic(objective_function, matrix)
            matrix = simulated_annealing(objective_function, matrix)

        result = objective_function(matrix.array)
        solution_time = time.perf_counter() - round_start_time
        solved = result == 0 and check_constraints(matrix.array)
        if report is not None:
            report.write(json.dumps({
                "round": round, "seconds": solution_time,
                "fitness": result, "solved": solved, "matrix": matrix.array,
            }) + "\n")
            report.flush()
        if solved:
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
            total_elapsed_time = time.perf_counter() - total_start_time
            print(f"Total execution time: {format_time(total_elapsed_time)}")
            return
        print("--------------------------------------------")

    total_elapsed_time = time.perf_counter() - total_start_time
    print(f"Number of solutions found: {count}/{round}")
    print(f"Total execution time: {format_time(total_elapsed_time)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ricerca di quadrati magici")
    parser.add_argument("--rounds", type=int, default=100)
    parser.add_argument("--size", type=int, default=N)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--report", help="Report JSONL dei tentativi completati")
    args = parser.parse_args()
    if args.rounds <= 0 or args.size <= 2:
        parser.error("--rounds deve essere positivo e --size almeno 3")
    if args.report:
        with open(args.report, "w", encoding="utf-8") as report:
            main(args.rounds, args.size, args.seed, report)
    else:
        main(args.rounds, args.size, args.seed)
