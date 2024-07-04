from typing import Dict, List

from lib.src.models.individual import Individual


class Penalties:
    """contains methods to calculate the penalties incured by a single individual."""

    def __init__(self):
        self.penalty_functions = [
            (self.preference_penalty, 5),
            (self.same_day_subject_penalty, 5),
            (self.subject_exhaustion_penalty, 5),
            (self.balance_penalty, 10),
            (self.overallocation_penalty, 3),
            (self.weekly_occurrence_penalty, 2),
            (self.consecutive_classes_penalty, 4),
            (self.free_time_distribution_penalty, 3),
        ]

    def calculate_total_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Tallies the penalties of an individual (timetable)"""
        return sum(
            weight * func(individual, preferences, subjects, time_slots)
            for func, weight in self.penalty_functions
        )

    def preference_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for not satisfying preferences"""
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

    def same_day_subject_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for scheduling the same subject multiple times on the same day."""
        penalty = 0
        for day, schedule in individual.timetable.items():
            subject_counts = {}
            for subject in schedule.values():
                if subject != "Free":
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1
            penalty += sum(count - 1 for count in subject_counts.values() if count > 1)
        return penalty

    def subject_exhaustion_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for not using all subjects"""
        used_subjects = set(
            subject
            for day in individual.timetable.values()
            for subject in day.values()
            if subject != "Free"
        )
        return len(subjects) - len(used_subjects)

    def balance_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for unbalanced distribution of subjects"""
        subject_counts = {
            subject: sum(
                1
                for day in individual.timetable.values()
                for slot in day.values()
                if slot == subject
            )
            for subject in subjects
        }
        mean_count = sum(subject_counts.values()) / len(subjects)
        return sum((count - mean_count) ** 2 for count in subject_counts.values())

    def overallocation_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for overallocating subjects instead of free time"""
        total_slots = len(individual.timetable) * len(time_slots)
        allocated_slots = sum(
            1
            for day in individual.timetable.values()
            for subject in day.values()
            if subject != "Free"
        )
        return max(0, allocated_slots - len(subjects)) * 5

    def weekly_occurrence_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for subjects occurring more than once a week"""
        penalty = 0
        for subject in subjects:
            occurrences = sum(
                1
                for day in individual.timetable.values()
                for slot in day.values()
                if slot == subject
            )
            if occurrences > 1:
                penalty += occurrences - 1
        return penalty

    def consecutive_classes_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for having too many consecutive classes.
        Default count is 2.
        """
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

    def free_time_distribution_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Penalty for poorly distributed free time"""
        penalty = 0
        for day, schedule in individual.timetable.items():
            free_slots = [
                i for i, slot in enumerate(schedule.values()) if slot == "Free"
            ]
            if len(free_slots) > 1:
                distances = [
                    free_slots[i + 1] - free_slots[i]
                    for i in range(len(free_slots) - 1)
                ]
                penalty += max(distances) - min(distances)
        return penalty
