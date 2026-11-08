"""Run every algorithm repeatedly for an inclusive range of square sizes."""

import argparse
from datetime import datetime
from pathlib import Path
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Algorithms.backtracking.backtracking import back_tracking
from Algorithms.configuration import validate_fixed_cells
from Algorithms.functions import check_constraints, error_function_absolute, error_function_square
from Algorithms.genetic.genetic import genetic
from Algorithms.simulated_annealing.simulated_annealing import simulated_annealing
from Entities.printer import Printer


def run_benchmark(rounds: int, min_size: int = 3, max_size: int = 6,
                  output: Path | None = None, f=error_function_square, fixed_by_size=None) -> Path:
    if rounds < 1 or min_size < 3 or max_size < min_size:
        raise ValueError("Use positive rounds and 3 <= min_size <= max_size")
    fixed_by_size = {n: validate_fixed_cells(n, cells) for n, cells in (fixed_by_size or {}).items()}
    if any(n < min_size or n > max_size for n in fixed_by_size):
        raise ValueError("Initial configuration outside the test size range")
    output = Path(output) if output is not None else (
        Path(__file__).resolve().parent
        / f"benchmark-{datetime.now():%Y%m%d-%H%M%S-%f}.txt"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    algorithms = (
        ("Backtracking", lambda n, fixed: back_tracking(n, fixed_cells=fixed)),
        ("Simulated annealing", lambda n, fixed: simulated_annealing(f, n, fixed_cells=fixed)),
        ("Genetic algorithm", lambda n, fixed: genetic(f, n, fixed_cells=fixed)),
    )
    with output.open("x", encoding="utf-8") as report:
        def emit(message=""):
            print(message, flush=True)
            print(message, file=report, flush=True)

        title_width = 44
        print("=" * title_width, file=report)
        print("MAGIC SQUARE".center(title_width), file=report)
        print("=" * title_width, file=report)
        emit(f"Sizes: {min_size}x{min_size} to {max_size}x{max_size} | Runs per algorithm and size: {rounds}")
        emit(f"Error function: {f.__name__}")
        emit(f"Report: {output.resolve()}")
        emit("Press Ctrl+C to stop and keep completed results.")
        try:
            for size in range(min_size, max_size + 1):
                emit()
                emit("_" * title_width)
                emit()
                emit(f"Size: {size}x{size}")
                fixed = fixed_by_size.get(size, {})
                emit("Fixed cells: " + (", ".join(
                    f"({cell // size + 1}, {cell % size + 1})={value}" for cell, value in sorted(fixed.items())
                ) or "none"))
                for name, solve in algorithms:
                    for attempt in range(1, rounds + 1):
                        emit()
                        emit(f"Starting {size}x{size} | {name} | Run {attempt}/{rounds}")
                        start = time.perf_counter()
                        try:
                            matrix = solve(size, fixed)
                            seconds = time.perf_counter() - start
                            score = f(matrix.array) if matrix is not None else None
                            valid = matrix is not None and check_constraints(matrix.array, fixed)
                            status = "SOLVED" if valid and score == 0 else "NOT SOLVED"
                        except Exception as error:
                            seconds = time.perf_counter() - start
                            matrix, score, valid, status = None, None, False, "ERROR"
                            emit(f"Error: {type(error).__name__}: {error}")
                        emit(f"Result: {status} | Valid constraints: {valid} | Fitness: {score} | Time: {Printer.format_time(seconds)}")
                        if matrix is not None:
                            emit("\nResult matrix:")
                            width = len(str(size * size))
                            for row in range(size):
                                emit(" ".join(f"{v:>{width}}" for v in matrix.array[row * size:(row + 1) * size]))
        except KeyboardInterrupt:
            emit("\nBenchmark interrupted. Completed results have been saved.")
    return output


def run_function_comparison(size: int):
    """One run per algorithm and objective, without fixed cells."""
    reports = []
    for f in (error_function_absolute, error_function_square):
        reports.append(run_benchmark(1, size, size, f=f))
    return reports


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--min-size", type=int, default=3)
    parser.add_argument("--max-size", type=int, default=6)
    args = parser.parse_args()
    if args.rounds < 1 or args.min_size < 3 or args.max_size < args.min_size:
        parser.error("Use positive rounds and 3 <= min-size <= max-size")
    from user_input import choose_initial_configuration, confirm_large_square
    Printer.clear_screen()
    if args.max_size > 10 and not confirm_large_square(args.max_size):
        return
    configurations = choose_initial_configuration(range(args.min_size, args.max_size + 1))
    if configurations is not None:
        Printer.clear_screen()
        run_benchmark(args.rounds, args.min_size, args.max_size, fixed_by_size=configurations)


def main() -> None:
    from user_input import HomeRequested, ExitRequested
    try:
        _main()
    except HomeRequested:
        from main import main as home
        Printer.clear_screen()
        home()
    except ExitRequested:
        return


if __name__ == "__main__":
    main()
