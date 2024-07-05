from abc import ABC, abstractmethod
from typing import Dict, List

from lib.src.models.individual import Individual


class BasePenalty(ABC):
    def __init__(self, weight: float):
        self.weight = weight

    @abstractmethod
    def calculate(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Calculates the penalty for the given individual. Child classes must override this method."""
        pass


class Penalties:
    def __init__(self):
        self.penalty_objects: List[BasePenalty] = []

    def register_penalty(self, penalty: BasePenalty):
        self.penalty_objects.append(penalty)

    def calculate_total_penalty(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        total_penalty = 0.0
        for penalty in self.penalty_objects:
            total_penalty += (
                penalty.calculate(individual, preferences, subjects, time_slots)
                * penalty.weight
            )
        return total_penalty
