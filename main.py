from Algorithms.genetic import genetic
import random

from Algorithms.functions import check_constraints, objective_function
from Algorithms.simulatedAnnealing import simulated_annealing
from Entities.cell import Cell
from Entities.matrix import Matrix

N = 4

def main() -> None:
    matrice = Matrix(N)
    generati = [0] * (N * N)

    for key in range(N * N):
        indice = random.randrange(N * N)
        while generati[indice] == 1:
            indice = random.randrange(N * N)

        generati[indice] = 1
        numero = indice + 1
        matrice[Cell(key, numero)] = numero

    matrice.stampa()

    if check_constraints(matrice.array):
        #matrice = genetic(objective_function, matrice)
        matrice = simulated_annealing(objective_function, matrice)

    matrice.stampa()

    for i in range(N):
        print(f"Somma riga {i + 1}: {matrice.somma_riga(i)}")

    for j in range(N):
        print(f"Somma colonna {j + 1}: {matrice.somma_colonna(j)}")

    print(f"Somma diagonale principale: {matrice.somma_diagonale_principale()}")
    print(f"Somma diagonale secondaria: {matrice.somma_diagonale_secondaria()}")


if __name__ == "__main__":
    main()
