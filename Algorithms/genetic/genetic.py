import random
from heapq import nsmallest
from math import factorial
from Algorithms.configuration import validate_fixed_cells

from Entities.geneticMatrix import GeneticMatrix
from .genetic_helpers import (
    _random_individual,
    _crossover,
    _mutate,
    _mutate_trials,
    _tournament,
    create_population,
    regenerate_population,
)

MAX_GENERATIONS_FACTOR = 350
POPULATION_SIZE_FACTOR = 5
ELITE_COUNT_DIVISOR = 10

MAX_ATTEMPTS = 100


def genetic(f, n, fixed_cells=None) -> GeneticMatrix:
    fixed = validate_fixed_cells(n, fixed_cells)
    best = None
    for _ in range(MAX_ATTEMPTS):
        result = _genetic_attempt(f, n, fixed)
        if best is None or result.fitnessValue < best.fitnessValue:
            best = result
        if best.fitnessValue == 0:
            break
    return best


def _genetic_attempt(f, n, fixed_cells=None) -> GeneticMatrix:
    fixed_cells = validate_fixed_cells(n, fixed_cells)
    max_generations = MAX_GENERATIONS_FACTOR * n * n
    cells = [i for i in range(n*n) if i not in fixed_cells]
    population_size = min(POPULATION_SIZE_FACTOR * n * n, factorial(len(cells)))
    elite_count = max(1, population_size // ELITE_COUNT_DIVISOR)

    indices = range(population_size)
    values = range(1, n * n + 1)

    # Create population
    population, population_keys, scores = create_population(f, values, population_size, fixed_cells)

    best_index = min(indices, key=scores.__getitem__)
    best, best_score = population[best_index], scores[best_index]
    stalled = 0

    if best_score == 0: 
        return GeneticMatrix(n, best, best_score)

    for _ in range(max_generations):

        generation_best_score = best_score
        elite_indices = nsmallest(elite_count, indices, key=scores.__getitem__)
        new_population = [population[i].copy() for i in elite_indices]
        new_scores = [scores[i] for i in elite_indices]
        new_keys = {tuple(array) for array in new_population}
        duplicate_attempts = 0

        while len(new_population) < population_size:

            # Tournament
            parent = _tournament(scores)
            donor = _tournament(scores, excluded=parent)
            
            # Crossover
            if scores[parent] > scores[donor]:
                parent, donor = donor, parent

            if random.random() < 0.80:
                child = _crossover(population[parent], population[donor], cells if fixed_cells else None)
                score = int(f(child))
            else:
                child = population[parent].copy()
                score = scores[parent]

            if score == 0:
                return GeneticMatrix(n, child, fitnessValue=0)
            
            # Mutation
            if stalled >= 50:
                child, score = _mutate(child, cells, score, f)
            elif random.random() < 0.35:
                child, score = _mutate_trials(child, score, f, cells, 2)

            # Add to new population[]
            key = tuple(child)
            if key in new_keys:
                duplicate_attempts += 1
                if duplicate_attempts < 10:
                    continue
                child, key = _random_individual(values, new_keys, fixed_cells)
                score = int(f(child))

            new_population.append(child)
            new_scores.append(score)
            new_keys.add(key)
            duplicate_attempts = 0

            if score < best_score:
                best, best_score, stalled = child, score, 0

        # Set population with the new population
        population = new_population
        scores = new_scores
        population_keys = new_keys

        # Count generations without improvement.
        if best_score == generation_best_score:
            stalled += 1

        # Regenerate 20% of the population.
        if stalled > 0 and stalled % 200 == 0 and population_size < factorial(len(cells)):
            # Replace individuals at randomly selected positions.
            solution, best, best_score, stalled = regenerate_population(
                f, n, values, population, scores, population_keys,
                best, best_score, stalled, divisor=5, fixed_cells=fixed_cells
            )
            if solution is not None:
                return solution

    # Best matrix
    return GeneticMatrix(n, best, fitnessValue=best_score)
