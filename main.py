from collections import defaultdict
import random
from pprint import pprint
random.seed(42)

subjects = ['Math', 'Physics', 'Chemistry', 'History', 'Biology', 'Akan', 'Science', 'RME']
time_slots = [
    'Mon 7-8 PM', 'Mon 8-9 PM', 
    'Tue 7-8 PM', 'Tue 8-9 PM',
    'Wed 7-8 PM', 'Wed 8-9 PM', 
    'Thu 8-9 PM'
]

prefs = {
    'Tue 7-8 PM': 'Math',
    'Thu 8-9 PM': 'Physics'
}


def generate_population(size, print=False):
    population = []
    for _ in range(size):
        new_pop = {time: random.choice(subjects) for time in time_slots}
        population.append(new_pop)
    return population

def evaluate_fitness(timetable, print=False):
    subject_counts = defaultdict(int)
    consective_penalty = 0
    prefered_time_score = 0
    
    previous_subj = None
    for time in time_slots:
        current_subject = timetable[time]
        subject_counts[current_subject]+=1
        if current_subject == previous_subj:
            consective_penalty+=1
        if prefs.get(time) == current_subject:
            prefered_time_score+=10
        previous_subj = current_subject

    ideal_repitition = len(time_slots)//len(subjects)
    balance_penalty =  sum(abs(subject_counts[subject]-ideal_repitition) for subject in subjects)

    total_fitness = -consective_penalty - balance_penalty + prefered_time_score

    return total_fitness


def selection(population):
    population = sorted(population, key=lambda x: evaluate_fitness(x), reverse=True)
    return population[:max(2, len(population)//2)]


def crossover(parent1, parent2, cross_rate=0.5):
    child = {}

    for time in time_slots:
        if random.random() < cross_rate:
            child[time] = parent1[time]
        child[time] = parent2[time]
    return child


def mutate(timetable, mutation_rate=0.4):
    for time in time_slots:
        if random.random() < mutation_rate:
            timetable[time] = random.choice(subjects)
    return timetable



class GenerativeAlgorithm:
    def __init__(self, population_size, num_generations) -> None:
        self.size = population_size
        self.num_generations = num_generations

    def train(self):
        population = generate_population(self.size)
        
        for i in range(self.num_generations):
            selected_population = selection(population=population)
            new_population = []
            
            for i in range(len(selected_population)//2):
                parent1 = selected_population[i]
                parent2 = selected_population[len(selected_population)-i-1]

                child1 = crossover(parent1, parent2, cross_rate=0.6)
                child2 = crossover(parent2, parent1)

                new_population.extend([mutate(child1, mutation_rate=.5),mutate(child2, mutation_rate=.5)])
        
            if new_population:
                population = new_population
            else:
                break
        if population:
            best_fit = max(new_population, key=lambda x: evaluate_fitness(x))
            return best_fit
        else:
            return None
        


# test lines 
model = GenerativeAlgorithm(10, 50000)
results = model.train()
pprint(results)

