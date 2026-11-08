# MagicSquare

## University benchmark

`python main.py` opens the main menu in English:
`1. Try algorithms` for interactive runs and `2. Run tests` for benchmarks.
The test menu lets you choose 3x3 to 6x6, 7x7 to 10x10, a single size n,
or a custom range from a to b (inclusive, with 3 <= a <= b).
It then asks for the number of runs and, finally, an optional initial
configuration.
For sizes greater than 10, it asks for confirmation and warns that the search
may take a long time. For each size, it runs all backtracking attempts first,
then simulated annealing, then the genetic algorithm.
Every attempt runs even if the previous one found a solution.
Interactive runs and tests use the squared error function by default.

`benchmark_unive/benchmark.py` saves an English text report to
`benchmark_unive/benchmark-DATE-TIME.txt`, including settings, execution times,
fitness scores, validity checks, and matrices. Reports are excluded from Git.
`Ctrl+C` interrupts the benchmark while preserving completed results.
No additional timeout is imposed on individual algorithms.

To configure the range from a x a to b x b and the number of runs from the command line:

```powershell
python benchmark_unive/benchmark.py --min-size 3 --max-size 6 --rounds 2
```

## Backtracking

`back_tracking(n)` takes the side length and uses a copy of `Matrix.empty(n)`,
the shared matrix template with all cells set to zero.
It returns the solved matrix, or `None` if no solution exists.

```python
from Algorithms.backtracking.backtracking import back_tracking

solution = back_tracking(3)
if solution is not None:
    solution.print_matrix()
```

The search uses MRV, LCV, forward checking for uniqueness, and minimum/maximum
bounds on row, column, and diagonal sums. When a line has only one empty cell,
it assigns the required value; it also removes candidates incompatible with
the sums from the domains. Propagation continues until the domains stabilize
and rejects a branch if a domain becomes empty or a sum is impossible.

## Interactive runs

`Try algorithms` asks which algorithm to run: `1` backtracking with constraint
propagation, `2` simulated annealing, or `3` the genetic algorithm.
Invalid choices are requested again.
The size selection screen does not offer a Back option.
Subsequent screens show `b. Back` (after `3.` in the algorithm menu):
the algorithm menu and confirmation screen return to size selection.
After a result, `h. Home` returns to the main menu with interactive runs and tests.
`e. Exit` closes the program.
During a search, `Ctrl+C` interrupts the computation and returns to the algorithm menu.
Before the algorithm menu, the program asks for the side length, an integer greater than 2.
Side lengths greater than 10 require confirmation because the search may take a long time.
`Matrix` and `Matrix.empty` also require a side length greater than 2.
The genetic algorithm manages up to 100 attempts internally (`MAX_ATTEMPTS`),
stopping at the first solution. Interactive runs and benchmarks call the same function.
For the other algorithms, interactive runs use `ROUNDS` from `main.py` (default: 100).
The `Printer` class in `Entities/printer.py` groups static methods for printing
menus, solutions, execution times, and summaries.

## Error functions

In `Algorithms/functions.py`, `error_function_square` sums the squared
deviations from the magic sum for rows, columns, and both diagonals.
`error_function_absolute` sums the absolute values of the same deviations.
Both return zero when all sums match the magic sum.
Backtracking uses its own constraints; the selected error function also
determines the fitness reported for its result.

## Initial configuration

As the final option, interactive runs and tests 1 to 4 ask whether to fix any
values (`y`, `n`, `b. Back`). The grid numbers cells from 1 to n squared.
Enter `Index` and then `Value`; the cell displays `index:value`.
Entering `0` or `.` displays `index:0` and leaves the cell free for the search.
Press Enter at the Index prompt to finish the matrix.
The screen clears after each entry. Home, Back, and Exit remain available.
For size ranges, enter one configuration per side length; it is shared by all
algorithms and runs for that size.

The APIs `back_tracking(n, fixed_cells=None)`, `genetic(f, n, fixed_cells=None)`,
and `simulated_annealing(f, n, fixed_cells=None)` accept a dictionary
`{index: value}` with zero-based linear indices. Zero entries in the input grid
are omitted from the fixed-cell dictionary.
The runner accepts `fixed_cells`; the benchmark accepts `fixed_by_size={n: fixed_cells}`.

## Test 5: Absolute vs Square

This test asks only for the side length and runs every algorithm once with
absolute error, then once with squared error, saving both reports.
It does not ask for the number of runs or an initial configuration.
For sizes greater than 10, it asks for confirmation because execution may take
a long time, as with the other tests.
