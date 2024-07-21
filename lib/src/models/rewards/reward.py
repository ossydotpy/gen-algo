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
    def __init__(self, rewards: List[BaseReward] = None) -> None:
        if rewards is None:
            self.rewards = []
        self.rewards = rewards

    def register_reward(self, reward: BaseReward) -> None:
        self.rewards.append(reward)

    def calculate_total_reward(
        self,
        *args, **kwargs
    ) -> float:
        total_reward = sum(reward.calculate(*args, **kwargs)*reward.weight for reward in self.rewards)
        return total_reward
