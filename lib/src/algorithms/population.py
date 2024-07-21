import random
from typing import Dict, List, Optional

from lib.src.models.individual import Individual


class PopulationInitializer:
    def __init__(
        self,
        subjects: List[str],
        days: List[str],
        time_slots: List[str],
        preferences: Optional[Dict]
    ):
        self.subjects = subjects
        self.days = days
        self.time_slots = time_slots
        self.preferences = preferences

    def generate_individual(self, consider_preferences: bool = False) -> Individual:
        """Generate a random individual.
        If consider_preferences is True, the algorithm will try to assign the preferred subject to the preferred time slot.

        Args:
            consider_preferences (bool): Whether to consider preferences or not. Defaults to False.
        """
        schedule = {
            day: {time: "Free" for time in self.time_slots} for day in self.days
        }
        subjects_needed = self.subjects * (
            len(self.days) * len(self.time_slots) // len(self.subjects)
        )
        random.shuffle(subjects_needed)

        if self.preferences is not None and consider_preferences:
            for subject, pref in self.preferences.items():
                for day, time in pref.items():
                    if time is not None:
                        schedule[day][time] = subject
                        if subject in subjects_needed:
                            subjects_needed.remove(subject)

        # Fill remaining slots
        for day in self.days:
            for time in self.time_slots:
                if schedule[day][time] == "Free" and subjects_needed:
                    schedule[day][time] = subjects_needed.pop()

        return Individual(schedule)

    def initialize_population(
        self, population_size: int, preference_adherent_percentage: float
    ) -> List[Individual]:
        preference_adherent_count = int(
            population_size * preference_adherent_percentage
        )
        random_count = population_size - preference_adherent_count

        preference_adherent_individuals = [
            self.generate_individual(consider_preferences=True)
            for _ in range(preference_adherent_count)
        ]
        random_individuals = [
            self.generate_individual(consider_preferences=False)
            for _ in range(random_count)
        ]

        return preference_adherent_individuals + random_individuals
