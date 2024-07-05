from abc import ABC, abstractmethod
from typing import Dict, List

from lib.src.models.individual import Individual


class BaseReward(ABC):
    def __init__(self, weight):
        self.weight = weight

    @abstractmethod
    def calculate(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Calculates the reward for the given individual. Child classes must implement this method."""
        pass


class Rewards:
    def __init__(self) -> None:
        self.rewards = []  # type: List[BaseReward]

    def register_reward(self, reward: BaseReward) -> None:
        self.rewards.append(reward)

    def calculate_total_reward(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        total_reward = 0.0
        for reward in self.rewards:
            total_reward += (
                reward.calculate(individual, preferences, subjects, time_slots)
                * reward.weight
            )
        return total_reward
