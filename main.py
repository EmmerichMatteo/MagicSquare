from algorithm_runner import run_algorithm
from benchmark_unive.benchmark import run_benchmark
from Entities.printer import Printer
from user_input import HomeRequested, ExitRequested, choose_initial_configuration, choose_error_function, choose_algorithm, choose_mode, choose_size, choose_test_rounds, choose_test_sizes, wait_for_home

ROUNDS = 100

def try_algorithms() -> bool:
    while True:
        size = choose_size()
        while True:
            Printer.clear_screen()
            algorithm = choose_algorithm()
            if algorithm is None:
                Printer.clear_screen()
                break
            Printer.clear_screen()
            f = choose_error_function()
            if f is None:
                continue
            Printer.clear_screen()
            configurations = choose_initial_configuration([size])
            if configurations is None:
                continue
            Printer.clear_screen()
            Printer.execution_details(size, algorithm)
            print(f"Error function: {f.__name__}\n")
            print("Press Ctrl+C during the search to go back to the algorithm menu.")
            try:
                run_algorithm(ROUNDS, size, algorithm, f=f, fixed_cells=configurations.get(size))
            except KeyboardInterrupt:
                print("\nSearch interrupted.")
                continue
            if not wait_for_home():
                return False
            return True


def main() -> None:
    Printer.title()
    while True:
        try:
            mode = choose_mode()
            Printer.clear_screen()
            if mode == 1:
                if not try_algorithms():
                    return
            else:
                while True:
                    sizes = choose_test_sizes()
                    if sizes is None:
                        break
                    min_size, max_size = sizes
                    print(f"Sizes: {min_size}x{min_size} to {max_size}x{max_size} | All algorithms")
                    rounds = choose_test_rounds()
                    if rounds is None:
                        continue
                    Printer.clear_screen()
                    f = choose_error_function()
                    if f is None:
                        continue
                    Printer.clear_screen()
                    configurations = choose_initial_configuration(range(min_size, max_size + 1))
                    if configurations is None:
                        continue
                    Printer.clear_screen()
                    run_benchmark(rounds, min_size, max_size, f=f, fixed_by_size=configurations)
                    if not wait_for_home():
                        return
                    break
            Printer.clear_screen()
        except HomeRequested:
            Printer.clear_screen()
        except ExitRequested:
            return


if __name__ == "__main__":
    main()
