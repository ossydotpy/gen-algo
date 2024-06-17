# from collections import defaultdict, Counter
# import random
# from pprint import pprint
# # random.seed(1)

# subjects = ['Math', 'Physics', 'Chemistry', 'History', 'Biology', 'Akan', 'Science', 'RME']
# time_slots = [
#     'Mon 7-8 PM', 'Mon 8-9 PM', 
#     'Tue 7-8 PM', 'Tue 8-9 PM',
#     'Wed 7-8 PM', 'Wed 8-9 PM', 
#     'Thu 8-9 PM'
# ]

# prefs = {
#     'Tue 7-8 PM': 'Math',
#     'Thu 8-9 PM': 'Physics'
# }


# def generate_population(size):
#     population = []

#     for _ in range(size):
#         candidate = prefs.copy() if prefs else {}
#         remaining_slots = set(time_slots) - set(candidate.keys())
#         remaining_subjects = list(set(subjects) - set(candidate.values()))
        
#         for slot in remaining_slots:
#                 if remaining_subjects:
#                     candidate[slot] = random.choice(remaining_subjects)
#                 else:
#                     candidate[slot] = None
#         population.append(candidate)

#     return population


# def evaluate_fitness(timetable, print=False):
#     consective_penalty = 0
#     prefered_time_score = 0
#     unused_subjects_penalty = 0
#     counts = Counter(timetable.values())

#     previous_subj = None
#     for time in time_slots:
#         current_subject = timetable[time]
        
#         if timetable[time] == prefs.get(time):
#             prefered_time_score+=1            
        
#         if current_subject == previous_subj:
#             consective_penalty+=1
        
#         previous_subj = current_subject

#     ideal_repitition = 1 if len(time_slots)//len(subjects)<1 else len(time_slots)//len(subjects)
#     balance_penalty =  sum(abs(counts[subject]-ideal_repitition**2) for subject in subjects)

#     unused_subjects_count = len(set(subj for subj in subjects if subj not in counts.keys())) 
#     if unused_subjects_count > 0 and balance_penalty>0:
#         unused_subjects_penalty +=1


#     total_fitness = -consective_penalty - balance_penalty - unused_subjects_penalty + prefered_time_score

#     return total_fitness


# def selection(population):
#     population = sorted(population, key=lambda x: evaluate_fitness(x), reverse=True)
#     return population[:max(2, len(population)//2)]


# def crossover(parent1, parent2, cross_rate=0.5):
#     child = prefs.copy() if prefs else {}
#     for time in time_slots:
#         if random.random() < cross_rate:
#             child[time] = parent1[time]
#         child[time] = parent2[time]
#     return child


# def mutate(timetable, mutation_rate=0.4):
#     for time in time_slots:
#         if random.random() < mutation_rate:
#             timetable[time] = random.choice(subjects)
#     return timetable



# class GenerativeAlgorithm:
#     def __init__(self, population_size, num_generations) -> None:
#         self.size = population_size
#         self.num_generations = num_generations

#     def train(self):
#         population = generate_population(self.size)
        
#         for i in range(self.num_generations):
#             selected_population = selection(population=population)
#             new_population = []
            
#             for i in range(len(selected_population)//2):
#                 parent1 = selected_population[i]
#                 parent2 = selected_population[len(selected_population)-i-1]

#                 child1 = crossover(parent1, parent2, cross_rate=0.6)
#                 child2 = crossover(parent2, parent1)

#                 new_population.extend([mutate(child1, mutation_rate=.5),mutate(child2, mutation_rate=.5)])
        
#             if new_population:
#                 population = new_population
#             else:
#                 break
#         if population:
#             best_fit = max(population, key=lambda x: evaluate_fitness(x))
#             return best_fit
#         else:
#             return None
        


# # test lines 
# model = GenerativeAlgorithm(10, 50000)
# results = model.train()
# # print(len(time_slots), len(subjects))
# # print('ideal repititions = {}'.format(len(time_slots)//len(subjects)))
# # pop = generate_population(50)
# # for x in pop:
# #     pprint(x)
# #     pprint(evaluate_fitness(x))

# pprint(results)
# pprint(evaluate_fitness(results))
