from collections import Counter
import random
import numpy as np

class GenerativeAlgorithm:
    def __init__(self, population_size, num_generations):
        self.size = population_size
        self.subjects = None
        self.time_slots = None
        self.preferences = None
        self.num_generations = num_generations

    def compile(self, subjects, time_slots, preferences):
        assert len(time_slots) // len(subjects) >= 1, 'too few time slots'
        self.subjects = subjects
        self.time_slots = time_slots
        self.preferences = preferences

    def generate_population(self, size=10):
        population = []

        for _ in range(size):
            candidate = self.preferences.copy() if self.preferences else {}
            remaining_slots = set(self.time_slots) - set(candidate.keys())
            remaining_subjects = list(set(self.subjects) - set(candidate.values()))
            
            for slot in remaining_slots:
                if remaining_subjects:
                    candidate[slot] = random.choice(remaining_subjects)
                else:
                    candidate[slot] = None
            population.append(candidate)
        return population
    
    def boltzmann_selection(self, population, temperature):
        fitness_values = np.array([self.evaluate_fitness(ind) for ind in population])
        exp_values = np.exp(fitness_values / temperature)
        probabilities = exp_values / np.sum(exp_values)
        selected_indices = np.random.choice(len(population), size=len(population) // 2, p=probabilities)
        selected_population = [population[i] for i in selected_indices]
        return selected_population

    def crossover(self, parent1, parent2, cross_rate=0.5):
        child = {}
        for time in self.time_slots:
            if random.random() < cross_rate:
                child[time] = parent1[time]
            else:
                child[time] = parent2[time]
        return child

    def mutate(self, timetable, mutation_rate=0.4):
        for time in self.time_slots:
            if random.random() < mutation_rate:
                timetable[time] = random.choice(self.subjects)
        return timetable

    def evaluate_fitness(self, timetable):
        consecutive_penalty = 0
        preferred_time_score = 0
        unused_subjects_penalty = 0
        subject_counts = Counter(timetable.values())

        previous_subj = None
        for time in self.time_slots:
            current_subject = timetable.get(time)
            if timetable[time] == self.preferences.get(time):
                preferred_time_score += 1            
            if current_subject == previous_subj:
                consecutive_penalty += 1
            previous_subj = current_subject

        ideal_repetition = 1 if len(self.time_slots) // len(self.subjects) < 1 else len(self.time_slots) // len(self.subjects)
        balance_penalty = sum(abs(subject_counts[subject] - ideal_repetition) ** 2 for subject in self.subjects)
        unused_subjects_count = len(set(subj for subj in self.subjects if subj not in subject_counts.keys())) 

        if unused_subjects_count > 0 and balance_penalty > 0:
            unused_subjects_penalty += 1

        total_fitness = -consecutive_penalty - balance_penalty - unused_subjects_penalty + preferred_time_score

        return total_fitness

    @staticmethod
    def top_k(k, population, func):
        _fitness = sorted(population, key=lambda x: func(x))
        return _fitness[:k]

    
    def train(self, verbose=False, **kwargs):
        cross_rate = kwargs.get('cross_rate', 0.5)
        mutation_rate_1 = kwargs.get('mutation_rate_1', 0.5)
        mutation_rate_2 = kwargs.get('mutation_rate_2', 0.5)
        initial_temperature = kwargs.get('initial_temperature', 1.0)
        final_temperature = kwargs.get('final_temperature', 0.1)
        num_generations = self.num_generations

        population = self.generate_population(self.size)
        
        for generation in range(num_generations):
            temperature = initial_temperature * (final_temperature / initial_temperature) ** (generation / num_generations)
            selected_population = self.boltzmann_selection(population, temperature)
            new_population = []

            for i in range(len(selected_population) // 2):
                top_n = self.top_k(2, selected_population, self.evaluate_fitness)
                parent1 = selected_population[i]
                parent2 = selected_population[len(selected_population) - i - 1]

                child1 = self.crossover(parent1, parent2, cross_rate=cross_rate)
                child2 = self.crossover(parent2, parent1, cross_rate=cross_rate)

                new_population.extend(
                    [self.mutate(child1, mutation_rate=mutation_rate_1),
                     self.mutate(child2, mutation_rate=mutation_rate_2)]
                    )

            if new_population:
                selected_population = new_population
                selected_population.extend(top_n)
            else:
                break

            best_fit = max(new_population, key=lambda x: self.evaluate_fitness(x))
            current_best_fitness = self.evaluate_fitness(best_fit)

            if verbose:
                print(f'population size: {len(selected_population)}')
                print(f"Generation {generation + 1}: Best Fitness = {current_best_fitness}")

        return best_fit

