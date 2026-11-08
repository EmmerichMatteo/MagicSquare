"""Esecuzione dei tentativi di ricerca e gestione dei risultati."""

import json
import time

from Algorithms.backtracking.backtracking import back_tracking
from Algorithms.functions import check_constraints, error_function_square
from Algorithms.genetic.genetic import genetic
from Algorithms.simulated_annealing.simulated_annealing import simulated_annealing
from Entities.printer import Printer


def run_algorithm(rounds: int, size: int, algorithm: int, report=None, f=error_function_square, fixed_cells=None) -> None:
    count = 0
    round = 0
    total_start_time = time.perf_counter()
    if algorithm == 1:
        solve = lambda n: back_tracking(n, fixed_cells=fixed_cells)
    elif algorithm == 2:
        solve = lambda n: simulated_annealing(f, n, fixed_cells=fixed_cells)
    else:
        solve = lambda n: genetic(f, n, fixed_cells=fixed_cells)

    # Genetic owns its retry budget; invoke it once, as the benchmark does.
    for i in range(1 if algorithm == 3 else rounds):
        round += 1
        round_start_time = time.perf_counter()
        matrix = solve(size)
        result = f(matrix.array) if matrix is not None else None
        solution_time = time.perf_counter() - round_start_time
        solved = matrix is not None and result == 0 and check_constraints(matrix.array, fixed_cells)
        if report is not None:
            report.write(json.dumps({
                "round": round, "seconds": solution_time,
                "fitness": result, "solved": solved,
                "matrix": matrix.array if matrix is not None else None,
            }) + "\n")
            report.flush()
        if solved:
            count = count + 1
            Printer.solution(matrix, result, solution_time)
            total_elapsed_time = time.perf_counter() - total_start_time
            Printer.summary(count, round, total_elapsed_time)
            return
        if matrix is None:
            Printer.no_solution()
            break
        Printer.separator()

    total_elapsed_time = time.perf_counter() - total_start_time
    Printer.summary(count, round, total_elapsed_time)
