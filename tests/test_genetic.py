import random
import unittest
from heapq import nsmallest
from itertools import combinations
from unittest.mock import patch

from Algorithms.functions import check_constraints, objective_function
from Algorithms.genetic import _crossover, _mutate, _mutate_trials, _tournament, genetic


class TournamentTests(unittest.TestCase):
    def test_lower_fitness_wins_in_either_draw_order(self):
        for draw in ([0, 1], [1, 0]):
            with self.subTest(draw=draw):
                with patch("Algorithms.genetic.random.randrange", side_effect=draw) as sample:
                    self.assertEqual(_tournament([20, 5, 10]), 1)
                    self.assertEqual(sample.call_count, 2)
                    self.assertTrue(all(call.args == (3,) for call in sample.call_args_list))

    def test_tie_keeps_first_drawn_candidate(self):
        with patch("Algorithms.genetic.random.randrange", side_effect=[1, 0]):
            self.assertEqual(_tournament([5, 5]), 1)

    def test_second_tournament_excludes_first_winner(self):
        with patch("Algorithms.genetic.random.randrange", side_effect=[2, 0, 0, 1, 1, 0, 2]):
            first = _tournament([1, 2, 3])
            second = _tournament([1, 2, 3], excluded=first)
            self.assertEqual((first, second), (0, 1))

    def test_two_individuals_select_remaining_candidate_without_draw(self):
        for scores, draw in (([1, 2], [1, 0]), ([2, 1], [0, 1]), ([1, 1], [1, 0])):
            with self.subTest(scores=scores, draw=draw):
                with patch("Algorithms.genetic.random.randrange", side_effect=draw) as sample:
                    first = _tournament(scores)
                    second = _tournament(scores, excluded=first)
                    self.assertNotEqual(first, second)
                    self.assertEqual({first, second}, {0, 1})
                    self.assertEqual(sample.call_count, 2)

    def test_repeated_index_is_drawn_again(self):
        with patch("Algorithms.genetic.random.randrange", side_effect=[1, 1, 1, 0]):
            self.assertEqual(_tournament([2, 1, 3]), 1)


class CrossoverTests(unittest.TestCase):
    def test_inherits_positions_and_completes_in_donor_order(self):
        parent = list(range(1, 10))
        donor = list(reversed(parent))
        with patch("Algorithms.genetic.random.sample", return_value=[2, 6]):
            child = _crossover(parent, donor)
        self.assertEqual(child, [9, 8, 3, 4, 5, 6, 7, 2, 1])
        self.assertTrue(check_constraints(child))
        self.assertEqual(parent, list(range(1, 10)))
        self.assertEqual(donor, list(range(9, 0, -1)))

    def test_every_child_uses_crossover_with_better_parent_as_base(self):
        for fitness in (lambda array: array[0], lambda array: 1):
            with self.subTest(fitness=fitness):
                with (
                    patch("Algorithms.genetic._tournament", side_effect=[1, 0] * 45),
                    patch("Algorithms.genetic._crossover", wraps=_crossover) as crossover,
                    patch("Algorithms.genetic.random.random", return_value=1.0),
                ):
                    genetic(fitness, 3, max_generations=1)
                self.assertEqual(crossover.call_count, 42)
                for call in crossover.call_args_list:
                    parent, donor = call.args
                    self.assertLessEqual(fitness(parent), fitness(donor))

    def test_short_search_preserves_constraints_and_permutation(self):
        state = random.getstate()
        evaluations = 0

        def checked_fitness(array):
            nonlocal evaluations
            evaluations += 1
            self.assertTrue(check_constraints(array))
            self.assertEqual(sorted(array), list(range(1, 10)))
            # Evita l'uscita anticipata per verificare più generazioni.
            return objective_function(array) + 1

        try:
            random.seed(42)
            result = genetic(checked_fitness, 3, max_generations=4)
        finally:
            random.setstate(state)

        self.assertGreaterEqual(evaluations, 45 + 4 * 42)
        self.assertTrue(check_constraints(result.array))
        self.assertEqual(result.fitnessValue, objective_function(result.array) + 1)


