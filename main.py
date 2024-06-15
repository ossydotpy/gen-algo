from collections import defaultdict
import random

random.seed(42)

subjects = ['Math', 'Physics', 'Chemistry', 'History', 'Biology', 'Akan', 'Science','RME']
time_slots = ['Mon 4-5 PM', 'Mon 5-6 PM','Mon 6-7 PM', 'Tue 4-5 PM', 'Tue 5-6 PM', 
              'Wed 4-5 PM', 'Wed 5-6 PM', 'Thu 4-5 PM', 'Thu 5-6 PM', 
              'Fri 4-5 PM', 'Fri 5-6 PM']
prefs = {
    'Tue 4-5 PM': 'Math',
    'Thu 5-6 PM': 'Physics',
    'Fri 5-6 PM': 'Chemistry'
}

def generate_population(size, print=False):
    population = []
    for _ in range(size):
        new_pop = {time: random.choice(subjects) for time in time_slots}
        population.append(new_pop)
    return population

def fitness(timetable, print=False):
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
            prefered_time_score+=1
        previous_subj = current_subject

    ideal_repitition = len(time_slots)//len(subjects)
    balance_penalty =  sum(abs(subject_counts[subject]-ideal_repitition) for subject in subjects)

    total_fitness = -consective_penalty - balance_penalty + prefered_time_score

    return total_fitness

a = generate_population(size=10)
for r in a:
    print(fitness(r))


