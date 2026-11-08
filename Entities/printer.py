import os


class Printer:
    @staticmethod
    def clear_screen() -> None:
        os.system("cls" if os.name == "nt" else "clear")
        Printer.title()

    @staticmethod
    def title() -> None:
        print("\n" + "=" * 44)
        print("MAGIC SQUARE".center(44))
        print("=" * 44 + "\n")

    @staticmethod
    def execution_details(size: int, algorithm: int) -> None:
        names = {
            1: "Backtracking with constraint propagation",
            2: "Simulated annealing",
            3: "Genetic algorithm",
        }
        print(f"n = {size}")
        print(f"M = {size * (size * size + 1) // 2}")
        print(f"Algorithm = {names[algorithm]}\n")

    @staticmethod
    def invalid_size() -> None:
        print("Invalid side length. Enter an integer greater than 2.\n")

    @staticmethod
    def large_square_warning(size: int) -> None:
        print(f"Solving a {size} x {size} magic square may take a long time.")

    @staticmethod
    def invalid_confirmation() -> None:
        print("Please enter y, n or b (back).\n")

    @staticmethod
    def format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    @staticmethod
    def menu() -> None:
        print("Choose the algorithm to run:")
        print("1. Backtracking with constraint propagation")
        print("2. Simulated annealing")
        print("3. Genetic algorithm")
        print("b. Back")

    @staticmethod
    def invalid_choice() -> None:
        print("Invalid choice. Enter 1, 2, 3 or b (back).\n")

    @staticmethod
    def separator() -> None:
        print("--------------------------------------------")

    @staticmethod
    def solution(matrix, fitness, seconds: float) -> None:
        matrix.print_matrix()
        for i in range(matrix.n):
            print(f"Row sum {i + 1}: {matrix.row_sum(i)}")
        for j in range(matrix.n):
            print(f"Column sum {j + 1}: {matrix.column_sum(j)}")
        print(f"Main diagonal sum: {matrix.main_diagonal_sum()}")
        print(f"Secondary diagonal sum: {matrix.secondary_diagonal_sum()}")
        print(f"Final fitness: {fitness}")

    @staticmethod
    def summary(count: int, rounds: int, seconds: float) -> None:
        print(f"Total execution time: {Printer.format_time(seconds)}\n")

    @staticmethod
    def no_solution() -> None:
        print("No solution found by backtracking.")

    @staticmethod
    def error_function_menu() -> None:
        print("Choose the error function:")
        print("1. Squared error")
        print("2. Absolute error")
        print("b. Back")

    @staticmethod
    def test_menu() -> None:
        print("Choose the test sizes | All algorithms:")
        print("1. 3x3 to 6x6")
        print("2. 7x7 to 10x10")
        print("3. Single size (n x n)")
        print("4. Custom range (a to b)")
        print("b. Back")

    @staticmethod
    def initial_configuration(size: int, fixed_cells) -> None:
        print(f"\nInitial configuration {size}x{size}")
        print("0 = empty cell; other numbers = fixed values")
        width = len(str(size * size))
        separator = "+" + "+".join("-" * (width + 2) for _ in range(size)) + "+"
        print(separator)
        for row in range(size):
            cells = [str(fixed_cells.get(row * size + col, 0)) for col in range(size)]
            print("|" + "|".join(f" {cell:^{width}} " for cell in cells) + "|")
            print(separator)
        print()
