from math import isqrt


def objective_function(X):
    N = isqrt(len(X))
    if N == 0 or N * N != len(X):
        raise ValueError()

    M = N * (N**2 + 1) // 2

    error = 0

    for i in range(N):
        row_sum = sum(X[i * N:(i + 1) * N])
        error += (row_sum - M)**2

    for j in range(N):
        col_sum = sum(X[i * N + j] for i in range(N))
        error += (col_sum - M)**2

    main_diag = sum(X[i * N + i] for i in range(N))
    error += (main_diag - M)**2

    second_diag = sum(X[i * N + (N - 1 - i)] for i in range(N))
    error += (second_diag - M)**2

    return error


def check_constraints(X, fixed_cells=None):
    N = isqrt(len(X))

    if N == 0 or N * N != len(X):
        return False

    if any(type(value) is not int for value in X):
        return False

    if sorted(X) != list(range(1, N**2 + 1)):
        return False

    return True
