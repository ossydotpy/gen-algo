from typing import List

from lib.src.models.individual import Individual


class TimetableValidator:
    @staticmethod
    def is_valid(
        individual: Individual, subjects: List[str], time_slots: List[str]
    ) -> bool:
        for day in individual.timetable.values():
            if set(day.keys()) != set(time_slots):
                return False
            if not all(
                subject in subjects or subject == "Free" for subject in day.values()
            ):
                return False
        return True
