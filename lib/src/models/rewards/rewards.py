from typing import Dict, List, Optional
from lib.src.models.individual import Individual
from lib.src.models.rewards.reward import BaseReward


class PreffredSlotReward(BaseReward):
    def __init__(self, weight: float):
        self.weight = weight

    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Reward scheduling subjects in their preferred slots"""
        reward = 0
        if preferences is not None:
            for subject, pref in preferences.items():
                for day, time in pref.items():
                    if individual.schedule.get(day).get(time) == subject:
                        reward += 1
        return reward * self.weight
    
class NoSameDayReward(BaseReward):
    def __init__(self, weight: float):
        self.weight = weight

    def calculate(
        self,
        individual: Individual,
        preferences: Optional[Dict],
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Reward no subject scheduled on the same day."""
        reward = 0
        days_with_unique_subjects = 0
        
        for day, schedule in individual.schedule.items():
            subjects_on_day = set()
            for subject in schedule.values():
                if subject in subjects_on_day:
                    break
                subjects_on_day.add(subject)
            else:
                days_with_unique_subjects += 1
        
        total_days = len(individual.schedule)
        reward = (days_with_unique_subjects / total_days) * self.weight
        
        return reward

reward_objects = [PreffredSlotReward(20), NoSameDayReward(30)]
