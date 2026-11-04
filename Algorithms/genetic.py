import random
from Algorithms.functions import check_constraints
from Entities.geneticMatrix import GeneticMatrix
from Entities.matrix import Matrix

# Costante N che definisce il numero di matrici da generare
N = 10000


def genetic_permutation(f, initial_or_n, n_matrices: int = N) -> list[GeneticMatrix]:
    n = initial_or_n.n if isinstance(initial_or_n, Matrix) else int(initial_or_n)
    base_elements = list(range(1, n * n + 1))
    matrices: list[GeneticMatrix] = []
    seen: set[tuple[int, ...]] = set()

    while len(matrices) < n_matrices:
        perm = list(base_elements)
        random.shuffle(perm)
        perm_tuple = tuple(perm)

        if perm_tuple not in seen and check_constraints(perm):
            seen.add(perm_tuple)
            fitness = int(f(perm))
            matrices.append(GeneticMatrix(n, perm, fitnessValue=fitness))

    matrices.sort(key=lambda m: m.fitnessValue)
    return matrices

def genetic(f, initial, max_generations: int = 1000):
    n = initial.n if isinstance(initial, Matrix) else int(initial)
    population = genetic_permutation(f, initial)

    total_cells = n * n
    x = (total_cells // 2) + 1 if total_cells % 2 != 0 else total_cells // 2

    generation = 0
    while len(population) > 1 and population[0].fitnessValue != 0 and generation < max_generations:
        generation += 1

        # Calcoliamo i pesi con interpolazione lineare:
        # l'individuo migliore (fitnessValue minore) ha peso 80, il peggiore ha peso 20,
        # e gli intermedi sono distribuiti uniformemente mantenendo l'ordine.
        num_pop = len(population)
        if num_pop == 1:
            weights = [1.0]
        else:
            step = (80.0 - 20.0) / (num_pop - 1)
            weights = [80.0 - i * step for i in range(num_pop)]

        new_population: list[GeneticMatrix] = []

        while len(new_population) < len(population):
            # Scelta randomica ponderata: chi ha fitnessValue più bassa ha probabilità maggiore
            m1, m2 = random.choices(population, weights=weights, k=2)
            while m2 is m1 and len(population) > 1:
                m2 = random.choices(population, weights=weights, k=1)[0]

            # Individua la matrice con fitness migliore (minor errore)
            if m1.fitnessValue <= m2.fitnessValue:
                best_parent, second_parent = m1, m2
            else:
                best_parent, second_parent = m2, m1

            # Salviamo i primi x valori della matrice con fitness migliore nelle stesse posizioni
            new_array = list(best_parent.array[:x])

            # Con un for scorriamo la seconda matrice e inseriamo i valori non ancora presenti
            for val in second_parent.array:
                if val not in new_array:
                    new_array.append(val)
                if len(new_array) == total_cells:
                    break
            
            # Mutazione: con una probabilità del 10% scambiamo due elementi casuali
            if random.random() < 0.10:
                idx1, idx2 = random.sample(range(total_cells), 2)
                new_array[idx1], new_array[idx2] = new_array[idx2], new_array[idx1]

            # Check dei vincoli di sicurezza, calcolo del fitness value e aggiunta a new_population
            if check_constraints(new_array):
                fitness = int(f(new_array))
                new_population.append(GeneticMatrix(n, new_array, fitnessValue=fitness))

        if not new_population:
            break

        # Ordiniamo la nuova popolazione per fitness e aggiorniamo population
        new_population.sort(key=lambda m: m.fitnessValue)
        population = new_population

    return population[0] if population else initial
