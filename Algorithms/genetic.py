import random
from math import ceil
from Algorithms.functions import check_constraints
from Algorithms.refinement import final_refine
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
    """Run the genetic search and refine its result with bounded swap searches."""
    result = _genetic_search(f, initial, max_generations)
    if not isinstance(result, GeneticMatrix) or result.fitnessValue == 0:
        return result
    refined = final_refine(result.array, f=f)
    return GeneticMatrix(result.n, refined['array'], fitnessValue=refined['fitness'])


def _genetic_search(f, initial, max_generations: int | None = None):
    n = initial.n if isinstance(initial, Matrix) else int(initial)
    if n <= 2:
        raise ValueError("n must be greater than 2")
    if max_generations is None:
        max_generations = 50 * n * n
    population = genetic_permutation(f, initial)

    total_cells = n * n
    x = (total_cells // 2) + 1 if total_cells % 2 != 0 else total_cells // 2

    # Relative rank weights, reused across all generations.
    num_pop = len(population)
    if num_pop <= 1 or population[0].fitnessValue == 0:
        return population[0] if population else initial
    step = (90.0 - 10.0) / (num_pop - 1)
    weights = [90.0 - i * step for i in range(num_pop)]
    elite_count = ceil(num_pop * 0.02)
    replacement_count = min(ceil(num_pop * 0.10), num_pop - elite_count)
    best_fitness = population[0].fitnessValue
    stagnant_generations = 0

    for _ in range(max_generations):
        # Carry elite individuals forward without changes.
        new_population: list[GeneticMatrix] = population[:elite_count]
        seen_population = {tuple(matrix.array) for matrix in new_population}

        while len(new_population) < len(population):
            # Lower fitness gives a higher probability of parent selection.
            m1, m2 = random.choices(population, weights=weights, k=2)
            while m2 is m1 and len(population) > 1:
                m2 = random.choices(population, weights=weights, k=1)[0]

            # Identify the parent with the lower fitness error.
            if m1.fitnessValue <= m2.fitnessValue:
                best_parent, second_parent = m1, m2
            else:
                best_parent, second_parent = m2, m1

            # Preserve x random positions from the better parent.
            new_array = [0] * total_cells
            selected_values = set()
            for idx in random.sample(range(total_cells), x):
                new_array[idx] = best_parent.array[idx]
                selected_values.add(best_parent.array[idx])

            # Fill the empty positions in the second parent's order.
            remaining_values = iter(
                val for val in second_parent.array if val not in selected_values
            )
            for idx in range(total_cells):
                if new_array[idx] == 0:
                    new_array[idx] = next(remaining_values)
            
            # Mutation: swap two random positions with a 15% probability.
            if random.random() < 0.15:
                idx1, idx2 = random.sample(range(total_cells), 2)
                new_array[idx1], new_array[idx2] = new_array[idx2], new_array[idx1]

            # Reject duplicates, including copies of elite individuals.
            new_key = tuple(new_array)
            if new_key in seen_population:
                continue

            # Validate constraints, evaluate fitness and add the child.
            if check_constraints(new_array):
                fitness = int(f(new_array))
                new_population.append(GeneticMatrix(n, new_array, fitnessValue=fitness))
                seen_population.add(new_key)
                if fitness == 0:
                    return new_population[-1]

        if not new_population:
            break

        # Track generations without an improvement to the best fitness.
        new_population.sort(key=lambda m: m.fitnessValue)
        if new_population[0].fitnessValue < best_fitness:
            best_fitness = new_population[0].fitnessValue
            stagnant_generations = 0
        else:
            stagnant_generations += 1

        # Replace the worst 10% after 100 stagnant generations.
        if stagnant_generations >= 100:
            retained_keys = {tuple(matrix.array) for matrix in new_population[:-replacement_count]}
            immigrants = genetic_permutation(f, n, n_matrices=replacement_count, excluded=retained_keys)
            if immigrants[0].fitnessValue == 0:
                return immigrants[0]
            new_population[-replacement_count:] = immigrants
            new_population.sort(key=lambda m: m.fitnessValue)
            best_fitness = new_population[0].fitnessValue
            stagnant_generations = 0

        population = new_population

    return population[0] if population else initial
