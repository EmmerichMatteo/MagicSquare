import random
from math import isqrt

from Algorithms.configuration import random_completion
from Algorithms.functions import error_function_square
from Entities.geneticMatrix import GeneticMatrix


def _tournament(scores, excluded=None):
    # Select the better of two distinct candidates, excluding the previous winner.
    size = len(scores)
    if size == 2 and excluded is not None:
        return 1 - excluded

    first = random.randrange(size)
    while first == excluded:
        first = random.randrange(size)
    second = random.randrange(size)
    while second == excluded or second == first:
        second = random.randrange(size)
    return first if scores[first] <= scores[second] else second


def _random_individual(values, excluded, fixed_cells=None):
    # Generate a permutation absent from the destination population.
    while True:
        array = (random_completion(isqrt(len(values)), fixed_cells) if fixed_cells
                 else random.sample(values, len(values)))
        key = tuple(array)
        if key not in excluded:
            return array, key


def _crossover(parent, donor, cells=None):
    if cells is not None:
        child = parent.copy()
        free = _crossover([parent[i] for i in cells], [donor[i] for i in cells])
        for i, value in zip(cells, free):
            child[i] = value
        return child
    # Copy a block from the base parent and fill the child in donor order.
    # Cuts are boundaries in the flat array; the block may span multiple rows.
    start, end = sorted(random.sample(range(len(parent) + 1), 2))
    block = parent[start:end]
    inherited = set(block)

    # Skip inherited values to preserve the permutation.
    remaining = [value for value in donor if value not in inherited]

    # Keep the block at its original positions in the base parent.
    return remaining[:start] + block + remaining[start:]


def _swap_fitness(child, score, i, j):
    # Update fitness before the swap using only the affected lines.
    n = isqrt(len(child))
    ri, ci = divmod(i, n)
    rj, cj = divmod(j, n)
    delta = child[j] - child[i]

    # The two row or column sums change by opposite amounts.
    if ri != rj:
        first = sum(child[ri * n:(ri + 1) * n])
        second = sum(child[rj * n:(rj + 1) * n])
        score += 2 * delta * (first - second + delta)
    if ci != cj:
        first = sum(child[k * n + ci] for k in range(n))
        second = sum(child[k * n + cj] for k in range(n))
        score += 2 * delta * (first - second + delta)

    target = n * (n * n + 1) // 2
    main_delta = delta * ((ri == ci) - (rj == cj))
    if main_delta:
        error = sum(child[k * n + k] for k in range(n)) - target
        score += main_delta * (2 * error + main_delta)
    other_delta = delta * ((ri + ci == n - 1) - (rj + cj == n - 1))
    if other_delta:
        error = sum(child[k * n + n - 1 - k] for k in range(n)) - target
        score += other_delta * (2 * error + other_delta)
    return score


def _mutate(child, cells, score=None, f=None):
    # Swap two distinct cells, preserving all values in the square.
    i, j = random.sample(cells, 2)
    incremental = f is error_function_square and score is not None
    if incremental:
        score = _swap_fitness(child, score, i, j)
    child[i], child[j] = child[j], child[i]
    if incremental:
        return child, score
    if f is not None:
        new_score = int(f(child))
        return child, new_score
    if score is not None:
        return child, score
    return child


def _mutate_trials(child, score, f, cells, n):
    # Try n distinct swaps on the original array and apply only the best.
    n = min(n, len(cells) * (len(cells) - 1) // 2)
    tried = set()
    best_pair, best_score = None, None

    while len(tried) < n:
        i, j = sorted(random.sample(cells, 2))
        if (i, j) in tried:
            continue
        tried.add((i, j))

        if f is error_function_square:
            candidate_score = _swap_fitness(child, score, i, j)
        else:
            child[i], child[j] = child[j], child[i]
            try:
                candidate_score = int(f(child))
            finally:
                child[i], child[j] = child[j], child[i]

        # The first swap wins ties; the original array is not a candidate.
        if best_score is None or candidate_score < best_score:
            best_pair, best_score = (i, j), candidate_score

    i, j = best_pair
    child[i], child[j] = child[j], child[i]
    return child, best_score


def create_population(f, values, population_size, fixed_cells=None):
    # Create distinct random individuals and calculate their fitness scores.
    population = []
    population_keys = set()
    while len(population) < population_size:
        array, key = _random_individual(values, population_keys, fixed_cells)
        population.append(array)
        population_keys.add(key)
    scores = [int(f(array)) for array in population]
    return population, population_keys, scores


def regenerate_population(
    f, n, values, population, scores, population_keys,
    best, best_score, stalled, divisor=5, fixed_cells=None
):
    # Replace a fraction (1 / divisor) of the population with distinct random individuals.
    population_size = len(population)
    for i in random.sample(range(population_size), population_size // divisor):
        immigrant, key = _random_individual(values, population_keys, fixed_cells)
        score = int(f(immigrant))
        if score == 0:
            return GeneticMatrix(n, immigrant, fitnessValue=0), best, best_score, stalled

        population_keys.remove(tuple(population[i]))
        population_keys.add(key)
        population[i], scores[i] = immigrant, score
        if score < best_score:
            best, best_score, stalled = immigrant, score, 0
    return None, best, best_score, stalled
