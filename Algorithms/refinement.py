from itertools import combinations
from time import process_time
from Algorithms.functions import objective_function, check_constraints


def refine(array, depth=1, max_steps=10, max_evaluations=200000, f=objective_function):
    start = process_time()
    current = list(array)
    score = int(f(current))
    original_score = score
    pairs = list(combinations(range(len(current)), 2))
    evaluations = 0
    moves = []
    exhausted = False
    reason = 'max_steps'
    for _ in range(max_steps):
        if score == 0:
            reason = 'zero'
            break
        best = None
        best_score = score
        best_depth = 0
        for i, j in pairs:
            if evaluations >= max_evaluations:
                exhausted = True
                break
            current[i], current[j] = current[j], current[i]
            value = int(f(current))
            evaluations += 1
            if value < best_score:
                best, best_score, best_depth = list(current), value, 1
            current[i], current[j] = current[j], current[i]
            if best_score == 0:
                break
        if best is None and depth == 2 and not exhausted:
            for pair_index, (i, j) in enumerate(pairs):
                current[i], current[j] = current[j], current[i]
                for second_index, (k, l) in enumerate(pairs):
                    if second_index == pair_index:
                        continue
                    if evaluations >= max_evaluations:
                        exhausted = True
                        break
                    current[k], current[l] = current[l], current[k]
                    value = int(f(current))
                    evaluations += 1
                    if value < best_score:
                        best, best_score, best_depth = list(current), value, 2
                    current[k], current[l] = current[l], current[k]
                    if best_score == 0:
                        break
                current[i], current[j] = current[j], current[i]
                if exhausted or best_score == 0:
                    break
        if best is not None:
            current, score = best, best_score
            moves.append(dict(swaps=best_depth, fitness=score))
        else:
            reason = 'budget' if exhausted else 'local_minimum'
            break
        if score == 0:
            reason = 'zero'
            break
        if exhausted:
            reason = 'budget'
            break
    assert score <= original_score
    assert check_constraints(current)
    assert int(f(current)) == score
    return dict(fitness=score, evaluations=evaluations, moves=moves,
                cpu_seconds=round(process_time()-start, 6), reason=reason,
                budget_exhausted=exhausted, array=current)


def beam_refine(array, width=50, max_depth=12, max_evaluations=100000, f=objective_function):
    from heapq import nsmallest
    start = process_time()
    initial = tuple(array)
    best, best_score = initial, int(f(list(initial)))
    evaluations = 0
    reason = 'max_depth'
    reached_depth = 0
    pairs = list(combinations(range(len(initial)), 2))
    seen = {initial}
    frontier = [(best_score, 0, initial)]
    if best_score == 0:
        return dict(fitness=0, evaluations=0, cpu_seconds=0.0, array=list(initial), reason='zero', depth=0)
    for depth in range(1, max_depth+1):
        reached_depth = depth
        candidates = []
        for _, _, parent in frontier:
            current = list(parent)
            for i, j in pairs:
                current[i], current[j] = current[j], current[i]
                key = tuple(current)
                if key not in seen:
                    if evaluations >= max_evaluations:
                        reason = 'budget'
                        break
                    seen.add(key)
                    score = int(f(current))
                    evaluations += 1
                    candidates.append((score, evaluations, key))
                    if score < best_score:
                        best, best_score = key, score
                    if best_score == 0:
                        reason = 'zero'
                        break
                current[i], current[j] = current[j], current[i]
            if reason in ('budget', 'zero'):
                break
        if reason in ('budget', 'zero'):
            break
        if not candidates:
            reason = 'exhausted'
            break
        frontier = nsmallest(width, candidates)
    assert check_constraints(list(best))
    assert int(f(list(best))) == best_score
    assert best_score <= int(f(list(initial)))
    return dict(fitness=best_score, evaluations=evaluations,
                cpu_seconds=round(process_time()-start, 6), array=list(best),
                reason=reason, depth=reached_depth)


def final_refine(array, f=objective_function):
    """Refine a matrix using bounded single-swap, double-swap and beam searches."""
    start = process_time()
    current = list(array)
    score = int(f(current))
    stages = []
    for name, function, options in (
        ('single', refine, dict(depth=1)),
        ('double', refine, dict(depth=2)),
        ('beam', beam_refine, dict(width=50, max_depth=12, max_evaluations=100000)),
        ('extended', beam_refine, dict(width=100, max_depth=30, max_evaluations=500000)),
    ):
        if score == 0:
            break
        result = function(current, f=f, **options)
        stages.append(dict(name=name, **result))
        current, score = result['array'], result['fitness']
    return dict(array=current, fitness=score,
                evaluations=sum(stage['evaluations'] for stage in stages),
                cpu_seconds=round(process_time()-start, 6), stages=stages)
