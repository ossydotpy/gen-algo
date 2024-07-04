import random
from typing import Dict, List, Tuple

from lib.src.algorithms.rewards import Rewards
from lib.src.models.individual import Individual
from lib.src.algorithms.penalties import Penalties
from lib.src.utils.validators import TimetableValidator


class PopulationInitializer:
    def __init__(
        self,
        subjects: List[str],
        days: List[str],
        time_slots: List[str],
        preferences: Dict,
    ):
        self.subjects = subjects
        self.days = days
        self.time_slots = time_slots
        self.preferences = preferences

    def generate_individual(self, consider_preferences: bool = False) -> Individual:
        """Generate a random individual.
        If consider_preferences is True, the algorithm will try to assign the preferred subject to the preferred time slot.

        Args:
            consider_preferences (bool): Whether to consider preferences or not. Defaults to False.
        """
        timetable = {
            day: {time: "Free" for time in self.time_slots} for day in self.days
        }
        subjects_needed = self.subjects * (
            len(self.days) * len(self.time_slots) // len(self.subjects)
        )
        random.shuffle(subjects_needed)

        # Assign preferences first if required
        if consider_preferences:
            for subject, pref in self.preferences.items():
                for day, time in pref.items():
                    if time is not None and timetable[day][time] == "Free":
                        timetable[day][time] = subject
                        if subject in subjects_needed:
                            subjects_needed.remove(subject)

        # Fill remaining slots
        for day in self.days:
            for time in self.time_slots:
                if timetable[day][time] == "Free" and subjects_needed:
                    timetable[day][time] = subjects_needed.pop()

        return Individual(timetable)

    def initialize_population(
        self, population_size: int, preference_adherent_percentage: float
    ) -> List[Individual]:
        preference_adherent_count = int(
            population_size * preference_adherent_percentage
        )
        random_count = population_size - preference_adherent_count

        preference_adherent_individuals = [
            self.generate_individual(consider_preferences=True)
            for _ in range(preference_adherent_count)
        ]
        random_individuals = [
            self.generate_individual(consider_preferences=False)
            for _ in range(random_count)
        ]

        return preference_adherent_individuals + random_individuals


class FitnessEvaluator:
    """Calculate the fitness of an individual.
    Args: subjects (List[str]): The list of subjects.
          time_slots (List[str]): The list of time slots.
          preferences (Dict): The preferences of the students.
    """

    def __init__(self, subjects: List[str], time_slots: List[str], preferences: Dict):
        self.subjects = subjects
        self.time_slots = time_slots
        self.preferences = preferences
        self.penalties = Penalties()
        self.rewards = Rewards()

    def calculate_fitness(self, individual: Individual) -> float:
        if not TimetableValidator.is_valid(individual, self.subjects, self.time_slots):
            return float("-inf")
        penalty = self.penalties.calculate_total_penalty(
            individual, self.preferences, self.subjects, self.time_slots
        )
        reward = self.rewards.calculate_total_reward(individual, self.preferences)
        return 1000 - penalty + reward


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


class Crossover:
    @staticmethod
    def single_point_crossover(
        parent1: Individual, parent2: Individual, days: List[str]
    ) -> Tuple[Individual, Individual]:
        assert len(parent1.timetable) == len(parent2.timetable), "Invalid parents"
        crossover_point = random.randint(1, len(days) - 1)
        child1_timetable = {
            **dict(list(parent1.timetable.items())[:crossover_point]),
            **dict(list(parent2.timetable.items())[crossover_point:]),
        }
        child2_timetable = {
            **dict(list(parent2.timetable.items())[:crossover_point]),
            **dict(list(parent1.timetable.items())[crossover_point:]),
        }
        return Individual(child1_timetable), Individual(child2_timetable)


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


class TimetableGenerator:
    def __init__(
        self,
        config: Dict,
        subjects: List[str],
        days: List[str],
        time_slots: List[str],
        preferences: Dict,
    ):
        self.config = config
        self.subjects = subjects
        self.days = days
        self.time_slots = time_slots
        self.preferences = preferences

        self.population_initializer = PopulationInitializer(
            subjects, days, time_slots, preferences
        )
        self.fitness_evaluator = FitnessEvaluator(subjects, time_slots, preferences)

    def elitism_with_diversity(
        self, population: List[Individual], elite_size: int
    ) -> List[Individual]:
        """Select the elite individuals from the population based on fitness and diversity.
        Args: population (List[Individual]): The population.
              elite_size (int): The number of elite individuals to select."""

        sorted_population = sorted(
            population, key=self.fitness_evaluator.calculate_fitness, reverse=True
        )

        elite = []
        for individual in sorted_population:
            if len(elite) == 0 or all(
                individual.calculate_diversity_between(e)
                > self.config["diversity_threshold"]
                for e in elite
            ):
                elite.append(individual)
            if len(elite) == elite_size:
                break

        if len(elite) < elite_size:
            elite.extend(sorted_population[len(elite) : elite_size])

        return elite

    def evolve(self, verbose=False):
        """Evolve the timetable for the given number of generations
        Args: verbose (bool): Whether to print progress
        Returns: Individual: The best individual
        """
        population_size = self.config["population_size"]
        num_generations = self.config["num_generations"]
        elite_size = int(self.config["elite_percentage"] * population_size)

        population = self.population_initializer.initialize_population(
            population_size,
            self.config.get("initial_preference_adherent_percentage", 0.2),
        )

        for generation in range(num_generations):
            new_population = []

            # Add the elite individuals to the new population
            elite = self.elitism_with_diversity(population, elite_size)
            new_population.extend(elite)

            # Generate offspring
            while len(new_population) < population_size:
                parent1 = Selection.tournament_selection(
                    population,
                    self.fitness_evaluator.calculate_fitness,
                    self.config.get("tournament_size", 2),
                    self.config.get("diversity_weight", 0.1),
                )
                parent2 = Selection.tournament_selection(
                    population,
                    self.fitness_evaluator.calculate_fitness,
                    self.config.get("tournament_size", 2),
                    self.config.get("diversity_weight", 0.1),
                )
                child1, child2 = Crossover.single_point_crossover(
                    parent1, parent2, self.days
                )

                mutation_rate = Mutation.adaptive_mutation_rate(
                    self.config["initial_mutation_rate"],
                    self.config["num_generations"],
                    self.config["final_mutation_rate"],
                )

                Mutation.random_mutation(child1, self.subjects, mutation_rate)
                Mutation.random_mutation(child2, self.subjects, mutation_rate)

                new_population.extend([child1, child2])

            # Truncate to population size
            population = new_population[:population_size]

            if verbose and generation % 10 == 0:
                best_individual = max(
                    population, key=self.fitness_evaluator.calculate_fitness
                )
                best_fitness = self.fitness_evaluator.calculate_fitness(best_individual)
                avg_diversity = sum(
                    ind.calculate_diversity() for ind in population
                ) / len(population)
                print(
                    f"Generation {generation}: Best Fitness = {best_fitness}, Avg Diversity = {avg_diversity:.2f}"
                )

        return max(population, key=self.fitness_evaluator.calculate_fitness)
