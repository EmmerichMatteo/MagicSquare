import importlib
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from Algorithms.configuration import validate_fixed_cells, random_completion
from Algorithms.functions import check_constraints, error_function_square, error_function_absolute
from Algorithms.backtracking.backtracking import back_tracking
from Algorithms.genetic.genetic import genetic
from Algorithms.genetic.genetic_helpers import _crossover, _mutate_trials
from Algorithms.simulated_annealing.simulated_annealing import simulated_annealing
from user_input import choose_initial_configuration

SOLVED = [8, 1, 6, 3, 5, 7, 4, 9, 2]


class ConfigurationTests(unittest.TestCase):
    def test_invalid_fixed_cells(self):
        for fixed in ({9: 1}, {-1: 1}, {0: 0}, {0: 10}, {0: 1, 1: 1}, {True: 2}):
            with self.subTest(fixed=fixed), self.assertRaises(ValueError):
                validate_fixed_cells(3, fixed)

    def test_solvers_complete_fixed_square_for_both_objectives(self):
        fixed = dict(enumerate(SOLVED[:-2]))
        for f in (error_function_square, error_function_absolute):
            for solve in (lambda: back_tracking(3, fixed),
                          lambda: genetic(f, 3, fixed),
                          lambda: simulated_annealing(f, 3, fixed)):
                result = solve()
                self.assertTrue(check_constraints(result.array, fixed))
                self.assertEqual(f(result.array), 0)

    def test_complete_unsolved_configuration(self):
        fixed = dict(enumerate(range(1, 10)))
        self.assertIsNone(back_tracking(3, fixed))
        for solve in (genetic, simulated_annealing):
            result = solve(error_function_square, 3, fixed)
            self.assertTrue(check_constraints(result.array, fixed))
            self.assertGreater(error_function_square(result.array), 0)

    def test_genetic_generations_preserve_fixed_cells(self):
        module = importlib.import_module("Algorithms.genetic.genetic")
        fixed = {0: 8, 4: 5}
        def fitness(array):
            self.assertTrue(check_constraints(array, fixed))
            return error_function_absolute(array) + 1
        with patch.object(module, "MAX_GENERATIONS_FACTOR", 1), patch.object(module, "MAX_ATTEMPTS", 1):
            result = genetic(fitness, 3, fixed)
        self.assertTrue(check_constraints(result.array, fixed))

    def test_initialization_and_operators_preserve_fixed_cells(self):
        fixed = {0: 8, 4: 5}
        free = [i for i in range(9) if i not in fixed]
        for _ in range(30):
            child = _crossover(random_completion(3, fixed), random_completion(3, fixed), free)
            child, score = _mutate_trials(child, error_function_square(child), error_function_square, free, 2)
            self.assertTrue(check_constraints(child, fixed))
            self.assertEqual(score, error_function_square(child))

    def test_configuration_input_validates_and_separates_sizes(self):
        answers = ["y", "0", "1", "8", "2", "8", "1", "5", "5", "", "1", "16", ""]
        with redirect_stdout(StringIO()), patch("builtins.input", side_effect=answers), patch("user_input.Printer.clear_screen"):
            result = choose_initial_configuration([3, 4])
        self.assertEqual(result, {3: {0: 8, 1: 1, 4: 5}, 4: {0: 16}})

    def test_annealing_search_preserves_fixed_cells(self):
        module = importlib.import_module("Algorithms.simulated_annealing.simulated_annealing")
        fixed = {0: 8, 4: 5}
        def fitness(array):
            self.assertTrue(check_constraints(array, fixed))
            return error_function_absolute(array) + 1
        with patch.object(module.time, "monotonic", side_effect=[0] * 22 + [1801]):
            result = simulated_annealing(fitness, 3, fixed)
        self.assertTrue(check_constraints(result.array, fixed))

    def test_configuration_preview_includes_explicit_empty_cells(self):
        output = StringIO()
        answers = ["y", "1", "8", "2", "0", "3", ".", ""]
        with redirect_stdout(output), patch("builtins.input", side_effect=answers), patch("user_input.Printer.clear_screen") as clear:
            self.assertEqual(choose_initial_configuration([3]), {3: {0: 8}})
        shown = output.getvalue()
        updated = shown.rsplit("Initial configuration 3x3", 1)[1]
        self.assertIn("1:8", updated)
        self.assertIn("2:0", updated)
        self.assertIn("3:0", updated)
        self.assertEqual(clear.call_count, 5)

    def test_home_and_exit_during_matrix_input(self):
        from user_input import HomeRequested, ExitRequested
        for action, exception in (("h", HomeRequested), ("e", ExitRequested)):
            for entries in (["y", action], ["y", "1", action]):
                with self.subTest(entries=entries), redirect_stdout(StringIO()), patch("builtins.input", side_effect=entries), patch("user_input.Printer.clear_screen"), self.assertRaises(exception):
                    choose_initial_configuration([3])

    def test_home_then_exit_returns_to_main_without_running(self):
        import main
        with redirect_stdout(StringIO()), patch("builtins.input", side_effect=["1", "3", "1", "y", "1", "h", "e"]), patch.object(main.Printer, "clear_screen"), patch.object(main, "run_algorithm") as run:
            main.main()
        run.assert_not_called()

    def test_navigation_clears_screen(self):
        from user_input import _read_choice, HomeRequested, wait_for_home
        for action in ("b", "back", "h", "home"):
            with self.subTest(action=action), patch("builtins.input", return_value=action), patch("user_input.Printer.clear_screen") as clear:
                if action in ("h", "home"):
                    with self.assertRaises(HomeRequested):
                        _read_choice("Choice: ")
                else:
                    self.assertEqual(_read_choice("Choice: "), action)
                clear.assert_called_once()
        with redirect_stdout(StringIO()), patch("builtins.input", return_value="h"), patch("user_input.Printer.clear_screen") as clear:
            self.assertTrue(wait_for_home())
            clear.assert_called_once()

    def test_zero_removes_a_previously_fixed_value(self):
        with redirect_stdout(StringIO()), patch("user_input.Printer.clear_screen"), patch("builtins.input", side_effect=["y", "1", "8", "1", ".", ""]):
            self.assertEqual(choose_initial_configuration([3]), {3: {}})

    def test_genetic_uses_generations_even_with_few_free_cells(self):
        from heapq import nsmallest
        module = importlib.import_module("Algorithms.genetic.genetic")
        for free_count in range(6):
            fixed = dict(enumerate(SOLVED[:9-free_count]))
            def fitness(array):
                self.assertTrue(check_constraints(array, fixed))
                return error_function_square(array) + 1
            with self.subTest(free_count=free_count), patch.object(module, "MAX_ATTEMPTS", 1), patch.object(module, "MAX_GENERATIONS_FACTOR", 1), patch.object(module, "nsmallest", wraps=nsmallest) as select:
                result = genetic(fitness, 3, fixed)
            self.assertEqual(select.call_count, 9)
            self.assertTrue(check_constraints(result.array, fixed))
