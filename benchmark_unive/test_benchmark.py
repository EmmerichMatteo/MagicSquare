import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from benchmark_unive import benchmark
from Entities.matrix import Matrix
import main
from Algorithms.functions import error_function_square


class BenchmarkTests(unittest.TestCase):
    def test_runs_every_attempt_in_size_algorithm_order(self):
        calls = []

        def solve(name, size):
            calls.append((size, name))
            return Matrix(size)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.txt"
            with redirect_stdout(StringIO()), \
                    patch.object(benchmark, "back_tracking", side_effect=lambda n, **kwargs: solve("back", n)), \
                    patch.object(benchmark, "simulated_annealing", side_effect=lambda f, n, **kwargs: solve("sa", n)), \
                    patch.object(benchmark, "genetic", side_effect=lambda f, n, **kwargs: solve("genetic", n)):
                self.assertEqual(benchmark.run_benchmark(2, 3, 6, output=output), output)
            self.assertEqual(calls, [
                (size, name) for size in range(3, 7)
                for name in ("back", "sa", "genetic") for _ in range(2)
            ])
            report = output.read_text(encoding="utf-8")
            self.assertEqual(report.count("Result: "), 24)
            self.assertNotIn("Size | Algorithm", report)
            self.assertNotIn("Total execution time:", report)
            self.assertIn("Result matrix:", report)
            self.assertIn("NOT SOLVED", report)
            self.assertNotIn("Seed", report)
            separator = "\n" + "_" * 44 + "\n\n"
            for size in range(3, 7):
                self.assertIn(separator + f"Size: {size}x{size}", report)

    def test_interruption_preserves_completed_results(self):
        solution = Matrix(3, [8, 1, 6, 3, 5, 7, 4, 9, 2])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.txt"
            with redirect_stdout(StringIO()), patch.object(
                benchmark, "back_tracking", side_effect=[solution, KeyboardInterrupt]
            ):
                benchmark.run_benchmark(2, 3, 3, output=output)
            report = output.read_text(encoding="utf-8")
            self.assertIn("Result: SOLVED", report)
            self.assertIn("Benchmark interrupted", report)
            self.assertEqual(report.count("Result: "), 1)

    def test_initial_menu_test_home_and_exit(self):
        with redirect_stdout(StringIO()), \
                patch("builtins.input", side_effect=["2", "1", "1", "n", "h", "2", "b", "1", "3", "1", "n", "e"]), \
                patch.object(main.Printer, "clear_screen"), \
                patch.object(main, "run_benchmark") as run_tests, \
                patch.object(main, "run_algorithm") as run_algorithm:
            main.main()
        run_tests.assert_called_once_with(1, 3, 6, f=error_function_square, fixed_by_size={})
        run_algorithm.assert_called_once_with(main.ROUNDS, 3, 1, f=error_function_square, fixed_cells=None)

    def test_function_comparison_uses_both_objectives_once(self):
        from Algorithms.functions import error_function_absolute
        with patch.object(benchmark, "run_benchmark") as run:
            benchmark.run_function_comparison(5)
        self.assertEqual(run.call_count, 2)
        self.assertEqual([call.args for call in run.call_args_list], [(1, 5, 5), (1, 5, 5)])
        self.assertEqual([call.kwargs for call in run.call_args_list], [
            {"f": error_function_absolute}, {"f": error_function_square}])

    def test_comparison_menu_only_asks_for_side(self):
        with redirect_stdout(StringIO()), patch("builtins.input", side_effect=["2", "5", "4", "e"]), patch.object(main.Printer, "clear_screen"), patch.object(main, "run_function_comparison") as compare, patch.object(main, "choose_initial_configuration") as config, patch.object(main, "choose_test_rounds") as rounds:
            main.main()
        compare.assert_called_once_with(4)
        config.assert_not_called()
        rounds.assert_not_called()


class TestSizeMenuTests(unittest.TestCase):
    def test_presets_single_and_custom_ranges(self):
        from user_input import choose_test_sizes
        cases = [(["5", "5"], ("comparison", 5)), (["1"], (3, 6)), (["2"], (7, 10)),
                 (["3", "8"], (8, 8)), (["4", "5", "9"], (5, 9)),
                 (["3", "11", "y"], (11, 11)),
                 (["4", "7", "12", "n", "2"], (7, 10)),
                 (["4", "2", "5", "4", "8"], (5, 8)),
                 (["3", "b", "b"], None)]
        for answers, expected in cases:
            with self.subTest(answers=answers), redirect_stdout(StringIO()), patch("builtins.input", side_effect=answers):
                self.assertEqual(choose_test_sizes(), expected)

    def test_warning_only_above_ten(self):
        from user_input import choose_test_sizes
        for side in (10, 11):
            with redirect_stdout(StringIO()), patch("builtins.input", side_effect=["3", str(side)]), patch("user_input.confirm_large_square", return_value=True) as confirm:
                self.assertEqual(choose_test_sizes(), (side, side))
            self.assertEqual(confirm.call_count, int(side > 10))


if __name__ == "__main__":
    unittest.main()
