import random
from typing import List

from lib.src.models.individual import Individual


class Mutation:
    @staticmethod
    def adaptive_mutation_rate(
        generation, max_generations, initial_mutation_rate=0.4, final_rate=0.01
    ):
        """Calculate the adaptive mutation rate for the given generation.
        A higher mutation rate is used in the beginning and it decreases as the generation increases.
        """
        return initial_mutation_rate - (initial_mutation_rate - final_rate) * (
            generation / max_generations
        )

    @staticmethod
    def random_mutation(
        individual: Individual, subjects: List[str], mutation_rate: float
    ):
        """Mutate the individual by randomly changing the subject of a slot."""
        for day in individual.timetable:
            for time in individual.timetable[day]:
                if random.random() < mutation_rate:
                    individual.set_slot(day, time, random.choice(subjects + ["Free"]))
