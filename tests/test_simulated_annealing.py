import itertools
import random
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import Algorithms.simulatedAnnealing as sa
from Algorithms.functions import objective_function
from Entities.matrix import Matrix


class SimulatedAnnealingTests(unittest.TestCase):
    def test_incremental_delta_for_every_pair(self):
        rng = random.Random(42)
        for n in range(2, 9):
            array = rng.sample(range(1, n * n + 1), n * n)
            errors = sa._line_errors(array, n)
            lines = sa._cell_lines(n)
            energy = objective_function(array)
            self.assertEqual(sum(e * e for e in errors), energy)
            for i, j in itertools.combinations(range(n * n), 2):
                changes = sa._swap_changes(array, i, j, lines)
                delta = sum(2 * errors[line] * change + change * change
                            for line, change in changes.items())
                candidate = array.copy()
                candidate[i], candidate[j] = candidate[j], candidate[i]
                self.assertEqual(delta, objective_function(candidate) - energy,
                                 (n, i, j))

    def test_errors_remain_exact_after_repeated_swaps(self):
        rng = random.Random(43)
        for n in (3, 6, 7):
            array = rng.sample(range(1, n * n + 1), n * n)
            errors = sa._line_errors(array, n)
            lines = sa._cell_lines(n)
            for _ in range(1000):
                i, j = rng.sample(range(n * n), 2)
                changes = sa._swap_changes(array, i, j, lines)
                array[i], array[j] = array[j], array[i]
                for line, change in changes.items():
                    errors[line] += change
                self.assertEqual(errors, sa._line_errors(array, n))

    def test_incremental_and_full_objective_follow_same_search(self):
        initial = Matrix(6, random.Random(5).sample(range(1, 37), 36))
        original = initial.array.copy()

        def run(f):
            calls = 0

            def clock():
                nonlocal calls
                calls += 1
                return 0 if calls <= 10001 else 1801

            random.seed(42)
            with patch.object(sa, 'time', SimpleNamespace(monotonic=clock)):
                result = sa.simulated_annealing(f, initial, initial_temperature=10)
            return result.array, random.getstate()

        incremental_result, incremental_state = run(objective_function)
        full_result, full_state = run(lambda array: objective_function(array))
        self.assertEqual(incremental_result, full_result)
        self.assertEqual(incremental_state, full_state)
        self.assertEqual(initial.array, original)
        self.assertLessEqual(objective_function(incremental_result),
                             objective_function(original))

    def test_returns_solved_input(self):
        initial = Matrix(3, [8, 1, 6, 3, 5, 7, 4, 9, 2])
        self.assertIs(sa.simulated_annealing(objective_function, initial), initial)


if __name__ == '__main__':
    unittest.main()
