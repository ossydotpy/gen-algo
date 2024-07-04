from typing import Dict


class Individual:
    def __init__(self, timetable: Dict[str, Dict[str, str]]):
        self.timetable = timetable
        self.subjects = {
            subject
            for day in timetable.values()
            for subject in day.values()
            if subject != "Free"
        }

    def get_slot(self, day: str, time: str) -> str:
        return self.timetable.get(day).get(time)

    def set_slot(self, day: str, time: str, subject: str):
        self.timetable[day][time] = subject

    def calculate_diversity(self) -> float:
        "Checks the number of unique subjects in the timetable"
        flattened_timetable = [
            subject for day in self.timetable.values() for subject in day.values()
        ]
        unique_subjects = set(flattened_timetable)
        return len(unique_subjects) / len(flattened_timetable)

    def calculate_diversity_between(self, other: "Individual") -> float:
        timetable1 = [
            subject for day in self.timetable.values() for subject in day.values()
        ]
        timetable2 = [
            subject for day in other.timetable.values() for subject in day.values()
        ]
        return sum(1 for a, b in zip(timetable1, timetable2) if a != b) / len(
            timetable1
        )