class MutationTests(unittest.TestCase):
    def test_incremental_score_matches_full_fitness_for_every_swap(self):
        rng = random.Random(42)
        for n in (3, 4, 5):
            for _ in range(3):
                array = rng.sample(range(1, n * n + 1), n * n)
                score = objective_function(array)
                for i, j in combinations(range(n * n), 2):
                    with self.subTest(n=n, i=i, j=j):
                        child = array.copy()
                        with patch("Algorithms.genetic.random.sample", return_value=[i, j]):
                            mutated, new_score = _mutate(child, range(n * n), score, objective_function)
                        self.assertIs(mutated, child)
                        self.assertEqual(new_score, objective_function(mutated))
                        self.assertTrue(check_constraints(mutated))

    def test_custom_fitness_uses_full_evaluation(self):
        calls = []

        def custom(array):
            calls.append(array.copy())
            return array[0] * 10 + array[1]

        with patch("Algorithms.genetic.random.sample", return_value=[0, 1]):
            array, score = _mutate(list(range(1, 10)), range(9), 12, custom)
        self.assertEqual(score, 21)
        self.assertEqual(calls, [array])

    def test_missing_score_uses_full_objective(self):
        with patch("Algorithms.genetic.random.sample", return_value=[0, 1]):
            array, score = _mutate(list(range(1, 10)), range(9), f=objective_function)
        self.assertEqual(score, objective_function(array))

    def test_probability_boundary_and_disabled_local_search(self):
        for draw, expected in ((0.0, 42), (0.349999, 42), (0.35, 0), (0.9, 0)):
            with self.subTest(draw=draw):
                with (
                    patch("Algorithms.genetic.random.random", return_value=draw) as probability,
                    patch("Algorithms.genetic._mutate_trials", wraps=_mutate_trials) as mutate,
                    patch("Algorithms.genetic._mutate_best", side_effect=AssertionError("local search enabled")),
                ):
                    genetic(lambda array: 1, 3, max_generations=1)
                self.assertEqual(mutate.call_count, expected)
                self.assertEqual(probability.call_count, 42)

    def test_two_trials_are_used_regardless_of_matrix_size(self):
        for n in (3, 4, 5):
            with self.subTest(n=n):
                with (
                    patch("Algorithms.genetic.random.random", return_value=0.0),
                    patch("Algorithms.genetic._mutate_trials", wraps=_mutate_trials) as mutate,
                ):
                    genetic(lambda array: 1, n, max_generations=1)
                self.assertEqual(mutate.call_count, 5 * n * n - n)
                self.assertTrue(all(call.args[-1] == 2 for call in mutate.call_args_list))

    def test_solution_skips_mutation(self):
        solved = [8, 1, 6, 3, 5, 7, 4, 9, 2]
        with (
            patch("Algorithms.genetic.random.sample", return_value=list(range(1, 10))),
            patch("Algorithms.genetic._crossover", return_value=solved),
            patch("Algorithms.genetic.random.random") as probability,
            patch("Algorithms.genetic._mutate_trials") as mutate,
        ):
            result = genetic(objective_function, 3, max_generations=1)
        self.assertEqual(result.fitnessValue, 0)
        probability.assert_not_called()
        mutate.assert_not_called()


