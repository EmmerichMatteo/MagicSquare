import random

from Entities.matrix import Matrix


def propose_next_step(current, errors=None, lines=None, cells=None):
    # Propose a random swap and calculate its fitness delta without applying it.
    array = current.array
    i, j = random.sample(range(len(array)) if cells is None else cells, 2)
    changes = None
    if errors is not None:
        # Calculate the delta using only the affected line errors.
        changes = Matrix._swap_changes(array, i, j, lines)
        de = sum(2 * errors[line] * change + change * change
                 for line, change in changes.items())
    else:
        # Evaluate the candidate and restore the original array, even on failure.
        array[i], array[j] = array[j], array[i]
        try:
            de = current.objective_function(array) - current.value
        finally:
            array[i], array[j] = array[j], array[i]
    return de, i, j, changes

def do_next_step(current, i, j, de, errors=None, changes=None):
    # Apply the accepted swap and update the cached fitness and line errors.
    current.swap(i, j, delta=de)
    if errors is not None:
        for line, change in changes.items():
            errors[line] += change
