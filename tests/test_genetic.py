import random
import unittest
from collections import Counter
from heapq import nsmallest
from itertools import combinations, cycle, islice, permutations
from unittest.mock import patch

from Algorithms.functions import check_constraints, objective_function
from Algorithms.genetic import _crossover, _mutate, _mutate_trials, _random_individual, _tournament, genetic


class SeededTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(random.setstate, random.getstate())
        random.seed(42)


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


class CrossoverTests(SeededTests):
    def test_inherits_positions_and_completes_in_donor_order(self):
        parent = list(range(1, 10))
        donor = list(reversed(parent))
        with patch("Algorithms.genetic.random.sample", return_value=[2, 6]):
            child = _crossover(parent, donor)
        self.assertEqual(child, [9, 8, 3, 4, 5, 6, 7, 2, 1])
        self.assertTrue(check_constraints(child))
        self.assertEqual(parent, list(range(1, 10)))
        self.assertEqual(donor, list(range(9, 0, -1)))

    def test_crossover_uses_better_parent_as_base(self):
        for fitness in (lambda array: array[0], lambda array: 1):
            with self.subTest(fitness=fitness):
                with (
                    patch("Algorithms.genetic._tournament", side_effect=lambda scores, excluded=None: 1 if excluded is None else 0),
                    patch("Algorithms.genetic._crossover", wraps=_crossover) as crossover,
                    patch("Algorithms.genetic.random.random", side_effect=cycle([0.0, 1.0])),
                ):
                    genetic(fitness, 3, max_generations=1)
                self.assertGreater(crossover.call_count, 0)
                for call in crossover.call_args_list:
                    parent, donor = call.args
                    self.assertLessEqual(fitness(parent), fitness(donor))

    def test_crossover_probability_boundary(self):
        for draw in (0.0, 0.799999, 0.8, 1.0):
            with self.subTest(draw=draw):
                with (
                    patch("Algorithms.genetic.random.random", side_effect=cycle([draw, 1.0])) as probability,
                    patch("Algorithms.genetic._crossover", wraps=_crossover) as crossover,
                ):
                    genetic(lambda array: 1, 3, max_generations=1)
                if draw < 0.8:
                    self.assertGreater(crossover.call_count, 0)
                    self.assertEqual(crossover.call_count, probability.call_count // 2)
                else:
                    crossover.assert_not_called()

    def test_skipping_crossover_copies_parent_before_mutation(self):
        parents = []
        originals = []

        def fitness(array):
            if len(parents) < 45:
                parents.append(array)
                originals.append(array.copy())
            return 1

        with patch("Algorithms.genetic.random.random", side_effect=cycle([1.0, 0.0])):
            genetic(fitness, 3, max_generations=1)
        self.assertEqual(parents, originals)

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

        self.assertGreater(evaluations, 45)
        self.assertTrue(check_constraints(result.array))
        self.assertEqual(result.fitnessValue, objective_function(result.array) + 1)


class MutationTests(SeededTests):
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
        for draw in (0.0, 0.349999, 0.35, 0.9):
            with self.subTest(draw=draw):
                with (
                    patch("Algorithms.genetic.random.random", side_effect=cycle([1.0, draw])) as probability,
                    patch("Algorithms.genetic._mutate_trials", wraps=_mutate_trials) as mutate,
                    patch("Algorithms.genetic._mutate_best", side_effect=AssertionError("local search enabled")),
                ):
                    genetic(lambda array: 1, 3, max_generations=1)
                expected = probability.call_count // 2 if draw < 0.35 else 0
                self.assertEqual(mutate.call_count, expected)

    def test_two_trials_are_used_regardless_of_matrix_size(self):
        for n in (3, 4, 5):
            with self.subTest(n=n):
                with (
                    patch("Algorithms.genetic.random.random", side_effect=cycle([1.0, 0.0])),
                    patch("Algorithms.genetic._mutate_trials", wraps=_mutate_trials) as mutate,
                ):
                    genetic(lambda array: 1, n, max_generations=1)
                self.assertGreater(mutate.call_count, 0)
                self.assertTrue(all(call.args[-1] == 2 for call in mutate.call_args_list))

    def test_solution_skips_mutation(self):
        solved = [8, 1, 6, 3, 5, 7, 4, 9, 2]
        with (
            patch("Algorithms.genetic._crossover", return_value=solved),
            patch("Algorithms.genetic.random.random", return_value=0.0) as probability,
            patch("Algorithms.genetic._mutate_trials") as mutate,
        ):
            result = genetic(objective_function, 3, max_generations=1)
        self.assertEqual(result.fitnessValue, 0)
        probability.assert_called_once()
        mutate.assert_not_called()


class StagnationMutationTests(SeededTests):
    def run_schedule(self, generations, improvement_generation=None,
                     immigration_improves=False, solve_generation=None):
        state = {"generation": 0, "single": Counter(), "trials": Counter(),
                 "better": set(), "immigrations": 0}
        solved = [8, 1, 6, 3, 5, 7, 4, 9, 2]

        def fitness(array):
            key = tuple(array)
            if solve_generation is not None and key == tuple(solved):
                return 0
            return 9 if key in state["better"] else 10

        def select(count, indices, key):
            state["generation"] += 1
            return nsmallest(count, indices, key=key)

        def single(child, cells, score, f):
            generation = state["generation"]
            state["single"][generation] += 1
            child, score = _mutate(child, cells, score, f)
            if generation == improvement_generation and not state["better"]:
                state["better"].add(tuple(child))
                score = 9
            return child, score

        def trials(child, score, f, cells, count):
            state["trials"][state["generation"]] += 1
            return _mutate_trials(child, score, f, cells, count)

        def individual(values, excluded):
            array, key = _random_individual(values, excluded)
            if len(excluded) == 45:
                state["immigrations"] += 1
                if immigration_improves:
                    state["better"].add(key)
            return array, key

        def crossover(parent, donor):
            if state["generation"] == solve_generation:
                return solved.copy()
            return _crossover(parent, donor)

        with (
            patch("Algorithms.genetic.nsmallest", side_effect=select),
            patch("Algorithms.genetic._mutate", side_effect=single),
            patch("Algorithms.genetic._mutate_trials", side_effect=trials),
            patch("Algorithms.genetic._random_individual", side_effect=individual),
            patch("Algorithms.genetic._crossover", side_effect=crossover),
            patch("Algorithms.genetic.random.random", return_value=0.0),
        ):
            result = genetic(fitness, 3, max_generations=generations)
        self.assertTrue(check_constraints(result.array))
        self.assertEqual(result.fitnessValue, fitness(result.array))
        return state, result

    def test_random_mutation_starts_after_50_complete_stalled_generations(self):
        state, _ = self.run_schedule(52)
        for generation in range(1, 51):
            self.assertGreater(state["trials"][generation], 0)
            self.assertEqual(state["single"][generation], 0)
        for generation in (51, 52):
            self.assertGreater(state["single"][generation], 0)
            self.assertEqual(state["trials"][generation], 0)

    def test_improvement_immediately_restores_normal_mutation_and_resets_stall(self):
        state, result = self.run_schedule(104, improvement_generation=53)
        self.assertEqual(result.fitnessValue, 9)
        self.assertEqual(state["single"][53], 1)
        self.assertGreater(state["trials"][53], 0)
        for generation in range(54, 104):
            self.assertGreater(state["trials"][generation], 0)
            self.assertEqual(state["single"][generation], 0)
        self.assertGreater(state["single"][104], 0)
        self.assertEqual(state["trials"][104], 0)

    def test_immigration_without_improvement_keeps_random_mutation_active(self):
        state, _ = self.run_schedule(201)
        self.assertEqual(state["immigrations"], 9)
        self.assertGreater(state["single"][201], 0)
        self.assertEqual(state["trials"][201], 0)

    def test_improving_immigration_restores_normal_mutation(self):
        state, result = self.run_schedule(201, immigration_improves=True)
        self.assertEqual(result.fitnessValue, 9)
        self.assertEqual(state["immigrations"], 9)
        self.assertEqual(state["single"][201], 0)
        self.assertGreater(state["trials"][201], 0)

    def test_solution_during_stall_skips_both_mutations(self):
        state, result = self.run_schedule(51, solve_generation=51)
        self.assertEqual(result.array, [8, 1, 6, 3, 5, 7, 4, 9, 2])
        self.assertEqual(result.fitnessValue, 0)
        self.assertEqual(state["single"][51], 0)
        self.assertEqual(state["trials"][51], 0)


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


class ElitismTests(SeededTests):
    def test_elite_count_and_remaining_population_size(self):
        for n, expected_elites in ((3, 4), (4, 8), (5, 12), (6, 18), (10, 50)):
            with self.subTest(n=n):
                with (
                    patch("Algorithms.genetic.nsmallest", wraps=nsmallest) as select,
                    patch("Algorithms.genetic._crossover", side_effect=lambda parent, donor: parent.copy()) as crossover,
                    patch("Algorithms.genetic.random.random", return_value=1.0),
                ):
                    genetic(lambda array: 1, n, max_generations=1)
                self.assertEqual(select.call_args.args[0], expected_elites)
                crossover.assert_not_called()


class PopulationTests(SeededTests):
    def setUp(self):
        super().setUp()
        self.score_by_key = {}
        self.key_by_score = {}
        self.populations = []

    def fitness(self, array):
        key = tuple(array)
        if key not in self.score_by_key:
            score = len(self.score_by_key) + 1
            self.score_by_key[key] = score
            self.key_by_score[score] = key
        return self.score_by_key[key]

    def select(self, count, indices, key):
        self.populations.append([self.key_by_score[key(i)] for i in indices])
        return nsmallest(count, indices, key=key)

    def assert_unique_populations(self, n):
        for population in self.populations:
            self.assertEqual(len(population), 5 * n * n)
            self.assertEqual(len(set(population)), len(population))
            self.assertTrue(all(check_constraints(array) for array in population))

    def test_random_individual_rejects_existing_matrix(self):
        original = list(range(1, 10))
        other = list(reversed(original))
        excluded = {tuple(original)}
        with patch("Algorithms.genetic.random.sample", side_effect=[original, other]) as sample:
            array, key = _random_individual(range(1, 10), excluded)
        self.assertEqual(array, other)
        self.assertEqual(key, tuple(other))
        self.assertEqual(sample.call_count, 2)
        self.assertEqual(excluded, {tuple(original)})

    def test_initial_population_rejects_duplicates_before_evaluating(self):
        candidates = [list(p) for p in islice(permutations(range(1, 10)), 45)]
        draws = [candidates[0], candidates[0]] + candidates[1:]
        with patch("Algorithms.genetic.random.sample", side_effect=draws) as sample:
            result = genetic(self.fitness, 3, max_generations=0)
        self.assertEqual(sample.call_count, 46)
        self.assertEqual(len(self.score_by_key), 45)
        self.assertEqual(result.fitnessValue, 1)

    def test_generations_preserve_unique_matrices_and_distinct_parent_indices(self):
        for n in (4, 5):
            with self.subTest(n=n):
                self.populations.clear()

                def tournament(scores, excluded=None):
                    index = _tournament(scores, excluded)
                    self.assertNotEqual(index, excluded)
                    return index

                with (
                    patch("Algorithms.genetic.nsmallest", side_effect=self.select),
                    patch("Algorithms.genetic._tournament", side_effect=tournament),
                ):
                    result = genetic(self.fitness, n, max_generations=4)
                self.assert_unique_populations(n)
                self.assertEqual(result.fitnessValue, self.fitness(result.array))

    def test_repeated_duplicate_children_use_bounded_retries_and_new_individuals(self):
        with (
            patch("Algorithms.genetic.nsmallest", side_effect=self.select),
            patch("Algorithms.genetic.random.random", side_effect=cycle([0.0, 1.0])),
            patch("Algorithms.genetic._crossover", side_effect=lambda parent, donor: list(self.key_by_score[1])) as crossover,
        ):
            result = genetic(self.fitness, 3, max_generations=2)
        self.assertEqual(crossover.call_count, 2 * (45 - 4) * 10)
        self.assert_unique_populations(3)
        self.assertEqual(result.fitnessValue, 1)

    def test_immigration_preserves_unique_population_and_global_best_record(self):
        rng = random.Random(42)
        replacements = []

        def sample(values, count):
            if values == range(45):
                replacements.append(count)
                return list(range(count))  # Sostituisce anche l'elite in posizione zero.
            return rng.sample(values, count)

        with (
            patch("Algorithms.genetic.random.sample", side_effect=sample),
            patch("Algorithms.genetic.random.random", return_value=1.0),
            patch("Algorithms.genetic.nsmallest", side_effect=self.select),
        ):
            result = genetic(self.fitness, 3, max_generations=201)
        self.assertEqual(replacements, [9])
        self.assert_unique_populations(3)
        self.assertIn(self.key_by_score[1], self.populations[199])
        self.assertNotIn(self.key_by_score[1], self.populations[200])
        self.assertEqual(tuple(result.array), self.key_by_score[1])
        self.assertEqual(result.fitnessValue, 1)


if __name__ == "__main__":
    unittest.main()
