from typing import Dict, List
from lib.src.models.individual import Individual
from lib.src.models.rewards.reward import BaseReward


class PreffredSlotReward(BaseReward):
    def __init__(self, weight: float):
        self.weight = weight

    def calculate(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Reward scheduling subjects in their preferred slots"""
        reward = 0
        for subject, pref in preferences.items():
            for day, time in pref.items():
                if individual.timetable.get(day).get(time) == subject:
                    reward += 1
        return reward * self.weight


reward_objects = [PreffredSlotReward(1)]
