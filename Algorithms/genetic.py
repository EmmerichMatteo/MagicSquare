import random

from Algorithms.functions import check_constraints
from Entities.geneticMatrix import GeneticMatrix
from Entities.matrix import Matrix


def genetic_permutation(
    f,
    initial_or_n,
    n_matrices: int | None = None,
    excluded: set[tuple[int, ...]] | None = None,
) -> list[GeneticMatrix]:
    """Genera candidati distinti e li ordina per errore crescente."""
    n = initial_or_n.n if isinstance(initial_or_n, Matrix) else int(initial_or_n)
    if n <= 2:
        raise ValueError("n must be greater than 2")
    if n_matrices is None:
        n_matrices = 5 * n * n

    values = range(1, n * n + 1)

    # Copia le esclusioni per poter aggiungere i candidati già generati
    # senza modificare l'insieme ricevuto dal chiamante.
    seen = set() if excluded is None else set(excluded)
    matrices = []

    while len(matrices) < n_matrices:
        # Estrae tutti i numeri senza ripetizioni, in ordine casuale.
        array = random.sample(values, len(values))
        key = tuple(array)
        if key in seen or not check_constraints(array):
            continue

        seen.add(key)
        score = int(f(array))
        matrices.append(GeneticMatrix(n, array, fitnessValue=score))

        # Una soluzione permette di terminare prima di completare la lista.
        if score == 0:
            break

    matrices.sort(key=lambda matrix: matrix.fitnessValue)
    return matrices


def _crossover(parent, donor):
    """Copia un blocco della base e completa il figlio nell'ordine del donatore."""
    # I tagli sono confini dell'array piatto. Il blocco può attraversare più righe.
    start, end = sorted(random.sample(range(len(parent) + 1), 2))
    block = parent[start:end]
    inherited = set(block)

    # Salta i valori già ereditati per conservare la permutazione.
    remaining = [value for value in donor if value not in inherited]

    # Rimette il blocco nelle stesse posizioni che occupava nella base.
    return remaining[:start] + block + remaining[start:]


def _mutate(child, cells, score=None, f=None):
    """Scambia due celle distinte, conservando tutti i valori del quadrato."""
    i, j = random.sample(cells, 2)
    child[i], child[j] = child[j], child[i]
    if f is not None:
        new_score = int(f(child))
        return child, new_score
    if score is not None:
        return child, score
    return child


def _mutate_best(child, score, f, cells,n):
    """Confronta il candidato con un massimo di dodici varianti."""
    best, best_score = child, score

    for _ in range(n):
        # Ogni variante riparte dallo stesso candidato.
        mutant = child.copy()
        _mutate(mutant, cells)

        mutant_score = int(f(mutant))

        # Accetta un miglioramento. A parità con il candidato originale,
        # preferisce la prima variante che raggiunge lo stesso errore.
        if mutant_score < best_score or (
            mutant_score == best_score and best is child
        ):
            best, best_score = mutant, mutant_score
        if best_score == 0:
            break

    return best, best_score


def genetic(f, initial, max_generations: int | None = None) -> GeneticMatrix:
    """Cerca un quadrato magico e restituisce il miglior candidato trovato."""
    # Se riceve una Matrix, ne usa la dimensione per creare una popolazione casuale.
    n = initial.n if isinstance(initial, Matrix) else int(initial)
    if n <= 2:
        raise ValueError("n must be greater than 2")
    if max_generations is None:
        max_generations = 350 * n * n

    population_size = 5 * n * n
    indices = range(population_size)
    cells = range(n * n)
    values = range(1, n * n + 1)

    # Ogni individuo è una permutazione dei numeri da 1 a n².
    # Il punteggio di population[i] è conservato in scores[i].
    population = [random.sample(values, len(cells)) for _ in indices]
    scores = [int(f(array)) for array in population]

    # Conserva il record a parte, anche se la sua posizione viene rigenerata.
    best_index = min(indices, key=scores.__getitem__)
    best, best_score = population[best_index], scores[best_index]
    stalled = 0

    if best_score == 0:
        return GeneticMatrix(n, best, fitnessValue=0)

    # Ciclo delle generazioni:
    # A ogni generazione viene creata una new_population di dimensione pari a population_size.
    # Quando new_population è completa, sostituisce la popolazione corrente (generational GA).
    for _ in range(max_generations):
        new_population = []
        new_scores = []

        while len(new_population) < population_size:
            parent, donor = random.sample(indices, 2)

            # Con punteggi diversi, il migliore fa da base nel 70% dei casi.
            # A parità, vale l'ordine di estrazione.
            if scores[parent] > scores[donor]:
                parent, donor = donor, parent
            if scores[parent] != scores[donor] and random.random() < 0.30:
                parent, donor = donor, parent

            # Se il crossover salta, il candidato di partenza è la base.
            child, score = population[parent], scores[parent]
            if random.random() < 0.65:
                child = _crossover(child, population[donor])
                score = int(f(child))
            
            # La mutazione ha una probabilità separata e salta se il candidato
            # è già una soluzione.
            if score!= 0 and random.random() < 0.85:
                child, score = _mutate_best(child, score, f, cells, n)
            if score!= 0 and random.random() < 0.15:
                child, score = _mutate(child.copy(), cells, score, f)

            if score == 0:
                return GeneticMatrix(n, child, fitnessValue=0)

            new_population.append(child)
            new_scores.append(score)

            if score < best_score:
                best, best_score, stalled = child, score, 0

        # Terminato il ciclo di generazione, la nuova popolazione sostituisce la precedente
        population = new_population
        scores = new_scores

        # Conta le generazioni che non migliorano il record globale.
        stalled += 1
        if stalled >= 500:
            # Rigenera il 20% della popolazione in posizioni scelte a caso.
            for i in random.sample(indices, population_size // 5):
                immigrant = random.sample(values, len(cells))
                score = int(f(immigrant))
                if score == 0:
                    return GeneticMatrix(n, immigrant, fitnessValue=0)

                population[i], scores[i] = immigrant, score
                if score < best_score:
                    best, best_score = immigrant, score

            stalled = 0

    # Al limite delle generazioni restituisce il record dell'intera ricerca.
    return GeneticMatrix(n, best, fitnessValue=best_score)