# from math import ceil, inf
from typing import Counter, Dict, List, Optional

from lib.src.models.individual import Individual
from lib.src.models.penalties.penalty import BasePenalty


class PreferencePenalty(BasePenalty):
    """Penalty for not satisfying preferences"""
    
    def __init__(self, weight: float = 10):
        self.weight = weight
    
    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        if preferences is None:
            return 0
        
        penalty = 0
        for subject, pref in preferences.items():
            subject_met = False
            for day, schedule in individual.schedule.items():
                for time, scheduled_subject in schedule.items():
                    if subject == scheduled_subject and pref.get(day) == time:
                        subject_met = True
                        break
                if subject_met:
                    break
            if not subject_met:
                penalty += 1
        
        return penalty * self.weight

class SameDaySubjectPenalty(BasePenalty):
    """Penalty for scheduling the same subject multiple times on the same day."""
    
    def __init__(self, weight: float = 10):
        self.weight = weight
    
    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        penalty = 0
        for day, schedule in individual.schedule.items():
            subject_counts = Counter(subject for subject in schedule.values() if subject != "Free")
            penalty += sum(count - 1 for count in subject_counts.values() if count > 1)
        
        return penalty

class DailyLoadPenalty:
    """Penalty for exceeding the maximum number of classes per day."""

    def __init__(self, weight: float = 5.0) -> None:
        self.weight = weight

    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        penalty = 0

        max_load = len(subjects) // len(time_slots)
        for day, schedule in individual.schedule.items():
            load = sum(1 for slot in schedule.values() if slot != "free")
            if load > max_load:
                penalty += (max_load - load) ** 2
        return penalty


class FreeTimeDistributionPenalty(BasePenalty):
    """Penalty for poorly distributed free time
    Arises when there are too many free slots in a row."""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        penalty = 0
        for day, schedule in individual.schedule.items():
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
    """Penalty for not using all subjects. 
    Arises when there are subjects that are not used in the schedule"""

    def __init__(self, weight: float = 5):
        self.weight = weight

    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        used_subjects = set()
        for day in individual.schedule.values():
            for subject in day.values():
                if subject != "Free":
                    used_subjects.add(subject)
        return len(subjects) - len(used_subjects)


class BalancePenalty(BasePenalty):
    """Penalty for unbalanced distribution of subjects
    Arises when there are subjects that are used more than others"""

    def __init__(self, weight: float = 10):
        self.weight = weight

    def calculate(
    self,
    individual: Individual,
    preferences: Optional[Dict],
    subjects: List[str],
    time_slots: List[str],
    ) -> float:
        subject_counts = {subject: sum(subject == sub for day in individual.schedule.values() for sub in day.values()) for subject in subjects}
        mean_count = sum(subject_counts.values()) // len(subjects)
        return self.weight * sum((count - mean_count) ** 2 for count in subject_counts.values())

penalty_objects = [
    PreferencePenalty(weight=10),
    DailyLoadPenalty(weight=5.0),
    FreeTimeDistributionPenalty(weight=3),
    SameDaySubjectPenalty(weight=5),
    SubjectExhaustionPenalty(weight=5),
    BalancePenalty(weight=3),
]
