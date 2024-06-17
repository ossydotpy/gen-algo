from pprint import pprint
from ga import GenerativeAlgorithm
from prettytable import PrettyTable
import random

random.seed(42)
if __name__ == '__main__':

    subjects = ['Math', 'Physics', 'Chemistry', 'History', 'Biology', 'Akan', 'Science', 'Social']
    time_slots = [
        'Mon 5-6 PM', 'Mon 6-7 PM',
        'Mon 7-8 PM', 'Mon 8-9 PM', 
        'Tue 7-8 PM', 'Tue 8-9 PM',
        'Wed 7-8 PM', 'Wed 8-9 PM',
        'Thu 7-8 PM', 'Thu 8-9 PM',

    ]

    prefs = {
        'Tue 7-8 PM': 'Math',
        'Thu 7-8 PM': 'Physics'
    }

    hparameters = { 'crossover_rate':.6,
                    'mutation_rate_1': .5,
                    'mutation_rate_2':.3
                }

    pop_size = len(time_slots)**2
    model = GenerativeAlgorithm(pop_size, 150000)
    model.compile(subjects, time_slots, preferences=prefs)
    results = model.train(hparameters)
    # pprint(results)
    # print(model.evaluate_fitness(results))
    table = PrettyTable()
    table.field_names = ['Period', 'Subject']

    for k, v in zip(results.keys(), results.values()):
        table.add_row([k, v])
    print(table)
    print(model.evaluate_fitness(results))
    # print(model.selection(model.generate_population()))

