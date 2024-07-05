import random
from typing import List
from lib.src.models.individual import Individual


class Selection:
    @staticmethod
    def tournament_selection(
        population: List[Individual],
        fitness_func,
        tournament_size: int,
        diversity_weight: float,
    ) -> Individual:
        """Select an individual from the population using tournament selection. If diversity_weight is 0, then it is equivalent to fitness-based selection.
        Args: population (List[Individual]): The population.
              fitness_func (function): The function to calculate the fitness of an individual. Must return a float.
              tournament_size (int): The size of the tournament. Must be >= 2. Defaults to 2.
              diversity_weight (float): The weight of diversity in the selection process. Must be >= 0. Defaults to 0.1.
        """
        assert tournament_size >= 2, "Tournament size must be >= 2"
        tournament = random.sample(population, tournament_size)
        return max(
            tournament,
            key=lambda ind: fitness_func(ind)
            + diversity_weight * ind.calculate_diversity(),
        )
