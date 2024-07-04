from typing import Dict, List
from lib.src.models.individual import Individual


class Rewards:
    def __init__(self):
        self.reward_functions = [
            (self.preferred_slot_reward, 5),
        ]

    def calculate_total_reward(
        self, individual: Individual, preferences: Dict
    ) -> float:
        """Calculates the total reward for an individual"""
        return sum(
            weight * func(individual, preferences)
            for func, weight in self.reward_functions
        )

    def preferred_slot_reward(self, individual: Individual, preferences: Dict) -> float:
        """Reward scheduling subjects in their preferred slots"""
        reward = 0
        for subject, pref in preferences.items():
            for day, time in pref.items():
                if individual.timetable.get(day).get(time) == subject:
                    reward += 1
        return reward
