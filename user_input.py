"""Interactive configuration for the magic square search."""

from Entities.printer import Printer
from Algorithms.functions import error_function_square, error_function_absolute


class HomeRequested(Exception):
    pass


class ExitRequested(Exception):
    pass


def _read_choice(prompt):
    choice = input(prompt + "[h. Home | e. Exit] ")
    action = choice.strip().lower()
    if action in ("h", "home", "b", "back"):
        Printer.clear_screen()
    if action in ("h", "home"):
        raise HomeRequested
    if action in ("e", "exit"):
        raise ExitRequested
    return choice


def choose_mode() -> int:
    print("1. Try algorithms")
    print("2. Run tests")
    while True:
        choice = _read_choice("Choice: ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Invalid choice. Enter 1 or 2.")


def choose_test_rounds() -> int | None:
    print("b. Back")
    while True:
        choice = _read_choice("How many runs per algorithm? ").strip().lower()
        if choice in ("b", "back"):
            return None
        try:
            rounds = int(choice)
            if rounds > 0:
                return rounds
        except ValueError:
            pass
        print("Invalid choice. Enter a positive integer or b to go back.")


def confirm_large_square(size: int) -> bool:
    Printer.large_square_warning(size)
    print("y. Yes")
    print("n. No")
    print("b. Back")
    while True:
        answer = _read_choice("Are you sure you want to continue? ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no", "b", "back"):
            return False
        Printer.invalid_confirmation()


def choose_size() -> int:
    while True:
        choice = _read_choice("Enter the side length of the magic square (at least 3): ").strip()
        try:
            size = int(choice)
        except ValueError:
            Printer.invalid_size()
            continue
        if size < 3:
            Printer.invalid_size()
            continue
        if size > 10 and not confirm_large_square(size):
            continue
        return size


def choose_algorithm() -> int | None:
    Printer.menu()
    while True:
        choice = _read_choice("Algorithm: ").strip().lower()
        if choice in ("b", "back"):
            return None
        if choice in ("1", "2", "3"):
            return int(choice)
        Printer.invalid_choice()


def wait_for_home() -> bool:
    print("h. Home")
    print("e. Exit\n")
    while True:
        choice = input("Choice: ").strip().lower()
        if choice in ("h", "home"):
            Printer.clear_screen()
            return True
        if choice in ("e", "exit"):
            return False
        print("Enter home or exit")


def choose_error_function():
    Printer.error_function_menu()
    while True:
        choice = _read_choice("Error function: ").strip().lower()
        if choice in ("b", "back"):
            return None
        if choice == "1":
            return error_function_square
        if choice == "2":
            return error_function_absolute
        print("Invalid choice. Enter 1, 2 or b (back).\n")


def _choose_test_side(prompt, minimum=3):
    while True:
        choice = _read_choice(prompt).strip().lower()
        if choice in ("b", "back"):
            return None
        try:
            value = int(choice)
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Invalid side length. Enter an integer at least {minimum} or b (back).")


def choose_test_sizes():
    while True:
        Printer.test_menu()
        choice = _read_choice("Test: ").strip().lower()
        if choice in ("b", "back"):
            return None
        if choice in ("1", "2", "3", "4"):
            Printer.clear_screen()
        if choice == "1":
            return 3, 6
        if choice == "2":
            return 7, 10
        if choice == "3":
            size = _choose_test_side("Side length n (at least 3): ")
            if size is None:
                continue
            lower = upper = size
        elif choice == "4":
            lower = _choose_test_side("First side length a (at least 3): ")
            if lower is None:
                continue
            upper = _choose_test_side(f"Last side length b (at least {lower}): ", lower)
            if upper is None:
                continue
        else:
            print("Invalid choice. Enter 1, 2, 3, 4 or b (back).")
            continue
        if upper > 10 and not confirm_large_square(upper):
            continue
        return lower, upper


def choose_initial_configuration(sizes):
    from Algorithms.configuration import validate_fixed_cells
    print("Use an initial configuration with fixed cells?")
    print("y. Yes")
    print("n. No")
    print("b. Back")
    while True:
        choice = _read_choice("Initial configuration: ").strip().lower()
        if choice in ("b", "back"):
            return None
        if choice in ("n", "no"):
            return {}
        if choice in ("y", "yes"):
            break
        Printer.invalid_confirmation()
    configurations = {}
    Printer.clear_screen()
    for size in sizes:
        fixed = {}
        for row in range(size):
            while True:
                Printer.initial_configuration(size, fixed)
                print(f"Enter {size} values separated by spaces; 0 or . = empty.")
                entry = _read_choice(f"Row {row + 1}: ").strip().lower()
                if entry in ("b", "back"):
                    return None
                try:
                    values = [0 if token == "." else int(token) for token in entry.split()]
                    if len(values) != size:
                        raise ValueError(f"Enter exactly {size} values")
                    candidate = dict(fixed)
                    candidate.update({row * size + col: value for col, value in enumerate(values) if value != 0})
                    validate_fixed_cells(size, candidate)
                except ValueError as error:
                    print(f"Invalid row: {error}")
                    continue
                fixed = candidate
                Printer.clear_screen()
                break
        configurations[size] = fixed
    return configurations
