import random
from typing import Dict, List, Tuple
from lib.src.models.individual import Individual
from lib.src.algorithms.penalties import Penalties
from lib.src.utils.validators import TimetableValidator


class GenerativeAlgorithm:
    def __init__(
        self,
        population_size: int,
        num_generations: int,
        subjects: List[str],
        days: List[str],
        time_slots: List[str],
        preferences: Dict,
    ):
        self.population_size = population_size
        self.num_generations = num_generations
        self.subjects = subjects
        self.days = days
        self.time_slots = time_slots
        self.preferences = preferences
        self.penalties = Penalties()
        self.preference_adherent_percentage = 0.0

    def generate_preference_adherent_individual(self) -> Individual:
        timetable = {day: {} for day in self.days}
        for day in self.days:
            for time in self.time_slots:
                preferred_subject = next(
                    (
                        subject
                        for subject, pref in self.preferences.items()
                        if pref.get(day) == time
                    ),
                    None,
                )
                if preferred_subject:
                    timetable[day][time] = preferred_subject
                else:
                    timetable[day][time] = random.choice(self.subjects + ["Free"])
        return Individual(timetable)

    def generate_individual(self) -> Individual:
        timetable = {day: {} for day in self.days}
        subjects_copy = self.subjects.copy()
        total_slots = len(self.days) * len(self.time_slots)

        for day in self.days:
            for time in self.time_slots:
                if subjects_copy and len(subjects_copy) / total_slots > random.random():
                    subject = random.choice(subjects_copy)
                    subjects_copy.remove(subject)
                    timetable[day][time] = subject
                else:
                    timetable[day][time] = "Free"

        for subject in self.subjects:
            if subject not in [
                slot for day in timetable.values() for slot in day.values()
            ]:
                day, time = random.choice(
                    [
                        (d, t)
                        for d in self.days
                        for t in self.time_slots
                        if timetable[d][t] == "Free"
                    ]
                )
                timetable[day][time] = subject

        return Individual(timetable)

    def initialize_population(self) -> List[Individual]:
        preference_adherent_count = int(
            self.population_size * self.preference_adherent_percentage
        )
        random_count = self.population_size - preference_adherent_count

        preference_adherent_individuals = [
            self.generate_preference_adherent_individual()
            for _ in range(preference_adherent_count)
        ]
        random_individuals = [self.generate_individual() for _ in range(random_count)]

        return preference_adherent_individuals + random_individuals

    def adjust_preference_adherent_percentage(self, generation: int):
        self.preference_adherent_percentage = max(
            0.1, 0.3 - (generation / self.num_generations) * 0.2
        )

    def fitness(self, individual: Individual) -> float:
        if not TimetableValidator.is_valid(individual, self.subjects, self.time_slots):
            return float("-inf")
        penalty = self.penalties.calculate_total_penalty(
            individual, self.preferences, self.subjects, self.time_slots
        )
        return 1000 - penalty

    def select_parent(self, population: List[Individual]) -> Individual:
        tournament_size = 3
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=self.fitness)

    def crossover(
        self, parent1: Individual, parent2: Individual
    ) -> Tuple[Individual, Individual]:
        crossover_point = random.randint(1, len(self.days) - 1)
        child1_timetable = {
            **dict(list(parent1.timetable.items())[:crossover_point]),
            **dict(list(parent2.timetable.items())[crossover_point:]),
        }
        child2_timetable = {
            **dict(list(parent2.timetable.items())[:crossover_point]),
            **dict(list(parent1.timetable.items())[crossover_point:]),
        }
        return Individual(child1_timetable), Individual(child2_timetable)

    def mutate(self, individual: Individual, mutation_rate: float):
        for day in individual.timetable:
            for time in individual.timetable[day]:
                if random.random() < mutation_rate:
                    individual.timetable[day][time] = random.choice(
                        self.subjects + ["Free"]
                    )

    def evolve(self, verbose=False):
        population = self.initialize_population()
        elite_size = int(0.2 * self.population_size)

        for generation in range(self.num_generations):
            new_population = []
            for _ in range(self.population_size // 2):
                parent1 = self.select_parent(population)
                parent2 = self.select_parent(population)
                child1, child2 = self.crossover(parent1, parent2)
                self.mutate(child1, mutation_rate=0.4)
                self.mutate(child2, mutation_rate=0.4)
                new_population.extend([child1, child2])

            elite_individuals = sorted(population, key=self.fitness, reverse=True)[
                :elite_size
            ]

            new_population.extend(elite_individuals + new_population)
            new_population = new_population[
                : self.population_size
            ]

            population = new_population
            best_individual = max(population, key=self.fitness)
            best_fitness = self.fitness(best_individual)

            self.adjust_preference_adherent_percentage(generation)

            if verbose and generation % 10 == 0:
                print(f"Generation {generation}: Best Fitness = {best_fitness}")

        return max(population, key=self.fitness)
