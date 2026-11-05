import random

from Algorithms.functions import check_constraints
from Entities.geneticMatrix import GeneticMatrix
from Entities.matrix import Matrix

def genetic_permutation(f, initial_or_n, n_matrices: int | None = None, excluded: set[tuple[int, ...]] | None = None) -> list[GeneticMatrix]:
    n = initial_or_n.n if isinstance(initial_or_n, Matrix) else int(initial_or_n)
    if n <= 2:
        raise ValueError("n must be greater than 2")
    if n_matrices is None:
        n_matrices = 5 * n * n
    base_elements = list(range(1, n * n + 1))
    matrices: list[GeneticMatrix] = []
    seen: set[tuple[int, ...]] = set() if excluded is None else set(excluded)

    while len(matrices) < n_matrices:
        perm = list(base_elements)
        random.shuffle(perm)
        perm_tuple = tuple(perm)

        if perm_tuple not in seen and check_constraints(perm):
            seen.add(perm_tuple)
            fitness = int(f(perm))
            matrices.append(GeneticMatrix(n, perm, fitnessValue=fitness))
            if fitness == 0:
                break

    matrices.sort(key=lambda m: m.fitnessValue)
    return matrices

def genetic(f, initial, max_generations: int | None = None):
    """Return the best individual found by genetic reproduction."""
    return _genetic_search(f, initial, max_generations)


def _crossover(parent, donor, cells):
    """Inherit a random number of positions, up to a third of the cells."""
    child = parent.copy()
    count = random.randint(1, len(cells) // 3)
    inherited = random.sample(cells, count)
    for index in inherited:
        value = donor[index]
        if child[index] != value:
            other = child.index(value)
            child[index], child[other] = child[other], child[index]
    return child if child != parent else None


def _mutate(child, cells, swaps, prefer_nearby=False):
    for _ in range(swaps):
        if prefer_nearby and random.random() < 0.90:
            i = random.randrange(len(cells))
            value = child[i]
            target = value + random.choice((-2, -1, -1, 1, 1, 2))
            if not 1 <= target <= len(cells):
                target = value + (1 if target < 1 else -1)
            j = child.index(target)
        else:
            i, j = random.sample(cells, 2)
        child[i], child[j] = child[j], child[i]


def _correct_one_line(child, lines, target):
    """Try one directed swap to make a sampled row, column or diagonal exact."""
    for line in random.sample(lines, 4):
        delta = target - sum(child[i] for i in line)
        if delta == 0:
            continue
        i = random.choice(line)
        desired = child[i] + delta
        if 1 <= desired <= len(child):
            j = child.index(desired)
            if j not in line:
                child[i], child[j] = child[j], child[i]
                return True
    return False


def _select_mutation(child, score, f, cells, lines, target, near_solution):
    for _ in range(3 if near_solution else 1):
        mutant = child.copy()
        swaps = random.choice((1, 1, 2, 2, 3, 4))
        if near_solution and random.random() < 0.60:
            _mutate(mutant, cells, swaps - 1, prefer_nearby=True)
            if not _correct_one_line(mutant, lines, target):
                _mutate(mutant, cells, 1, prefer_nearby=True)
        else:
            _mutate(mutant, cells, swaps, prefer_nearby=near_solution)
        mutant_score = int(f(mutant))
        if mutant_score <= score:
            child, score = mutant, mutant_score
            if score == 0:
                break
    return child, score


def _exploration_chance(array, lines, target):
    """Probability that two independently sampled lines both need repair."""
    incorrect = sum(sum(array[i] for i in line) != target for line in lines)
    return (incorrect / len(lines)) ** 2


def _genetic_search(f, initial, max_generations: int | None = None):
    n = initial.n if isinstance(initial, Matrix) else int(initial)
    if n <= 2:
        raise ValueError("n must be greater than 2")
    if max_generations is None:
        max_generations = 350 * n * n

    population_size = 48
    indices = range(population_size)
    cells = range(n * n)
    values = range(1, n * n + 1)
    target = n * (n * n + 1) // 2
    lines = [range(i * n, (i + 1) * n) for i in range(n)]
    lines += [range(i, n * n, n) for i in range(n)]
    lines += [range(0, n * n, n + 1), range(n - 1, n * n - 1, n - 1)]
    population = [random.sample(values, len(cells)) for _ in indices]
    scores = [int(f(array)) for array in population]
    exploration = [_exploration_chance(array, lines, target) for array in population]
    stalled = [0] * population_size
    best_index = min(indices, key=scores.__getitem__)
    best_array, best_score = population[best_index], scores[best_index]
    if best_score == 0:
        return GeneticMatrix(n, best_array, fitnessValue=0)

    # One generation attempts one offspring per population slot on average.
    # Replace parents immediately, preserving multiple lines of descent.
    for _ in range(max_generations):
        for _ in indices:
            parent, donor = random.sample(indices, 2)
            if scores[parent] != scores[donor]:
                if scores[donor] < scores[parent]:
                    parent, donor = donor, parent
                if random.random() < 0.30:
                    parent, donor = donor, parent

            parent_score = scores[parent]
            preserve_lines = random.random() >= exploration[parent]
            child = _crossover(population[parent], population[donor], cells)
            if child is None:
                child, score = _select_mutation(
                    population[parent], parent_score, f, cells, lines, target, preserve_lines
                )
            else:
                score = int(f(child))
                if score and random.random() < 0.65:
                    child, score = _select_mutation(child, score, f, cells, lines, target, preserve_lines)
            if score == 0:
                return GeneticMatrix(n, child, fitnessValue=0)
            if score < best_score:
                best_array, best_score = child, score

            if score <= parent_score and child is not population[parent]:
                population[parent], scores[parent] = child, score
                exploration[parent] = _exploration_chance(child, lines, target)
            if score < parent_score:
                stalled[parent] = 0
                continue

            stalled[parent] += 1
            if stalled[parent] >= 250:
                elite = sorted(indices, key=scores.__getitem__)[:population_size // 4]
                founder = random.choice(elite)
                immigrant = population[founder].copy()
                # Preserve more of a good founder's structure on most restarts.
                nearby_restart = random.random() < 0.85 * (1 - exploration[founder])
                _mutate(immigrant, cells, random.randint(2, 7), prefer_nearby=nearby_restart)
                score = int(f(immigrant))
                if score == 0:
                    return GeneticMatrix(n, immigrant, fitnessValue=0)
                population[parent], scores[parent], stalled[parent] = immigrant, score, 0
                exploration[parent] = _exploration_chance(immigrant, lines, target)
                if score < best_score:
                    best_array, best_score = immigrant, score

    return GeneticMatrix(n, best_array, fitnessValue=best_score)
