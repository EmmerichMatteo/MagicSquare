"""Interactive configuration for the magic square search."""

from Entities.printer import Printer


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
        if choice in ("1", "2", "3", "4", "5"):
            Printer.clear_screen()
        if choice == "1":
            return 3, 6
        if choice == "2":
            return 7, 10
        if choice in ("3", "5"):
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
            print("Invalid choice. Enter 1, 2, 3, 4, 5 or b (back).")
            continue
        if upper > 10 and not confirm_large_square(upper):
            continue
        if choice == "5":
            return "comparison", lower
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
        displayed = {}
        while True:
            Printer.initial_configuration(size, displayed)
            print("Enter Index then Value (0 or . = empty).")
            print("Press Enter on Index to finish; b. Back")
            entry = _read_choice("Index: ").strip().lower()
            if entry in ("b", "back"):
                return None
            if not entry:
                configurations[size] = fixed
                Printer.clear_screen()
                break
            try:
                index = int(entry)
                if not 1 <= index <= size * size:
                    raise ValueError(f"Index must be between 1 and {size * size}")
            except ValueError as error:
                print(f"Invalid index: {error}")
                continue
            while True:
                entry = _read_choice("Value: ").strip().lower()
                if entry in ("b", "back"):
                    return None
                try:
                    value = 0 if entry == "." else int(entry)
                    candidate = dict(fixed)
                    candidate.pop(index - 1, None)
                    if value != 0:
                        candidate[index - 1] = value
                    validate_fixed_cells(size, candidate)
                except ValueError as error:
                    print(f"Invalid value: {error}")
                    continue
                fixed = candidate
                displayed[index - 1] = value
                Printer.clear_screen()
                break
    return configurations
