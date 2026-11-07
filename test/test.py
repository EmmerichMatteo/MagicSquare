"""Esegue due tentativi di simulated annealing per ciascun lato da 4 a 8."""

import argparse
from datetime import datetime
import os
from pathlib import Path
import random
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Algorithms.functions import check_constraints, objective_function
from Algorithms.simulatedAnnealing import simulated_annealing
from Entities.matrix import Matrix

def format_time(seconds):
    ticks = round(seconds * 10000)
    hours, ticks = divmod(ticks, 3600 * 10000)
    minutes, ticks = divmod(ticks, 60 * 10000)
    secs, fraction = divmod(ticks, 10000)
    return f'{hours:02d}:{minutes:02d}:{secs:02d}.{fraction:04d}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--sizes', type=int, nargs='+', default=[4, 5, 6, 7, 8])
    parser.add_argument('--rounds', type=int, default=2)
    parser.add_argument('--output', type=Path, help='Percorso del report di testo')
    args = parser.parse_args()
    if any(n < 3 for n in args.sizes):
        parser.error('I lati devono essere almeno 3')
    if args.rounds < 1:
        parser.error('--rounds deve essere positivo')

    output = args.output or (
        Path(__file__).resolve().parent / 'results'
        / f'simulated-{datetime.now():%Y%m%d-%H%M%S-%f}.txt'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f'Report: {output.resolve()}', flush=True)
    results = []
    with output.open('x', encoding='utf-8') as report:
        def emit(message):
            print(message, flush=True)
            print(message, file=report, flush=True)

        def save_report():
            report.flush()
            os.fsync(report.fileno())

        emit('Algoritmo: simulated annealing | limite: 1800 secondi per tentativo')
        for n in args.sizes:
            for attempt in range(1, args.rounds + 1):
                save_report()
                seed = args.seed + attempt - 1
                random.seed(seed)
                values = random.sample(range(1, n * n + 1), n * n)
                initial = Matrix(n, values)
                initial_temperature = 0.38 * initial.n**2.5 * (initial.n**2 - 3)
                emit(f'\nAvvio {n}x{n} | tentativo {attempt}/{args.rounds} | '
                     f'seed {seed} | temperatura {initial_temperature:.2f} | '
                     f'fitness iniziale {objective_function(values)}')
                start = time.monotonic()
                result = simulated_annealing(
                    objective_function, initial, initial_temperature=initial_temperature
                )
                seconds = time.monotonic() - start
                score = objective_function(result.array)
                valid = check_constraints(result.array)
                solved = valid and score == 0
                results.append((n, attempt, solved, valid, score, seconds))
                emit(f'Esito: {"RISOLTO" if solved else "NON RISOLTO"} | '
                     f'vincoli validi: {valid} | fitness {score} | tempo {format_time(seconds)}')
                emit('Matrice risultato:')
                width = len(str(n * n))
                for row in range(n):
                    emit(' '.join(f'{v:>{width}}' for v in
                                  result.array[row * n:(row + 1) * n]))
                save_report()

        emit('\nLato | Tentativo | Risolto | Vincoli validi | Fitness | Tempo (HH:MM:SS.ssss)')
        for n, attempt, solved, valid, score, seconds in results:
            emit(f'{n}x{n} | {attempt} | {solved} | {valid} | {score} | {format_time(seconds)}')
        save_report()


if __name__ == '__main__':
    main()
