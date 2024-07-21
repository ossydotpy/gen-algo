from datetime import datetime
import json
from math import inf
import random
from typing import Dict, List, Optional, Tuple, Union

from lib.src.algorithms.crossover import Crossover
from lib.src.algorithms.fitness import FitnessEvaluator
from lib.src.algorithms.mutatation import Mutation
from lib.src.algorithms.population import PopulationInitializer
from lib.src.algorithms.selection import Selection

from lib.src.models.individual import Individual
from lib.src.utils.helpers import create_directory_if_not_exists

class TimetableGenerator:
    def __init__(
        self,
        config: Dict,
        subjects: List[str],
        days: List[str],
        time_slots: List[str],
        preferences: Optional[Dict] = None,
        save_interval: Optional[int] = None,
        save_at_step: Optional[Union[int, List[int]]] = None,
    ):
        self.config = config
        self.subjects = subjects
        self.days = days
        self.time_slots = time_slots
        self.preferences = preferences
        self.save_interval = save_interval
        self.save_at_step = save_at_step

        self.population_initializer = PopulationInitializer(
            subjects, days, time_slots, preferences
        )
        self.fitness_evaluator = FitnessEvaluator(subjects, time_slots, preferences)

        self.current_generation = 0
        self.population = []

    def checkpoint(self, file_name: str):
        """Save the state of the schedule generator to a file."""
        CHECKPOINT_DIR = "checkpoints"
        create_directory_if_not_exists(CHECKPOINT_DIR)
        state = {
            "current_generation": self.current_generation,
            "config": self.config,
            "subjects": self.subjects,
            "days": self.days,
            "time_slots": self.time_slots,
            "preferences": self.preferences,
            "best_individual": max(
                self.population, key=self.fitness_evaluator.calculate_fitness
            ).schedule,
            "population": [ind.schedule for ind in self.population],
        }
        time_now = datetime.now().strftime("%y%m%d_%H%M%S")
        file_name = f"{CHECKPOINT_DIR}/{time_now}{file_name}"
        with open(file_name, "w") as f:
            json.dump(state, f, indent=4)

    def load_state(self, file_name: str):
        """Load the state of the schedule generator from a file."""
        with open(file_name, "r") as f:
            state = json.load(f)
        self.config = state["config"]
        self.subjects = state["subjects"]
        self.days = state["days"]
        self.time_slots = state["time_slots"]
        self.preferences = state["preferences"]
        self.population = state["population"]
        self.current_generation = state["current_generation"]
        self.population_initializer = PopulationInitializer(
            self.subjects, self.days, self.time_slots, self.preferences
        )
        self.fitness_evaluator = FitnessEvaluator(
            self.subjects, self.time_slots, self.preferences
        )

    def initialize_from_partial_state(self, partial_state: Dict[str, Dict[str, str]]):
        """Initialize the population from a partial state."""
        self.population = []
        for _ in range(self.config["population_size"]):
            individual = self.complete_partial_state(partial_state)
            self.population.append(individual)

    def complete_partial_solution(
        self, partial_solution: Dict[str, Dict[str, str]]
    ) -> Individual:
        """Complete a partial solution randomly."""
        complete_solution = {day: {} for day in self.days}
        remaining_subjects = self.subjects.copy()

        for day in self.days:
            for time in self.time_slots:
                if day in partial_solution and time in partial_solution[day]:
                    subject = partial_solution[day][time]
                    complete_solution[day][time] = subject
                    if subject in remaining_subjects:
                        remaining_subjects.remove(subject)
                else:
                    if remaining_subjects:
                        subject = random.choice(remaining_subjects)
                        remaining_subjects.remove(subject)
                    else:
                        subject = "Free"
                    complete_solution[day][time] = subject

        return Individual(complete_solution)

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

    def evolve(
    self,
    initial_solution: Optional[Individual] = None,
    start_generation: int = 0,
    max_generations=None,
    verbose=False,
    save_best=False
    ):
        """Evolve the schedule for the given number of generations or continue from the current state."""
        population_size = self.config["population_size"]
        num_generations = max_generations or self.config["num_generations"]
        elite_size = int(self.config["elite_percentage"] * population_size)

        if initial_solution:
            self.population = (
                self.population_initializer.initialize_population_with_seed(
                    population_size, initial_solution
                )
            )
        else:
            self.population = self.population_initializer.initialize_population(
                population_size,
                self.config.get("initial_preference_adherent_percentage", 0.2),
            )

        self.current_generation = start_generation
        highest_fitness = -inf

        for generation in range(self.current_generation, num_generations):
            self.current_generation = generation
            new_population = []

            # Add the elite individuals to the new population
            elite = self.elitism_with_diversity(self.population, elite_size)
            new_population.extend(elite)

            # Generate offspring
            while len(new_population) < population_size:
                parent1 = Selection.tournament_selection(
                    self.population,
                    self.fitness_evaluator.calculate_fitness,
                    self.config.get("tournament_size", 2),
                    self.config.get("diversity_weight", 0.1),
                )
                parent2 = Selection.tournament_selection(
                    self.population,
                    self.fitness_evaluator.calculate_fitness,
                    self.config.get("tournament_size", 2),
                    self.config.get("diversity_weight", 0.1),
                )
                child1, child2 = Crossover.single_point_crossover(
                    parent1, parent2, self.days
                )

                mutation_rate = Mutation.adaptive_mutation_rate(
                    generation,
                    num_generations,
                    self.config["initial_mutation_rate"],
                    self.config["final_mutation_rate"],
                )

                Mutation.random_mutation(child1, self.subjects, mutation_rate)
                Mutation.random_mutation(child2, self.subjects, mutation_rate)

                new_population.extend([child1, child2])

            # Truncate to population size
            self.population = new_population[:population_size]
            best_individual = max(self.population, key=self.fitness_evaluator.calculate_fitness)
            best_fitness = self.fitness_evaluator.calculate_fitness(best_individual)

            if verbose and generation % 10 == 0:
                
                avg_diversity = sum(
                    ind.calculate_diversity() for ind in self.population
                ) / len(self.population)
                print(
                    f"Generation {generation}: Best Fitness = {best_fitness}, Avg Diversity = {avg_diversity:.2f}"
                )

            if self.save_interval and generation % self.save_interval == 0:
                self.checkpoint(f"generation_{generation}.json")
            if self.save_at_step:
                if isinstance(self.save_at_step, int):
                    if generation == self.save_at_step:
                        self.checkpoint(f"generation_{generation}.json")
                else:
                    if generation in self.save_at_step:
                        self.checkpoint(f"generation_{generation}.json")

            if save_best and best_fitness > highest_fitness:
                if generation != 0:
                    highest_fitness = best_fitness
                    self.checkpoint(f"autocheckpointgen{generation}_{highest_fitness}.json")

        return best_individual
