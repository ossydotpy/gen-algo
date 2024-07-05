from typing import Dict, List

from lib.src.models.individual import Individual
from lib.src.models.penalties.penalty import Penalties, BasePenalty


class PreferencePenalty(BasePenalty):
    """Penalty for not satisfying preferences"""
    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        penalty = 0
        preference_met = {subject: False for subject in preferences}

        for day, schedule in individual.timetable.items():
            for time, subject in schedule.items():
                if subject in preferences and preferences[subject].get(day) is not None:
                    if preferences[subject][day] == time:
                        preference_met[subject] = True

        for subject, met in preference_met.items():
            if not met:
                penalty += 1
        return penalty


class SameDaySubjectPenalty(BasePenalty):
    """Penalty for scheduling the same subject multiple times on the same day."""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        penalty = 0
        for day, schedule in individual.timetable.items():
            subject_counts = {}
            for subject in schedule.values():
                if subject != "Free":
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1
            penalty += sum(count - 1 for count in subject_counts.values() if count > 1)
        return penalty
    

class ConsecutiveClassesPenalty(BasePenalty):
    """Penalty for having too many consecutive classes."""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        penalty = 0
        for day, schedule in individual.timetable.items():
            consecutive_count = 0
            for slot in schedule.values():
                if slot != "Free":
                    consecutive_count += 1
                else:
                    consecutive_count = 0
                if consecutive_count > 2:
                    penalty += consecutive_count - 2
        return penalty
    

class FreeTimeDistributionPenalty(BasePenalty):
    """Penalty for poorly distributed free time"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        penalty = 0
        for day, schedule in individual.timetable.items():
            free_slots = []
            for i, slot in enumerate(schedule.values()):
                if slot == "Free":
                    free_slots.append(i)
            if len(free_slots) > 1:
                distances = []
                for i in range(len(free_slots) - 1):
                    distances.append(free_slots[i + 1] - free_slots[i])
                penalty += max(distances) - min(distances)
        return penalty
        

class SubjectExhaustionPenalty(BasePenalty):
    """Penalty for not using all subjects"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        used_subjects = set()
        for day in individual.timetable.values():
            for subject in day.values():
                if subject != "Free":
                    used_subjects.add(subject)
        return len(subjects) - len(used_subjects)
    
class BalancePenalty(BasePenalty):
    """Penalty for unbalanced distribution of subjects"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        subject_counts = {}
        for subject in subjects:
            subject_counts[subject] = sum()
        mean_count = sum(subject_counts.values()) / len(subjects)
        return sum((count - mean_count) ** 2 for count in subject_counts.values())
    

class OverallocationPenalty(BasePenalty):
    """Penalty for overallocating subjects instead of free time"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        total_slots = len(individual.timetable) * len(time_slots)
        allocated_slots = sum()
        return max(0, allocated_slots - len(subjects)) * 5
    

class WeeklyOccurrencePenalty(BasePenalty):
    """Penalty for subjects occurring more than once a week"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        penalty = 0
        for subject in subjects:
            occurrences = sum() # TODO
            if occurrences > 1:
                penalty += occurrences - 1
        return penalty


class FreeTimePenalty(BasePenalty):
    """Penalty for not having enough free time"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(self, individual: Individual, preferences: Dict, subjects: List[str], time_slots: List[str]) -> float:
        penalty = 0
        for day, schedule in individual.timetable.items():
            free_slots = []
            for i, slot in enumerate(schedule.values()):
                if slot == "Free":
                    free_slots.append(i)
            if len(free_slots) < 2:
                penalty += 1
        return penalty
    

penalty_objects = [
    PreferencePenalty(weight=5),
    ConsecutiveClassesPenalty(weight=10),
    # FreeTimeDistributionPenalty(weight=3),
    SameDaySubjectPenalty(weight=5),
    SubjectExhaustionPenalty(weight=5),
    # BalancePenalty(weight=10),
    # OverallocationPenalty(weight=3),
    # WeeklyOccurrencePenalty(weight=2),
    FreeTimePenalty(weight=5)
]

