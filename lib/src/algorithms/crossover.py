import random
from typing import List, Tuple
from lib.src.models.individual import Individual


class Crossover:
    @staticmethod
    def single_point_crossover(
        parent1: Individual, parent2: Individual, days: List[str]
    ) -> Tuple[Individual, Individual]:
        assert len(parent1.schedule) == len(parent2.schedule), "Invalid parents"
        crossover_point = random.randint(1, len(days) - 1)
        child1_schedule = {
            **dict(list(parent1.schedule.items())[:crossover_point]),
            **dict(list(parent2.schedule.items())[crossover_point:]),
        }
        child2_schedule = {
            **dict(list(parent2.schedule.items())[:crossover_point]),
            **dict(list(parent1.schedule.items())[crossover_point:]),
        }
        return Individual(child1_schedule), Individual(child2_schedule)