class MutationTrialTests(unittest.TestCase):
    def test_distinct_swaps_start_from_original_and_allow_worsening(self):
        original = list(range(1, 10))
        child = original.copy()
        candidates = []
        scores = iter([7, 4, 5])

        def custom(array):
            candidates.append(array.copy())
            return next(scores)

        with patch("Algorithms.genetic.random.sample", side_effect=[[0, 1], [1, 0], [2, 3], [4, 5]]) as sample:
            result, score = _mutate_trials(child, 1, custom, range(9), 3)

        self.assertEqual(sample.call_count, 4)
        self.assertEqual(len(candidates), 3)
        for candidate, (i, j) in zip(candidates, ((0, 1), (2, 3), (4, 5))):
            expected = original.copy()
            expected[i], expected[j] = expected[j], expected[i]
            self.assertEqual(candidate, expected)
        self.assertIs(result, child)
        self.assertEqual(result, candidates[1])
        self.assertEqual(score, 4)
        self.assertGreater(score, 1)

    def test_ties_keep_first_swap(self):
        with patch("Algorithms.genetic.random.sample", side_effect=[[0, 1], [2, 3], [4, 5]]):
            result, score = _mutate_trials(list(range(1, 10)), 1, lambda array: 5, range(9), 3)
        self.assertEqual(result, [2, 1] + list(range(3, 10)))
        self.assertEqual(score, 5)

    def test_incremental_trials_match_best_of_full_evaluations(self):
        rng = random.Random(42)
        for n in (3, 4, 5):
            for trial in range(10):
                with self.subTest(n=n, trial=trial):
                    original = rng.sample(range(1, n * n + 1), n * n)
                    pairs = rng.sample(list(combinations(range(n * n), 2)), n)
                    candidates = []
                    for i, j in pairs:
                        candidate = original.copy()
                        candidate[i], candidate[j] = candidate[j], candidate[i]
                        candidates.append(candidate)
                    expected = min(candidates, key=objective_function)
                    child = original.copy()
                    with patch("Algorithms.genetic.random.sample", side_effect=pairs) as sample:
                        result, score = _mutate_trials(child, objective_function(original), objective_function, range(n * n), n)
                    self.assertEqual(sample.call_count, n)
                    self.assertEqual(result, expected)
                    self.assertEqual(score, objective_function(expected))
                    self.assertTrue(check_constraints(result))

    def test_custom_fitness_error_restores_original(self):
        child = list(range(1, 10))
        with (
            patch("Algorithms.genetic.random.sample", return_value=[0, 1]),
            self.assertRaisesRegex(ValueError, "fitness failed"),
        ):
            _mutate_trials(child, 1, lambda array: (_ for _ in ()).throw(ValueError("fitness failed")), range(9), 3)
        self.assertEqual(child, list(range(1, 10)))


class ElitismTests(unittest.TestCase):
    def test_elite_count_and_remaining_population_size(self):
        for n, expected_elites in ((3, 3), (4, 4), (5, 5), (6, 6), (10, 10)):
            with self.subTest(n=n):
                with (
                    patch("Algorithms.genetic.nsmallest", wraps=nsmallest) as select,
                    patch("Algorithms.genetic._crossover", side_effect=lambda parent, donor: parent.copy()) as crossover,
                    patch("Algorithms.genetic.random.random", return_value=1.0),
                ):
                    genetic(lambda array: 1, n, max_generations=1)
                self.assertEqual(select.call_args.args[0], expected_elites)
                self.assertEqual(crossover.call_count, 5 * n * n - expected_elites)

    def test_best_survives_generations_but_can_be_replaced_by_immigration(self):
        best = list(range(1, 10))
        worse = [2, 1] + list(range(3, 10))
        regenerated = False

        def sample(values, count):
            nonlocal regenerated
            if values == range(45):
                regenerated = True
                return list(range(count))  # Include l'elite in posizione zero.
            return (worse if regenerated else best).copy()

        with (
            patch("Algorithms.genetic.random.sample", side_effect=sample),
            patch("Algorithms.genetic.random.random", return_value=1.0),
            patch("Algorithms.genetic._tournament", side_effect=lambda scores, excluded=None: 0 if excluded is None else 1),
            patch("Algorithms.genetic._crossover", side_effect=lambda parent, donor: worse.copy()),
            patch("Algorithms.genetic.nsmallest", wraps=nsmallest) as select,
        ):
            result = genetic(lambda array: array[0], 3, max_generations=201)

        self.assertTrue(regenerated)
        # Prima della rigenerazione l'elite conserva il punteggio 1.
        before_scores = select.call_args_list[199].kwargs["key"].__self__
        self.assertEqual(min(before_scores), 1)
        # Dopo la rigenerazione non resta nella popolazione, ma il record resta.
        after_scores = select.call_args_list[200].kwargs["key"].__self__
        self.assertEqual(min(after_scores), 2)
        self.assertEqual(result.array, best)
        self.assertEqual(result.fitnessValue, 1)


if __name__ == "__main__":
    unittest.main()
