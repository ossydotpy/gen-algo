# Example usage:
from pprint import pprint
from lib.src.algorithms.generative_algorithm import (
    PopulationInitializer,
    TimetableGenerator,
)
from config import CONFIG

subjects = [
    "Math",
    "Science",
    "English",
    "History",
    "Geography",
    "Chemistry",
    "Biology",
]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
time_slots = ["15:00", "17:00", "18:00", "20:00", "21:00"]
preferences = {
    "Math": {
        "Monday": "15:00",
        "Tuesday": None,
        "Wednesday": "17:00",
        "Thursday": None,
        "Friday": None,
    },
    "Science": {
        "Monday": None,
        "Tuesday": "15:00",
        "Wednesday": None,
        "Thursday": "17:00",
        "Friday": None,
    },
    "History": {
        "Monday": None,
        "Tuesday": None,
        "Wednesday": None,
        "Thursday": "18:00",
        "Friday": None,
    },
    "English": {
        "Monday": None,
        "Tuesday": None,
        "Wednesday": None,
        "Thursday": None,
        "Friday": None,
    },
    "Chemistry": {
        "Monday": None,
        "Tuesday": None,
        "Wednesday": None,
        "Thursday": None,
        "Friday": None,
    },
    "Geography": {
        "Monday": None,
        "Tuesday": None,
        "Wednesday": None,
        "Thursday": "15:00",
        "Friday": None,
    },
}

ga = TimetableGenerator(
    subjects=subjects,
    days=days,
    time_slots=time_slots,
    preferences=preferences,
    config=CONFIG,
)
best_timetable = ga.evolve(verbose=True)
print("Best Timetable:")
for day, schedule in best_timetable.timetable.items():
    print(f"{day}: {schedule}")
print("diversity: ", best_timetable.calculate_diversity())