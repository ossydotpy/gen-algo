from typing import Dict


class Individual:
    def __init__(self, schedule: Dict[str, Dict[str, str]]):
        self.schedule = schedule
        self.subjects = {
            subject
            for day in schedule.values()
            for subject in day.values()
            if subject != "Free"
        }

    def get_slot(self, day: str, time: str) -> str:
        return self.schedule.get(day).get(time)

    def set_slot(self, day: str, time: str, subject: str):
        self.schedule[day][time] = subject

    def calculate_diversity(self) -> float:
        "Checks the number of unique subjects in the schedule"
        flattened_schedule = [
            subject for day in self.schedule.values() for subject in day.values()
        ]
        unique_subjects = set(flattened_schedule)
        return len(unique_subjects) / len(flattened_schedule)

    def calculate_diversity_between(self, other: "Individual") -> float:
        schedule1 = [
            subject for day in self.schedule.values() for subject in day.values()
        ]
        schedule2 = [
            subject for day in other.schedule.values() for subject in day.values()
        ]
        return sum(1 for a, b in zip(schedule1, schedule2) if a != b) / len(
            schedule1
        )
