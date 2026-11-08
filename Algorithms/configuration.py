"""Shared validation and random completion of fixed cells (zero-based indices)."""
import random
from Entities.matrix import Matrix


def validate_fixed_cells(n, fixed_cells=None):
    Matrix._validate_size(n)
    fixed = dict(fixed_cells or {})
    if any(type(cell) is not int or not 0 <= cell < n*n for cell in fixed):
        raise ValueError("Fixed cell outside the square")
    if any(type(value) is not int or not 1 <= value <= n*n for value in fixed.values()):
        raise ValueError("Fixed values must be integers from 1 to n squared")
    if len(set(fixed.values())) != len(fixed):
        raise ValueError("Fixed values must be distinct")
    return fixed


def random_completion(n, fixed_cells=None):
    fixed = validate_fixed_cells(n, fixed_cells)
    remaining = [value for value in range(1, n*n+1) if value not in fixed.values()]
    random.shuffle(remaining)
    return [fixed[cell] if cell in fixed else remaining.pop() for cell in range(n*n)]
