from Entities.matrix import Matrix


class GeneticMatrix(Matrix):
    def __init__(self, n: int, array: list[int] | None = None, fitnessValue: int = 0):
        super().__init__(n, array)
        self.fitnessValue = fitnessValue


# Alias per compatibilità con eventuale naming precedente
genetic_matrix = GeneticMatrix

